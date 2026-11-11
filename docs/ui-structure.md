# Crosswalk product structure

Crosswalk is a workbench for an integration engineer. The primary experience
is a quiet sequence of inspectable tasks, not a conversational assistant. Every
screen should answer three questions: what am I looking at, what evidence
supports it, and what decision can I make next?

## Navigation

The product has five stable areas:

1. **Projects** — customer integrations and their current health.
2. **Discover** — import an OpenAPI document and sample responses.
3. **Review queue** — fields that need a human decision.
4. **Mappings** — approved mappings, alternatives, and generated transforms.
5. **Runs** — adapter executions, failures, drift, and repair proposals.

The active project and environment remain visible in the shell. Navigation is
task based and uses plain nouns; there is no chat panel, prompt box, or token
meter in the primary workflow.

## First usable workflow

The first vertical slice is one project from import to an approved mapping:

1. Create a project with a name, source label, and environment.
2. Import an OpenAPI file or URL and attach a representative sample payload.
3. Inspect discovered endpoints and fields. Unsupported schema constructs are
   shown as explicit warnings.
4. Open the review queue. Each row shows the external field, proposed target,
   confidence, evidence, and alternatives.
5. Approve, correct, or leave unresolved with a short rationale.
6. View the approved mapping and export the generated adapter package.

The user can always return to the source evidence. A decision is never hidden
behind a generated explanation or an uninspectable score.

## Screen hierarchy

### Project home

The project home is a work summary: import status, fields discovered, fields
awaiting review, approved mappings, recent runs, and unresolved warnings. The
next action is a prominent task card, while the rest is supporting context.

### Discovery

Discovery is a two-column inspection view. The left column contains the source
document, endpoints, and schema warnings. The right column contains the sample
payload and normalized field list. Selecting a field opens its profile without
leaving the page.

### Review queue

The queue is a dense, keyboard-friendly table with filters for state, reviewer,
action, and confidence. Selecting a row opens a side panel containing evidence,
the proposed target, alternatives, and the decision controls. The table stays
visible while deciding so context is not lost.

### Mapping detail

Mapping detail shows the approved target, transformation steps, source and
target types, enum translation, date and currency handling, decision history,
and generated artifact status. It separates facts from actions.

### Runs and drift

Runs show input, output, duration, and failures. Drift is presented as a change
to a known field or schema, with the affected mapping and suggested repair. A
repair requires the same review pattern as a new mapping.

## Interaction rules

- Use progressive disclosure for evidence; keep the primary row readable.
- Preserve filters and selection after every decision.
- Make destructive actions explicit and reversible where possible.
- Prefer status text and timestamps to decorative badges.
- Show uncertainty as a useful next action, never as a personality or a chat
  response.
- Keep empty states instructional: explain what input is needed and provide
  one direct action.

This structure is deliberately independent of visual styling. Color, type,
motion, and illustration can be selected after the first workflow is usable.
