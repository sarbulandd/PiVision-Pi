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

    def create_event(self, timestamp: str, snapshot_path: str, video_path: str,
                     face_detected: bool = False, recognised_person: str = None) -> dict:
        events = self.get_events()

        event = {
            "event_id": f"evt_{timestamp}",
            "timestamp": datetime.now().isoformat(),
            "snapshot_path": str(snapshot_path),
            "video_path": str(video_path),
            "face_detected": face_detected,
            "recognised_person": recognised_person
        }

        events.append(event)

        with open(self.events_file, "w") as f:
            json.dump(events, f, indent=2)

        return event

    def delete_event(self, event_id: str) -> bool:
        events = self.get_events()
        filtered = [e for e in events if e["event_id"] != event_id]
        if len(filtered) == len(events):
            return False
        with open(self.events_file, "w") as f:
            json.dump(filtered, f, indent=2)
        return True

    def update_event(self, event_id: str, **fields) -> bool:
        events = self.get_events()
        for event in events:
            if event["event_id"] == event_id:
                event.update(fields)
                with open(self.events_file, "w") as f:
                    json.dump(events, f, indent=2)
                return True
        return False

    def clear_events(self) -> None:
        with open(self.events_file, "w") as f:
            json.dump([], f)