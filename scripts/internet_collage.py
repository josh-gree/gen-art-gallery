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
  - name: num_images
    distribution: randint
    low: 2
    high: 4
  - name: blend_mode
    distribution: choice
    values: ["multiply", "screen", "overlay", "soft_light"]
  - name: palette
    distribution: choice
    values: [
      ["#ff006e", "#fb5607", "#ffbe0b", "#8338ec", "#3a86ff"],
      ["#06ffa5", "#00d4ff", "#7c3aed", "#f8b500", "#ff6b6b"],
      ["#e63946", "#f1faee", "#a8dadc", "#457b9d", "#1d3557"],
      ["#f72585", "#b5179e", "#7209b7", "#560bad", "#3a0ca3"],
      ["#00f5ff", "#ffd60a", "#ff006e", "#06ffa5", "#7209b7"]
    ]
  - name: overlay_style
    distribution: choice
    values: ["circles", "lines", "polygons", "mixed"]
  - name: glitch_intensity
    distribution: uniform
    loc: 0.0
    scale: 0.3
  - name: colour_shift
    distribution: uniform
    loc: -30
    scale: 60
  - name: overlay_alpha
    distribution: uniform
    loc: 0.3
    scale: 0.5
"""

from PIL import Image, ImageDraw, ImageEnhance, ImageChops
import random
import requests
from io import BytesIO
import math

random.seed(seed)

def fetch_image(width, height, seed_val):
    url = f"https://picsum.photos/{width}/{height}?random={seed_val}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    except Exception as e:
        # Fallback to solid colour if fetch fails
        fallback = Image.new("RGB", (width, height),
                            (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
        return fallback

def apply_blend(base, overlay, mode):
    if mode == "multiply":
        return ImageChops.multiply(base, overlay)
    elif mode == "screen":
        return ImageChops.screen(base, overlay)
    elif mode == "overlay":
        # Overlay blend mode
        base_arr = base
        overlay_arr = overlay
        return ImageChops.blend(base_arr, overlay_arr, 0.5)
    elif mode == "soft_light":
        return ImageChops.soft_light(base, overlay)
    return ImageChops.blend(base, overlay, 0.5)

def apply_colour_shift(img, shift_r, shift_g, shift_b):
    r, g, b = img.split()
    r = r.point(lambda i: max(0, min(255, i + shift_r)))
    g = g.point(lambda i: max(0, min(255, i + shift_g)))
    b = b.point(lambda i: max(0, min(255, i + shift_b)))
    return Image.merge("RGB", (r, g, b))

def add_glitch_effect(img, intensity):
    if intensity < 0.01:
        return img

    img_copy = img.copy()
    r, g, b = img_copy.split()

    # Shift channels
    shift = int(width * intensity * 0.05)
    if shift > 0:
        r = ImageChops.offset(r, shift, 0)
        b = ImageChops.offset(b, -shift, 0)

    return Image.merge("RGB", (r, g, b))

# Fetch random images from the internet
print(f"Fetching {num_images} images from the internet...")
images = []
for i in range(num_images):
    img_seed = seed + i * 1000
    img = fetch_image(width, height, img_seed)
    images.append(img)

# Start with first image as base
result = images[0].copy()

# Blend subsequent images
for i in range(1, len(images)):
    result = apply_blend(result, images[i], blend_mode)

# Apply colour shift
shift_r = int(colour_shift + random.uniform(-20, 20))
shift_g = int(colour_shift + random.uniform(-20, 20))
shift_b = int(colour_shift + random.uniform(-20, 20))
result = apply_colour_shift(result, shift_r, shift_g, shift_b)

# Enhance contrast
enhancer = ImageEnhance.Contrast(result)
result = enhancer.enhance(random.uniform(1.1, 1.4))

# Apply glitch effect
result = add_glitch_effect(result, glitch_intensity)

# Convert to RGBA for overlays
result = result.convert("RGBA")

# Create overlay layer
overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

# Add geometric overlays
num_shapes = random.randint(10, 30)
alpha = int(overlay_alpha * 255)

for _ in range(num_shapes):
    colour_hex = random.choice(palette)
    r = int(colour_hex[1:3], 16)
    g = int(colour_hex[3:5], 16)
    b = int(colour_hex[5:7], 16)
    colour = (r, g, b, alpha)

    if overlay_style == "circles" or (overlay_style == "mixed" and random.random() < 0.4):
        # Draw circles
        x = random.randint(-100, width + 100)
        y = random.randint(-100, height + 100)
        radius = random.randint(20, 150)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                    fill=colour, outline=None)

    elif overlay_style == "lines" or (overlay_style == "mixed" and random.random() < 0.4):
        # Draw lines
        x1 = random.randint(-100, width + 100)
        y1 = random.randint(-100, height + 100)
        x2 = random.randint(-100, width + 100)
        y2 = random.randint(-100, height + 100)
        thickness = random.randint(2, 20)
        draw.line([(x1, y1), (x2, y2)], fill=colour, width=thickness)

    elif overlay_style == "polygons" or overlay_style == "mixed":
        # Draw triangles or rectangles
        if random.random() < 0.5:
            # Triangle
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(50, 200)
            points = [
                (x, y),
                (x + size, y),
                (x + size // 2, y + int(size * 0.866))
            ]
            draw.polygon(points, fill=colour)
        else:
            # Rectangle
            x = random.randint(-100, width)
            y = random.randint(-100, height)
            w = random.randint(50, 300)
            h = random.randint(50, 300)
            draw.rectangle([x, y, x + w, y + h], fill=colour)

# Composite overlay onto result
result = Image.alpha_composite(result, overlay)

# Convert back to RGB
result = result.convert("RGB")

result
