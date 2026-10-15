from collections import Counter

from .models import Feedback, FeedbackKind


def summarize_feedback(items: tuple[Feedback, ...]) -> dict[str, int]:
    counts = Counter(item.kind.value for item in items)
    return {kind.value: counts.get(kind.value, 0) for kind in FeedbackKind}
