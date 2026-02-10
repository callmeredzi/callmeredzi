import requests
import math
import os
from datetime import datetime
import pytz

# Konfigurasi
GITHUB_USERNAME = "callmeredzi"  # Ganti dengan username GitHub kamu
FRAME_WIDTH = 800
FRAME_HEIGHT = 320
PIXEL_SIZE = 48  # Ukuran karakter pixel
BARANG_SIZE = 32  # Ukuran barang
STACK_COLS = 10  # Jumlah kolom barang per layar
STACK_ROWS = 5   # Barang per kolom (stack ke atas)
SCROLL_TRIGGER = int(STACK_COLS / 2)  # Scroll jika sudah setengah frame
TIMEZONE = pytz.timezone('Asia/Jakarta')  # Timezone lokal

# GraphQL query untuk mengambil data kontribusi
def get_github_contributions():
    """Fetch total contributions from GitHub using GraphQL API"""
    token = os.environ.get('GITHUB_TOKEN')

    # GraphQL query untuk mengambil total kontribusi
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

    headers = {
        "Content-Type": "application/json",
    }

    # Tambahkan token jika tersedia (untuk rate limit yang lebih tinggi)
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

# Generate SVG animasi
def generate_svg(progress_count):
    # Fitur 6: Background dinamis (siang/malam) dengan timezone Asia/Jakarta
    local_time = datetime.now(TIMEZONE)
    hour = local_time.hour
    day_time = 6 <= hour < 18  # Pagi sampai sore = siang

    bg_color = "#222" if day_time else "#181c2a"
    bg_gradient = f'<linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="{bg_color}"/><stop offset="100%" stop-color="#2a2d3a"/></linearGradient>'

    svg = [
        f'<svg width="{FRAME_WIDTH}" height="{FRAME_HEIGHT}" viewBox="0 0 {FRAME_WIDTH} {FRAME_HEIGHT}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">',
        bg_gradient,
        '<rect width="100%" height="100%" fill="url(#bgGrad)"/>',
    ]

    # Fitur 3: Progress bar/counter
    percent = min(1.0, progress_count / (STACK_COLS * STACK_ROWS))
    svg.append(f'<rect x="40" y="12" width="{int(700*percent)}" height="12" rx="6" fill="#58a6ff" opacity="0.3"/>')
    svg.append(f'<text x="400" y="22" text-anchor="middle" fill="#58a6ff" font-family="monospace" font-size="14">Contributions: {progress_count}</text>')

    # Fitur 1, 2, 4, 7: Barang SVG, shadow, tooltip, dan variasi
    for i in range(min(progress_count, STACK_COLS * STACK_ROWS)):
        col = (i // STACK_ROWS)
        row = STACK_ROWS - 1 - (i % STACK_ROWS)
        x = 120 + col * (BARANG_SIZE + 8)
        y = 32 + row * (BARANG_SIZE + 8)

        # Shadow
        svg.append(f'<rect x="{x+2}" y="{y+8}" width="{BARANG_SIZE}" height="8" fill="#000" opacity="0.15" rx="4"/>')

        # Barang SVG (box-package) dengan tooltip
        tooltip_text = f"Contribution #{i+1}"
        svg.append(f'<g><title>{tooltip_text}</title><image xlink:href="assets/img/box-package.svg" x="{x}" y="{y}" width="{BARANG_SIZE}" height="{BARANG_SIZE}" /></g>')

    # Mascot - Pixel-Art.svg
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
    <image xlink:href="assets/img/Pixel-Art.svg" x="{px}" y="{py}" width="{PIXEL_SIZE}" height="{PIXEL_SIZE}" filter="url(#glow)">
        <animate attributeName="x" values="{px};{px+16};{px}" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="y" values="{py};{py-8};{py}" dur="1.5s" repeatCount="indefinite"/>
    </image>
</g>
''')

    svg.append('</svg>')
    return "\n".join(svg)

if __name__ == "__main__":
    progress = get_github_contributions()
    svg_content = generate_svg(progress)
    with open("pixel-mascot-anim.svg", "w") as f:
        f.write(svg_content)
    print(f"SVG animasi pixel mascot berhasil dibuat! Total contributions: {progress}")
