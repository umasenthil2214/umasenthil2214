"""
Edit this file to personalise your profile. Everything else is generated.
"""

USERNAME = "umasenthil2214"
DISPLAY_NAME = "Uma Senthil"          # shown after `$ whoami`
HOST = "github"                       # shown as  uma@github  in the info card

# Neofetch-style info card. Each section is (title, colour, [(key, value), ...])
# Colours available: orange, blue, green, cyan, white, purple
SECTIONS = [
    ("About", "orange", [
        ("Role", "Senior Mobile & IoT Engineer"),
        ("Experience", "15+ years of production apps"),
        ("Location", "Canada"),
        ("Focus", "Mobile · BLE Mesh · AI / LLM"),
        ("Now", "Firmware & mobile @ DBTech"),
    ]),
    ("Stack", "blue", [
        ("Mobile", "Kotlin · Swift · Flutter · RN"),
        ("Android", "Compose · Room · WorkManager"),
        ("Embedded", "C · STM32WB55 · BLE Mesh · OTA"),
        ("AI", "RAG · Pinecone · GPT-4o · LLaMA 3"),
        ("Cloud", "AWS · Supabase · Node.js · TS"),
    ]),
    ("Highlights", "green", [
        ("FASTER", "BLE Mesh SOS safety wearable"),
        ("Private AI", "On-prem RAG assistant"),
        ("Levven", "Smart-home app, Play & App Store"),
        ("Stash", "Offline NFC password manager"),
    ]),
]

# ASCII portrait width in characters (rows are worked out from the photo's proportions).
ASCII_COLS = 110
# Tones darker than this (0-1) are left blank, so hair/clothing don't turn into noise.
ASCII_DARK_CUTOFF = 0.22

# Custom portrait (PNG, ideally with the background removed). Delete it to use your GitHub avatar instead.
PORTRAIT_PATH = "assets/portrait.png"
# Pre-rendered ASCII portrait (plain text). Used first if present; delete it to regenerate from the photo.
PORTRAIT_ASCII = "assets/portrait-ascii.txt"
# Crop box as fractions (left, top, right, bottom) - frames head and shoulders.
PORTRAIT_CROP = (0.12, 0.0, 0.88, 0.78)

OUTPUT_DIR = "assets"
README_PATH = "README.md"
