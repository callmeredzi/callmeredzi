import requests
import math
import os
import base64
from datetime import datetime
import pytz

# Konfigurasi
GITHUB_USERNAME = "callmeredzi"
FRAME_WIDTH = 800
FRAME_HEIGHT = 320
PIXEL_SIZE = 48
BARANG_SIZE = 32
STACK_COLS = 10
STACK_ROWS = 5
SCROLL_TRIGGER = int(STACK_COLS / 2)
TIMEZONE = pytz.timezone('Asia/Jakarta')

# Baca file SVG dan convert ke base64
def get_svg_as_base64(filepath):
    """Baca file SVG dan return sebagai base64 data URI"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        # Encode to base64
        b64 = base64.b64encode(content.encode()).decode()
        return f"data:image/svg+xml;base64,{b64}"
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def get_github_contributions():
    """Fetch total contributions from GitHub using GraphQL API"""
    token = os.environ.get('GITHUB_TOKEN')

    query = """
    query($username: String!) {
        user(login: $username) {
            contributionsCollection {
                contributionCalendar {
                    totalContributions
                }
            }
        }
    }
    """

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"username": GITHUB_USERNAME}},
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        if "data" in data and "user" in data["data"]:
            total = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
            return total
        else:
            print("Warning: Could not fetch contribution data, using fallback")
            return 0
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        return 0

def generate_svg(progress_count, mascot_b64, box_b64):
    """Generate SVG dengan embedded base64 images"""
    local_time = datetime.now(TIMEZONE)
    hour = local_time.hour
    day_time = 6 <= hour < 18

    bg_color = "#222" if day_time else "#181c2a"
    bg_gradient = f'<linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="{bg_color}"/><stop offset="100%" stop-color="#2a2d3a"/></linearGradient>'

    svg = [
        f'<svg width="{FRAME_WIDTH}" height="{FRAME_HEIGHT}" viewBox="0 0 {FRAME_WIDTH} {FRAME_HEIGHT}" xmlns="http://www.w3.org/2000/svg">',
        bg_gradient,
        '<rect width="100%" height="100%" fill="url(#bgGrad)"/>',
    ]

    # Progress bar
    percent = min(1.0, progress_count / (STACK_COLS * STACK_ROWS))
    svg.append(f'<rect x="40" y="12" width="{int(700*percent)}" height="12" rx="6" fill="#58a6ff" opacity="0.3"/>')
    svg.append(f'<text x="400" y="22" text-anchor="middle" fill="#58a6ff" font-family="monospace" font-size="14">Contributions: {progress_count}</text>')

    # Barang dengan base64 image
    for i in range(min(progress_count, STACK_COLS * STACK_ROWS)):
        col = (i // STACK_ROWS)
        row = STACK_ROWS - 1 - (i % STACK_ROWS)
        x = 120 + col * (BARANG_SIZE + 8)
        y = 32 + row * (BARANG_SIZE + 8)

        svg.append(f'<rect x="{x+2}" y="{y+8}" width="{BARANG_SIZE}" height="8" fill="#000" opacity="0.15" rx="4"/>')
        svg.append(f'<g><title>Contribution #{i+1}</title><image xlink:href="{box_b64}" x="{x}" y="{y}" width="{BARANG_SIZE}" height="{BARANG_SIZE}" /></g>')

    # Mascot dengan base64
    next_col = (progress_count // STACK_ROWS)
    next_row = STACK_ROWS - 1 - (progress_count % STACK_ROWS)
    px = 120 + next_col * (BARANG_SIZE + 8) - 8
    py = 32 + next_row * (BARANG_SIZE + 8) - 8

    svg.append(f'''
<g>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
        <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>
    <image xlink:href="{mascot_b64}" x="{px}" y="{py}" width="{PIXEL_SIZE}" height="{PIXEL_SIZE}" filter="url(#glow)">
        <animate attributeName="x" values="{px};{px+16};{px}" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="y" values="{py};{py-8};{py}" dur="1.5s" repeatCount="indefinite"/>
    </image>
</g>
''')

    svg.append('</svg>')
    return "\n".join(svg)

def generate_html_embed(svg_content):
    """Generate HTML embed code untuk README - SVG langsung tanpa wrapper tambahan"""
    # Remove the opening <svg> tag and just get the inner content
    lines = svg_content.split('\n')
    inner_content = []
    skip_first = True
    for line in lines:
        if skip_first and '<svg' in line:
            continue
        if '</svg>' in line:
            continue
        inner_content.append(line)
    inner_svg = '\n'.join(inner_content[1:])  # Skip gradient line too and get actual content

    return f'''<!-- Pixel Mascot Interaktif -->
<div align="center">
{svg_content}
  <br/>
  <sub>
    <b>Pixel mascot interaktif:</b> animasi real-time, barang diangkat & ditaruh, progress bar, background dinamis, shadow, tooltip, dan animasi smooth!<br/>
    <i>Powered by Python & GitHub Actions</i>
  </sub>
</div>'''

if __name__ == "__main__":
    # Baca assets dan convert ke base64
    mascot_b64 = get_svg_as_base64("assets/img/Pixel-Art.svg")
    box_b64 = get_svg_as_base64("assets/img/box-package.svg")

    if not mascot_b64 or not box_b64:
        print("Error: Could not read asset files")
        exit(1)

    # Get contributions
    progress = get_github_contributions()

    # Generate SVG
    svg_content = generate_svg(progress, mascot_b64, box_b64)

    # Simpan SVG standalone
    with open("pixel-mascot.svg", "w") as f:
        f.write(svg_content)

    # Generate HTML embed untuk README
    html_embed = generate_html_embed(svg_content)
    with open("pixel-mascot-embed.html", "w") as f:
        f.write(html_embed)

    print(f"SVG pixel mascot berhasil dibuat! Total contributions: {progress}")
    print(f"HTML embed saved to pixel-mascot-embed.html")
