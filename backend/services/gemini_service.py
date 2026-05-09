import os
import json
import re
import base64
from io import BytesIO

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=GEMINI_API_KEY)


def _strip_json(text: str) -> str:
    """Remove markdown code fences and extract JSON."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _detect_mime(raw_bytes: bytes) -> str:
    """Detect image MIME type from magic bytes."""
    if raw_bytes[:4] == b'RIFF' and raw_bytes[8:12] == b'WEBP':
        return "image/webp"
    if raw_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    if raw_bytes[:2] == b'\xff\xd8':
        return "image/jpeg"
    if raw_bytes[:4] == b'GIF8':
        return "image/gif"
    if raw_bytes[:4] == b'<svg' or b'<svg' in raw_bytes[:500]:
        return "image/svg+xml"
    if raw_bytes.lstrip()[:5] == b'<?xml' and b'<svg' in raw_bytes[:1000]:
        return "image/svg+xml"
    return "image/png"


def _image_to_part(image_bytes: bytes) -> types.Part:
    """Convert image bytes to a google.genai Part. Handles SVG, WebP, and all common formats."""
    mime = _detect_mime(image_bytes)
    # SVG: convert to PNG first (Gemini doesn't support SVG)
    if mime == "image/svg+xml":
        try:
            import cairosvg
            png_bytes = cairosvg.svg2png(bytestring=image_bytes)
            return types.Part.from_bytes(data=png_bytes, mime_type="image/png")
        except Exception:
            return types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    # WebP: send raw bytes directly
    if mime == "image/webp":
        return types.Part.from_bytes(data=image_bytes, mime_type=mime)
    # Raster images: try PIL re-encode for safety, fallback to raw
    try:
        from PIL import Image
        img = Image.open(BytesIO(image_bytes))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")
    except Exception:
        return types.Part.from_bytes(data=image_bytes, mime_type=mime)


def call_agent(system_prompt: str, user_message: str, images: list[bytes] | None = None) -> dict:
    """Call Gemini with a system prompt, user message, and optional images. Returns parsed JSON."""
    content_parts = []

    if images:
        for img_bytes in images:
            content_parts.append(_image_to_part(img_bytes))

    content_parts.append(user_message)

    last_error = None
    for attempt in range(3):
        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=content_parts,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_modalities=["TEXT"],
            ),
        )

        # Extract text from response parts (handles mixed content responses)
        raw_text = ""
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.text:
                    raw_text += part.text

        if not raw_text:
            last_error = "Agent returned empty response (no text parts found)"
            continue

        cleaned = _strip_json(raw_text)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            last_error = f"Failed to parse agent response as JSON: {e}\nRaw response:\n{raw_text}"
            continue

    raise ValueError(last_error)
