import json
from datetime import datetime

from src.config import EVENTS_DIR


class EventService:
    def __init__(self):
        self.events_file = EVENTS_DIR / "events.json"
        if not self.events_file.exists():
            self.events_file.write_text("[]")

    def get_events(self) -> list:
        with open(self.events_file, "r") as f:
            return json.load(f)

    def create_event(self, timestamp: str, snapshot_path: str, video_path: str) -> dict:
        events = self.get_events()

        event = {
            "event_id": f"evt_{timestamp}",
            "timestamp": datetime.now().isoformat(),
            "snapshot_path": str(snapshot_path),
            "video_path": str(video_path),
            "face_detected": False,
            "recognised_person": None
        }

        events.append(event)

        with open(self.events_file, "w") as f:
            json.dump(events, f, indent=2)

        return event