import os
import base64
from io import BytesIO

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
IMAGE_MODEL = os.getenv("GEMINI_MODEL", "nano-banana-pro-preview")

client = genai.Client(api_key=GEMINI_API_KEY)


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


def _image_bytes_to_part(raw_bytes: bytes, filename: str | None = None) -> types.Part:
    """Convert raw image bytes to a google.genai Part. Handles SVG, WebP, and all common formats."""
    mime = _detect_mime(raw_bytes)
    # SVG: convert to PNG first (Gemini doesn't support SVG)
    if mime == "image/svg+xml":
        try:
            import cairosvg
            png_bytes = cairosvg.svg2png(bytestring=raw_bytes)
            return types.Part.from_bytes(data=png_bytes, mime_type="image/png")
        except Exception:
            return types.Part.from_bytes(data=raw_bytes, mime_type="image/png")
    # WebP: send raw bytes directly
    if mime == "image/webp":
        return types.Part.from_bytes(data=raw_bytes, mime_type=mime)
    # Raster images: try PIL re-encode for safety, fallback to raw
    try:
        from PIL import Image
        img = Image.open(BytesIO(raw_bytes))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")
    except Exception:
        return types.Part.from_bytes(data=raw_bytes, mime_type=mime)


def generate_image(
    prompt: str,
    product_image_bytes: bytes | None = None,
    magazine_mode: bool = False,
    product_info: dict | None = None,
    filename: str | None = None,
    logo_image_bytes: bytes | None = None,
    model_image_bytes: bytes | None = None,
    scenic_background: bool = False,
) -> dict:
    """Generate a mockup image. If magazine_mode=True, generates a magazine-style layout."""
    try:
        contents = []

        # Extract actual product color from pipeline analysis
        product_color = ""
        if product_info:
            analysis_data = product_info.get("analysis", {})
            if isinstance(analysis_data, dict):
                product_obj = analysis_data.get("product", {})
                if isinstance(product_obj, dict):
                    product_color = product_obj.get("color", "")

        color_note = f" The product color is {product_color.upper()} — keep it {product_color.upper()}, do NOT change the color." if product_color else ""

        # Add the product image as reference if provided
        if product_image_bytes:
            contents.append(_image_bytes_to_part(product_image_bytes, filename))
            contents.append(f"IMAGE 1 ABOVE: This is the EXACT product. Reproduce THIS EXACT product in your output — same shape, same cap, same color, same proportions.{color_note}")

        # Add the logo image as separate reference
        if logo_image_bytes:
            contents.append(_image_bytes_to_part(logo_image_bytes))
            contents.append(
                "IMAGE 2 ABOVE: This is the EXACT brand logo/emblem. You MUST reproduce this logo PIXEL-PERFECTLY as shown — same icon, same crest, same emblem shape, same colors, same layout. "
                "If the logo is an EMBLEM or CREST (like a shield, badge, circular seal, or illustrated mark), you MUST reproduce that EXACT visual emblem — do NOT replace it with plain text of the brand name. "
                "The logo is a VISUAL IMAGE, not just text. Keep every visual detail: icons, crowns, shields, animals, stars, borders, shapes. "
                "NEVER create, invent, redesign, simplify, or replace the logo with generated text. "
                "NEVER substitute the logo with just the brand name written in a font — the logo IMAGE must appear as-is."
            )

        # Add the fashion model image as reference
        model_instruction = ""
        if model_image_bytes:
            img_label = "IMAGE 3" if logo_image_bytes else "IMAGE 2"
            contents.append(_image_bytes_to_part(model_image_bytes))
            contents.append(
                f"{img_label} ABOVE: This is the FASHION MODEL reference photo — THIS IS THE PERSON WHO MUST APPEAR IN THE OUTPUT. "
                f"CRITICAL IDENTITY RULE: The generated image MUST show THIS EXACT PERSON — you must COPY their face from this photo. "
                f"Same FACE (exact facial structure, jawline, cheekbones, eyes, nose, lips, eyebrows), "
                f"same SKIN TONE (exact complexion — do not lighten, darken, or change), "
                f"same HAIR (exact hairstyle, hair color, hair length, hair texture), "
                f"same GLASSES (if they wear glasses, keep glasses; if no glasses, no glasses). "
                f"Do NOT generate a RANDOM or DIFFERENT person. Do NOT use a generic stock model face. "
                f"The output person must be RECOGNIZABLY IDENTICAL to {img_label}. "
                f"If you cannot reproduce the exact face, it is better to make the face very similar than to use a completely different person."
            )

            # Extract model interaction info from pipeline
            model_scene = {}
            model_direction = {}
            model_info = {}
            if product_info:
                analysis_data = product_info.get("analysis", {})
                if isinstance(analysis_data, dict):
                    model_info = analysis_data.get("fashion_model", {})
                prod_data = product_info.get("product", {})
                if isinstance(prod_data, dict):
                    model_scene = prod_data.get("model_scene", {})
                editor_data = product_info.get("editor", {})
                if isinstance(editor_data, dict):
                    model_direction = editor_data.get("model_direction", {})

            model_parts = []
            if model_scene.get("has_model"):
                if model_scene.get("model_action"):
                    model_parts.append(f"Model action: {model_scene['model_action']}")
                if model_scene.get("model_pose"):
                    model_parts.append(f"Model pose: {model_scene['model_pose']}")
                if model_scene.get("product_visibility"):
                    model_parts.append(f"Product visibility: {model_scene['product_visibility']}")
                if model_scene.get("environment"):
                    model_parts.append(f"Environment: {model_scene['environment']}")
                if model_scene.get("camera_framing"):
                    model_parts.append(f"Camera framing: {model_scene['camera_framing']}")
            if model_direction.get("has_model"):
                if model_direction.get("key_light_on_model"):
                    model_parts.append(f"Model lighting: {model_direction['key_light_on_model']}")
                if model_direction.get("camera_for_model"):
                    model_parts.append(f"Model camera: {model_direction['camera_for_model']}")
                if model_direction.get("motion_treatment"):
                    model_parts.append(f"Motion: {model_direction['motion_treatment']}")

            face_match_instruction = (
                f"\n\nMODEL IDENTITY (THE MOST IMPORTANT RULE — HIGHER PRIORITY THAN EVERYTHING ELSE): "
                f"The person in the output image MUST be the EXACT SAME PERSON as {img_label}. "
                f"This is NON-NEGOTIABLE — if the face doesn't match, the entire image is a FAILURE. "
                f"\n\nFACE COPY CHECKLIST (check every item): "
                f"- FACE SHAPE: Same jawline, same cheekbone structure, same chin shape as {img_label}. "
                f"- EYES: Same eye shape, same eye size, same eye color as {img_label}. "
                f"- NOSE: Same nose shape, same nose size as {img_label}. "
                f"- LIPS: Same lip shape, same lip fullness as {img_label}. "
                f"- EYEBROWS: Same eyebrow shape and thickness as {img_label}. "
                f"- SKIN: Same skin tone and complexion as {img_label} — do NOT change ethnicity. "
                f"- HAIR: Same hairstyle, same hair color, same hair length as {img_label}. "
                f"- GLASSES: If {img_label} wears glasses, the output must have glasses. If no glasses, no glasses. "
                f"- AGE: Same approximate age as {img_label}. "
                f"- GENDER: Same gender as {img_label}. "
                f"\nDo NOT substitute with a DIFFERENT person. Do NOT generate a RANDOM model. "
                f"Do NOT use a generic attractive face — use THE EXACT FACE from {img_label}. "
                f"Look at {img_label} carefully and REPRODUCE that specific person."
            )

            hand_instruction = (
                "\n\nHAND & BODY REALISM (CRITICAL): "
                "The model's hands must have exactly 5 fingers each, natural proportions, and correct anatomy. "
                "Hands should be relaxed and natural — NOT gripping unnaturally, NOT fused together, NOT oversized. "
                "If the model holds the product, show a NATURAL grip — like a real person casually holding it. "
                "All body proportions must be anatomically correct and photorealistic."
            )

            if model_parts:
                model_instruction = (
                    "FASHION MODEL DIRECTION:\n" + "\n".join(model_parts) +
                    face_match_instruction + hand_instruction
                )
            else:
                interaction_desc = model_info.get("interaction_description", "model naturally interacting with the product")
                model_instruction = (
                    f"FASHION MODEL DIRECTION:\nThe model must be shown {interaction_desc}."
                    + face_match_instruction + hand_instruction
                )

        logo_instruction = ""
        
        # Detect if product is wearable (shoes, clothing, accessories) — changes how model interacts
        is_wearable = False
        wearable_type = ""
        if model_image_bytes and product_info:
            analysis_data = product_info.get("analysis", {})
            if isinstance(analysis_data, dict):
                product_obj = analysis_data.get("product", {})
                product_type = ""
                if isinstance(product_obj, dict):
                    product_type = (product_obj.get("type", "") or "").lower()
                model_data = analysis_data.get("fashion_model", {})
                interaction_type = ""
                if isinstance(model_data, dict):
                    interaction_type = (model_data.get("interaction_type", "") or "").lower()
                
                wearable_keywords = ["shoe", "sneaker", "boot", "sandal", "heel", "slipper", 
                                     "clothing", "shirt", "jacket", "dress", "pants", "jeans",
                                     "hat", "cap", "watch", "bracelet", "necklace", "ring",
                                     "glasses", "sunglasses", "backpack", "bag"]
                for kw in wearable_keywords:
                    if kw in product_type:
                        is_wearable = True
                        wearable_type = kw
                        break
                if not is_wearable and interaction_type in ("wearing", "carrying"):
                    is_wearable = True
                    wearable_type = interaction_type

        # Strengthen model_instruction for wearable products
        if is_wearable and model_instruction:
            model_instruction += (
                f"\n\nWEARABLE PRODUCT (CRITICAL): This product is a WEARABLE item ({wearable_type}). "
                "The model MUST be WEARING or USING this product on their body — NOT holding it, NOT standing next to it. "
                "For shoes/sneakers: the model wears them on their feet, shown walking, running, or posing. "
                "For clothing: the model wears it on their body. "
                "For bags: the model carries it on shoulder/hand. "
                "For watches/jewelry: shown on wrist/neck/hand. "
                "The product must be CLEARLY VISIBLE on the model's body. "
                "Do NOT place the product standing separately on the ground next to the model."
            )

        if logo_image_bytes:
            # Extract logo overlay info from product_info (pipeline results)
            # Determine logo usage mode from analysis agent
            logo_mode = "label"  # default to label
            logo_overlay = {}
            if product_info:
                analysis_data = product_info.get("analysis", {})
                if isinstance(analysis_data, dict):
                    logo_usage = analysis_data.get("logo_usage", {})
                    if isinstance(logo_usage, dict):
                        logo_mode = logo_usage.get("mode", "label")

                # Check prompt agent's logo_overlay
                prompt_data = product_info.get("prompt", {})
                if isinstance(prompt_data, dict):
                    logo_overlay = prompt_data.get("logo_overlay", {})

                # Fallback: check product agent's logo_overlay
                if not logo_overlay or not logo_overlay.get("enabled"):
                    prod_data = product_info.get("product", {})
                    if isinstance(prod_data, dict):
                        logo_overlay = prod_data.get("logo_overlay", {})

                # Fallback: check analysis agent's logo_usage for overlay info
                if not logo_overlay or not logo_overlay.get("enabled"):
                    if isinstance(analysis_data, dict):
                        logo_usage = analysis_data.get("logo_usage", {})
                        if logo_usage.get("mode") in ("overlay", "both"):
                            logo_overlay = {
                                "enabled": True,
                                "position": logo_usage.get("overlay_position", "top-left"),
                            }

            overlay_enabled = logo_overlay.get("enabled", False) if logo_overlay else False
            overlay_position = logo_overlay.get("position", "top-left") if logo_overlay else "top-left"
            brand_name = logo_overlay.get("brand_name", "") if logo_overlay else ""

            # Build position description map
            position_map = {
                "top-left": "at the TOP-LEFT corner of the image, approximately 5% from the left edge and 5% from the top edge",
                "top-center": "at the TOP-CENTER of the image, centered horizontally and approximately 5% from the top edge",
                "top-right": "at the TOP-RIGHT corner of the image, approximately 5% from the right edge and 5% from the top edge",
                "bottom-left": "at the BOTTOM-LEFT corner of the image, approximately 5% from the left edge and 5% from the bottom edge",
                "bottom-center": "at the BOTTOM-CENTER of the image, centered horizontally and approximately 5% from the bottom edge",
                "bottom-right": "at the BOTTOM-RIGHT corner of the image, approximately 5% from the right edge and 5% from the bottom edge",
            }

            # Decide based on logo_mode: label, overlay, or both
            needs_label = logo_mode in ("label", "both")
            needs_overlay = logo_mode == "overlay" or (logo_mode == "both" and overlay_enabled)

            # For pure overlay mode (rare - only when product is fully branded already)
            if logo_mode == "overlay" and overlay_enabled and overlay_position and overlay_position != "none":
                pos_desc = position_map.get(overlay_position, position_map["top-left"])
                brand_ref = f"'{brand_name}' " if brand_name else ""
                logo_instruction = (
                    f"A second reference image (IMAGE 2) shows the EXACT logo/brand mark. "
                    f"You MUST reproduce this logo EXACTLY as shown — same font, same icon, same colors, same layout. "
                    f"NEVER create, invent, or redesign the logo. NEVER guess or make up text — copy ONLY what is visible in IMAGE 2. "
                    f"Do NOT change, simplify, or redesign the logo in any way. "
                    f"Place the {brand_ref}logo as an OVERLAY {pos_desc}. "
                    f"The logo should be clearly visible, properly sized (not too small, not too large), "
                    f"and positioned precisely at the specified location like a magazine masthead or brand watermark. "
                )
            else:
                # Label mode: extract product shape and label details from pipeline
                product_shape = ""
                label_position = ""
                label_note = ""
                logo_shape = ""
                if product_info:
                    analysis_data = product_info.get("analysis", {})
                    prod_data = product_info.get("product", {})
                    if isinstance(analysis_data, dict):
                        product_obj = analysis_data.get("product", {})
                        if isinstance(product_obj, dict):
                            product_shape = product_obj.get("shape", "")
                        logos_list = analysis_data.get("logos", [])
                        if logos_list and isinstance(logos_list, list) and isinstance(logos_list[0], dict):
                            logo_shape = logos_list[0].get("shape", "")
                    if isinstance(prod_data, dict):
                        label_note = prod_data.get("label_note", "")
                        layouts = prod_data.get("logo_layout", [])
                        if layouts and isinstance(layouts, list) and isinstance(layouts[0], dict):
                            label_position = layouts[0].get("position", "")

                # Build shape-aware label instruction
                is_cylindrical = any(kw in product_shape.lower() for kw in ["cylindrical", "cylinder", "round", "tube"])
                is_tall_narrow = any(kw in product_shape.lower() for kw in ["cylindrical", "cylinder", "round", "tube", "tall", "narrow", "slim", "elongated", "vertical"])

                # Check recommended orientation from analysis agent
                recommended_orientation = ""
                if product_info:
                    analysis_data = product_info.get("analysis", {})
                    if isinstance(analysis_data, dict):
                        logos_list = analysis_data.get("logos", [])
                        if logos_list and isinstance(logos_list, list) and isinstance(logos_list[0], dict):
                            recommended_orientation = logos_list[0].get("recommended_orientation", "")

                # Check label placement from analysis
                label_placement = ""
                label_style = ""
                if product_info:
                    analysis_data = product_info.get("analysis", {})
                    if isinstance(analysis_data, dict):
                        logo_usage = analysis_data.get("logo_usage", {})
                        if isinstance(logo_usage, dict):
                            label_placement = logo_usage.get("label_placement", "")
                            label_style = logo_usage.get("label_style", "")

                # Only rotate vertical if explicitly recommended by analysis agent
                should_rotate_vertical = recommended_orientation == "rotate_90_vertical"
                is_vertical_logo = recommended_orientation == "vertical_as_is"

                # 3D surface conformity instruction — logo must warp to match product geometry
                surface_conform = (
                    "CRITICAL 3D SURFACE RULE: The logo MUST be WARPED and DEFORMED to perfectly conform to the product's 3D surface shape. "
                    "It should NOT look like a flat image pasted on — it must look like it was physically printed/adhered onto the curved surface. "
                    "Apply proper perspective distortion, foreshortening at edges, and surface curvature so the logo follows the product's geometry exactly. "
                    "The logo must also match the product's LIGHTING — same highlights, same shadows, same reflections. "
                    "If light hits the bottle from the left, the logo text should also be brighter on the left. "
                    "Think of it as a REAL PHOTOGRAPH of a product that already has this label printed on it during manufacturing. "
                )

                if should_rotate_vertical:
                    wrap_instruction = (
                        "ROTATE the logo 90 degrees so it reads VERTICALLY along the product height. "
                    )
                    if is_cylindrical:
                        wrap_instruction += (
                            "The rotated logo MUST curve with the bottle's cylindrical surface — the edges of the logo should bend away from the viewer "
                            "following the round cross-section of the bottle. Apply realistic barrel distortion. "
                        )
                elif is_vertical_logo:
                    wrap_instruction = (
                        "The logo is VERTICAL/TALL — place it VERTICALLY along the product height WITHOUT rotating. "
                        "The logo should run top-to-bottom on the front face of the product, like a tall label strip. "
                    )
                    if is_cylindrical:
                        wrap_instruction += (
                            "The vertical logo MUST follow the bottle's curved surface — the left and right edges of the logo should curve inward "
                            "following the cylinder's round shape, creating a realistic wrapped-on-surface appearance. "
                        )
                elif is_cylindrical:
                    wrap_instruction = (
                        "The logo MUST WRAP HORIZONTALLY around the cylindrical surface with realistic perspective curvature. "
                        "The left and right edges of the logo should visibly curve AWAY from the viewer, following the bottle's round cross-section. "
                        "The center of the logo faces the camera while the edges foreshorten and bend — exactly like a real product label on a round bottle. "
                        "Apply slight barrel distortion to the logo shape so it conforms to the cylinder geometry. "
                    )
                else:
                    wrap_instruction = (
                        "The logo MUST look physically PRINTED/STUCK on the product surface — like a real sticker or label. "
                        "It should have proper perspective distortion matching the product's angle, tilt, and surface curvature. "
                        "If the surface is curved or angled, the logo must warp accordingly — no flat pasting. "
                    )

                label_pos_text = f"Position on product: {label_placement or label_position}. " if (label_placement or label_position) else ""
                label_style_text = f"Label style: {label_style}. " if label_style else ""

                logo_instruction = (
                    f"Apply the logo from IMAGE 2 as a LABEL/STICKER directly onto the product surface. "
                    f"CRITICAL: reproduce the logo EXACTLY as shown in IMAGE 2 — same text, same font, same icon, same colors. "
                    f"NEVER create, invent, or make up any logo text. Copy ONLY what is visible in IMAGE 2. "
                    f"The logo must look PHYSICALLY PRINTED on the product — not floating or hovering. "
                    f"{surface_conform}{wrap_instruction}{label_pos_text}{label_style_text}"
                )

                # In "both" mode, add a small overlay instruction too
                if logo_mode == "both" and overlay_enabled and overlay_position and overlay_position != "none":
                    pos_desc = position_map.get(overlay_position, position_map["top-left"])
                    logo_instruction += (
                        f"ADDITIONALLY, place a SMALL version of the same logo as a subtle brand watermark OVERLAY {pos_desc}. "
                    )

        # Extract scene info from pipeline for richer context
        scene_headline = ""
        scene_atmosphere = ""
        scene_surface = ""
        scene_props = ""
        scene_bg_description = ""
        editor_lighting = ""
        editor_camera = ""
        editor_dof = ""
        editor_atmo = ""
        if product_info:
            prod_data = product_info.get("product", {})
            if isinstance(prod_data, dict):
                scene_data = prod_data.get("scene", {})
                if isinstance(scene_data, dict):
                    scene_headline = scene_data.get("headline", "")
                    scene_atmosphere = scene_data.get("atmosphere", "")
                    scene_surface = scene_data.get("surface", "")
                    scene_bg_description = scene_data.get("background_description", "")
                    props_list = scene_data.get("props", [])
                    if props_list and isinstance(props_list, list):
                        scene_props = ", ".join(props_list)

            editor_data = product_info.get("editor", {})
            if isinstance(editor_data, dict):
                editor_lighting = editor_data.get("lighting_setup", "")
                editor_camera = editor_data.get("camera_angle", "")
                editor_dof = editor_data.get("depth_of_field", "")
                editor_atmo = editor_data.get("atmosphere_effects", "")

        # Build the rich scene block that the image model should follow
        scene_block = ""
        if scene_headline or scene_surface or scene_bg_description:
            scene_parts = []
            if scene_headline:
                scene_parts.append(f"SCENE: \"{scene_headline}\"")
            if scene_surface:
                if is_wearable and model_instruction:
                    scene_parts.append(f"The model stands on {scene_surface}.")
                else:
                    scene_parts.append(f"The product stands on {scene_surface}.")
            if scene_props:
                scene_parts.append(f"Near the product: {scene_props}.")
            if scene_bg_description:
                scene_parts.append(f"Background: {scene_bg_description}")
            if scene_atmosphere:
                scene_parts.append(f"Atmosphere: {scene_atmosphere}.")
            if editor_lighting:
                scene_parts.append(f"Lighting: {editor_lighting}")
            if editor_camera:
                scene_parts.append(f"Camera: {editor_camera}.")
            if editor_dof:
                scene_parts.append(f"Depth of field: {editor_dof}.")
            if editor_atmo and editor_atmo.lower() != "none":
                scene_parts.append(f"Effects: {editor_atmo}.")
            scene_block = "\n".join(scene_parts)

        # Photorealism integration block — prevents composited/edited look
        photorealism_block = (
            "\n\nPHOTOREALISM (CRITICAL — THIS IS THE #1 PRIORITY):\n"
            "This must look like a SINGLE REAL PHOTOGRAPH taken by a professional photographer with ONE camera in ONE location.\n"
            "It must NOT look like separate elements composited together in Photoshop.\n\n"
            "LIGHTING COHERENCE: Every element (product, model, surface, background, props) must be lit by the SAME light source.\n"
            "- If the main light comes from the LEFT, ALL shadows must fall to the RIGHT — on the product, on the model, on the ground.\n"
            "- The color temperature of light must be IDENTICAL across all elements — if warm golden light hits the background, the same warm golden light hits the product and model.\n"
            "- Specular highlights on the product must match the light direction hitting the model and environment.\n\n"
            "SHADOW INTEGRATION: Objects must cast NATURAL shadows that CONNECT them to the surface they stand/sit on.\n"
            "- Contact shadows: dark, soft shadows directly where the product/model TOUCHES the surface.\n"
            "- Cast shadows: longer directional shadows matching the key light angle.\n"
            "- Ambient occlusion: subtle darkening in crevices and where surfaces meet.\n"
            "- Shadows must fall ON the actual scene surface, not floating or missing.\n\n"
            "COLOR & TONE UNITY: The entire image must have ONE cohesive color grade — as if processed through one camera sensor with one white balance setting.\n"
            "- No element should look 'pasted in' with different contrast, saturation, or white balance.\n"
            "- Skin tones, product colors, and background colors must all live in the same color space.\n"
            "- Apply the SAME level of contrast and saturation to ALL elements.\n\n"
            "DEPTH & PERSPECTIVE: All elements must share the SAME camera perspective and focal plane.\n"
            "- If the camera is at eye-level looking slightly down, EVERYTHING must have that same perspective.\n"
            "- Depth of field must be physically consistent — objects at the same distance are equally sharp or blurred.\n"
            "- No element should appear 'cut out' or have an unnaturally sharp edge against the background.\n\n"
            "NATURAL IMPERFECTIONS (makes it look REAL, not CGI):\n"
            "- Subtle lens characteristics: very slight chromatic aberration at edges, natural vignetting.\n"
            "- Environmental interaction: product reflects surrounding colors, environment reflects on glossy product surfaces.\n"
            "- Surface micro-details: dust motes in light beams, tiny texture variations, subtle grain.\n"
            "- Avoid over-processed HDR look — keep dynamic range natural.\n\n"
            "ANTI-COMPOSITE RULES:\n"
            "- NO hard edges or halos around any element.\n"
            "- NO mismatched resolution between foreground and background.\n"
            "- NO inconsistent noise/grain levels between elements.\n"
            "- The product/model must INTERACT with the environment: reflections on nearby surfaces, color spill from environment onto product.\n"
        )

        # Build wearable-aware constraints
        if is_wearable and model_instruction:
            framing_text = (
                "FRAMING (MANDATORY): Show the FASHION MODEL as the HERO — full body or 3/4 body shot. "
                "The product must be WORN/USED by the model — NOT placed separately next to them. "
                "The model is ACTIVELY using the product in a natural, dynamic way."
            )
            product_constraint = (
                "- The product (IMAGE 1) must be WORN or USED by the model — shoes on feet, bag on shoulder, watch on wrist, etc. "
                "Do NOT place the product standing alone next to the model. The model IS using it."
            )
            model_constraint = (
                "- FASHION MODEL IDENTITY (CRITICAL): The person in this image MUST be the EXACT SAME PERSON as the model reference photo. "
                "COPY their face — same facial structure, eyes, nose, lips, skin tone, hair. Do NOT use a different person. "
                "Show them actively WEARING/USING the product in a natural, dynamic pose. The product must be clearly visible ON the model."
            )
        else:
            framing_text = (
                "FRAMING (MANDATORY): The ENTIRE product must be visible — from the very top of the cap to the very bottom of the base. "
                "Leave generous empty space above and below the product. The product should occupy about 50%% of the frame height, centered vertically. "
                "NEVER crop or cut off ANY part of the product."
            )
            product_constraint = "- Product stands UPRIGHT, fully visible from top to bottom, not cropped or tilted."
            model_constraint = ("- FASHION MODEL IDENTITY (CRITICAL): The person MUST be the EXACT SAME PERSON as the model reference photo — "
                "same face, same hair, same skin tone, same glasses. Do NOT use a different or random person. "
                "They must actively interact with the product.") if model_instruction else ""

        if magazine_mode:
            # Build magazine design block from pipeline results
            mag_design = ""
            mag_prompt = prompt  # fallback to regular prompt
            if product_info:
                # Get magazine_positive from prompt agent (preferred over generic positive)
                prompt_data = product_info.get("prompt", {})
                if isinstance(prompt_data, dict):
                    mag_prompt = prompt_data.get("magazine_positive", "") or prompt

                # Get magazine_design from product agent
                product_data = product_info.get("product", {})
                analysis = product_info.get("analysis", {})
                
                # Extract brand name from analysis for magazine copy
                brand_name = ""
                if isinstance(analysis, dict):
                    logos = analysis.get("logos", [])
                    if isinstance(logos, list) and logos:
                        first_logo = logos[0] if isinstance(logos[0], dict) else {}
                        brand_name = first_logo.get("brand", "")
                    if not brand_name or brand_name.lower() == "unknown":
                        logo_usage = analysis.get("logo_usage", {})
                        if isinstance(logo_usage, dict):
                            brand_name = logo_usage.get("brand_name", "")
                
                brand_instruction = ""
                if brand_name and brand_name.lower() != "unknown":
                    if logo_image_bytes:
                        brand_instruction = (
                            f"\nCRITICAL — BRAND IDENTITY: The brand is \"{brand_name}\". "
                            f"The ACTUAL LOGO from IMAGE 2 (the emblem/crest/visual mark) MUST appear prominently in this ad — "
                            f"reproduce the EXACT logo image, do NOT replace it with plain text of the brand name. "
                            f"You may ALSO add the brand name \"{brand_name.upper()}\" as typography text, "
                            f"but the LOGO IMAGE from IMAGE 2 must be the primary brand element. "
                            f"The logo must be clearly visible, properly sized, and positioned like a real brand mark."
                        )
                    else:
                        brand_instruction = (
                            f"\nCRITICAL — BRAND NAME: The brand is \"{brand_name}\". "
                            f"The headline/text in this ad MUST prominently feature \"{brand_name.upper()}\". "
                            f"Do NOT use generic slogans. The brand name must be the HERO text."
                        )
                
                if isinstance(product_data, dict):
                    mag_data = product_data.get("magazine_design", {})
                    if isinstance(mag_data, dict) and mag_data:
                        mag_parts = []
                        # New magazine COVER format
                        masthead = mag_data.get("masthead", "")
                        masthead_font = mag_data.get("masthead_font", "massive bold serif capitals")
                        issue_info = mag_data.get("issue_info", "")
                        cover_headline = mag_data.get("cover_headline", "")
                        cover_headline_font = mag_data.get("cover_headline_font", "bold uppercase sans-serif")
                        cover_headline_pos = mag_data.get("cover_headline_position", "bottom-right")
                        article_teasers = mag_data.get("article_teasers", [])
                        website_url = mag_data.get("website_url", "")
                        headline_color = mag_data.get("headline_color", "white")
                        text_color_scheme = mag_data.get("text_color_scheme", "")
                        layout = mag_data.get("layout_composition", "")
                        style = mag_data.get("magazine_style", "")
                        visual_effect = mag_data.get("visual_effect", "")
                        special = mag_data.get("special_effects", "none")
                        
                        # Fallback to old format fields
                        if not masthead:
                            masthead = mag_data.get("headline", "")
                        
                        if style:
                            mag_parts.append(f"Magazine cover style: {style}")
                        if masthead:
                            mag_parts.append(f"MASTHEAD (top of cover, LARGEST text): \"{masthead}\" in {masthead_font}, {headline_color}")
                        if issue_info:
                            mag_parts.append(f"Issue info (small text near masthead): \"{issue_info}\"")
                        if website_url:
                            mag_parts.append(f"Website URL (small text): \"{website_url}\"")
                        if cover_headline:
                            mag_parts.append(f"COVER STORY HEADLINE (bold, positioned at {cover_headline_pos}): \"{cover_headline}\" in {cover_headline_font}")
                        if article_teasers and isinstance(article_teasers, list):
                            mag_parts.append("ARTICLE TEASERS (small headline + description, arranged around the subject):")
                            for teaser in article_teasers:
                                if isinstance(teaser, dict):
                                    t_headline = teaser.get("headline", "")
                                    t_desc = teaser.get("description", "")
                                    t_pos = teaser.get("position", "")
                                    mag_parts.append(f"  - \"{t_headline}\" + \"{t_desc}\" at {t_pos}")
                                elif isinstance(teaser, str):
                                    mag_parts.append(f"  - {teaser}")
                        if text_color_scheme:
                            mag_parts.append(f"Text color scheme: {text_color_scheme}")
                        if layout:
                            mag_parts.append(f"Cover composition: {layout}")
                        if visual_effect:
                            mag_parts.append(f"DEPTH/VISUAL EFFECT: {visual_effect}")
                        if special and special.lower() != "none":
                            mag_parts.append(f"Text effects: {special}")
                        mag_design = "\n".join(mag_parts)

            if scenic_background:
                logo_section = ""
                if logo_instruction:
                    logo_section = (
                        f"\n\nLOGO ON PRODUCT (CRITICAL — read carefully):\n"
                        f"{logo_instruction}\n"
                        f"The logo must look like a REAL PRINTED LABEL — as if photographed on an actual product. "
                        f"NOT a Photoshop paste. Match the product's lighting, shadows, and reflections."
                    )
                contents.append(
                    f"Generate a professional MAGAZINE COVER — like Vogue, GQ, Harper's Bazaar, or Cosmopolitan.\n\n"
                    f"This must look like a REAL magazine cover you'd see on a newsstand — NOT a product advertisement.\n\n"
                    f"{brand_instruction}\n\n"
                    f"CREATIVE VISION:\n"
                    f"{mag_prompt}\n\n"
                    f"MAGAZINE COVER LAYOUT (follow this structure precisely):\n"
                    f"{mag_design if mag_design else 'Create a professional magazine cover with masthead at top, article teasers on sides, and cover headline at bottom.'}\n\n"
                    f"MANDATORY COVER RULES:\n"
                    f"1. MASTHEAD at the VERY TOP — the brand/magazine name in the LARGEST font on the cover.\n"
                    f"2. ISSUE INFO near the masthead — date, volume, website in small text.\n"
                    f"3. The model/product occupies the CENTER of the cover as the HERO visual.\n"
                    f"4. At least 3 ARTICLE TEASERS (bold headline + small description) arranged on LEFT and RIGHT sides.\n"
                    f"5. A bold COVER STORY HEADLINE at the bottom or side.\n"
                    f"6. DEPTH TRICK: The masthead letters should be partially BEHIND the model's head — this is what makes it look like a real magazine.\n"
                    f"7. Text wraps AROUND the subject — NOT just placed on one side.\n\n"
                    f"{scene_block}"
                    f"{logo_section}\n\n"
                    f"FRAMING: {framing_text} Leave space for typography on all sides.\n\n"
                    f"{model_instruction + chr(10) + chr(10) if model_instruction else ''}"
                    f"{photorealism_block}\n\n"
                    f"RULES:\n"
                    f"- ONE seamless image. No collages or split panels.\n"
                    f"- Product must EXACTLY match IMAGE 1.\n"
                    f"- ALL text must be SHARP and READABLE — never blurry or garbled.\n"
                    f"- Multiple text blocks with different sizes — this is what makes a cover look REAL.\n"
                    f"{model_constraint + chr(10) if model_constraint else ''}"
                    f"The BACKGROUND must support the cover aesthetic — vivid but not distracting from the text layout."
                )
            else:
                logo_section = ""
                if logo_instruction:
                    logo_section = (
                        f"\n\nLOGO ON PRODUCT (CRITICAL — read carefully):\n"
                        f"{logo_instruction}\n"
                        f"The logo must look like a REAL PRINTED LABEL — as if photographed on an actual product. "
                        f"NOT a Photoshop paste. Match the product's lighting, shadows, and reflections."
                    )
                contents.append(
                    f"Generate a professional MAGAZINE COVER — like Vogue, GQ, Harper's Bazaar, or a Business magazine.\n\n"
                    f"This must look like a REAL magazine cover you'd see on a newsstand — NOT a product advertisement.\n\n"
                    f"{brand_instruction}\n\n"
                    f"MAGAZINE COVER LAYOUT (follow this structure precisely):\n"
                    f"{mag_design if mag_design else 'Create a professional magazine cover with masthead at top, article teasers on sides, and cover headline at bottom.'}\n\n"
                    f"MANDATORY COVER RULES:\n"
                    f"1. MASTHEAD at the VERY TOP — the brand/magazine name in the LARGEST font on the cover.\n"
                    f"2. ISSUE INFO near the masthead — date, volume, website in small text.\n"
                    f"3. The model/product occupies the CENTER of the cover as the HERO visual.\n"
                    f"4. At least 3 ARTICLE TEASERS (bold headline + small description) arranged on LEFT and RIGHT sides.\n"
                    f"5. A bold COVER STORY HEADLINE at the bottom or side.\n"
                    f"6. DEPTH TRICK: The masthead letters should be partially BEHIND the model's head — this is what makes it look like a real magazine.\n"
                    f"7. Text wraps AROUND the subject — NOT just placed on one side.\n\n"
                    f"{model_instruction + chr(10) + chr(10) if model_instruction else ''}"
                    f"{logo_section}\n\n"
                    f"FRAMING: {framing_text}\n\n"
                    f"{photorealism_block}\n\n"
                    f"RULES:\n"
                    f"- ONE seamless image. No collages or split panels.\n"
                    f"- Product must EXACTLY match IMAGE 1.\n"
                    f"- ALL text must be SHARP and READABLE — never blurry or garbled.\n"
                    f"- Multiple text blocks with different sizes — this is what makes a cover look REAL.\n"
                    f"{model_constraint + chr(10) if model_constraint else ''}"
                    f"BACKGROUND: Clean, solid-color backdrop (deep charcoal, navy, light gray, or brand color). "
                    f"Professional studio lighting with rim light on the subject. "
                    f"Think GQ or Business magazine covers — clean but sophisticated."
                )
        else:
            if scenic_background:
                logo_section = ""
                if logo_instruction:
                    logo_section = (
                        f"\n\nLOGO ON PRODUCT (CRITICAL — read carefully):\n"
                        f"{logo_instruction}\n"
                        f"The logo must look like a REAL PRINTED LABEL — as if photographed on an actual product in a real photoshoot. "
                        f"NOT a Photoshop paste. The logo must have the SAME lighting, shadows, and reflections as the product surface."
                    )
                contents.append(
                    f"Generate a product mockup photo.\n\n"
                    f"{framing_text}\n\n"
                    f"SCENE VISION (this is the MOST IMPORTANT part — follow this closely):\n"
                    f"{prompt}\n\n"
                    f"{scene_block}"
                    f"{logo_section}\n\n"
                    f"{model_instruction + chr(10) + chr(10) if model_instruction else ''}"
                    f"{photorealism_block}\n\n"
                    f"CONSTRAINTS:\n"
                    f"- ONE single seamless image. No collages, panels, or split compositions.\n"
                    f"- Product must EXACTLY match IMAGE 1 (shape, cap, color, proportions).\n"
                    f"{product_constraint}\n"
                    f"- 8K, sharp focus on product, beautiful bokeh on background.\n"
                    f"{model_constraint + chr(10) if model_constraint else ''}\n"
                    f"The BACKGROUND and ENVIRONMENT described in SCENE VISION above are CRITICAL — do NOT use a plain solid-color studio backdrop. "
                    f"Create a REAL, VIVID environment with depth, props, and atmosphere as described."
                )
            else:
                logo_section = ""
                if logo_instruction:
                    logo_section = (
                        f"\n\nLOGO ON PRODUCT (CRITICAL — read carefully):\n"
                        f"{logo_instruction}\n"
                        f"The logo must look like a REAL PRINTED LABEL — as if photographed on an actual product in a real photoshoot. "
                        f"NOT a Photoshop paste. The logo must have the SAME lighting, shadows, and reflections as the product surface."
                    )
                contents.append(
                    f"Generate a professional studio product photo.\n\n"
                    f"{framing_text}\n\n"
                    f"{model_instruction + chr(10) + chr(10) if model_instruction else ''}"
                    f"{logo_section}\n\n"
                    f"{photorealism_block}\n\n"
                    f"CONSTRAINTS:\n"
                    f"- ONE single seamless image. No collages, panels, or split compositions.\n"
                    f"- Product must EXACTLY match IMAGE 1 (shape, cap, color, proportions).\n"
                    f"{product_constraint}\n"
                    f"- 8K, sharp focus on product.\n"
                    f"{model_constraint + chr(10) if model_constraint else ''}\n"
                    f"BACKGROUND: Use ONLY a clean, plain, solid-color studio backdrop. "
                    f"Choose a single smooth color (white, light gray, soft beige, or a subtle gradient). "
                    f"Absolutely NO grass, NO nature, NO outdoor scenes, NO props, NO environment, NO scenery, NO patterns, NO textures. "
                    f"The background must be completely clean and empty — like a professional e-commerce product photo on a seamless studio backdrop."
                )

        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        # Extract image from response
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    b64 = base64.b64encode(part.inline_data.data).decode("utf-8")
                    return {"image_base64": b64, "format": "png"}

        return {"error": "No image generated in response", "image_base64": None, "format": None}

    except Exception as e:
        error_msg = str(e)
        return {
            "error": f"Image generation failed: {error_msg}",
            "image_base64": None,
            "format": None,
        }
