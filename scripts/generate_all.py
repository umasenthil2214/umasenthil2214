"""
Runs all three generators, then injects the cards into README.md between markers:
terminal-card + info-card side by side in an HTML <table>, contribution graph centred below.
Anything outside the markers in README.md is left untouched.

Run from the repository root:  python scripts/generate_all.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
import generate_contributions  # noqa: E402
import generate_info  # noqa: E402
import generate_terminal  # noqa: E402

START = "<!-- PROFILE-CARDS:START -->"
END = "<!-- PROFILE-CARDS:END -->"


def block():
    d = config.OUTPUT_DIR
    return f"""{START}
<table align="center" border="0">
  <tr>
    <td width="50%" valign="top"><img src="./{d}/terminal-card.svg" alt="ASCII portrait of {config.DISPLAY_NAME} in an animated terminal" width="100%"/></td>
    <td width="50%" valign="top"><img src="./{d}/info-card.svg" alt="Neofetch-style info card for {config.DISPLAY_NAME}" width="100%"/></td>
  </tr>
</table>

<p align="center">
  <img src="./{d}/github-contribution-animation.svg" alt="Animated GitHub contribution graph for @{config.USERNAME}" width="100%"/>
</p>
{END}"""


def inject_readme():
    path = config.README_PATH
    existing = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = f.read()
    new_block = block()
    if START in existing and END in existing:
        pre = existing.split(START)[0]
        post = existing.split(END, 1)[1]
        out = pre + new_block + post
    else:
        out = new_block + ("\n\n" + existing if existing.strip() else "\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"[readme] updated {path}")


def main():
    generate_terminal.main()        # first: info card matches its height
    generate_info.main()
    generate_contributions.main()
    inject_readme()


if __name__ == "__main__":
    main()
