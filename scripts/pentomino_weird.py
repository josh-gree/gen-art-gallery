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
    values: ["entity", "embroidery", "interference", "recursive", "portal", "magnetic"]
  - name: mood
    distribution: choice
    values: ["dark", "light", "vivid"]
"""

from PIL import Image, ImageDraw, ImageFilter
import random
import math

random.seed(seed)

moods = {
    'dark': {'bg': '#0a0a0f', 'fg': ['#c9ada7', '#9a8c98', '#4a4e69', '#22223b', '#f2e9e4']},
    'light': {'bg': '#fefae0', 'fg': ['#283618', '#606c38', '#dda15e', '#bc6c25', '#264653']},
    'vivid': {'bg': '#10002b', 'fg': ['#e0aaff', '#c77dff', '#9d4edd', '#7b2cbf', '#5a189a']}
}

colours = moods[mood]['fg']
bg_colour = moods[mood]['bg']

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

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def shape_to_points(shape, scale=80):
    rows = [p[0] for p in shape]
    cols = [p[1] for p in shape]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)
    shape_h = (max_r - min_r + 1) * scale
    shape_w = (max_c - min_c + 1) * scale
    offset_x = (width - shape_w) // 2 - min_c * scale + scale // 2
    offset_y = (height - shape_h) // 2 - min_r * scale + scale // 2
    return {(r, c): (offset_x + c * scale, offset_y + r * scale) for r, c in shape}

def get_adjacencies(shape):
    adj = []
    shape_set = set(shape)
    for r, c in shape:
        for dr, dc in [(0, 1), (1, 0)]:
            n = (r + dr, c + dc)
            if n in shape_set:
                adj.append(((r, c), n))
    return adj

def draw_entity_style(draw, shape, img):
    """Eldritch entity with eyes and tentacles"""
    points = shape_to_points(shape, scale=90)
    adjacencies = get_adjacencies(shape)

    # Pulsating flesh background for shape area
    flesh_colour = hex_to_rgb(colours[0])

    # Draw tentacles extending from edges
    edge_cells = []
    shape_set = set(shape)
    for r, c in shape:
        neighbours = sum(1 for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)] if (r+dr,c+dc) in shape_set)
        if neighbours < 4:
            edge_cells.append((r, c))

    for r, c in edge_cells:
        px, py = points[(r, c)]
        # Find outward direction
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            if (r+dr, c+dc) not in shape_set:
                # Draw tentacle in this direction
                angle = math.atan2(dr, dc)
                num_tentacles = random.randint(1, 3)
                for _ in range(num_tentacles):
                    draw_tentacle(draw, px, py, angle + random.uniform(-0.5, 0.5), colours)

    # Draw main body mass
    body_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    body_draw = ImageDraw.Draw(body_img)

    for (r, c), (px, py) in points.items():
        # Lumpy flesh
        for _ in range(8):
            ox, oy = random.randint(-20, 20), random.randint(-20, 20)
            rad = random.randint(30, 50)
            r_var = random.randint(-15, 15)
            body_draw.ellipse([px+ox-rad, py+oy-rad, px+ox+rad+r_var, py+oy+rad+r_var],
                             fill=(*flesh_colour, 200))

    body_img = body_img.filter(ImageFilter.GaussianBlur(5))
    img.paste(Image.alpha_composite(img.convert("RGBA"), body_img).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img)

    # Draw eyes on each cell
    for (r, c), (px, py) in points.items():
        num_eyes = random.randint(1, 4)
        for _ in range(num_eyes):
            ex = px + random.randint(-25, 25)
            ey = py + random.randint(-25, 25)
            draw_eye(draw, ex, ey, random.randint(8, 18))

def draw_tentacle(draw, start_x, start_y, angle, colours):
    """Draw a curving tentacle"""
    length = random.randint(60, 150)
    segments = 20
    thickness = random.randint(6, 12)

    x, y = start_x, start_y
    curr_angle = angle

    colour = hex_to_rgb(random.choice(colours[1:3]))

    for i in range(segments):
        t = i / segments
        curr_thickness = thickness * (1 - t * 0.8)
        seg_len = length / segments

        nx = x + math.cos(curr_angle) * seg_len
        ny = y + math.sin(curr_angle) * seg_len

        if curr_thickness > 0.5:
            draw.line([x, y, nx, ny], fill=colour, width=int(curr_thickness))

        x, y = nx, ny
        curr_angle += random.uniform(-0.4, 0.4)

    # Sucker at end
    draw.ellipse([x-3, y-3, x+3, y+3], fill=hex_to_rgb(colours[-1]))

def draw_eye(draw, cx, cy, radius):
    """Draw a creepy eye"""
    # Outer eye
    draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill='#f0e6d3')
    # Bloodshot veins
    for _ in range(5):
        angle = random.uniform(0, 2*math.pi)
        vein_len = radius * 0.8
        draw.line([cx, cy, cx + math.cos(angle)*vein_len, cy + math.sin(angle)*vein_len],
                 fill='#8b0000', width=1)
    # Iris
    iris_r = radius * 0.6
    iris_colour = random.choice(['#2d4a3e', '#4a3728', '#1a1a2e', '#4a1942'])
    draw.ellipse([cx-iris_r, cy-iris_r, cx+iris_r, cy+iris_r], fill=iris_colour)
    # Pupil
    pupil_r = radius * 0.3
    # Pupil looks in random direction
    px = cx + random.randint(-3, 3)
    py = cy + random.randint(-3, 3)
    draw.ellipse([px-pupil_r, py-pupil_r, px+pupil_r, py+pupil_r], fill='#000000')
    # Highlight
    draw.ellipse([cx-radius*0.2, cy-radius*0.3, cx+radius*0.1, cy-radius*0.1], fill='#ffffff')

def draw_embroidery_style(draw, shape, img):
    """Cross-stitch and embroidery aesthetic"""
    points = shape_to_points(shape, scale=100)
    adjacencies = get_adjacencies(shape)

    # Fabric texture background
    fabric = hex_to_rgb(bg_colour)
    for y in range(0, height, 3):
        for x in range(0, width, 3):
            var = random.randint(-8, 8)
            col = tuple(max(0, min(255, c + var)) for c in fabric)
            draw.rectangle([x, y, x+2, y+2], fill=col)

    thread_colour = hex_to_rgb(colours[0])
    accent_colour = hex_to_rgb(colours[2])

    # Draw running stitch outline around entire shape
    all_edges = get_shape_outline(shape, points, 100)
    for (x1, y1), (x2, y2) in all_edges:
        draw_running_stitch(draw, x1, y1, x2, y2, thread_colour)

    # Fill each cell with cross stitches
    for (r, c), (px, py) in points.items():
        cell_colour = hex_to_rgb(random.choice(colours))
        draw_cross_stitch_fill(draw, px - 40, py - 40, 80, 80, cell_colour)

    # Decorative french knots at corners
    for (r, c), (px, py) in points.items():
        for dx, dy in [(-35, -35), (35, -35), (-35, 35), (35, 35)]:
            if random.random() < 0.5:
                draw_french_knot(draw, px + dx, py + dy, accent_colour)

    # Connecting chain stitch between adjacent cells
    for (r1, c1), (r2, c2) in adjacencies:
        p1, p2 = points[(r1, c1)], points[(r2, c2)]
        draw_chain_stitch(draw, p1[0], p1[1], p2[0], p2[1], accent_colour)

def get_shape_outline(shape, points, scale):
    """Get outline edges of shape"""
    edges = []
    shape_set = set(shape)
    half = scale // 2

    for r, c in shape:
        px, py = points[(r, c)]
        # Check each side
        if (r-1, c) not in shape_set:  # Top
            edges.append(((px-half, py-half), (px+half, py-half)))
        if (r+1, c) not in shape_set:  # Bottom
            edges.append(((px-half, py+half), (px+half, py+half)))
        if (r, c-1) not in shape_set:  # Left
            edges.append(((px-half, py-half), (px-half, py+half)))
        if (r, c+1) not in shape_set:  # Right
            edges.append(((px+half, py-half), (px+half, py+half)))

    return edges

def draw_running_stitch(draw, x1, y1, x2, y2, colour):
    """Draw dashed running stitch"""
    dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    stitch_len = 8
    gap_len = 4
    steps = int(dist / (stitch_len + gap_len))

    dx = (x2 - x1) / dist if dist > 0 else 0
    dy = (y2 - y1) / dist if dist > 0 else 0

    for i in range(steps):
        sx = x1 + (i * (stitch_len + gap_len)) * dx
        sy = y1 + (i * (stitch_len + gap_len)) * dy
        ex = sx + stitch_len * dx
        ey = sy + stitch_len * dy
        draw.line([sx, sy, ex, ey], fill=colour, width=2)

def draw_cross_stitch_fill(draw, x, y, w, h, colour):
    """Fill area with cross stitches"""
    stitch_size = 10
    for sy in range(int(y), int(y + h), stitch_size):
        for sx in range(int(x), int(x + w), stitch_size):
            # Draw X
            draw.line([sx, sy, sx+stitch_size-2, sy+stitch_size-2], fill=colour, width=2)
            draw.line([sx+stitch_size-2, sy, sx, sy+stitch_size-2], fill=colour, width=2)

def draw_french_knot(draw, x, y, colour):
    """Draw a french knot (small bumpy circle)"""
    draw.ellipse([x-4, y-4, x+4, y+4], fill=colour)
    draw.ellipse([x-2, y-3, x+2, y+1], fill=tuple(min(255, c+40) for c in colour))

def draw_chain_stitch(draw, x1, y1, x2, y2, colour):
    """Draw chain stitch between two points"""
    dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    chains = int(dist / 12)

    for i in range(chains):
        t = i / chains
        cx = x1 + (x2 - x1) * t
        cy = y1 + (y2 - y1) * t
        draw.ellipse([cx-4, cy-4, cx+4, cy+4], outline=colour, width=2)

def draw_interference_style(draw, shape, img):
    """Moiré interference patterns"""
    points = shape_to_points(shape, scale=90)

    line_colour = hex_to_rgb(colours[0])

    # Create two sets of concentric patterns that interfere
    centres = list(points.values())

    # Draw concentric circles from each cell centre
    for cx, cy in centres:
        for radius in range(5, 300, 6):
            # Only draw within bounds
            opacity = max(0, 255 - radius)
            for angle in range(0, 360, 2):
                rad = math.radians(angle)
                x = cx + math.cos(rad) * radius
                y = cy + math.sin(rad) * radius

                # Check if point is reasonably close to any pentomino cell
                min_dist = min(math.sqrt((x-px)**2 + (y-py)**2) for px, py in centres)

                if 0 <= x < width and 0 <= y < height and min_dist < 200:
                    # Interference: darken where circles overlap
                    overlaps = sum(1 for px, py in centres
                                  if abs(math.sqrt((x-px)**2 + (y-py)**2) - radius) < 4)

                    if overlaps > 0:
                        intensity = min(255, 50 + overlaps * 60)
                        draw.point([x, y], fill=(*line_colour[:2], intensity))

    # Add wave patterns
    wave_colour = hex_to_rgb(colours[2])
    for cx, cy in centres:
        for i in range(50):
            angle = i * 0.3
            for t in range(100):
                r = t * 3
                wave = math.sin(r * 0.1 + angle) * 10
                x = cx + math.cos(angle) * (r + wave)
                y = cy + math.sin(angle) * (r + wave)
                if 0 <= x < width and 0 <= y < height:
                    draw.point([x, y], fill=wave_colour)

def draw_recursive_style(draw, shape, img):
    """Pentominoes made of smaller pentominoes"""
    points = shape_to_points(shape, scale=110)

    # For each cell, draw a smaller random pentomino
    for idx, ((r, c), (px, py)) in enumerate(points.items()):
        mini_shape = random.choice(list(pentominoes.values()))
        colour = hex_to_rgb(colours[idx % len(colours)])

        # Calculate bounds of mini shape
        mini_rows = [p[0] for p in mini_shape]
        mini_cols = [p[1] for p in mini_shape]
        mini_h = max(mini_rows) - min(mini_rows) + 1
        mini_w = max(mini_cols) - min(mini_cols) + 1

        mini_scale = min(80 // mini_h, 80 // mini_w)

        mini_offset_x = px - (mini_w * mini_scale) // 2 - min(mini_cols) * mini_scale
        mini_offset_y = py - (mini_h * mini_scale) // 2 - min(mini_rows) * mini_scale

        # Draw the mini pentomino
        for mr, mc in mini_shape:
            mx = mini_offset_x + mc * mini_scale
            my = mini_offset_y + mr * mini_scale

            # Draw with slight 3D effect
            shadow = tuple(max(0, c - 50) for c in colour)
            draw.rectangle([mx+2, my+2, mx+mini_scale-2+2, my+mini_scale-2+2], fill=shadow)
            draw.rectangle([mx, my, mx+mini_scale-2, my+mini_scale-2], fill=colour)

            # Even smaller pentominoes inside (if scale allows)
            if mini_scale > 15:
                tiny_shape = random.choice(list(pentominoes.values()))
                tiny_scale = 3
                for tr, tc in tiny_shape[:3]:  # Just first 3 cells
                    tx = mx + 5 + tc * tiny_scale
                    ty = my + 5 + tr * tiny_scale
                    highlight = tuple(min(255, c + 60) for c in colour)
                    draw.rectangle([tx, ty, tx+tiny_scale-1, ty+tiny_scale-1], fill=highlight)

def draw_portal_style(draw, shape, img):
    """Each cell is a portal to somewhere else"""
    points = shape_to_points(shape, scale=100)

    # Different "dimensions" for each cell
    dimensions = ['void', 'fire', 'water', 'static', 'eyes']

    for idx, ((r, c), (px, py)) in enumerate(points.items()):
        dimension = dimensions[idx % len(dimensions)]

        # Portal frame
        frame_colour = hex_to_rgb(colours[idx % len(colours)])

        # Outer glow
        for radius in range(50, 35, -3):
            alpha = 150 - (50 - radius) * 10
            draw.ellipse([px-radius, py-radius, px+radius, py+radius],
                        outline=frame_colour, width=2)

        # Inner dimension content
        if dimension == 'void':
            # Pure black with distant stars
            draw.ellipse([px-35, py-35, px+35, py+35], fill='#000000')
            for _ in range(20):
                sx = px + random.randint(-30, 30)
                sy = py + random.randint(-30, 30)
                if math.sqrt((sx-px)**2 + (sy-py)**2) < 30:
                    draw.point([sx, sy], fill='#ffffff')

        elif dimension == 'fire':
            # Flames
            for _ in range(30):
                fx = px + random.randint(-25, 25)
                fy = py + random.randint(-20, 30)
                if math.sqrt((fx-px)**2 + (fy-py)**2) < 32:
                    fire_colours = ['#ff0000', '#ff4500', '#ff8c00', '#ffd700']
                    size = random.randint(2, 8)
                    draw.ellipse([fx-size, fy-size, fx+size, fy+size],
                                fill=random.choice(fire_colours))

        elif dimension == 'water':
            # Ripples
            draw.ellipse([px-35, py-35, px+35, py+35], fill='#001a33')
            for radius in range(5, 35, 7):
                draw.ellipse([px-radius, py-radius, px+radius, py+radius],
                            outline='#4488aa', width=1)

        elif dimension == 'static':
            # TV static
            for sy in range(int(py-32), int(py+32), 2):
                for sx in range(int(px-32), int(px+32), 2):
                    if math.sqrt((sx-px)**2 + (sy-py)**2) < 32:
                        grey = random.randint(0, 255)
                        draw.rectangle([sx, sy, sx+1, sy+1], fill=(grey, grey, grey))

        elif dimension == 'eyes':
            # Many small eyes
            draw.ellipse([px-35, py-35, px+35, py+35], fill='#1a0a1a')
            for _ in range(8):
                ex = px + random.randint(-25, 25)
                ey = py + random.randint(-25, 25)
                if math.sqrt((ex-px)**2 + (ey-py)**2) < 28:
                    draw_eye(draw, ex, ey, random.randint(4, 8))

        # Swirling edge effect
        for i in range(60):
            angle = i * 0.1 + random.uniform(0, 0.5)
            r = 38 + math.sin(i * 0.5) * 5
            ex = px + math.cos(angle) * r
            ey = py + math.sin(angle) * r
            draw.ellipse([ex-2, ey-2, ex+2, ey+2], fill=frame_colour)

def draw_magnetic_style(draw, shape, img):
    """Magnetic field lines emanating from cells"""
    points = shape_to_points(shape, scale=90)

    # Assign polarity to each cell
    polarities = {pos: random.choice([-1, 1]) for pos in points.keys()}

    pos_colour = hex_to_rgb(colours[0])
    neg_colour = hex_to_rgb(colours[2])

    # Draw field lines
    for start_pos, (start_x, start_y) in points.items():
        polarity = polarities[start_pos]
        colour = pos_colour if polarity > 0 else neg_colour

        # Multiple field lines from each pole
        for line_idx in range(12):
            angle = line_idx * (2 * math.pi / 12) + random.uniform(-0.2, 0.2)

            x, y = start_x, start_y

            # Trace field line
            for step in range(150):
                # Calculate field direction at this point
                fx, fy = 0, 0

                for other_pos, (ox, oy) in points.items():
                    dx = x - ox
                    dy = y - oy
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < 1:
                        continue

                    other_polarity = polarities[other_pos]
                    strength = other_polarity / (dist_sq + 100)

                    dist = math.sqrt(dist_sq)
                    fx += strength * dx / dist
                    fy += strength * dy / dist

                # Normalize
                f_mag = math.sqrt(fx*fx + fy*fy)
                if f_mag < 0.001:
                    break

                fx /= f_mag
                fy /= f_mag

                # Move along field
                step_size = 4
                nx = x + fx * step_size * polarity
                ny = y + fy * step_size * polarity

                # Draw segment
                alpha = max(0, 255 - step * 2)
                draw.line([x, y, nx, ny], fill=colour, width=1)

                x, y = nx, ny

                # Stop if out of bounds
                if x < 0 or x >= width or y < 0 or y >= height:
                    break

    # Draw poles
    for (r, c), (px, py) in points.items():
        polarity = polarities[(r, c)]
        colour = pos_colour if polarity > 0 else neg_colour

        # Glowing pole
        for radius in [20, 15, 10, 5]:
            draw.ellipse([px-radius, py-radius, px+radius, py+radius], fill=colour)

        # + or - symbol
        symbol_colour = '#ffffff' if polarity > 0 else '#000000'
        draw.line([px-6, py, px+6, py], fill=symbol_colour, width=2)
        if polarity > 0:
            draw.line([px, py-6, px, py+6], fill=symbol_colour, width=2)


# Pick a random pentomino
shape = random.choice(list(pentominoes.values()))

# Create image
img = Image.new("RGB", (width, height), bg_colour)
draw = ImageDraw.Draw(img)

# Apply the selected style
if style == "entity":
    draw_entity_style(draw, shape, img)
elif style == "embroidery":
    draw_embroidery_style(draw, shape, img)
elif style == "interference":
    draw_interference_style(draw, shape, img)
elif style == "recursive":
    draw_recursive_style(draw, shape, img)
elif style == "portal":
    draw_portal_style(draw, shape, img)
elif style == "magnetic":
    draw_magnetic_style(draw, shape, img)

img
