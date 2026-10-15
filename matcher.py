from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError


@dataclass
class MatchResult:
    ok: bool
    score: float = 0.0
    guess: str | None = None
    error: str | None = None


def match(image_bytes: bytes, point_id: str) -> MatchResult:
    try:
        Image.open(BytesIO(image_bytes)).verify()
    except (UnidentifiedImageError, OSError):
        return MatchResult(ok=False, error="Файл не открылся как фотография. Подойдёт JPG или PNG.")

    return MatchResult(ok=True, score=1.0, guess=point_id)
