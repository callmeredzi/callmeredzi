import requests
import math
from datetime import datetime

# Konfigurasi
GITHUB_USERNAME = "callmeredzi"  # Ganti dengan username GitHub kamu
FRAME_WIDTH = 800
FRAME_HEIGHT = 320
PIXEL_SIZE = 48  # Ukuran karakter pixel
BARANG_SIZE = 32  # Ukuran barang
STACK_COLS = 10  # Jumlah kolom barang per layar
STACK_ROWS = 5   # Barang per kolom (stack ke atas)
SCROLL_TRIGGER = int(STACK_COLS / 2)  # Scroll jika sudah setengah frame

# Ambil data progres (misal: total commits bulan ini)
def get_github_progress():
    # Contoh: ambil jumlah repo publik
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    repos = requests.get(url).json()
    return len(repos)

# Generate SVG animasi

def generate_svg(progress_count):
        # Fitur 6: Background dinamis (siang/malam)
        hour = datetime.now().hour
        bg_color = "#222" if hour < 18 and hour > 6 else "#181c2a"
        bg_gradient = f'<linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{bg_color}"/><stop offset="100%" stop-color="#2a2d3a"/></linearGradient>'
        svg = [
                f'<svg width="{FRAME_WIDTH}" height="{FRAME_HEIGHT}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">',
                bg_gradient,
                '<rect width="100%" height="100%" fill="url(#bgGrad)"/>',
        ]
        # Fitur 3: Progress bar/counter
        percent = min(1.0, progress_count / (STACK_COLS * STACK_ROWS))
        svg.append(f'<rect x="40" y="12" width="{int(700*percent)}" height="12" rx="6" fill="#58a6ff" opacity="0.3"/>' )
        svg.append(f'<text x="400" y="22" text-anchor="middle" fill="#58a6ff" font-family="monospace" font-size="14">Progress: {progress_count}</text>')

        # Fitur 1, 2, 4, 7: Barang SVG, shadow, tooltip, dan variasi
        for i in range(progress_count):
                col = (i // STACK_ROWS)
                row = STACK_ROWS - 1 - (i % STACK_ROWS)
                x = 120 + col * (BARANG_SIZE + 8)
                y = 32 + row * (BARANG_SIZE + 8)
                # Shadow
                svg.append(f'<rect x="{x+2}" y="{y+8}" width="{BARANG_SIZE}" height="8" fill="#000" opacity="0.15" rx="4"/>' )
                # Barang SVG (box), dengan tooltip
                svg.append(f'<g><title>Progress #{i+1}</title><image xlink:href="assets/img/box-package.svg" x="{x}" y="{y}" width="{BARANG_SIZE}" height="{BARANG_SIZE}" /></g>')

        # Fitur 5: Ekspresi pixel art dinamis (dummy: happy jika progress > 10)
        mood = "Pixel-Art.svg"
        if progress_count > 10:
                mood = "Pixel-Art.svg" # Ganti ke ekspresi lain jika ada file lain

        # Fitur 8: Animasi loop smooth (pakai animasi SVG sederhana)
        next_col = (progress_count // STACK_ROWS)
        next_row = STACK_ROWS - 1 - (progress_count % STACK_ROWS)
        px = 120 + next_col * (BARANG_SIZE + 8) - 8
        py = 32 + next_row * (BARANG_SIZE + 8) - 8
        svg.append(f'<g>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <image xlink:href="assets/img/{mood}" x="{px}" y="{py}" width="{PIXEL_SIZE}" height="{PIXEL_SIZE}" filter="url(#glow)">
                <animate attributeName="x" values="{px};{px+16};{px}" dur="2s" repeatCount="indefinite"/>
                <animate attributeName="y" values="{py};{py-8};{py}" dur="1.5s" repeatCount="indefinite"/>
            </image>
        </g>')

        svg.append('</svg>')
        return "\n".join(svg)

if __name__ == "__main__":
    progress = get_github_progress()
    svg_content = generate_svg(progress)
    with open("pixel-mascot-anim.svg", "w") as f:
        f.write(svg_content)
    print("SVG animasi pixel mascot berhasil dibuat!")
