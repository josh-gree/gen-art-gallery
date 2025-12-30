# Generative Art Gallery

Automated gallery for generative art created with [gen-art-framework](https://github.com/josh-gree/gen-art).

## How It Works

1. Add Python art scripts to the `scripts/` directory
2. Commit and push to `main`
3. GitHub Actions automatically:
   - Generates 10 unique images from each script
   - Builds a static gallery website
   - Deploys to GitHub Pages

## Setup

### 1. Create GitHub Repository

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to your repository settings
2. Navigate to **Pages** (under Code and automation)
3. Under **Build and deployment**:
   - Source: **GitHub Actions**
4. Save changes

### 3. Enable Workflow Permissions

1. Go to repository **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests**
5. Save

Your gallery will be available at: `https://YOUR_USERNAME.github.io/YOUR_REPO/`

## Adding New Art

1. Create a Python script in `scripts/` with parameter space defined in the docstring
2. Commit and push to `main`
3. The workflow runs automatically and updates the gallery

### Example Script

```python
"""
parameters:
  - name: width
    distribution: constant
    value: 800
  - name: height
    distribution: constant
    value: 600
  - name: seed
    distribution: randint
    low: 0
    high: 10000
"""

from PIL import Image, ImageDraw
import random

random.seed(seed)

img = Image.new("RGB", (width, height), "#1a1a2e")
draw = ImageDraw.Draw(img)

# Your generative art code here

img
```

## Local Testing

Generate art locally:

```bash
gen-art sample scripts/your_script.py -n 10 -o output
```

## Tech Stack

- **gen-art-framework**: Generative art framework
- **GitHub Actions**: Automated workflow
- **GitHub Pages**: Free static hosting
- **Vanilla JS**: Gallery frontend
