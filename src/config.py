from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

CAPTURES_DIR = DATA_DIR / "captures"
SNAPSHOTS_DIR = CAPTURES_DIR / "snapshots"
VIDEOS_DIR = CAPTURES_DIR / "videos"
EVENTS_DIR = DATA_DIR / "events"
FACES_DIR = DATA_DIR / "faces"

LOG_DIR = BASE_DIR / "logs"

# Create directories automatically
for p in (DATA_DIR, CAPTURES_DIR, SNAPSHOTS_DIR, VIDEOS_DIR, EVENTS_DIR, FACES_DIR, LOG_DIR):
    p.mkdir(parents=True, exist_ok=True)

# PIR settings
PIR_GPIO_PIN = 17
WARMUP_SECONDS = 30

# Recording settings
VIDEO_DURATION = 10
COOLDOWN_SECONDS = 5

# System settings
DEFAULT_ARMED = True

# Face recognition settings
VIDEO_FRAME_INTERVAL = 15