"""
parameters:
  - name: width
    distribution: constant
    value: 500
  - name: height
    distribution: constant
    value: 500
  - name: square_size
    distribution: constant
    value: 70
  - name: seed
    distribution: randint
    low: 0
    high: 10000
  - name: style
    distribution: choice
    values: ["neon", "watercolour", "isometric", "retro", "glassmorphic"]
  - name: background
    distribution: choice
    values: ["#1a1a2e", "#0f0f23", "#2d1b4e", "#0a192f", "#1c1c1c"]
  - name: palette
    distribution: choice
    values: ["sunset", "ocean", "forest", "candy", "aurora"]
"""

from PIL import Image, ImageDraw, ImageFilter
import random
import math
import colorsys

random.seed(seed)

# Colour palettes
palettes = {
    'sunset': ['#ff6b6b', '#feca57', '#ff9ff3', '#ff6348', '#ffa502'],
    'ocean': ['#00cec9', '#0984e3', '#74b9ff', '#a29bfe', '#6c5ce7'],
    'forest': ['#00b894', '#55efc4', '#81ecec', '#74b9ff', '#a29bfe'],
    'candy': ['#fd79a8', '#e84393', '#d63031', '#fdcb6e', '#f8a5c2'],
    'aurora': ['#a29bfe', '#6c5ce7', '#00cec9', '#55efc4', '#fd79a8']
}

colours = palettes[palette]

# Define the 12 pentominoes as sets of (row, col) coordinates
pentominoes = {
    'F': [(0, 1), (1, 0), (1, 1), (1, 2), (2, 2)],
    'I': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    'L': [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],
    'N': [(0, 1), (1, 1), (2, 0), (2, 1), (3, 0)],
    'P': [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
    'T': [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)],
    'U': [(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)],
    'V': [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    'W': [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
    'X': [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
    'Y': [(0, 1), (1, 0), (1, 1), (2, 1), (3, 1)],
    'Z': [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)]
}

def hex_to_rgb(hex_colour):
    hex_colour = hex_colour.lstrip('#')
    return tuple(int(hex_colour[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def lighten(hex_colour, factor=0.3):
    r, g, b = hex_to_rgb(hex_colour)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return rgb_to_hex((r, g, b))

def darken(hex_colour, factor=0.3):
    r, g, b = hex_to_rgb(hex_colour)
    r = int(r * (1 - factor))
    g = int(g * (1 - factor))
    b = int(b * (1 - factor))
    return rgb_to_hex((r, g, b))

def draw_neon_style(draw, shape, offset_x, offset_y, square_size, base_colour, img):
    """Neon glow effect with multiple blur layers"""
    glow_colour = base_colour

    # Create glow layers
    for glow_size in [15, 10, 5]:
        glow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)

        for row, col in shape:
            x = offset_x + col * square_size
            y = offset_y + row * square_size
            glow_draw.rectangle(
                [x + 2, y + 2, x + square_size - 2, y + square_size - 2],
                outline=glow_colour,
                width=3
            )

        glow_img = glow_img.filter(ImageFilter.GaussianBlur(glow_size))
        img.paste(Image.alpha_composite(img.convert("RGBA"), glow_img).convert("RGB"), (0, 0))

    draw = ImageDraw.Draw(img)

    # Draw inner dark fill
    for row, col in shape:
        x = offset_x + col * square_size
        y = offset_y + row * square_size
        dark_fill = darken(base_colour, 0.7)
        draw.rectangle([x + 4, y + 4, x + square_size - 4, y + square_size - 4], fill=dark_fill)

    # Draw bright outline
    for row, col in shape:
        x = offset_x + col * square_size
        y = offset_y + row * square_size
        draw.rectangle(
            [x + 2, y + 2, x + square_size - 2, y + square_size - 2],
            outline=lighten(base_colour, 0.5),
            width=2
        )

def draw_watercolour_style(draw, shape, offset_x, offset_y, square_size, base_colour, img):
    """Soft watercolour effect with bleeding edges"""
    r, g, b = hex_to_rgb(base_colour)

    # Multiple semi-transparent layers with slight offsets
    for layer in range(8):
        layer_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer_img)

        offset_jitter_x = random.randint(-3, 3)
        offset_jitter_y = random.randint(-3, 3)
        size_jitter = random.randint(-2, 2)

        alpha = random.randint(40, 80)

        for row, col in shape:
            x = offset_x + col * square_size + offset_jitter_x
            y = offset_y + row * square_size + offset_jitter_y

            colour_var = (
                max(0, min(255, r + random.randint(-20, 20))),
                max(0, min(255, g + random.randint(-20, 20))),
                max(0, min(255, b + random.randint(-20, 20))),
                alpha
            )

            layer_draw.ellipse(
                [x - 5 + size_jitter, y - 5 + size_jitter,
                 x + square_size + 5 - size_jitter, y + square_size + 5 - size_jitter],
                fill=colour_var
            )

        layer_img = layer_img.filter(ImageFilter.GaussianBlur(8))
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer_img).convert("RGB"), (0, 0))

    # Add some speckles
    draw = ImageDraw.Draw(img)
    for row, col in shape:
        x = offset_x + col * square_size
        y = offset_y + row * square_size
        for _ in range(15):
            sx = x + random.randint(5, square_size - 5)
            sy = y + random.randint(5, square_size - 5)
            speckle_r = random.uniform(0.5, 2)
            draw.ellipse([sx - speckle_r, sy - speckle_r, sx + speckle_r, sy + speckle_r],
                        fill=darken(base_colour, 0.3))

def draw_isometric_style(draw, shape, offset_x, offset_y, square_size, base_colour, img):
    """3D isometric cube effect"""
    depth = int(square_size * 0.3)
    top_colour = lighten(base_colour, 0.2)
    right_colour = darken(base_colour, 0.2)
    left_colour = darken(base_colour, 0.4)

    # Sort by row+col to draw back to front
    sorted_shape = sorted(shape, key=lambda p: (p[0] + p[1]))

    for row, col in sorted_shape:
        x = offset_x + col * square_size
        y = offset_y + row * square_size

        # Right face
        right_face = [
            (x + square_size, y),
            (x + square_size + depth, y - depth//2),
            (x + square_size + depth, y + square_size - depth//2),
            (x + square_size, y + square_size)
        ]
        draw.polygon(right_face, fill=right_colour)

        # Top face
        top_face = [
            (x, y),
            (x + depth, y - depth//2),
            (x + square_size + depth, y - depth//2),
            (x + square_size, y)
        ]
        draw.polygon(top_face, fill=top_colour)

        # Front face
        draw.rectangle([x, y, x + square_size, y + square_size], fill=base_colour)

        # Outlines
        draw.line([x, y, x + square_size, y], fill=darken(base_colour, 0.5), width=2)
        draw.line([x, y, x, y + square_size], fill=darken(base_colour, 0.5), width=2)
        draw.line([x + square_size, y, x + square_size, y + square_size], fill=darken(base_colour, 0.5), width=2)
        draw.line([x, y + square_size, x + square_size, y + square_size], fill=darken(base_colour, 0.5), width=2)

def draw_retro_style(draw, shape, offset_x, offset_y, square_size, base_colour, img):
    """Retro 80s style with scan lines and chromatic aberration"""
    # Draw offset colour channels for chromatic aberration
    for channel_offset, channel_colour in [(-3, '#ff0000'), (3, '#00ffff')]:
        channel_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        channel_draw = ImageDraw.Draw(channel_img)

        for row, col in shape:
            x = offset_x + col * square_size + channel_offset
            y = offset_y + row * square_size
            r, g, b = hex_to_rgb(channel_colour)
            channel_draw.rectangle([x, y, x + square_size, y + square_size], fill=(r, g, b, 60))

        img.paste(Image.alpha_composite(img.convert("RGBA"), channel_img).convert("RGB"), (0, 0))

    draw = ImageDraw.Draw(img)

    # Main shape with gradient-ish effect
    for row, col in shape:
        x = offset_x + col * square_size
        y = offset_y + row * square_size

        # Draw horizontal gradient lines
        for i in range(square_size):
            factor = i / square_size
            line_colour = lighten(base_colour, 0.3 - factor * 0.3)
            draw.line([x, y + i, x + square_size, y + i], fill=line_colour)

        # Bold outline
        draw.rectangle([x, y, x + square_size, y + square_size], outline='#ffffff', width=3)

    # Add scan lines
    for y_line in range(0, height, 4):
        draw.line([0, y_line, width, y_line], fill=(0, 0, 0, 30), width=1)

def draw_glassmorphic_style(draw, shape, offset_x, offset_y, square_size, base_colour, img):
    """Modern glassmorphic frosted glass effect"""
    # Create background gradient/pattern
    for i in range(height):
        factor = i / height
        bg_r = int(30 + factor * 40)
        bg_g = int(20 + factor * 30)
        bg_b = int(60 + factor * 50)
        draw.line([0, i, width, i], fill=(bg_r, bg_g, bg_b))

    # Add some background blobs
    for _ in range(5):
        blob_x = random.randint(0, width)
        blob_y = random.randint(0, height)
        blob_r = random.randint(50, 150)
        blob_colour = random.choice(colours)
        r, g, b = hex_to_rgb(blob_colour)

        blob_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        blob_draw = ImageDraw.Draw(blob_img)
        blob_draw.ellipse([blob_x - blob_r, blob_y - blob_r, blob_x + blob_r, blob_y + blob_r],
                         fill=(r, g, b, 100))
        blob_img = blob_img.filter(ImageFilter.GaussianBlur(30))
        img.paste(Image.alpha_composite(img.convert("RGBA"), blob_img).convert("RGB"), (0, 0))

    draw = ImageDraw.Draw(img)

    # Create frosted glass effect
    glass_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glass_draw = ImageDraw.Draw(glass_img)

    for row, col in shape:
        x = offset_x + col * square_size
        y = offset_y + row * square_size

        # Semi-transparent fill
        r, g, b = hex_to_rgb(base_colour)
        glass_draw.rectangle([x, y, x + square_size, y + square_size], fill=(r, g, b, 80))

        # Highlight on top edge
        glass_draw.line([x + 2, y + 2, x + square_size - 2, y + 2], fill=(255, 255, 255, 100), width=2)

        # Subtle border
        glass_draw.rectangle([x, y, x + square_size, y + square_size],
                            outline=(255, 255, 255, 60), width=1)

    img.paste(Image.alpha_composite(img.convert("RGBA"), glass_img).convert("RGB"), (0, 0))

    # Add subtle inner shadow
    draw = ImageDraw.Draw(img)
    for row, col in shape:
        x = offset_x + col * square_size
        y = offset_y + row * square_size
        draw.line([x + 2, y + square_size - 2, x + square_size - 2, y + square_size - 2],
                 fill=(0, 0, 0, 30), width=1)
        draw.line([x + square_size - 2, y + 2, x + square_size - 2, y + square_size - 2],
                 fill=(0, 0, 0, 30), width=1)


# Pick a random pentomino
shape = random.choice(list(pentominoes.values()))
base_colour = random.choice(colours)

# Create image
img = Image.new("RGB", (width, height), background)
draw = ImageDraw.Draw(img)

# Calculate bounds of shape for better centring
rows = [p[0] for p in shape]
cols = [p[1] for p in shape]
shape_height = (max(rows) - min(rows) + 1) * square_size
shape_width = (max(cols) - min(cols) + 1) * square_size

# Centre the pentomino
offset_x = (width - shape_width) // 2 - min(cols) * square_size
offset_y = (height - shape_height) // 2 - min(rows) * square_size

# Apply the selected style
if style == "neon":
    draw_neon_style(draw, shape, offset_x, offset_y, square_size, base_colour, img)
elif style == "watercolour":
    draw_watercolour_style(draw, shape, offset_x, offset_y, square_size, base_colour, img)
elif style == "isometric":
    draw_isometric_style(draw, shape, offset_x, offset_y, square_size, base_colour, img)
elif style == "retro":
    draw_retro_style(draw, shape, offset_x, offset_y, square_size, base_colour, img)
elif style == "glassmorphic":
    draw_glassmorphic_style(draw, shape, offset_x, offset_y, square_size, base_colour, img)

img
