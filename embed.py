import os
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageOps

MODEL = Path(os.environ.get("EMBED_MODEL", Path(__file__).parent / "models" / "dinov2-small.onnx"))
DIM = 384

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_session = None


def load(path) -> Image.Image:
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def preprocess(img: Image.Image) -> np.ndarray:
    w, h = img.size
    scale = 256 / min(w, h)
    img = img.resize((round(w * scale), round(h * scale)), Image.Resampling.BICUBIC)
    w, h = img.size
    left, top = (w - 224) // 2, (h - 224) // 2
    img = img.crop((left, top, left + 224, top + 224))
    x = (np.asarray(img, dtype=np.float32) / 255 - MEAN) / STD
    return x.transpose(2, 0, 1)


def embed(images: list[Image.Image]) -> np.ndarray:
    global _session
    if _session is None:
        _session = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    batch = np.stack([preprocess(img) for img in images])
    cls = _session.run(None, {"pixel_values": batch})[0][:, 0]
    return cls / np.linalg.norm(cls, axis=1, keepdims=True)
