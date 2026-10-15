import json
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import UnidentifiedImageError

from embed import embed, load

BASE = Path(__file__).parent
SKIP = {p["id"] for p in json.loads((BASE / "data" / "points.json").read_text(encoding="utf-8")) if p.get("skip")}

HEAD = BASE / "data" / "head.npz"
head = np.load(HEAD) if HEAD.exists() else None
if head is None:
    print(f"matcher: {HEAD} not found, accepting every photo")


@dataclass
class MatchResult:
    ok: bool
    score: float = 0.0
    guess: str | None = None
    error: str | None = None


def match(image_bytes: bytes, point_id: str) -> MatchResult:
    try:
        img = load(BytesIO(image_bytes))
    except (UnidentifiedImageError, OSError):
        return MatchResult(ok=False, error="Файл не открылся как фотография. Подойдёт JPG или PNG.")

    if point_id in SKIP or head is None:
        return MatchResult(ok=True, score=1.0, guess=point_id)

    logits = embed([img])[0] @ head["W"].T + head["b"]
    probs = np.exp(logits - logits.max())
    probs /= probs.sum()

    classes = head["classes"].tolist()
    guess = classes[probs.argmax()]
    score = float(probs[classes.index(point_id)])
    ok = guess == point_id and score >= float(head["threshold"])
    return MatchResult(ok=ok, score=score, guess=None if guess == "other" else guess)
