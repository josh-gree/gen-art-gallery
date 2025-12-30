"""
parameters:
  - name: width
    distribution: constant
    value: 400
  - name: height
    distribution: constant
    value: 400
  - name: square_size
    distribution: constant
    value: 60
  - name: seed
    distribution: randint
    low: 0
    high: 10000
  - name: background
    distribution: choice
    values: ["#ffffff", "#f0f0f0", "#e8e8e8"]
  - name: colour
    distribution: choice
    values: ["#e94560", "#f39c12", "#00b894", "#6c5ce7", "#fd79a8", "#a29bfe"]
"""

from PIL import Image, ImageDraw
import random

random.seed(seed)

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

# Pick a random pentomino
shape = random.choice(list(pentominoes.values()))

# Create image
img = Image.new("RGB", (width, height), background)
draw = ImageDraw.Draw(img)

# Centre the pentomino
offset_x = (width - square_size * 3) // 2
offset_y = (height - square_size * 5) // 2

# Draw the pentomino (filled squares first)
for row, col in shape:
    x = offset_x + col * square_size
    y = offset_y + row * square_size
    draw.rectangle([x, y, x + square_size, y + square_size], fill=colour)

# Draw grid lines (each edge only once)
drawn_edges = set()
corner_points = set()

for row, col in shape:
    x = offset_x + col * square_size
    y = offset_y + row * square_size

    # Collect corner points
    corner_points.add((x, y))
    corner_points.add((x + square_size, y))
    corner_points.add((x, y + square_size))
    corner_points.add((x + square_size, y + square_size))

    # Top edge
    edge = ('h', row, col, col + 1)
    if edge not in drawn_edges:
        draw.line([x, y, x + square_size, y], fill="#000000", width=5, joint="curve")
        drawn_edges.add(edge)

    # Bottom edge
    edge = ('h', row + 1, col, col + 1)
    if edge not in drawn_edges:
        draw.line([x, y + square_size, x + square_size, y + square_size], fill="#000000", width=5, joint="curve")
        drawn_edges.add(edge)

    # Left edge
    edge = ('v', col, row, row + 1)
    if edge not in drawn_edges:
        draw.line([x, y, x, y + square_size], fill="#000000", width=5, joint="curve")
        drawn_edges.add(edge)

    # Right edge
    edge = ('v', col + 1, row, row + 1)
    if edge not in drawn_edges:
        draw.line([x + square_size, y, x + square_size, y + square_size], fill="#000000", width=5, joint="curve")
        drawn_edges.add(edge)

# Draw circles at corners to fill gaps and create rounded joins
radius = 2.5
for px, py in corner_points:
    draw.ellipse([px - radius, py - radius, px + radius, py + radius], fill="#000000")

img
