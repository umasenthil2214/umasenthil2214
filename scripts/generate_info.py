"""
File 3: assets/info-card.svg

Neofetch-style card (About / Stack / Highlights) that sits next to the ASCII portrait.
Each line slides up and fades in with a 0.06s stagger, like a terminal printing output.
Height matches terminal-card.svg when it exists so the two cards line up in the README.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
from common import BORDER, MUTED, TEXT, NEON, FONT, esc, defs_common, glass_panel, title_bar  # noqa: E402

CARD_W = 440
LINE_H = 19
STAGGER = 0.06


def terminal_height(default=438):
    path = os.path.join(config.OUTPUT_DIR, "terminal-card.svg")
    try:
        with open(path, encoding="utf-8") as f:
            m = re.search(r'<svg[^>]*\sheight="(\d+)"', f.read(2000))
        return int(m.group(1)) if m else default
    except OSError:
        return default


TOP = 34 + 30


def build_lines():

    user = f"{config.DISPLAY_NAME.split()[0].lower()}@{config.HOST}"
    lines = []  # (kind, payload)
    lines.append(("header", user))
    lines.append(("rule", len(user)))
    for title, colour, rows in config.SECTIONS:
        lines.append(("gap", None))
        lines.append(("section", (title, colour)))
        for k, v in rows:
            lines.append(("kv", (k, v, colour)))
    lines.append(("gap", None))
    lines.append(("palette", None))
    return lines


def content_height():
    """Height the card needs for its own content (used by the terminal card to match)."""
    return int(TOP + sum(LINE_H * (0.55 if k == "gap" else 1) for k, _ in build_lines()) + 24)


def render():
    uid = "ic"
    pad = 24
    key_x = pad + 16
    val_x = pad + 128
    top = TOP
    lines = build_lines()
    H = max(content_height(), terminal_height())

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{H}" viewBox="0 0 {CARD_W} {H}">',
         "<defs>", defs_common(uid), "</defs>",
         glass_panel(uid, 1, 1, CARD_W - 2, H - 2, 14),
         title_bar(1, 1, CARD_W - 2, "neofetch")]

    start = 0.35
    y = top
    idx = 0
    p.append(f'<g font-family="{FONT}" font-size="13">')
    for kind, data in lines:
        if kind == "gap":
            y += LINE_H * 0.55
            continue
        t = start + idx * STAGGER
        idx += 1
        anim = (f'<animate attributeName="opacity" values="0;1" begin="{t:.2f}s" dur="0.35s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 10;0 0" begin="{t:.2f}s" dur="0.35s" '
                f'fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>')
        inner = ""
        if kind == "header":
            name, host = data.split("@")
            inner = (f'<text x="{pad}" y="{y}" font-size="15" font-weight="700" filter="url(#{uid}-softglow)">'
                     f'<tspan fill="{NEON["cyan"]}">{esc(name)}</tspan><tspan fill="{TEXT}">@</tspan>'
                     f'<tspan fill="{NEON["cyan"]}">{esc(host)}</tspan></text>')
        elif kind == "rule":
            inner = f'<text x="{pad}" y="{y - 4}" fill="{MUTED}">{"-" * (data + 2)}</text>'
        elif kind == "section":
            title, colour = data
            c = NEON[colour]
            inner = (f'<text x="{pad}" y="{y}" font-weight="700" fill="{c}" filter="url(#{uid}-softglow)">▸ {esc(title)}</text>'
                     f'<line x1="{pad + 22 + len(title) * 8}" y1="{y - 4}" x2="{CARD_W - pad}" y2="{y - 4}" stroke="{c}" stroke-opacity="0.25"/>')
        elif kind == "kv":
            k, v, colour = data
            inner = (f'<text x="{key_x}" y="{y}" fill="{NEON[colour]}" font-weight="600">{esc(k)}</text>'
                     f'<text x="{val_x}" y="{y}" fill="{NEON["white"]}">{esc(v)}</text>')
        elif kind == "palette":
            sw = ["#0d1117", "#ff5f57", NEON["green"], "#febc2e", NEON["blue"], NEON["purple"], NEON["cyan"], NEON["white"]]
            inner = "".join(f'<rect x="{pad + i * 26}" y="{y - 13}" width="24" height="15" rx="2" fill="{c}" stroke="{BORDER}"/>'
                            for i, c in enumerate(sw))
        p.append(f'<g opacity="0">{anim}{inner}</g>')
        y += LINE_H
    p.append("</g>")

    # blinking prompt caret at the end of the output
    t_end = start + idx * STAGGER + 0.3
    p.append(f'<rect x="{pad}" y="{H - 30}" width="8" height="14" fill="{NEON["white"]}" opacity="0">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" begin="{t_end:.2f}s" repeatCount="indefinite"/></rect>')
    p.append("</svg>")
    return "\n".join(p)


def main():
    svg = render()
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    out = os.path.join(config.OUTPUT_DIR, "info-card.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[info] wrote {out}")


if __name__ == "__main__":
    main()
