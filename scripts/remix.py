"""
parameters:
  - name: width
    distribution: constant
    value: 1000
  - name: height
    distribution: constant
    value: 1000
  - name: seed
    distribution: randint
    low: 0
    high: 100000
  - name: base_image_seed
    distribution: randint
    low: 1
    high: 1000
  - name: composition
    distribution: choice
    values: ["strips", "grid", "triangles", "diagonal", "spiral"]
    mode: distribution
  - name: warp_intensity
    distribution: uniform
    loc: 0.0
    scale: 0.5
    mode: distribution
  - name: rotation_angle
    distribution: uniform
    loc: -45
    scale: 90
    mode: distribution
  - name: colour_mode
    distribution: choice
    values: ["chromatic", "invert", "solarize", "channel_swap", "extreme_contrast"]
    mode: distribution
  - name: effect_type
    distribution: choice
    values: ["heavy_glitch", "kaleidoscope", "mirror", "displace", "liquify"]
    mode: distribution
  - name: piece_size
    distribution: randint
    low: 50
    high: 200
    mode: distribution
  - name: blend_mode
    distribution: choice
    values: ["normal", "multiply", "screen", "overlay"]
    mode: distribution
  - name: colour_palette
    distribution: choice
    values: [
      ["#ff006e", "#8338ec", "#3a86ff"],
      ["#06ffa5", "#7c3aed", "#f8b500"],
      ["#e63946", "#457b9d", "#1d3557"],
      ["#f72585", "#7209b7", "#3a0ca3"]
    ]
"""

from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
import random
import requests
from io import BytesIO
import math

# Use specific image IDs for consistent results
def fetch_image(width, height, image_id):
    # Lorem Picsum has images with IDs 0-1000+
    # Use modulo to ensure valid ID
    img_id = image_id % 1000
    url = f"https://picsum.photos/id/{img_id}/{width}/{height}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    except Exception:
        # Fallback
        return Image.new("RGB", (width, height),
                        (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

# Download 3 source images based on base_image_seed (constant for all samples)
print(f"Downloading 3 source images (IDs: {base_image_seed}, {base_image_seed+1}, {base_image_seed+2})...")
source_images = []
for i in range(3):
    img_id = base_image_seed + i
    img = fetch_image(width, height, img_id)
    source_images.append(img)

# Now create variations using randomness (seeded differently for each run)
# The composition parameter and other mode:distribution params provide variation

canvas = Image.new("RGB", (width, height), "black")

def apply_colour_effect(img, mode, palette):
    if mode == "invert":
        return ImageOps.invert(img)
    elif mode == "solarize":
        return ImageOps.solarize(img, threshold=random.randint(60, 180))
    elif mode == "channel_swap":
        # Swap RGB channels randomly
        r, g, b = img.split()
        channels = [r, g, b]
        random.shuffle(channels)
        return Image.merge("RGB", tuple(channels))
    elif mode == "extreme_contrast":
        # Extreme contrast and saturation
        img_copy = img.copy()
        enhancer = ImageEnhance.Contrast(img_copy)
        img_copy = enhancer.enhance(random.uniform(2.0, 4.0))
        enhancer = ImageEnhance.Color(img_copy)
        img_copy = enhancer.enhance(random.uniform(1.5, 3.0))
        return img_copy
    elif mode == "chromatic":
        # Chromatic aberration effect
        from PIL import ImageChops
        r, g, b = img.split()
        offset = random.randint(10, 40)
        r = ImageChops.offset(r, offset, 0)
        b = ImageChops.offset(b, -offset, 0)
        return Image.merge("RGB", (r, g, b))
    return img

def apply_effect(img, effect):
    if effect == "heavy_glitch":
        # Heavy RGB channel shift with blocks
        from PIL import ImageChops
        r, g, b = img.split()
        r = ImageChops.offset(r, random.randint(-60, 60), random.randint(-20, 20))
        g = ImageChops.offset(g, random.randint(-30, 30), random.randint(-20, 20))
        b = ImageChops.offset(b, random.randint(-60, 60), random.randint(-20, 20))
        return Image.merge("RGB", (r, g, b))
    elif effect == "kaleidoscope":
        # Kaleidoscope effect - flip and rotate quadrants
        w, h = img.size
        hw, hh = w // 2, h // 2
        # Take one quadrant and mirror it
        quad = img.crop((0, 0, hw, hh))
        quad_flip_h = ImageOps.mirror(quad)
        quad_flip_v = ImageOps.flip(quad)
        quad_flip_both = ImageOps.flip(ImageOps.mirror(quad))
        result = Image.new("RGB", (w, h))
        result.paste(quad, (0, 0))
        result.paste(quad_flip_h, (hw, 0))
        result.paste(quad_flip_v, (0, hh))
        result.paste(quad_flip_both, (hw, hh))
        return result
    elif effect == "mirror":
        # Random mirror effect
        if random.random() > 0.5:
            return ImageOps.mirror(img)
        else:
            return ImageOps.flip(img)
    elif effect == "displace":
        # Displacement/slice effect
        w, h = img.size
        result = img.copy()
        num_slices = random.randint(5, 15)
        slice_height = h // num_slices
        for i in range(num_slices):
            y = i * slice_height
            slice_img = result.crop((0, y, w, min(y + slice_height, h)))
            offset_x = random.randint(-100, 100)
            from PIL import ImageChops
            slice_img = ImageChops.offset(slice_img, offset_x, 0)
            result.paste(slice_img, (0, y))
        return result
    elif effect == "liquify":
        # Liquify/warp effect
        w, h = img.size
        intensity = random.uniform(0.3, 0.8)
        # Perspective transform with random coefficients
        coeffs = [
            1 + random.uniform(-intensity, intensity),
            random.uniform(-intensity * 0.5, intensity * 0.5),
            random.randint(-50, 50),
            random.uniform(-intensity * 0.5, intensity * 0.5),
            1 + random.uniform(-intensity, intensity),
            random.randint(-50, 50),
            random.uniform(-0.001, 0.001),
            random.uniform(-0.001, 0.001)
        ]
        return img.transform(img.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    return img

def warp_image(img, intensity):
    if intensity < 0.1:
        return img
    # Simple perspective-like warp
    w, h = img.size
    shift = int(w * intensity * 0.3)
    return img.transform(img.size, Image.AFFINE,
                        (1, intensity * 0.3, -shift, intensity * 0.2, 1, -shift))

def blend_images(base, overlay, mode):
    if mode == "multiply":
        from PIL import ImageChops
        return ImageChops.multiply(base, overlay)
    elif mode == "screen":
        from PIL import ImageChops
        return ImageChops.screen(base, overlay)
    elif mode == "overlay":
        return Image.blend(base, overlay, 0.5)
    return overlay

# Get variation values
comp = composition.rvs() if hasattr(composition, 'rvs') else composition
warp_int = warp_intensity.rvs() if hasattr(warp_intensity, 'rvs') else warp_intensity
rotation = rotation_angle.rvs() if hasattr(rotation_angle, 'rvs') else rotation_angle
col_mode = colour_mode.rvs() if hasattr(colour_mode, 'rvs') else colour_mode
effect = effect_type.rvs() if hasattr(effect_type, 'rvs') else effect_type
p_size = int(piece_size.rvs() if hasattr(piece_size, 'rvs') else piece_size)
blend = blend_mode.rvs() if hasattr(blend_mode, 'rvs') else blend_mode

# Create composition based on style
if comp == "strips":
    # Horizontal or vertical strips
    strip_height = max(50, p_size)
    y_pos = 0
    while y_pos < height:
        img_idx = random.randint(0, 2)
        img = source_images[img_idx].copy()

        # Apply effects
        img = apply_colour_effect(img, col_mode, colour_palette)
        img = apply_effect(img, effect)
        img = warp_image(img, warp_int)

        # Crop strip
        strip = img.crop((0, y_pos, width, min(y_pos + strip_height, height)))
        canvas.paste(strip, (0, y_pos))

        y_pos += strip_height

elif comp == "grid":
    # Grid of pieces
    grid_size = max(50, p_size)
    for y in range(0, height, grid_size):
        for x in range(0, width, grid_size):
            img_idx = random.randint(0, 2)
            img = source_images[img_idx].copy()

            # Apply effects
            img = apply_colour_effect(img, col_mode, colour_palette)
            img = apply_effect(img, effect)

            # Crop piece
            piece = img.crop((x, y, min(x + grid_size, width), min(y + grid_size, height)))

            # Maybe rotate
            if random.random() > 0.5:
                piece = piece.rotate(rotation, expand=False)

            canvas.paste(piece, (x, y))

elif comp == "triangles":
    # Triangular pieces
    num_triangles = random.randint(20, 50)

    for _ in range(num_triangles):
        img_idx = random.randint(0, 2)
        img = source_images[img_idx].copy()

        # Apply effects
        img = apply_colour_effect(img, col_mode, colour_palette)
        img = apply_effect(img, effect)

        # Random triangle
        x1, y1 = random.randint(0, width), random.randint(0, height)
        size = random.randint(p_size, p_size * 2)

        # Create triangle mask
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        points = [
            (x1, y1),
            (x1 + size, y1),
            (x1 + size // 2, y1 + int(size * 0.866))
        ]
        draw.polygon(points, fill=255)

        canvas.paste(img, (0, 0), mask)

elif comp == "diagonal":
    # Diagonal strips
    num_strips = random.randint(10, 30)

    for i in range(num_strips):
        img_idx = random.randint(0, 2)
        img = source_images[img_idx].copy()

        # Apply effects
        img = apply_colour_effect(img, col_mode, colour_palette)
        img = apply_effect(img, effect)
        img = warp_image(img, warp_int)

        # Create diagonal mask
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)

        offset = (width + height) * i // num_strips
        strip_width = max(30, p_size // 2)

        points = [
            (offset - strip_width, 0),
            (offset + strip_width, 0),
            (offset - height + strip_width, height),
            (offset - height - strip_width, height)
        ]
        draw.polygon(points, fill=255)

        canvas.paste(img, (0, 0), mask)

else:  # spiral
    # Spiral composition
    center_x, center_y = width // 2, height // 2
    angle = 0
    radius = 10

    while radius < max(width, height):
        img_idx = random.randint(0, 2)
        img = source_images[img_idx].copy()

        # Apply effects
        img = apply_colour_effect(img, col_mode, colour_palette)
        img = apply_effect(img, effect)

        # Calculate position
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))

        # Create circular mask
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        circle_size = p_size // 2
        draw.ellipse([x - circle_size, y - circle_size,
                     x + circle_size, y + circle_size], fill=255)

        canvas.paste(img, (0, 0), mask)

        angle += 0.5
        radius += 2

# Apply final blend if needed
if blend != "normal":
    overlay_img = source_images[random.randint(0, 2)].copy()
    overlay_img = apply_effect(overlay_img, effect)
    canvas = blend_images(canvas, overlay_img, blend)

canvas
