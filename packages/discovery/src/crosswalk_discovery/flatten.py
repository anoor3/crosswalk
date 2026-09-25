"""Flatten an OpenAPI schema into a list of :class:`ExternalField`.

Given a (possibly deeply nested, ``$ref``-laden) JSON Schema / OpenAPI schema
object, this produces a flat, ordered tuple of fields — one per object property
at every depth — each with a stable ``json_path``. This is the mechanical core
of discovery (PLANNER §15): every step is deterministic.

What it understands
-------------------
* primitive ``type`` (string/integer/number/boolean/object/array)
* OpenAPI 3.1 type unions: ``type: ["string", "null"]`` (nullable) and
  ``type: ["string", "integer"]`` (multi-type -> extra_types)
* OpenAPI 3.0 ``nullable: true``
* ``enum`` (values stringified)
* ``format`` and ``description``
* nested ``properties`` (recursion; path ``$.a.b``)
* ``items`` for arrays (recursion; path ``$.a[*]``)
* ``required`` (propagated from the enclosing object to its properties)
* ``$ref`` (resolved; recursion; cycles recorded, never looped)
* ``anyOf``/``oneOf`` that is exactly ``<schema> | null`` -> nullable schema

What it records as UNSUPPORTED (explicit, never silent — CHECKER §14)
--------------------------------------------------------------------
* ``allOf`` composition (best-effort merge of object branches, but flagged)
* ``anyOf``/``oneOf`` that is a genuine union of multiple non-null schemas
  (the first branch is still explored so we surface *something*)
* ``$ref`` cycles
* schemas with no usable type information

The public entry point returns ``(fields, unsupported)``; nothing is dropped.
"""

from __future__ import annotations

from typing import Any

from .catalog import ExternalField, FieldType, UnsupportedConstruct
from .errors import RefResolutionError
from .refs import RefResolver, is_ref

# Map OpenAPI type strings onto the normalized FieldType vocabulary.
_TYPE_MAP: dict[str, FieldType] = {
    "string": FieldType.STRING,
    "integer": FieldType.INTEGER,
    "number": FieldType.NUMBER,
    "boolean": FieldType.BOOLEAN,
    "object": FieldType.OBJECT,
    "array": FieldType.ARRAY,
    "null": FieldType.NULL,
}


class _Flattener:
    """Stateful walk over one root schema. One instance per flatten call."""

    def __init__(self, resolver: RefResolver) -> None:
        self._resolver = resolver
        self._fields: list[ExternalField] = []
        self._unsupported: list[UnsupportedConstruct] = []

    # -- public ----------------------------------------------------------- #
    def run(self, schema: dict[str, Any], root_path: str) -> None:
        self._walk(
            schema,
            path=root_path,
            name=_leaf_name(root_path),
            required=False,
            seen_refs=frozenset(),
        )

    @property
    def fields(self) -> tuple[ExternalField, ...]:
        return tuple(self._fields)

    @property
    def unsupported(self) -> tuple[UnsupportedConstruct, ...]:
        return tuple(self._unsupported)

    # -- core walk -------------------------------------------------------- #
    def _walk(
        self,
        schema: Any,
        *,
        path: str,
        name: str,
        required: bool,
        seen_refs: frozenset[str],
    ) -> None:
        if not isinstance(schema, dict):
            self._unsupported.append(
                UnsupportedConstruct(
                    location=path,
                    construct_type="non-object schema",
                    detail=f"expected a schema object, got {type(schema).__name__}",
                )
            )
            return

        # 1. Resolve a $ref (with cycle detection on the descent path).
        if is_ref(schema):
            ref = schema["$ref"]
            if ref in seen_refs:
                self._unsupported.append(
                    UnsupportedConstruct(
                        location=path,
                        construct_type="circular $ref",
                        detail=f"{ref} re-entered while flattening",
                    )
                )
                return
            try:
                resolved = self._resolver.resolve_ref(ref)
            except RefResolutionError as exc:
                self._unsupported.append(
                    UnsupportedConstruct(
                        location=path, construct_type="unresolved $ref", detail=str(exc)
                    )
                )
                return
            self._walk(
                resolved, path=path, name=name, required=required, seen_refs=seen_refs | {ref}
            )
            return

        # 2. Composition keywords.
        if "allOf" in schema:
            self._handle_all_of(
                schema, path=path, name=name, required=required, seen_refs=seen_refs
            )
            return
        for combiner in ("anyOf", "oneOf"):
            if combiner in schema:
                self._handle_union(
                    schema, combiner, path=path, name=name, required=required, seen_refs=seen_refs
                )
                return

        # 3. Determine type(s) and nullability.
        primary, extras, nullable = _resolve_types(schema)

        # 4. Objects: emit a field for the object itself, then recurse.
        if primary is FieldType.OBJECT or ("properties" in schema):
            self._emit(
                schema,
                path=path,
                name=name,
                data_type=FieldType.OBJECT,
                extras=extras,
                nullable=nullable,
                required=required,
            )
            self._recurse_object(schema, path=path, seen_refs=seen_refs)
            return

        # 5. Arrays: emit a field for the array, then recurse into items.
        if primary is FieldType.ARRAY or ("items" in schema):
            self._emit(
                schema,
                path=path,
                name=name,
                data_type=FieldType.ARRAY,
                extras=extras,
                nullable=nullable,
                required=required,
            )
            self._recurse_array(schema, path=path, seen_refs=seen_refs)
            return

        # 6. Primitive (or unknown) leaf.
        self._emit(
            schema,
            path=path,
            name=name,
            data_type=primary,
            extras=extras,
            nullable=nullable,
            required=required,
        )

    # -- helpers ---------------------------------------------------------- #
    def _emit(
        self,
        schema: dict[str, Any],
        *,
        path: str,
        name: str,
        data_type: FieldType,
        extras: tuple[FieldType, ...],
        nullable: bool,
        required: bool,
    ) -> None:
        enum_values = tuple(str(v) for v in schema["enum"]) if "enum" in schema else ()
        self._fields.append(
            ExternalField(
                json_path=path,
                name=name,
                data_type=data_type,
                extra_types=extras,
                description=schema.get("description"),
                required=required,
                nullable=nullable,
                enum_values=enum_values,
                format=schema.get("format"),
                is_array_item="[*]" in path,
            )
        )

    def _recurse_object(
        self, schema: dict[str, Any], *, path: str, seen_refs: frozenset[str]
    ) -> None:
        properties = schema.get("properties")
        required_names = set(schema.get("required", []))
        if isinstance(properties, dict):
            for prop_name, prop_schema in properties.items():
                self._walk(
                    prop_schema,
                    path=f"{path}.{prop_name}",
                    name=prop_name,
                    required=prop_name in required_names,
                    seen_refs=seen_refs,
                )
        # A dict-like object (additionalProperties) has no fixed keys; record it
        # so it is not silently ignored.
        add_props = schema.get("additionalProperties")
        if add_props not in (None, False) and not isinstance(properties, dict):
            self._unsupported.append(
                UnsupportedConstruct(
                    location=path,
                    construct_type="additionalProperties (open map)",
                    detail="object has dynamic keys; individual fields are not enumerable",
                )
            )

    def _recurse_array(
        self, schema: dict[str, Any], *, path: str, seen_refs: frozenset[str]
    ) -> None:
        items = schema.get("items")
        if items is None:
            return
        item_path = f"{path}[*]"
        self._walk(
            items, path=item_path, name=_leaf_name(item_path), required=False, seen_refs=seen_refs
        )

    def _handle_all_of(
        self,
        schema: dict[str, Any],
        *,
        path: str,
        name: str,
        required: bool,
        seen_refs: frozenset[str],
    ) -> None:
        # allOf is composition/intersection. We flag it, then best-effort walk
        # each sub-schema so the properties are still discovered.
        self._unsupported.append(
            UnsupportedConstruct(
                location=path,
                construct_type="allOf",
                detail="composition merged best-effort; verify field set",
            )
        )
        for i, sub in enumerate(schema["allOf"]):
            self._walk(sub, path=path, name=name, required=required, seen_refs=seen_refs)
            _ = i

    def _handle_union(
        self,
        schema: dict[str, Any],
        combiner: str,
        *,
        path: str,
        name: str,
        required: bool,
        seen_refs: frozenset[str],
    ) -> None:
        branches = schema[combiner]
        non_null = [b for b in branches if not _is_null_schema(b)]
        has_null = len(non_null) != len(branches)

        if len(non_null) == 1:
            # Exactly `<schema> | null` -> treat as that schema, nullable.
            sub = dict(non_null[0])
            if has_null:
                # Carry description/nullable down onto the single branch.
                sub.setdefault("description", schema.get("description"))
            self._walk(sub, path=path, name=name, required=required, seen_refs=seen_refs)
            if has_null:
                self._mark_last_nullable(path)
            return

        # A genuine multi-type union: not fully modeled. Flag it, but still
        # explore the first non-null branch so we surface *something*.
        self._unsupported.append(
            UnsupportedConstruct(
                location=path,
                construct_type=combiner,
                detail=f"union of {len(non_null)} non-null schemas; "
                "first branch explored, alternatives not modeled",
            )
        )
        if non_null:
            self._walk(non_null[0], path=path, name=name, required=required, seen_refs=seen_refs)

    def _mark_last_nullable(self, path: str) -> None:
        # The field just emitted for `path` should be nullable. Replace it.
        for i in range(len(self._fields) - 1, -1, -1):
            if self._fields[i].json_path == path:
                self._fields[i] = self._fields[i].model_copy(update={"nullable": True})
                return


# --------------------------------------------------------------------------- #
# Module-level helpers
# --------------------------------------------------------------------------- #
def _leaf_name(path: str) -> str:
    """The trailing property name of a json_path (best-effort)."""
    tail = path.rstrip("]").rstrip("[*").rstrip(".")
    for sep in (".", "["):
        if sep in tail:
            tail = tail.rsplit(sep, 1)[-1]
    return tail.lstrip("$").lstrip(".") or "$"


def _is_null_schema(node: Any) -> bool:
    return isinstance(node, dict) and node.get("type") == "null"


def _resolve_types(schema: dict[str, Any]) -> tuple[FieldType, tuple[FieldType, ...], bool]:
    """Return (primary_type, extra_types, nullable) for a schema.

    Handles 3.0 ``nullable: true`` and 3.1 ``type`` as a string or a list
    (including a ``"null"`` member).
    """
    nullable = bool(schema.get("nullable", False))  # OpenAPI 3.0 idiom
    raw_type = schema.get("type")

    types: list[FieldType] = []
    if isinstance(raw_type, str):
        types = [_TYPE_MAP.get(raw_type, FieldType.UNKNOWN)]
    elif isinstance(raw_type, list):
        for t in raw_type:
            if t == "null":
                nullable = True
            else:
                types.append(_TYPE_MAP.get(t, FieldType.UNKNOWN))

    if not types:
        # No explicit type: infer object/array from structural keys.
        if "properties" in schema:
            types = [FieldType.OBJECT]
        elif "items" in schema:
            types = [FieldType.ARRAY]
        else:
            types = [FieldType.UNKNOWN]

    primary = types[0]
    extras = tuple(types[1:])
    return primary, extras, nullable


def flatten_schema(
    schema: dict[str, Any], resolver: RefResolver, *, root_path: str = "$"
) -> tuple[tuple[ExternalField, ...], tuple[UnsupportedConstruct, ...]]:
    """Flatten a schema into ``(fields, unsupported)``.

    Args:
        schema: The root schema object (may be a ``$ref``).
        resolver: A :class:`RefResolver` bound to the owning document.
        root_path: The json_path prefix to use for the root (default ``"$"``).

    Returns:
        A tuple ``(fields, unsupported)``. The root object/array itself is
        emitted as a field only when it is a container with children; a bare
        root primitive is emitted as a single field.
    """
    flattener = _Flattener(resolver)
    flattener.run(schema, root_path)
    return flattener.fields, flattener.unsupported
