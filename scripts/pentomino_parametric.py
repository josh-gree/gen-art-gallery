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
  - name: cell_scale
    distribution: gamma
    a: 4
    loc: 50
    scale: 20
  - name: cell_jitter
    distribution: expon
    loc: 0
    scale: 10
  - name: hue_base
    distribution: uniform
    loc: 0
    scale: 360
  - name: hue_spread
    distribution: pareto
    b: 2
    loc: 0
    scale: 30
  - name: saturation
    distribution: beta
    a: 3
    b: 1.5
    loc: 0.3
    scale: 0.7
  - name: lightness
    distribution: triang
    c: 0.6
    loc: 0.25
    scale: 0.5
  - name: bg_lightness
    distribution: beta
    a: 1.5
    b: 5
    loc: 0
    scale: 0.3
  - name: stroke_weight
    distribution: expon
    loc: 0
    scale: 3
  - name: fill_opacity
    distribution: beta
    a: 5
    b: 2
    loc: 0.2
    scale: 0.8
  - name: blur_amount
    distribution: expon
    loc: 0
    scale: 4
  - name: rotation_deg
    distribution: vonmises
    kappa: 0.5
    loc: 0
    scale: 57.3
  - name: tentacle_count
    distribution: poisson
    mu: 2
  - name: tentacle_length
    distribution: lognorm
    s: 0.5
    loc: 20
    scale: 50
  - name: tentacle_curl
    distribution: beta
    a: 2
    b: 2
    loc: 0
    scale: 0.6
  - name: dot_density
    distribution: beta
    a: 0.5
    b: 2
    loc: 0
    scale: 1
  - name: dot_size_min
    distribution: uniform
    loc: 1
    scale: 4
  - name: dot_size_max
    distribution: gamma
    a: 2
    loc: 5
    scale: 5
  - name: glow_intensity
    distribution: beta
    a: 1
    b: 3
    loc: 0
    scale: 1
  - name: glow_radius
    distribution: gamma
    a: 3
    loc: 5
    scale: 10
  - name: connection_style
    distribution: uniform
    loc: 0
    scale: 1
  - name: shape_distortion
    distribution: expon
    loc: 0
    scale: 0.15
  - name: noise_amount
    distribution: expon
    loc: 0
    scale: 15
  - name: ring_count
    distribution: poisson
    mu: 1.5
  - name: ring_spacing
    distribution: gamma
    a: 2
    loc: 4
    scale: 5
  - name: hatching_density
    distribution: beta
    a: 0.8
    b: 3
    loc: 0
    scale: 1
  - name: hatching_angle
    distribution: vonmises
    kappa: 1
    loc: 45
    scale: 30
  - name: secondary_hue_offset
    distribution: norm
    loc: 120
    scale: 40
  - name: gradient_strength
    distribution: beta
    a: 2
    b: 4
    loc: 0
    scale: 1
  - name: corner_radius_factor
    distribution: beta
    a: 1.5
    b: 1.5
    loc: 0
    scale: 0.5
  - name: shadow_offset
    distribution: expon
    loc: 0
    scale: 8
  - name: shadow_opacity
    distribution: beta
    a: 2
    b: 3
    loc: 0
    scale: 0.8
"""

from PIL import Image, ImageDraw, ImageFilter
import random
import math
import colorsys

random.seed(seed)

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

def hsl_to_rgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))

def get_colour(offset=0):
    h = (hue_base + offset) % 360
    return hsl_to_rgb(h, saturation, lightness)

def get_secondary_colour():
    return get_colour(secondary_hue_offset)

def rotate_point(x, y, cx, cy, angle_rad):
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    dx, dy = x - cx, y - cy
    return cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a

def get_adjacencies(shape):
    adj = []
    shape_set = set(shape)
    for r, c in shape:
        for dr, dc in [(0, 1), (1, 0)]:
            n = (r + dr, c + dc)
            if n in shape_set:
                adj.append(((r, c), n))
    return adj

# Pick shape and calculate positions
shape = random.choice(list(pentominoes.values()))

# Calculate bounds
rows = [p[0] for p in shape]
cols = [p[1] for p in shape]
min_r, max_r = min(rows), max(rows)
min_c, max_c = min(cols), max(cols)

# Centre position
centre_x = width // 2
centre_y = height // 2

# Calculate cell positions with jitter and rotation
angle_rad = math.radians(rotation_deg)
points = {}
for r, c in shape:
    jx = random.uniform(-cell_jitter, cell_jitter)
    jy = random.uniform(-cell_jitter, cell_jitter)

    base_x = (c - (min_c + max_c) / 2) * cell_scale + jx
    base_y = (r - (min_r + max_r) / 2) * cell_scale + jy

    rx, ry = rotate_point(base_x, base_y, 0, 0, angle_rad)
    points[(r, c)] = (centre_x + rx, centre_y + ry)

adjacencies = get_adjacencies(shape)

# Create image with background
bg_colour = hsl_to_rgb(hue_base, saturation * 0.3, bg_lightness)
img = Image.new("RGB", (width, height), bg_colour)
draw = ImageDraw.Draw(img)

# Background noise
if noise_amount > 0:
    for _ in range(int(noise_amount * 500)):
        nx = random.randint(0, width - 1)
        ny = random.randint(0, height - 1)
        noise_var = random.randint(-int(noise_amount), int(noise_amount))
        current = img.getpixel((nx, ny))
        noisy = tuple(max(0, min(255, c + noise_var)) for c in current)
        draw.point([nx, ny], fill=noisy)

# Draw shadows first
if shadow_offset > 0.5 and shadow_opacity > 0.05:
    shadow_colour = (0, 0, 0, int(shadow_opacity * 255))
    shadow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)

    for (r, c), (px, py) in points.items():
        sx, sy = px + shadow_offset, py + shadow_offset
        half = cell_scale / 2
        corner_r = half * corner_radius_factor

        if corner_r > 1:
            shadow_draw.rounded_rectangle(
                [sx - half, sy - half, sx + half, sy + half],
                radius=int(corner_r), fill=shadow_colour
            )
        else:
            shadow_draw.rectangle(
                [sx - half, sy - half, sx + half, sy + half],
                fill=shadow_colour
            )

    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_offset / 2))
    img = Image.alpha_composite(img.convert("RGBA"), shadow_img).convert("RGB")
    draw = ImageDraw.Draw(img)

# Draw glow layer
if glow_intensity > 0.05:
    glow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    glow_colour = (*get_colour(), int(glow_intensity * 150))

    for (r, c), (px, py) in points.items():
        glow_draw.ellipse(
            [px - glow_radius, py - glow_radius, px + glow_radius, py + glow_radius],
            fill=glow_colour
        )

    glow_img = glow_img.filter(ImageFilter.GaussianBlur(glow_radius * 0.7))
    img = Image.alpha_composite(img.convert("RGBA"), glow_img).convert("RGB")
    draw = ImageDraw.Draw(img)

# Draw connections between adjacent cells
for (r1, c1), (r2, c2) in adjacencies:
    p1, p2 = points[(r1, c1)], points[(r2, c2)]
    conn_colour = get_secondary_colour()

    if connection_style < 0.33:
        w = max(1, int(stroke_weight * 1.5))
        draw.line([p1, p2], fill=conn_colour, width=w)
    elif connection_style < 0.66:
        ctrl_x = (p1[0] + p2[0]) / 2 + random.uniform(-20, 20)
        ctrl_y = (p1[1] + p2[1]) / 2 + random.uniform(-20, 20)
        steps = 20
        prev = p1
        for i in range(1, steps + 1):
            t = i / steps
            x = (1-t)**2 * p1[0] + 2*(1-t)*t * ctrl_x + t**2 * p2[0]
            y = (1-t)**2 * p1[1] + 2*(1-t)*t * ctrl_y + t**2 * p2[1]
            draw.line([prev, (x, y)], fill=conn_colour, width=max(1, int(stroke_weight)))
            prev = (x, y)
    else:
        dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
        num_dots = max(3, int(dist / 15))
        for i in range(num_dots):
            t = i / (num_dots - 1)
            dx = p1[0] + (p2[0] - p1[0]) * t
            dy = p1[1] + (p2[1] - p1[1]) * t
            dot_r = 2 + stroke_weight * 0.5
            draw.ellipse([dx-dot_r, dy-dot_r, dx+dot_r, dy+dot_r], fill=conn_colour)

# Draw each cell
for idx, ((r, c), (px, py)) in enumerate(points.items()):
    half = cell_scale / 2

    cell_hue_offset = (idx / len(points)) * hue_spread
    cell_colour = get_colour(cell_hue_offset)
    fill_colour = (*cell_colour, int(fill_opacity * 255))

    distort = shape_distortion * half * 0.5
    corners = [
        (px - half + random.uniform(-distort, distort), py - half + random.uniform(-distort, distort)),
        (px + half + random.uniform(-distort, distort), py - half + random.uniform(-distort, distort)),
        (px + half + random.uniform(-distort, distort), py + half + random.uniform(-distort, distort)),
        (px - half + random.uniform(-distort, distort), py + half + random.uniform(-distort, distort)),
    ]

    cell_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cell_draw = ImageDraw.Draw(cell_img)

    corner_r = half * corner_radius_factor

    if shape_distortion < 0.1 and corner_r > 1:
        cell_draw.rounded_rectangle(
            [px - half, py - half, px + half, py + half],
            radius=int(corner_r), fill=fill_colour
        )
    else:
        cell_draw.polygon(corners, fill=fill_colour)

    if gradient_strength > 0.05:
        for i in range(int(half * 2)):
            t = i / (half * 2)
            alpha = int(gradient_strength * 80 * (1 - t))
            cell_draw.line(
                [px - half, py - half + i, px + half, py - half + i],
                fill=(255, 255, 255, alpha)
            )

    img = Image.alpha_composite(img.convert("RGBA"), cell_img).convert("RGB")
    draw = ImageDraw.Draw(img)

    if stroke_weight > 0.5:
        stroke_colour = hsl_to_rgb((hue_base + cell_hue_offset) % 360, saturation, min(0.9, lightness + 0.2))
        if shape_distortion < 0.1 and corner_r > 1:
            draw.rounded_rectangle(
                [px - half, py - half, px + half, py + half],
                radius=int(corner_r), outline=stroke_colour, width=int(stroke_weight)
            )
        else:
            draw.polygon(corners, outline=stroke_colour)

    if ring_count > 0:
        ring_colour = hsl_to_rgb((hue_base + 180) % 360, saturation, lightness)
        for ring in range(int(ring_count)):
            r_offset = (ring + 1) * ring_spacing
            if r_offset < half - 5:
                draw.ellipse(
                    [px - r_offset, py - r_offset, px + r_offset, py + r_offset],
                    outline=ring_colour, width=max(1, int(stroke_weight * 0.5))
                )

    if hatching_density > 0.1:
        hatch_spacing = int(10 - hatching_density * 8) + 2
        hatch_angle_rad = math.radians(hatching_angle)
        hatch_colour = hsl_to_rgb(hue_base, saturation * 0.5, lightness * 0.5)

        for offset in range(-int(half * 2), int(half * 2), hatch_spacing):
            cos_h = math.cos(hatch_angle_rad)
            sin_h = math.sin(hatch_angle_rad)

            x1 = px + offset * cos_h - half * 2 * sin_h
            y1 = py + offset * sin_h + half * 2 * cos_h
            x2 = px + offset * cos_h + half * 2 * sin_h
            y2 = py + offset * sin_h - half * 2 * cos_h

            if abs(x1 - px) < half and abs(y1 - py) < half:
                draw.line([x1, y1, x2, y2], fill=hatch_colour, width=1)

    if dot_density > 0.1:
        num_dots = int(dot_density * 30)
        for _ in range(num_dots):
            dx = px + random.uniform(-half * 0.8, half * 0.8)
            dy = py + random.uniform(-half * 0.8, half * 0.8)
            dot_r = random.uniform(dot_size_min, dot_size_max)
            dot_colour = hsl_to_rgb(
                (hue_base + random.uniform(0, hue_spread)) % 360,
                saturation,
                random.uniform(lightness * 0.8, min(1, lightness * 1.2))
            )
            draw.ellipse([dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r], fill=dot_colour)

    if tentacle_count > 0:
        shape_set = set(shape)
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if (r + dr, c + dc) not in shape_set:
                for _ in range(int(tentacle_count) // 4 + 1):
                    angle = math.atan2(dr, dc) + random.uniform(-0.5, 0.5)
                    start_x = px + dc * half * 0.8
                    start_y = py + dr * half * 0.8

                    tx, ty = start_x, start_y
                    curr_angle = angle
                    tent_colour = get_secondary_colour()

                    for seg in range(int(tentacle_length / 5)):
                        seg_len = 5
                        thickness = max(1, int((1 - seg / (tentacle_length / 5)) * stroke_weight * 1.5))

                        nx = tx + math.cos(curr_angle) * seg_len
                        ny = ty + math.sin(curr_angle) * seg_len

                        draw.line([tx, ty, nx, ny], fill=tent_colour, width=thickness)

                        tx, ty = nx, ny
                        curr_angle += tentacle_curl * random.uniform(-1, 1)

if blur_amount > 0.5:
    img = img.filter(ImageFilter.GaussianBlur(blur_amount))

img
