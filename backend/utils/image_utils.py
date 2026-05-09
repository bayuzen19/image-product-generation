import base64
from io import BytesIO
from PIL import Image


def bytes_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


def resize_image(image_bytes: bytes, max_size: tuple[int, int] = (1024, 1024)) -> bytes:
    """Resize image to fit within max dimensions while preserving aspect ratio."""
    img = Image.open(BytesIO(image_bytes))
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    buf = BytesIO()
    img_format = img.format or "PNG"
    img.save(buf, format=img_format)
    return buf.getvalue()
