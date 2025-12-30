"""
parameters:
  - name: seed
    distribution: randint
    low: 0
    high: 1000000
  - name: width
    distribution: constant
    value: 2400
  - name: height
    distribution: constant
    value: 1600
  - name: border_size
    distribution: constant
    value: 150
  - name: num_people
    distribution: randint
    low: 2500
    high: 4500
  - name: arrangement_type
    distribution: choice
    values: ["random", "grid", "spiral"]
  - name: palette_name
    distribution: choice
    values: ["vibrant", "pastel", "earthy", "oceanic"]
  - name: min_scale
    distribution: constant
    value: 0.4
  - name: max_scale
    distribution: constant
    value: 1.0
  - name: jitter
    distribution: uniform
    loc: 0.0
    scale: 5.0
"""

from PIL import Image, ImageDraw
import random
import math

random.seed(seed)


def get_palette(name):
    if name == "vibrant":
        return ["#FF5733", "#33FF57", "#3357FF", "#F033FF", "#FF33A8", "#33FFF5"]
    elif name == "pastel":
        return ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF"]
    elif name == "earthy":
        return ["#8D6E63", "#D7CCC8", "#5D4037", "#795548", "#A1887F"]
    elif name == "oceanic":
        return ["#0288D1", "#B3E5FC", "#03A9F4", "#0277BD", "#E1F5FE"]
    return ["#000000"]


def draw_abstract_person(draw, x, y, scale, color):
    # Distinct Archetypes for stronger variation
    archetypes = ["standard", "soft", "blocky", "tall", "wide"]
    style = random.choice(archetypes)

    # Common dimensions
    base_height = 60 * scale
    head_size = 5.5 * scale

    if style == "tall":
        height_factor = random.uniform(1.2, 1.4)
        width_factor = random.uniform(0.7, 0.9)
    elif style == "wide":
        height_factor = random.uniform(0.85, 1.0)
        width_factor = random.uniform(1.3, 1.6)
    else:
        height_factor = random.uniform(0.9, 1.15)
        width_factor = random.uniform(0.9, 1.2)

    total_height = base_height * height_factor
    shoulder_width = 10 * scale * width_factor

    shoulder_y = y - total_height + head_size * 2
    feet_y = y

    lean = random.uniform(-4, 4) * scale

    # Shadow Parameters
    shadow_color = (0, 0, 0, 80)  # Standard black shadow

    shadow_skew_x = 0.6
    shadow_scale_y = 0.3
    shadow_offset_x = 10 * scale
    shadow_offset_y = 2 * scale

    def get_shadow_point(px, py):
        sx = px + (feet_y - py) * shadow_skew_x + shadow_offset_x
        sy = feet_y - (feet_y - py) * shadow_scale_y + shadow_offset_y
        return (sx, sy)

    # Calculate Body Points
    points = []

    if style == "soft":
        steps = 16  # Smoother curves for high res
        for i in range(steps + 1):
            t = i / steps
            w = shoulder_width * (0.5 + 0.5 * math.sin(t * math.pi))
            py = shoulder_y + (feet_y - shoulder_y) * t
            px = x + lean * (1 - t)
            points.append((px - w / 2, py))
        points.append((x + lean * 0.1, feet_y))
        for i in range(steps, -1, -1):
            t = i / steps
            w = shoulder_width * (0.5 + 0.5 * math.sin(t * math.pi))
            py = shoulder_y + (feet_y - shoulder_y) * t
            px = x + lean * (1 - t)
            points.append((px + w / 2, py))

    elif style == "blocky":
        points = [
            (x - shoulder_width / 2 + lean, shoulder_y),
            (x + shoulder_width / 2 + lean, shoulder_y),
            (x + shoulder_width / 2, feet_y),
            (x - shoulder_width / 2, feet_y),
        ]

    else:
        s_l_y = shoulder_y + random.uniform(-2, 2) * scale
        s_r_y = shoulder_y + random.uniform(-2, 2) * scale
        taper = random.uniform(0.3, 0.7)
        feet_w = shoulder_width * taper
        points = [
            (x - shoulder_width / 2 + lean, s_l_y),
            (x + shoulder_width / 2 + lean, s_r_y),
            (x + feet_w / 2, feet_y),
            (x - feet_w / 2, feet_y),
        ]

    # Draw Shadow
    shadow_points = [get_shadow_point(px, py) for px, py in points]
    draw.polygon(shadow_points, fill=shadow_color)

    # Head Shadow
    head_center_y = shoulder_y - head_size * 0.6
    head_x = x + lean
    hx, hy = get_shadow_point(head_x, head_center_y)
    draw.ellipse(
        [
            hx - head_size / 2,
            hy - head_size * shadow_scale_y / 2,
            hx + head_size / 2,
            hy + head_size * shadow_scale_y / 2,
        ],
        fill=shadow_color,
    )

    # Draw Body
    draw.polygon(points, fill=color)

    # Arms/Coats
    if random.random() < 0.2:
        coat_y = feet_y - random.uniform(0, 10) * scale
        c_p1 = [
            (x - shoulder_width / 2 + lean, shoulder_y + 10 * scale),
            (x - shoulder_width * 0.8, coat_y),
            (x - shoulder_width / 2 + lean / 2, shoulder_y + 20 * scale),
        ]
        draw.polygon(c_p1, fill=color)
        c_p2 = [
            (x + shoulder_width / 2 + lean, shoulder_y + 10 * scale),
            (x + shoulder_width * 0.8, coat_y),
            (x + shoulder_width / 2 + lean / 2, shoulder_y + 20 * scale),
        ]
        draw.polygon(c_p2, fill=color)

    # Draw Head
    head_center_y = shoulder_y - head_size * 0.6
    head_x = x + lean

    if style == "blocky":
        draw.rectangle(
            [
                head_x - head_size / 2,
                head_center_y - head_size / 2,
                head_x + head_size / 2,
                head_center_y + head_size / 2,
            ],
            fill=color,
        )
    elif style == "soft":
        h_r = head_size / 2
        draw.ellipse(
            [head_x - h_r, head_center_y - h_r, head_x + h_r, head_center_y + h_r],
            fill=color,
        )
    else:
        h_w = head_size * random.uniform(0.8, 1.0)
        h_h = head_size * random.uniform(1.0, 1.3)
        draw.ellipse(
            [
                head_x - h_w / 2,
                head_center_y - h_h / 2,
                head_x + h_w / 2,
                head_center_y + h_h / 2,
            ],
            fill=color,
        )


# Initialize Image: Use RGBA for transparency support (for shadows) then convert to RGB
bg_color = "#f5f5f5"  # Always light background now
img = Image.new("RGBA", (width, height), bg_color)
draw = ImageDraw.Draw(img)

colors = get_palette(palette_name)


# Noise / Density Map Generation
def simple_noise(x, y, scale=0.002, seed_offset=0):
    # Sum of sines to simulate organic noise without heavy deps
    # Octaves for detail
    v = 0
    v += math.sin(x * scale + seed_offset)
    v += math.sin(y * scale + seed_offset + 10) * 0.5
    v += math.sin((x + y) * scale * 2 + seed_offset) * 0.25
    # Normalize approx to 0..1 range (v is roughly -1.75 to 1.75)
    return (v + 1.75) / 3.5


# Rejection Sampling for Arrangement
people = []
max_attempts = num_people * 5  # Prevent infinite loops
attempts = 0

min_x = border_size
max_x = width - border_size
min_y = border_size
max_y = height - border_size

if arrangement_type == "random":
    while len(people) < num_people and attempts < max_attempts:
        attempts += 1
        x = random.randint(int(min_x), int(max_x))
        y = random.randint(int(min_y), int(max_y))

        # Density check
        noise_val = simple_noise(x, y, seed_offset=seed)
        # Threshold: if noise_val is high, high chance of placement
        # Create distinct "voids" by sharpening the curve
        probability = math.pow(noise_val, 2)  # Squaring pushes lows lower -> more voids

        if random.random() < probability:
            normalized_y = (y - min_y) / (max_y - min_y)
            scale = min_scale + normalized_y * (max_scale - min_scale)
            scale *= random.uniform(0.9, 1.1)
            people.append((y, x, scale, random.choice(colors)))

elif arrangement_type == "grid":
    rows = int(math.sqrt(num_people * 1.5))  # More rows/cols to account for rejection
    cols = int(num_people * 1.5 / rows) + 1
    x_step = width / (cols + 1)
    y_step = height / (rows + 1)

    for r in range(rows):
        for c in range(cols):
            x = (c + 1) * x_step + random.uniform(-jitter, jitter)
            y = (r + 1) * y_step + random.uniform(-jitter, jitter)

            # Density Check for Grid
            noise_val = simple_noise(x, y, seed_offset=seed)
            probability = math.pow(
                noise_val, 3
            )  # Stricter for grid to break it up more

            if random.random() < probability:
                if min_x < x < max_x and min_y < y < max_y:
                    normalized_y = (y) / (height)
                    scale = min_scale + normalized_y * (max_scale - min_scale)
                    people.append((y, x, scale, random.choice(colors)))

            if len(people) >= num_people:
                break
        if len(people) >= num_people:
            break

elif arrangement_type == "spiral":
    # Spiral inherently has spatial structure, but we can break it up
    cx, cy = width / 2, height / 2
    i = 0
    while len(people) < num_people and attempts < max_attempts:
        attempts += 1
        i += 1
        angle = i * 0.15
        dist = i * 0.8 + 10

        angle += random.uniform(-0.05, 0.05)
        dist += random.uniform(-5, 5)

        x = cx + math.cos(angle) * dist
        y = cy + math.sin(angle) * dist

        noise_val = simple_noise(x, y, seed_offset=seed)
        if random.random() < noise_val:  # Less strict for spiral to keep shape visible
            if min_x < x < max_x and min_y < y < max_y:
                normalized_y = (y) / (height)
                scale = min_scale + normalized_y * (max_scale - min_scale)
                people.append((y, x, scale, random.choice(colors)))

people.sort(key=lambda p: p[0])

for p in people:
    y, x, s, c = p
    draw_abstract_person(draw, x, y, s, c)

img.convert("RGB")
