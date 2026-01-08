"""
parameters:
  - name: width
    distribution: constant
    value: 600
  - name: height
    distribution: constant
    value: 600
  - name: seed
    distribution: randint
    low: 0
    high: 10000
  - name: style
    distribution: choice
    values: ["blob", "constellation", "roots", "circuit", "splatter", "contour"]
  - name: palette
    distribution: choice
    values: ["ember", "deep_sea", "botanical", "cosmic", "rust"]
"""

from PIL import Image, ImageDraw, ImageFilter
import random
import math

random.seed(seed)

# Colour palettes
palettes = {
    'ember': ['#ff6b35', '#f7c59f', '#efefef', '#2e2e2e', '#ff3d00'],
    'deep_sea': ['#0d1b2a', '#1b263b', '#415a77', '#778da9', '#e0e1dd'],
    'botanical': ['#606c38', '#283618', '#fefae0', '#dda15e', '#bc6c25'],
    'cosmic': ['#7400b8', '#6930c3', '#5e60ce', '#5390d9', '#4ea8de'],
    'rust': ['#9c6644', '#7f5539', '#b08968', '#ddb892', '#ede0d4']
}

colours = palettes[palette]

# Define pentominoes as connectivity graphs (which cells connect to which)
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

def get_adjacencies(shape):
    """Find which cells are adjacent in the pentomino"""
    adjacencies = []
    shape_set = set(shape)
    for r, c in shape:
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbour = (r + dr, c + dc)
            if neighbour in shape_set and (neighbour, (r, c)) not in adjacencies:
                adjacencies.append(((r, c), neighbour))
    return adjacencies

def shape_to_points(shape, scale=80, jitter=0):
    """Convert grid coords to screen coords with optional jitter"""
    rows = [p[0] for p in shape]
    cols = [p[1] for p in shape]

    # Centre calculation
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    shape_h = (max_r - min_r + 1) * scale
    shape_w = (max_c - min_c + 1) * scale

    offset_x = (width - shape_w) // 2 - min_c * scale + scale // 2
    offset_y = (height - shape_h) // 2 - min_r * scale + scale // 2

    points = {}
    for r, c in shape:
        jx = random.randint(-jitter, jitter) if jitter else 0
        jy = random.randint(-jitter, jitter) if jitter else 0
        points[(r, c)] = (offset_x + c * scale + jx, offset_y + r * scale + jy)

    return points

def draw_blob_style(draw, shape, img):
    """Organic blob shapes that merge together"""
    points = shape_to_points(shape, scale=100, jitter=15)
    adjacencies = get_adjacencies(shape)

    base_colour = random.choice(colours)
    r, g, b = hex_to_rgb(base_colour)

    # Draw connecting blobs between adjacent cells
    blob_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    blob_draw = ImageDraw.Draw(blob_img)

    # First pass: large blobs at each cell
    for (row, col), (px, py) in points.items():
        radius = random.randint(45, 60)
        # Draw multiple overlapping circles for organic feel
        for _ in range(5):
            ox = random.randint(-15, 15)
            oy = random.randint(-15, 15)
            r_var = random.randint(-10, 10)
            blob_draw.ellipse([px - radius + ox - r_var, py - radius + oy - r_var,
                              px + radius + ox + r_var, py + radius + oy + r_var],
                             fill=(r, g, b, 180))

    # Second pass: connecting tissue between adjacent cells
    for (r1, c1), (r2, c2) in adjacencies:
        p1 = points[(r1, c1)]
        p2 = points[(r2, c2)]

        # Draw blobs along the connection
        steps = 8
        for i in range(steps):
            t = i / (steps - 1)
            cx = p1[0] + (p2[0] - p1[0]) * t
            cy = p1[1] + (p2[1] - p1[1]) * t
            radius = 30 + random.randint(-5, 5)
            blob_draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                             fill=(r, g, b, 200))

    # Apply blur for smooth edges
    blob_img = blob_img.filter(ImageFilter.GaussianBlur(8))
    img.paste(Image.alpha_composite(img.convert("RGBA"), blob_img).convert("RGB"), (0, 0))

    # Add highlight spots
    draw = ImageDraw.Draw(img)
    for (row, col), (px, py) in points.items():
        highlight_x = px - 15 + random.randint(-5, 5)
        highlight_y = py - 15 + random.randint(-5, 5)
        for size in [12, 8, 4]:
            alpha = 255 - size * 15
            draw.ellipse([highlight_x - size, highlight_y - size,
                         highlight_x + size, highlight_y + size],
                        fill=(255, 255, 255))

def draw_constellation_style(draw, shape, img):
    """Stars connected by faint lines like a constellation"""
    points = shape_to_points(shape, scale=90, jitter=20)
    adjacencies = get_adjacencies(shape)

    # Dark background with subtle gradient
    for y in range(height):
        factor = y / height
        bg = int(10 + factor * 15)
        draw.line([0, y, width, y], fill=(bg, bg, bg + 10))

    # Add background stars
    for _ in range(200):
        sx = random.randint(0, width)
        sy = random.randint(0, height)
        brightness = random.randint(50, 150)
        size = random.choice([1, 1, 1, 2])
        draw.ellipse([sx - size, sy - size, sx + size, sy + size],
                    fill=(brightness, brightness, brightness))

    star_colour = hex_to_rgb(random.choice(colours))

    # Draw connecting lines (faint, multiple strokes)
    for (r1, c1), (r2, c2) in adjacencies:
        p1 = points[(r1, c1)]
        p2 = points[(r2, c2)]

        # Multiple faint lines for glow effect
        for offset in range(-2, 3):
            alpha = 100 - abs(offset) * 30
            line_colour = (star_colour[0], star_colour[1], star_colour[2])
            draw.line([p1[0] + offset, p1[1], p2[0] + offset, p2[1]],
                     fill=line_colour, width=1)
            draw.line([p1[0], p1[1] + offset, p2[0], p2[1] + offset],
                     fill=line_colour, width=1)

    # Draw stars at each cell
    for (row, col), (px, py) in points.items():
        # Glow effect
        for radius in [20, 15, 10, 5]:
            alpha = 255 - radius * 10
            glow_r = min(255, star_colour[0] + 50)
            glow_g = min(255, star_colour[1] + 50)
            glow_b = min(255, star_colour[2] + 50)
            draw.ellipse([px - radius, py - radius, px + radius, py + radius],
                        fill=(glow_r, glow_g, glow_b))

        # Bright centre
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))

        # Star rays
        ray_length = random.randint(25, 40)
        for angle in [0, 90, 45, 135]:
            rad = math.radians(angle)
            ex = px + math.cos(rad) * ray_length
            ey = py + math.sin(rad) * ray_length
            draw.line([px, py, ex, ey], fill=(255, 255, 255), width=1)
            ex2 = px - math.cos(rad) * ray_length
            ey2 = py - math.sin(rad) * ray_length
            draw.line([px, py, ex2, ey2], fill=(255, 255, 255), width=1)

def draw_roots_style(draw, shape, img):
    """Organic branching roots growing from each cell"""
    points = shape_to_points(shape, scale=100, jitter=10)
    adjacencies = get_adjacencies(shape)

    # Earthy background
    bg_colour = hex_to_rgb(colours[-1])
    draw.rectangle([0, 0, width, height], fill=bg_colour)

    root_colour = hex_to_rgb(colours[1])

    def draw_branch(start_x, start_y, angle, length, thickness, depth=0):
        if depth > 6 or length < 3:
            return

        end_x = start_x + math.cos(angle) * length
        end_y = start_y + math.sin(angle) * length

        # Draw tapered line
        draw.line([start_x, start_y, end_x, end_y],
                 fill=root_colour, width=max(1, int(thickness)))

        # Branching
        if random.random() < 0.7:
            new_angle = angle + random.uniform(-0.8, 0.8)
            draw_branch(end_x, end_y, new_angle, length * 0.75, thickness * 0.7, depth + 1)

        if random.random() < 0.4:
            branch_angle = angle + random.choice([-1, 1]) * random.uniform(0.5, 1.2)
            draw_branch(end_x, end_y, branch_angle, length * 0.6, thickness * 0.5, depth + 1)

    # Draw main connections as thick roots
    for (r1, c1), (r2, c2) in adjacencies:
        p1 = points[(r1, c1)]
        p2 = points[(r2, c2)]

        # Curved root connection
        ctrl_x = (p1[0] + p2[0]) / 2 + random.randint(-20, 20)
        ctrl_y = (p1[1] + p2[1]) / 2 + random.randint(-20, 20)

        steps = 20
        prev = p1
        for i in range(1, steps + 1):
            t = i / steps
            # Quadratic bezier
            x = (1-t)**2 * p1[0] + 2*(1-t)*t * ctrl_x + t**2 * p2[0]
            y = (1-t)**2 * p1[1] + 2*(1-t)*t * ctrl_y + t**2 * p2[1]
            thickness = 8 - abs(t - 0.5) * 6
            draw.line([prev[0], prev[1], x, y], fill=root_colour, width=int(thickness))
            prev = (x, y)

    # Draw branching roots from each node
    for (row, col), (px, py) in points.items():
        # Central node
        draw.ellipse([px - 12, py - 12, px + 12, py + 12], fill=root_colour)

        # Radiating roots
        num_roots = random.randint(3, 6)
        for i in range(num_roots):
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(40, 80)
            draw_branch(px, py, angle, length, 5)

def draw_circuit_style(draw, shape, img):
    """Electronic circuit board aesthetic"""
    points = shape_to_points(shape, scale=100, jitter=0)
    adjacencies = get_adjacencies(shape)

    # PCB green or dark background
    bg = hex_to_rgb(colours[0])
    draw.rectangle([0, 0, width, height], fill=bg)

    trace_colour = hex_to_rgb(colours[-1])
    node_colour = hex_to_rgb(colours[2])

    # Draw grid pattern in background
    grid_colour = tuple(max(0, c - 20) for c in bg)
    for x in range(0, width, 20):
        draw.line([x, 0, x, height], fill=grid_colour, width=1)
    for y in range(0, height, 20):
        draw.line([0, y, width, y], fill=grid_colour, width=1)

    # Draw traces (connections) with right-angle routing
    for (r1, c1), (r2, c2) in adjacencies:
        p1 = points[(r1, c1)]
        p2 = points[(r2, c2)]

        # Route with one bend (horizontal then vertical or vice versa)
        if random.random() < 0.5:
            mid = (p2[0], p1[1])
        else:
            mid = (p1[0], p2[1])

        # Draw thick trace
        draw.line([p1, mid], fill=trace_colour, width=6)
        draw.line([mid, p2], fill=trace_colour, width=6)

        # Inner highlight
        highlight = tuple(min(255, c + 40) for c in trace_colour)
        draw.line([p1, mid], fill=highlight, width=2)
        draw.line([mid, p2], fill=highlight, width=2)

    # Draw component pads at each node
    for (row, col), (px, py) in points.items():
        # Outer ring
        draw.ellipse([px - 18, py - 18, px + 18, py + 18], fill=trace_colour)
        # Inner pad
        draw.ellipse([px - 12, py - 12, px + 12, py + 12], fill=node_colour)
        # Centre hole
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=bg)

        # Add small vias nearby
        for _ in range(random.randint(1, 3)):
            vx = px + random.randint(-40, 40)
            vy = py + random.randint(-40, 40)
            draw.ellipse([vx - 3, vy - 3, vx + 3, vy + 3], fill=trace_colour)
            draw.ellipse([vx - 1, vy - 1, vx + 1, vy + 1], fill=bg)

def draw_splatter_style(draw, shape, img):
    """Paint splatter explosion from pentomino shape"""
    points = shape_to_points(shape, scale=80, jitter=10)
    adjacencies = get_adjacencies(shape)

    # Create splatter from each cell
    for idx, ((row, col), (px, py)) in enumerate(points.items()):
        colour = hex_to_rgb(colours[idx % len(colours)])

        # Main splat
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(5, 100)
            # Bias distance based on adjacencies
            sx = px + math.cos(angle) * distance
            sy = py + math.sin(angle) * distance

            size = random.uniform(3, 25) * (1 - distance / 150)
            if size > 1:
                draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=colour)

        # Drips
        for _ in range(5):
            drip_x = px + random.randint(-30, 30)
            drip_y = py + random.randint(0, 20)
            drip_length = random.randint(30, 100)
            drip_width = random.randint(2, 6)

            # Tapered drip
            for i in range(drip_length):
                t = i / drip_length
                w = drip_width * (1 - t * 0.8)
                if w > 0.5:
                    draw.ellipse([drip_x - w, drip_y + i - w,
                                 drip_x + w, drip_y + i + w], fill=colour)

    # Connect adjacent cells with splatter trails
    for (r1, c1), (r2, c2) in adjacencies:
        p1 = points[(r1, c1)]
        p2 = points[(r2, c2)]
        colour = hex_to_rgb(random.choice(colours))

        for _ in range(40):
            t = random.uniform(0, 1)
            sx = p1[0] + (p2[0] - p1[0]) * t + random.randint(-20, 20)
            sy = p1[1] + (p2[1] - p1[1]) * t + random.randint(-20, 20)
            size = random.uniform(2, 10)
            draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=colour)

def draw_contour_style(draw, shape, img):
    """Topographic contour lines following pentomino topology"""
    points = shape_to_points(shape, scale=90, jitter=0)

    # Background
    bg = hex_to_rgb(colours[-1])
    draw.rectangle([0, 0, width, height], fill=bg)

    line_colour = hex_to_rgb(colours[1])

    # Create height field based on distance to pentomino cells
    def get_height(x, y):
        min_dist = float('inf')
        for (row, col), (px, py) in points.items():
            dist = math.sqrt((x - px)**2 + (y - py)**2)
            min_dist = min(min_dist, dist)
        return min_dist

    # Draw contour lines
    contour_levels = [20, 40, 60, 80, 100, 130, 160, 200]

    for level in contour_levels:
        # March around finding contour
        contour_points = []

        step = 8
        for x in range(0, width, step):
            for y in range(0, height, step):
                h = get_height(x, y)
                h_right = get_height(x + step, y) if x + step < width else h
                h_down = get_height(x, y + step) if y + step < height else h

                # Check for contour crossing
                if (h < level <= h_right) or (h_right < level <= h):
                    t = (level - h) / (h_right - h) if h_right != h else 0.5
                    contour_points.append((x + t * step, y))

                if (h < level <= h_down) or (h_down < level <= h):
                    t = (level - h) / (h_down - h) if h_down != h else 0.5
                    contour_points.append((x, y + t * step))

        # Draw points as small marks
        thickness = 3 if level in [40, 80, 130] else 1
        alpha = 255 if level in [40, 80, 130] else 150

        for px, py in contour_points:
            r, g, b = line_colour
            draw.ellipse([px - thickness, py - thickness,
                         px + thickness, py + thickness], fill=(r, g, b))

    # Mark the pentomino cells
    accent = hex_to_rgb(colours[0])
    for (row, col), (px, py) in points.items():
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=accent)
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 255))


# Pick a random pentomino
shape = random.choice(list(pentominoes.values()))

# Create image
bg_colour = "#1a1a1a" if style in ["constellation", "splatter"] else colours[-1]
img = Image.new("RGB", (width, height), bg_colour)
draw = ImageDraw.Draw(img)

# Apply the selected style
if style == "blob":
    draw_blob_style(draw, shape, img)
elif style == "constellation":
    draw_constellation_style(draw, shape, img)
elif style == "roots":
    draw_roots_style(draw, shape, img)
elif style == "circuit":
    draw_circuit_style(draw, shape, img)
elif style == "splatter":
    draw_splatter_style(draw, shape, img)
elif style == "contour":
    draw_contour_style(draw, shape, img)

img
