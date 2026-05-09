from services.gemini_service import _image_to_part
from services.image_service import _image_bytes_to_part

svg = b'<svg width="10" height="10"><rect fill="red"/></svg>'

p1 = _image_to_part(svg)
print("gemini_service mime:", p1.inline_data.mime_type, "bytes:", len(p1.inline_data.data))

p2 = _image_bytes_to_part(svg)
print("image_service mime:", p2.inline_data.mime_type, "bytes:", len(p2.inline_data.data))

print("OK - SVG converted to PNG")
