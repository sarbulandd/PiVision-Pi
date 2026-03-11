import time
from pathlib import Path

from src.config import SNAPSHOTS_DIR, VIDEOS_DIR


class StorageService:
    def generate_timestamp(self) -> str:
        return time.strftime("%Y%m%d-%H%M%S")

    def build_snapshot_path(self, timestamp: str) -> Path:
        return SNAPSHOTS_DIR / f"intruder_{timestamp}.jpg"

    def build_video_path(self, timestamp: str) -> Path:
        return VIDEOS_DIR / f"intruder_{timestamp}.mp4"