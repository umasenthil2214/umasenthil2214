"""
File 2: assets/terminal-card.svg

Fetches the GitHub avatar, converts it to dense ASCII art with Pillow and places it inside a
macOS-style terminal. Rows reveal top-to-bottom while a white block cursor sweeps each row
left-to-right. Footer types `$ whoami` and prints the display name. Pure SMIL.
"""
import io
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
from common import BG, MUTED, TEXT, NEON, FONT, esc, defs_common, glass_panel, title_bar  # noqa: E402

# Dark background: brightest pixels get the densest glyphs.
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

CARD_W = 440
TERM_FONT = 13
TERM_CW = TERM_FONT * 0.6


def load_portrait(user):
    """Prefer a custom photo committed to the repo (config.PORTRAIT_PATH); else the GitHub avatar.
    A PNG with transparency (background removed) gives the cleanest ASCII silhouette."""
    path = getattr(config, "PORTRAIT_PATH", None)
    if path and os.path.exists(path):
        print(f"[terminal] using {path}")
        img = Image.open(path).convert("RGBA")
        l, t, r, b = getattr(config, "PORTRAIT_CROP", (0, 0, 1, 1))
        w, h = img.size
        img = img.crop((int(w * l), int(h * t), int(w * r), int(h * b)))
        sharp = img.convert("RGB").filter(ImageFilter.UnsharpMask(3, 120, 2))
        sharp.putalpha(img.getchannel("A"))
        return sharp
    try:
        import requests
        r = requests.get(f"https://github.com/{user}.png?size=460", timeout=20,
                         headers={"User-Agent": "profile-readme-generator"})
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content))
    except Exception as e:
        print(f"[terminal] avatar fetch failed ({e}); using placeholder portrait")
        return placeholder_portrait()


def placeholder_portrait(size=460):
    """Simple lit bust silhouette so the script still produces a sensible card offline."""
    img = Image.new("L", (size, size), 10)
    d = ImageDraw.Draw(img)
    d.ellipse((size * .30, size * .12, size * .70, size * .58), fill=200)
    d.ellipse((size * .12, size * .60, size * .88, size * 1.25), fill=150)
    d.ellipse((size * .36, size * .20, size * .56, size * .40), fill=245)
    img = img.filter(ImageFilter.GaussianBlur(size * .03))
    return img.convert("RGB")


def to_ascii(img, cols, rows=None):
    """Brightness -> glyph density, tuned for a dark terminal.

    With a background-removed PNG (alpha channel): the background stays blank, dark areas
    (hair, clothing) stay blank except for a faint dotted outline of the silhouette, and the
    remaining tones are stretched across the full ramp so facial features read clearly.
    Without alpha (a normal avatar): classic full-frame ASCII with a soft circular vignette.
    """
    img = img.convert("RGBA")
    alpha = img.getchannel("A")
    has_mask = alpha.getextrema()[0] < 250
    if rows is None:  # keep the photo's proportions: glyph cell is ~0.6 wide : ~0.98 tall
        rows = round(cols * 0.6 / 0.98 * img.size[1] / img.size[0])
    g = ImageOps.grayscale(img.convert("RGB")).filter(ImageFilter.UnsharpMask(2, 80, 2))
    n = len(RAMP) - 1
    lines = []
    if has_mask:
        solid = alpha.point(lambda a: 255 if a > 128 else 0)
        g = ImageOps.autocontrast(g, cutoff=(1, 0.5), mask=solid)
        g = g.resize((cols, rows), Image.LANCZOS)
        a = alpha.resize((cols, rows), Image.LANCZOS)
        edge = a.filter(ImageFilter.FIND_EDGES)
        gp, ap, ep = g.load(), a.load(), edge.load()
        cut = getattr(config, "ASCII_DARK_CUTOFF", 0.22)
        for y in range(rows):
            row = []
            for x in range(cols):
                v = gp[x, y] / 255
                if ap[x, y] < 128:
                    ch = " "
                elif v < cut:
                    ch = "." if ep[x, y] > 60 and 0 < y < rows - 1 and 0 < x < cols - 1 else " "  # skip frame border
                else:
                    t = (v - cut) / (1 - cut)
                    ch = RAMP[max(1, min(n, int(t * n + 0.5)))]
                row.append(ch)
            lines.append("".join(row).rstrip() or " ")
        return lines

    g = ImageOps.equalize(ImageOps.autocontrast(g, cutoff=2)).resize((cols, rows), Image.LANCZOS)
    gp = g.load()
    for y in range(rows):
        row = []
        for x in range(cols):
            dx = (x - (cols - 1) / 2) / (cols / 2)
            dy = (y - (rows - 1) / 2) / (rows / 2)
            r = (dx * dx + dy * dy) ** 0.5
            v = gp[x, y] / 255 * (1.0 if r < 0.82 else max(0.0, 1 - (r - 0.82) / 0.2))
            row.append(RAMP[min(n, int(v * n))])
        lines.append("".join(row).rstrip() or " ")
    return lines


def render(lines):
    uid = "tc"
    cols = config.ASCII_COLS
    rows = len(lines)
    pad = 22
    art_w = CARD_W - 2 * pad
    cw = art_w / cols                     # exact cell width enforced with textLength
    fs = round(cw / 0.6, 2)               # monospace glyph ≈ 0.6em wide
    lh = round(fs * 0.98, 2)
    top = 34 + 18
    art_h = rows * lh
    foot_y = top + art_h + 26
    import generate_info  # match the neighbouring card's height
    H = max(int(foot_y + 3 * 20 + 10), generate_info.content_height())

    row_dur = round(min(0.08, 3.0 / rows), 3)  # whole reveal takes ~3s
    start = 0.4

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{H}" viewBox="0 0 {CARD_W} {H}">',
         "<defs>", defs_common(uid),
         f'''<linearGradient id="{uid}-ascii" gradientUnits="userSpaceOnUse" x1="{pad}" y1="{top}" x2="{pad + art_w}" y2="{top + art_h}">
      <stop offset="0" stop-color="{NEON['cyan']}"/>
      <stop offset="0.55" stop-color="#9be7ff"/>
      <stop offset="1" stop-color="{NEON['purple']}"/>
    </linearGradient>''']

    # one clipPath per row - its rect widens as the cursor passes
    for i in range(rows):
        t = start + i * row_dur
        y = top + i * lh
        p.append(f'<clipPath id="{uid}-r{i}"><rect x="{pad}" y="{y - 1:.2f}" width="0" height="{lh + 2:.2f}">'
                 f'<animate attributeName="width" from="0" to="{art_w + cw:.2f}" begin="{t:.3f}s" dur="{row_dur}s" fill="freeze"/></rect></clipPath>')

    # typewriter clip for "whoami"
    cmd = "whoami"
    prompt = f"{config.DISPLAY_NAME.split()[0].lower()}@{config.HOST}:~$ "
    type_start = start + rows * row_dur + 0.35
    char_t = 0.11
    px0 = pad + len(prompt) * TERM_CW
    widths = ";".join(f"{k * TERM_CW:.2f}" for k in range(len(cmd) + 1))
    p.append(f'<clipPath id="{uid}-type"><rect x="{px0:.2f}" y="{foot_y - 14}" width="0" height="20">'
             f'<animate attributeName="width" values="{widths}" calcMode="discrete" begin="{type_start:.2f}s" dur="{(len(cmd) + 1) * char_t:.2f}s" fill="freeze"/></rect></clipPath>')
    p.append("</defs>")

    p.append(glass_panel(uid, 1, 1, CARD_W - 2, H - 2, 14))
    p.append(title_bar(1, 1, CARD_W - 2, f"{config.USERNAME} — ascii — zsh"))

    # ASCII rows
    p.append(f'<g font-family="{FONT}" font-size="{fs}" fill="url(#{uid}-ascii)" xml:space="preserve">')
    for i, line in enumerate(lines):
        y = top + (i + 1) * lh - lh * 0.22
        L = len(line)
        # non-breaking spaces: renderers may collapse normal spaces, which smears the portrait
        p.append(f'<text x="{pad}" y="{y:.2f}" textLength="{L * cw:.2f}" lengthAdjust="spacing" xml:space="preserve" clip-path="url(#{uid}-r{i})">{esc(line).replace(" ", "&#160;")}</text>')
    p.append("</g>")

    # sweeping white cursor block, one per row
    for i in range(rows):
        t = start + i * row_dur
        y = top + i * lh
        p.append(f'<rect x="{pad}" y="{y:.2f}" width="{cw:.2f}" height="{lh:.2f}" fill="#ffffff" opacity="0" filter="url(#{uid}-softglow)">'
                 f'<set attributeName="opacity" to="0.95" begin="{t:.3f}s"/>'
                 f'<animate attributeName="x" from="{pad}" to="{pad + art_w:.2f}" begin="{t:.3f}s" dur="{row_dur}s" fill="freeze"/>'
                 f'<set attributeName="opacity" to="0" begin="{t + row_dur:.3f}s"/></rect>')

    # footer
    p.append(f'<line x1="{pad}" y1="{foot_y - 22}" x2="{CARD_W - pad}" y2="{foot_y - 22}" stroke="#30363d" stroke-dasharray="3 4"/>')
    p.append(f'<g font-family="{FONT}" font-size="{TERM_FONT}" opacity="0">'
             f'<animate attributeName="opacity" values="0;1" begin="{type_start - 0.3:.2f}s" dur="0.3s" fill="freeze"/>'
             f'<text x="{pad}" y="{foot_y}" textLength="{len(prompt) * TERM_CW:.2f}" xml:space="preserve">'
             f'<tspan fill="{NEON["green"]}">{esc(prompt.split(":")[0])}</tspan><tspan fill="{TEXT}">:</tspan>'
             f'<tspan fill="{NEON["blue"]}">~</tspan><tspan fill="{TEXT}">$ </tspan></text>'
             f'<text x="{px0:.2f}" y="{foot_y}" fill="{TEXT}" textLength="{len(cmd) * TERM_CW:.2f}" clip-path="url(#{uid}-type)">{cmd}</text>'
             f'</g>')

    # caret while typing
    xs = ";".join(f"{px0 + k * TERM_CW:.2f}" for k in range(len(cmd) + 1))
    type_end = type_start + (len(cmd) + 1) * char_t
    p.append(f'<rect x="{px0:.2f}" y="{foot_y - 12}" width="{TERM_CW:.2f}" height="15" fill="#ffffff" opacity="0">'
             f'<set attributeName="opacity" to="1" begin="{type_start - 0.3:.2f}s"/>'
             f'<animate attributeName="x" values="{xs}" calcMode="discrete" begin="{type_start:.2f}s" dur="{(len(cmd) + 1) * char_t:.2f}s" fill="freeze"/>'
             f'<set attributeName="opacity" to="0" begin="{type_end + 0.15:.2f}s"/></rect>')

    # output: display name (glowing)
    out_t = type_end + 0.25
    p.append(f'<text x="{pad}" y="{foot_y + 20}" font-family="{FONT}" font-size="{TERM_FONT + 1}" font-weight="700" fill="{NEON["cyan"]}" filter="url(#{uid}-softglow)" opacity="0">'
             f'{esc(config.DISPLAY_NAME)}'
             f'<animate attributeName="opacity" values="0;1" begin="{out_t:.2f}s" dur="0.25s" fill="freeze"/></text>')

    # fresh prompt with blinking caret
    np_t = out_t + 0.45
    p.append(f'<g font-family="{FONT}" font-size="{TERM_FONT}" opacity="0">'
             f'<animate attributeName="opacity" values="0;1" begin="{np_t:.2f}s" dur="0.2s" fill="freeze"/>'
             f'<text x="{pad}" y="{foot_y + 40}" textLength="{len(prompt) * TERM_CW:.2f}" xml:space="preserve">'
             f'<tspan fill="{NEON["green"]}">{esc(prompt.split(":")[0])}</tspan><tspan fill="{TEXT}">:</tspan>'
             f'<tspan fill="{NEON["blue"]}">~</tspan><tspan fill="{TEXT}">$ </tspan></text>'
             f'<rect x="{px0:.2f}" y="{foot_y + 28}" width="{TERM_CW:.2f}" height="15" fill="#ffffff">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" begin="{np_t:.2f}s" repeatCount="indefinite"/></rect>'
             f'</g>')

    p.append("</svg>")
    return "\n".join(p)


def main():
    ascii_path = getattr(config, "PORTRAIT_ASCII", None)
    if ascii_path and os.path.exists(ascii_path):
        # Pre-rendered portrait (plain text) - no image needed in the repo
        print(f"[terminal] using {ascii_path}")
        with open(ascii_path, encoding="utf-8") as f:
            lines = [ln.rstrip("\n").rstrip() or " " for ln in f]
        config.ASCII_COLS = max(config.ASCII_COLS, max(len(ln) for ln in lines))
    else:
        img = load_portrait(config.USERNAME)
        lines = to_ascii(img, config.ASCII_COLS, getattr(config, "ASCII_ROWS", None))
        if ascii_path:  # cache it so later runs (and the GitHub Action) can reuse it
            os.makedirs(os.path.dirname(ascii_path) or ".", exist_ok=True)
            with open(ascii_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
    svg = render(lines)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    out = os.path.join(config.OUTPUT_DIR, "terminal-card.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[terminal] wrote {out}")


if __name__ == "__main__":
    main()
