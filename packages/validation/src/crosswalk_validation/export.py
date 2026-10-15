import json

from .models import ValidationSession


def export_session(session: ValidationSession) -> str:
    return json.dumps(session.model_dump(mode="json"), sort_keys=True)
