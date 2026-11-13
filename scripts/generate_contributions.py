"""
File 1: assets/github-contribution-animation.svg

53x7 contribution calendar with a diagonal "slant reveal" (bottom-left -> top-right).
Each square flashes a white/green specular glint, then settles to its level colour.
Level 3+ squares get an outer glow. Pure SMIL, no CSS/JS.

Data source: the public https://github.com/users/<user>/contributions page (no token needed).
If it can't be fetched (offline), a deterministic sample pattern is used so the script still runs.
"""
import datetime as dt
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
from common import BG, MUTED, TEXT, NEON, FONT, esc, defs_common, glass_panel  # noqa: E402

LEVEL_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP = 12, 3
STEP = CELL + GAP
WEEKS, DAYS = 53, 7


def fetch_calendar(user):
    """Return (grid[week][day] -> level|None, dates grid, total) from GitHub's public calendar."""
    try:
        import requests
        html = requests.get(
            f"https://github.com/users/{user}/contributions",
            headers={"User-Agent": "profile-readme-generator"},
            timeout=20,
        ).text
    except Exception as e:  # pragma: no cover
        print(f"[contrib] fetch failed ({e}); using sample data")
        return None

    cells = re.findall(r'<td[^>]*?data-date="(\d{4}-\d{2}-\d{2})"[^>]*?data-level="(\d)"', html)
    if not cells:
        cells = [(d, l) for l, d in re.findall(r'<td[^>]*?data-level="(\d)"[^>]*?data-date="(\d{4}-\d{2}-\d{2})"', html)]
    if not cells:
        print("[contrib] no cells parsed; using sample data")
        return None

    m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
    total = int(m.group(1).replace(",", "")) if m else None

    by_date = {dt.date.fromisoformat(d): int(l) for d, l in cells}
    return by_date, total


def sample_calendar():
    rnd = random.Random(config.USERNAME)
    today = dt.date.today()
    by_date = {}
    for i in range(371):
        d = today - dt.timedelta(days=i)
        weekday_bias = 0.75 if d.weekday() < 5 else 0.4
        r = rnd.random() * weekday_bias + 0.25 * (0.5 + 0.5 * __import__("math").sin(i / 17))
        by_date[d] = 0 if r < 0.35 else 1 if r < 0.55 else 2 if r < 0.72 else 3 if r < 0.85 else 4
    return by_date, None


def build_grid(by_date):
    """Align to GitHub's layout: columns are weeks (Sun..Sat), last column contains today."""
    last = max(by_date)
    # Sunday that starts the final week column
    last_sunday = last - dt.timedelta(days=(last.weekday() + 1) % 7)
    start = last_sunday - dt.timedelta(weeks=WEEKS - 1)
    grid = []
    for w in range(WEEKS):
        col = []
        for d in range(DAYS):
            day = start + dt.timedelta(days=w * 7 + d)
            col.append((day, by_date.get(day) if day <= last else None))
        grid.append(col)
    return grid


def render(grid, total, approx):
    uid = "cg"
    pad_l, pad_t = 46, 62
    grid_w = WEEKS * STEP - GAP
    grid_h = DAYS * STEP - GAP
    W = pad_l + grid_w + 30
    H = pad_t + grid_h + 58

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             "<defs>", defs_common(uid),
             f'''<filter id="{uid}-cellglow" x="-150%" y="-150%" width="400%" height="400%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="2.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>''',
             f'''<linearGradient id="{uid}-sweep" x1="0" y1="1" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{NEON['green']}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>''',
             "</defs>",
             glass_panel(uid, 1, 1, W - 2, H - 2, 16)]

    label = f"{total:,} contributions in the last year" if total is not None else (
        "Contribution activity · last 12 months" if not approx else "Contribution activity (sample preview)")
    parts.append(f'''
  <text x="{pad_l - 20}" y="34" font-family="{FONT}" font-size="14" font-weight="700" fill="{TEXT}">
    <tspan fill="{NEON['green']}">❯</tspan> {esc(label)}
    <animate attributeName="opacity" values="0;1" dur="0.6s" fill="freeze"/>
  </text>''')

    # month labels
    seen = None
    for w, col in enumerate(grid):
        m = col[0][0].month
        if m != seen and col[0][0].day <= 7:
            parts.append(f'<text x="{pad_l + w * STEP}" y="{pad_t - 9}" font-family="{FONT}" font-size="10" fill="{MUTED}">{col[0][0].strftime("%b")}</text>')
            seen = m
    for d, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{pad_l - 8}" y="{pad_t + d * STEP + 9.5}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{MUTED}">{name}</text>')

    # cells - diagonal reveal: delay grows with column and with distance from bottom row
    k = 0.022
    base = 0.35
    for w, col in enumerate(grid):
        for d, (day, lvl) in enumerate(col):
            if lvl is None:
                continue
            x = pad_l + w * STEP
            y = pad_t + d * STEP
            t = base + (w + (DAYS - 1 - d)) * k
            color = LEVEL_COLORS[lvl]
            glow = f' filter="url(#{uid}-cellglow)"' if lvl >= 3 else ""
            cx, cy = x + CELL / 2, y + CELL / 2
            parts.append(
                f'<g opacity="0">'
                f'<set attributeName="opacity" to="1" begin="{t:.3f}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" values="{cx * 0.4:.1f} {cy * 0.4:.1f};0 0" '
                f'begin="{t:.3f}s" dur="0.35s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
                f'<g>'
                f'<animateTransform attributeName="transform" type="scale" values="0.6;1" begin="{t:.3f}s" dur="0.35s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="#ffffff"{glow}>'
                f'<animate attributeName="fill" values="#ffffff;#b6ffcf;{color}" keyTimes="0;0.25;1" begin="{t:.3f}s" dur="0.55s" fill="freeze"/>'
                f'</rect>'
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="#ffffff" opacity="0">'
                f'<animate attributeName="opacity" values="0;0.9;0" keyTimes="0;0.15;1" begin="{t:.3f}s" dur="0.45s" fill="freeze"/>'
                f'</rect>'
                f'</g></g>'
            )

    end = base + (WEEKS + DAYS) * k

    # legend
    ly = pad_t + grid_h + 26
    lx = pad_l + grid_w - 5 * STEP - 30
    parts.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" begin="{end:.2f}s" dur="0.6s" fill="freeze"/>')
    parts.append(f'<text x="{lx - 8}" y="{ly + 9.5}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{MUTED}">Less</text>')
    for i, c in enumerate(LEVEL_COLORS):
        g = f' filter="url(#{uid}-cellglow)"' if i >= 3 else ""
        parts.append(f'<rect x="{lx + i * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"{g}/>')
    parts.append(f'<text x="{lx + 5 * STEP + 4}" y="{ly + 9.5}" font-family="{FONT}" font-size="10" fill="{MUTED}">More</text>')
    parts.append(f'<text x="{pad_l - 20}" y="{ly + 9.5}" font-family="{FONT}" font-size="10" fill="{MUTED}">@{esc(config.USERNAME)}</text>')
    parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    data = fetch_calendar(config.USERNAME)
    approx = data is None
    by_date, total = data if data else sample_calendar()
    svg = render(build_grid(by_date), total, approx)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    out = os.path.join(config.OUTPUT_DIR, "github-contribution-animation.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[contrib] wrote {out}")


if __name__ == "__main__":
    main()
