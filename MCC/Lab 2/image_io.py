# file: image_io.py

import numpy as np
from PIL import Image


def read_grayscale_image(path: str) -> np.ndarray:
    """
    зчитує зображення, повертає матрицю float у [0, 1]
    """
    img = Image.open(path).convert("L")      # L - grayscale
    arr = np.asarray(img, dtype=np.float64)
    arr /= 255.0
    return arr


def save_grayscale_image(path: str, matrix: np.ndarray) -> None:
    """
    зберігає матрицю (float або int) як 8-бітне зображення,значення матриці обрізаються до [0, 1] перед масштабуванням
    """
    mat = np.asarray(matrix, dtype=np.float64)
    mat = np.clip(mat, 0.0, 1.0)
    img_uint8 = (mat * 255.0).round().astype(np.uint8)
    img = Image.fromarray(img_uint8, mode="L")
    img.save(path)
