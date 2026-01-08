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
  - name: cell_jitter_dist
    distribution: laplace
    loc: 0
    scale: 8
    mode: distribution
  - name: hue_base
    distribution: uniform
    loc: 0
    scale: 360
  - name: hue_spread
    distribution: pareto
    b: 2
    loc: 0
    scale: 30
  - name: saturation_dist
    distribution: beta
    a: 3
    b: 1.5
    loc: 0.3
    scale: 0.7
    mode: distribution
  - name: lightness_dist
    distribution: triang
    c: 0.6
    loc: 0.25
    scale: 0.5
    mode: distribution
  - name: bg_lightness
    distribution: beta
    a: 1.5
    b: 5
    loc: 0
    scale: 0.3
  - name: stroke_weight_dist
    distribution: expon
    loc: 0
    scale: 3
    mode: distribution
  - name: fill_opacity_dist
    distribution: beta
    a: 5
    b: 2
    loc: 0.2
    scale: 0.8
    mode: distribution
  - name: blur_amount
    distribution: expon
    loc: 0
    scale: 1
  - name: rotation_deg
    distribution: vonmises
    kappa: 0.5
    loc: 0
    scale: 57.3
  - name: tentacle_count_dist
    distribution: poisson
    mu: 2
    mode: distribution
  - name: tentacle_length_dist
    distribution: lognorm
    s: 0.5
    loc: 20
    scale: 50
    mode: distribution
  - name: tentacle_curl_dist
    distribution: cauchy
    loc: 0
    scale: 0.1
    mode: distribution
  - name: dot_density_dist
    distribution: beta
    a: 0.5
    b: 2
    loc: 0
    scale: 1
    mode: distribution
  - name: dot_size_dist
    distribution: gamma
    a: 2
    loc: 1
    scale: 4
    mode: distribution
  - name: glow_intensity
    distribution: beta
    a: 1
    b: 3
    loc: 0
    scale: 1
  - name: glow_radius_dist
    distribution: gamma
    a: 3
    loc: 5
    scale: 10
    mode: distribution
  - name: connection_style
    distribution: uniform
    loc: 0
    scale: 1
  - name: shape_distortion_dist
    distribution: expon
    loc: 0
    scale: 0.15
    mode: distribution
  - name: noise_amount
    distribution: expon
    loc: 0
    scale: 15
  - name: ring_count_dist
    distribution: poisson
    mu: 1.5
    mode: distribution
  - name: ring_spacing_dist
    distribution: gamma
    a: 2
    loc: 4
    scale: 5
    mode: distribution
  - name: hatching_density_dist
    distribution: beta
    a: 0.8
    b: 3
    loc: 0
    scale: 1
    mode: distribution
  - name: hatching_angle_dist
    distribution: vonmises
    kappa: 1
    loc: 0.78
    scale: 1
    mode: distribution
  - name: secondary_hue_offset
    distribution: norm
    loc: 120
    scale: 40
  - name: gradient_strength_dist
    distribution: beta
    a: 2
    b: 4
    loc: 0
    scale: 1
    mode: distribution
  - name: corner_radius_dist
    distribution: beta
    a: 1.5
    b: 1.5
    loc: 0
    scale: 0.5
    mode: distribution
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
  - name: cell_rotation_dist
    distribution: vonmises
    kappa: 2
    loc: 0
    scale: 0.5
    mode: distribution
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
    s = max(0, min(1, s))
    l = max(0, min(1, l))
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))

def get_colour(offset=0, sat=None, light=None):
    h = (hue_base + offset) % 360
    s = sat if sat is not None else saturation_dist.rvs()
    l = light if light is not None else lightness_dist.rvs()
    return hsl_to_rgb(h, s, l)

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

# Calculate cell positions with per-cell jitter and rotation
angle_rad = math.radians(rotation_deg)
points = {}
cell_properties = {}

for r, c in shape:
    # Sample per-cell jitter from laplace (can have outliers)
    jx = cell_jitter_dist.rvs()
    jy = cell_jitter_dist.rvs()

    base_x = (c - (min_c + max_c) / 2) * cell_scale + jx
    base_y = (r - (min_r + max_r) / 2) * cell_scale + jy

    rx, ry = rotate_point(base_x, base_y, 0, 0, angle_rad)
    points[(r, c)] = (centre_x + rx, centre_y + ry)

    # Sample per-cell properties
    cell_properties[(r, c)] = {
        'saturation': saturation_dist.rvs(),
        'lightness': lightness_dist.rvs(),
        'stroke_weight': stroke_weight_dist.rvs(),
        'fill_opacity': fill_opacity_dist.rvs(),
        'corner_radius': corner_radius_dist.rvs(),
        'shape_distortion': shape_distortion_dist.rvs(),
        'ring_count': int(ring_count_dist.rvs()),
        'ring_spacing': ring_spacing_dist.rvs(),
        'hatching_density': hatching_density_dist.rvs(),
        'hatching_angle': hatching_angle_dist.rvs(),
        'dot_density': dot_density_dist.rvs(),
        'gradient_strength': gradient_strength_dist.rvs(),
        'tentacle_count': int(tentacle_count_dist.rvs()),
        'glow_radius': glow_radius_dist.rvs(),
        'cell_rotation': cell_rotation_dist.rvs(),
    }

adjacencies = get_adjacencies(shape)

# Sample a base saturation/lightness for background consistency
base_sat = saturation_dist.rvs()
base_light = lightness_dist.rvs()

# Create image with background
bg_colour = hsl_to_rgb(hue_base, base_sat * 0.3, bg_lightness)
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
        props = cell_properties[(r, c)]
        sx, sy = px + shadow_offset, py + shadow_offset
        half = cell_scale / 2
        corner_r = half * props['corner_radius']

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

# Draw glow layer with per-cell radius
if glow_intensity > 0.05:
    glow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)

    for (r, c), (px, py) in points.items():
        props = cell_properties[(r, c)]
        glow_colour = (*get_colour(0, props['saturation'], props['lightness']), int(glow_intensity * 150))
        gr = props['glow_radius']

        glow_draw.ellipse([px - gr, py - gr, px + gr, py + gr], fill=glow_colour)

    glow_img = glow_img.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img.convert("RGBA"), glow_img).convert("RGB")
    draw = ImageDraw.Draw(img)

# Draw connections between adjacent cells
for (r1, c1), (r2, c2) in adjacencies:
    p1, p2 = points[(r1, c1)], points[(r2, c2)]
    conn_colour = get_secondary_colour()
    avg_stroke = (cell_properties[(r1, c1)]['stroke_weight'] + cell_properties[(r2, c2)]['stroke_weight']) / 2

    if connection_style < 0.33:
        w = max(1, int(avg_stroke * 1.5))
        draw.line([p1, p2], fill=conn_colour, width=w)
    elif connection_style < 0.66:
        ctrl_x = (p1[0] + p2[0]) / 2 + cell_jitter_dist.rvs() * 2
        ctrl_y = (p1[1] + p2[1]) / 2 + cell_jitter_dist.rvs() * 2
        steps = 20
        prev = p1
        for i in range(1, steps + 1):
            t = i / steps
            x = (1-t)**2 * p1[0] + 2*(1-t)*t * ctrl_x + t**2 * p2[0]
            y = (1-t)**2 * p1[1] + 2*(1-t)*t * ctrl_y + t**2 * p2[1]
            draw.line([prev, (x, y)], fill=conn_colour, width=max(1, int(avg_stroke)))
            prev = (x, y)
    else:
        dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
        num_dots = max(3, int(dist / 15))
        for i in range(num_dots):
            t = i / (num_dots - 1)
            dx = p1[0] + (p2[0] - p1[0]) * t
            dy = p1[1] + (p2[1] - p1[1]) * t
            dot_r = 2 + avg_stroke * 0.5
            draw.ellipse([dx-dot_r, dy-dot_r, dx+dot_r, dy+dot_r], fill=conn_colour)

# Draw each cell with its own properties
for idx, ((r, c), (px, py)) in enumerate(points.items()):
    props = cell_properties[(r, c)]
    half = cell_scale / 2

    cell_hue_offset = (idx / len(points)) * hue_spread
    cell_colour = get_colour(cell_hue_offset, props['saturation'], props['lightness'])
    fill_colour = (*cell_colour, int(props['fill_opacity'] * 255))

    # Per-cell distortion
    distort = props['shape_distortion'] * half * 0.5
    cell_rot = props['cell_rotation']

    # Generate corners with distortion and per-cell rotation
    base_corners = [
        (-half + random.uniform(-distort, distort), -half + random.uniform(-distort, distort)),
        (half + random.uniform(-distort, distort), -half + random.uniform(-distort, distort)),
        (half + random.uniform(-distort, distort), half + random.uniform(-distort, distort)),
        (-half + random.uniform(-distort, distort), half + random.uniform(-distort, distort)),
    ]

    corners = []
    for bx, by in base_corners:
        rx, ry = rotate_point(bx, by, 0, 0, cell_rot)
        corners.append((px + rx, py + ry))

    cell_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cell_draw = ImageDraw.Draw(cell_img)

    corner_r = half * props['corner_radius']

    if props['shape_distortion'] < 0.1 and corner_r > 1 and abs(cell_rot) < 0.1:
        cell_draw.rounded_rectangle(
            [px - half, py - half, px + half, py + half],
            radius=int(corner_r), fill=fill_colour
        )
    else:
        cell_draw.polygon(corners, fill=fill_colour)

    # Per-cell gradient
    if props['gradient_strength'] > 0.05:
        for i in range(int(half * 2)):
            t = i / (half * 2)
            alpha = int(props['gradient_strength'] * 80 * (1 - t))
            cell_draw.line(
                [px - half, py - half + i, px + half, py - half + i],
                fill=(255, 255, 255, alpha)
            )

    img = Image.alpha_composite(img.convert("RGBA"), cell_img).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Per-cell stroke
    if props['stroke_weight'] > 0.5:
        stroke_colour = hsl_to_rgb(
            (hue_base + cell_hue_offset) % 360,
            props['saturation'],
            min(0.9, props['lightness'] + 0.2)
        )
        if props['shape_distortion'] < 0.1 and corner_r > 1 and abs(cell_rot) < 0.1:
            draw.rounded_rectangle(
                [px - half, py - half, px + half, py + half],
                radius=int(corner_r), outline=stroke_colour, width=int(props['stroke_weight'])
            )
        else:
            draw.polygon(corners, outline=stroke_colour)

    # Per-cell rings
    if props['ring_count'] > 0:
        ring_colour = hsl_to_rgb((hue_base + 180) % 360, props['saturation'], props['lightness'])
        for ring in range(props['ring_count']):
            r_offset = (ring + 1) * props['ring_spacing']
            if r_offset < half - 5:
                draw.ellipse(
                    [px - r_offset, py - r_offset, px + r_offset, py + r_offset],
                    outline=ring_colour, width=max(1, int(props['stroke_weight'] * 0.5))
                )

    # Per-cell hatching with per-cell angle
    if props['hatching_density'] > 0.1:
        hatch_spacing = int(10 - props['hatching_density'] * 8) + 2
        hatch_angle_rad = props['hatching_angle']
        hatch_colour = hsl_to_rgb(hue_base, props['saturation'] * 0.5, props['lightness'] * 0.5)

        for offset in range(-int(half * 2), int(half * 2), hatch_spacing):
            cos_h = math.cos(hatch_angle_rad)
            sin_h = math.sin(hatch_angle_rad)

            x1 = px + offset * cos_h - half * 2 * sin_h
            y1 = py + offset * sin_h + half * 2 * cos_h
            x2 = px + offset * cos_h + half * 2 * sin_h
            y2 = py + offset * sin_h - half * 2 * cos_h

            if abs(x1 - px) < half and abs(y1 - py) < half:
                draw.line([x1, y1, x2, y2], fill=hatch_colour, width=1)

    # Per-cell dots with per-dot sizes
    if props['dot_density'] > 0.1:
        num_dots = int(props['dot_density'] * 30)
        for _ in range(num_dots):
            dx = px + random.uniform(-half * 0.8, half * 0.8)
            dy = py + random.uniform(-half * 0.8, half * 0.8)
            dot_r = dot_size_dist.rvs()
            dot_colour = hsl_to_rgb(
                (hue_base + random.uniform(0, hue_spread)) % 360,
                saturation_dist.rvs(),
                lightness_dist.rvs()
            )
            draw.ellipse([dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r], fill=dot_colour)

    # Per-cell tentacles with per-tentacle properties
    if props['tentacle_count'] > 0:
        shape_set = set(shape)
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if (r + dr, c + dc) not in shape_set:
                for _ in range(props['tentacle_count'] // 4 + 1):
                    angle = math.atan2(dr, dc) + random.uniform(-0.5, 0.5)
                    start_x = px + dc * half * 0.8
                    start_y = py + dr * half * 0.8

                    tx, ty = start_x, start_y
                    curr_angle = angle
                    tent_colour = get_secondary_colour()
                    tent_length = tentacle_length_dist.rvs()

                    for seg in range(int(tent_length / 5)):
                        seg_len = 5
                        thickness = max(1, int((1 - seg / (tent_length / 5)) * props['stroke_weight'] * 1.5))

                        # Per-segment curl from cauchy (heavy tails = occasional sharp turns)
                        curl = tentacle_curl_dist.rvs()
                        curr_angle += curl

                        nx = tx + math.cos(curr_angle) * seg_len
                        ny = ty + math.sin(curr_angle) * seg_len

                        draw.line([tx, ty, nx, ny], fill=tent_colour, width=thickness)
                        tx, ty = nx, ny

if blur_amount > 0.5:
    img = img.filter(ImageFilter.GaussianBlur(blur_amount))

img
