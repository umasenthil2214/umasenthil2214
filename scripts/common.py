"""Shared palette, filters and helpers for all three SVGs."""
from xml.sax.saxutils import escape

BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"

NEON = {
    "cyan": "#22d3ee",
    "green": "#3fb950",
    "orange": "#ff9e3d",
    "purple": "#bc8cff",
    "blue": "#58a6ff",
    "white": "#e6edf3",
}

FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"


def esc(s: str) -> str:
    return escape(str(s), {'"': "&quot;"})


def defs_common(uid: str) -> str:
    """Glow filters + glass gradient. `uid` prevents id clashes between SVGs."""
    return f"""
    <filter id="{uid}-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="{uid}-softglow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="{uid}-glass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.07"/>
      <stop offset="0.45" stop-color="#ffffff" stop-opacity="0.015"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0.04"/>
    </linearGradient>
    <linearGradient id="{uid}-edge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{NEON['cyan']}"/>
      <stop offset="0.5" stop-color="{NEON['purple']}"/>
      <stop offset="1" stop-color="{NEON['green']}"/>
    </linearGradient>
    <radialGradient id="{uid}-ambient" cx="0.15" cy="0" r="0.9">
      <stop offset="0" stop-color="{NEON['cyan']}" stop-opacity="0.16"/>
      <stop offset="1" stop-color="{NEON['cyan']}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="{uid}-ambient2" cx="0.95" cy="1" r="0.8">
      <stop offset="0" stop-color="{NEON['purple']}" stop-opacity="0.14"/>
      <stop offset="1" stop-color="{NEON['purple']}" stop-opacity="0"/>
    </radialGradient>"""


def glass_panel(uid: str, x, y, w, h, r=14) -> str:
    """Dark glass card: base, ambient neon light, frosted sheen, glowing gradient edge."""
    return f"""
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{BG}"/>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{uid}-ambient)"/>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{uid}-ambient2)"/>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{uid}-glass)"/>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="url(#{uid}-edge)" stroke-opacity="0.35" stroke-width="1.2" filter="url(#{uid}-softglow)">
    <animate attributeName="stroke-opacity" values="0.25;0.55;0.25" dur="6s" repeatCount="indefinite"/>
  </rect>"""


def title_bar(x, y, w, title: str) -> str:
    """macOS-style traffic lights + centred title."""
    dots = "".join(
        f'<circle cx="{x + 20 + i * 18}" cy="{y + 17}" r="5.5" fill="{c}"/>'
        for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"])
    )
    return f"""
  {dots}
  <text x="{x + w / 2}" y="{y + 21}" text-anchor="middle" font-family="{FONT}" font-size="11.5" fill="{MUTED}">{esc(title)}</text>
  <line x1="{x}" y1="{y + 34}" x2="{x + w}" y2="{y + 34}" stroke="{BORDER}" stroke-opacity="0.8"/>"""
