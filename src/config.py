from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CAPTURE_DIR = DATA_DIR / "captures"
LOG_DIR = BASE_DIR / "logs"

# Ensure folders exist (in case script is run standalone)
for p in (DATA_DIR, CAPTURE_DIR, LOG_DIR):
    p.mkdir(parents=True, exist_ok=True)

# Camera settings
CAMERA_RESOLUTION = (1280, 720) 
CAMERA_FRAMERATE = 30

# How long to preview before auto-capturing (seconds)
PREVIEW_DURATION = 10
