"""
parameters:
  - name: width
    distribution: constant
    value: 1200
  - name: height
    distribution: constant
    value: 1200
  - name: seed
    distribution: randint
    low: 0
    high: 100000
  - name: background
    distribution: choice
    values: ["#0a0a0a", "#1a1a1a", "#0d1117", "#000000"]
  - name: network_type
    distribution: choice
    values: ["barabasi_albert", "watts_strogatz", "random_geometric", "erdos_renyi", "powerlaw_cluster"]
  - name: num_nodes
    distribution: randint
    low: 50
    high: 200
  - name: palette
    distribution: choice
    values: [
      ["#ff006e", "#fb5607", "#ffbe0b", "#8338ec", "#3a86ff"],
      ["#06ffa5", "#00d4ff", "#7c3aed", "#f8b500", "#ff6b6b"],
      ["#e63946", "#f1faee", "#a8dadc", "#457b9d", "#1d3557"],
      ["#f72585", "#b5179e", "#7209b7", "#560bad", "#3a0ca3"],
      ["#00f5ff", "#00d9ff", "#00bfff", "#0099ff", "#0077ff"]
    ]
  - name: node_size
    distribution: uniform
    loc: 2
    scale: 6
    mode: distribution
  - name: edge_alpha
    distribution: uniform
    loc: 0.1
    scale: 0.3
  - name: layout_type
    distribution: choice
    values: ["spring", "circular", "random", "shell"]
  - name: edge_thickness
    distribution: uniform
    loc: 0.5
    scale: 2
    mode: distribution
"""

from PIL import Image, ImageDraw
import random
import networkx as nx
import math

random.seed(seed)

# Create image
img = Image.new("RGBA", (width, height), background)
draw = ImageDraw.Draw(img)

# Generate network based on type
if network_type == "barabasi_albert":
    # Scale-free network (preferential attachment)
    m = max(2, num_nodes // 20)
    G = nx.barabasi_albert_graph(num_nodes, m, seed=seed)
elif network_type == "watts_strogatz":
    # Small-world network
    k = max(4, num_nodes // 10)
    p = random.uniform(0.1, 0.3)
    G = nx.watts_strogatz_graph(num_nodes, k, p, seed=seed)
elif network_type == "random_geometric":
    # Geometric network (nodes connected if close enough)
    radius = random.uniform(0.15, 0.25)
    G = nx.random_geometric_graph(num_nodes, radius, seed=seed)
elif network_type == "erdos_renyi":
    # Random network
    p = random.uniform(0.02, 0.08)
    G = nx.erdos_renyi_graph(num_nodes, p, seed=seed)
else:  # powerlaw_cluster
    # Powerlaw cluster network
    m = max(2, num_nodes // 30)
    p = random.uniform(0.1, 0.5)
    G = nx.powerlaw_cluster_graph(num_nodes, m, p, seed=seed)

# Calculate layout
margin = 100
if layout_type == "spring":
    pos = nx.spring_layout(G, seed=seed, k=1/math.sqrt(num_nodes))
elif layout_type == "circular":
    pos = nx.circular_layout(G)
elif layout_type == "shell":
    pos = nx.shell_layout(G)
else:  # random
    pos = nx.random_layout(G, seed=seed)

# For random_geometric, use the built-in positions
if network_type == "random_geometric":
    pos = nx.get_node_attributes(G, 'pos')

# Scale positions to fit canvas with margin
min_x = min(x for x, y in pos.values())
max_x = max(x for x, y in pos.values())
min_y = min(y for x, y in pos.values())
max_y = max(y for x, y in pos.values())

scaled_pos = {}
for node, (x, y) in pos.items():
    scaled_x = margin + (x - min_x) / (max_x - min_x) * (width - 2 * margin)
    scaled_y = margin + (y - min_y) / (max_y - min_y) * (height - 2 * margin)
    scaled_pos[node] = (scaled_x, scaled_y)

# Draw edges
edge_alpha_int = int(edge_alpha * 255)
for edge in G.edges():
    x1, y1 = scaled_pos[edge[0]]
    x2, y2 = scaled_pos[edge[1]]

    color_idx = random.randint(0, len(palette) - 1)
    base_color = palette[color_idx]

    # Convert hex to RGB
    r = int(base_color[1:3], 16)
    g = int(base_color[3:5], 16)
    b = int(base_color[5:7], 16)

    edge_color = (r, g, b, edge_alpha_int)

    thickness = int(edge_thickness.rvs())
    draw.line([(x1, y1), (x2, y2)], fill=edge_color, width=thickness)

# Draw nodes
for node, (x, y) in scaled_pos.items():
    color_idx = random.randint(0, len(palette) - 1)
    node_color = palette[color_idx]

    # Draw node with glow effect
    radius = node_size.rvs()

    # Outer glow
    for i in range(3):
        alpha = int(100 / (i + 1))
        r = int(node_color[1:3], 16)
        g = int(node_color[3:5], 16)
        b = int(node_color[5:7], 16)
        glow_color = (r, g, b, alpha)

        glow_radius = radius + (3 - i) * 2
        draw.ellipse(
            [x - glow_radius, y - glow_radius, x + glow_radius, y + glow_radius],
            fill=glow_color
        )

    # Main node
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        fill=node_color
    )

# Convert to RGB
img = img.convert("RGB")

img
