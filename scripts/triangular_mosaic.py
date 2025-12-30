"""
parameters:
  - name: width
    distribution: constant
    value: 1000
  - name: height
    distribution: constant
    value: 800
  - name: seed
    distribution: randint
    low: 0
    high: 100000
  - name: background
    distribution: choice
    values: ["#0a0a0a", "#1a1a1a", "#0d1117"]
  - name: num_points
    distribution: randint
    low: 100
    high: 300
  - name: palette
    distribution: choice
    values: [
      ["#ff006e", "#fb5607", "#ffbe0b", "#8338ec", "#3a86ff"],
      ["#06ffa5", "#00d4ff", "#7c3aed", "#f8b500", "#ff6b6b"],
      ["#e63946", "#f1faee", "#a8dadc", "#457b9d", "#1d3557"],
      ["#f72585", "#b5179e", "#7209b7", "#560bad", "#3a0ca3"]
    ]
  - name: triangle_alpha
    distribution: uniform
    loc: 0.6
    scale: 0.3
  - name: stroke_width
    distribution: randint
    low: 0
    high: 3
    mode: distribution
"""

from PIL import Image, ImageDraw
import random
from scipy.spatial import Delaunay

random.seed(seed)

img = Image.new("RGBA", (width, height), background)
draw = ImageDraw.Draw(img)

# Generate random points
points = []
for _ in range(num_points):
    x = random.uniform(-width * 0.2, width * 1.2)
    y = random.uniform(-height * 0.2, height * 1.2)
    points.append([x, y])

# Create Delaunay triangulation
tri = Delaunay(points)

# Draw triangles
for simplex in tri.simplices:
    triangle = [tuple(points[i]) for i in simplex]

    # Pick random colour from palette
    colour = random.choice(palette)

    # Calculate alpha
    alpha = int(255 * triangle_alpha)
    colour_with_alpha = colour + f"{alpha:02x}"

    # Draw filled triangle
    draw.polygon(triangle, fill=colour_with_alpha)

    # Optional stroke
    if stroke_width.rvs() > 0:
        stroke_col = "#000000" if random.random() > 0.5 else "#ffffff"
        stroke_alpha = int(255 * 0.3)
        draw.polygon(triangle, outline=stroke_col + f"{stroke_alpha:02x}",
                    width=int(stroke_width.rvs()))

img
