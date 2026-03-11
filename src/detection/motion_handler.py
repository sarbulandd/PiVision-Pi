import time

from src.camera.snapshot_service import SnapshotService
from src.camera.video_service import VideoService
from src.config import COOLDOWN_SECONDS, VIDEO_DURATION
from src.services.arm_service import ArmService
from src.services.event_service import EventService
from src.services.storage_service import StorageService


class MotionHandler:
    def __init__(self):
        self.busy = False
        self.storage_service = StorageService()
        self.snapshot_service = SnapshotService()
        self.video_service = VideoService()
        self.arm_service = ArmService()
        self.event_service = EventService()

    def handle_motion(self) -> None:
        if self.busy:
            return

        if not self.arm_service.is_armed():
            print("System disarmed. Ignoring motion.")
            return

        self.busy = True
        timestamp = self.storage_service.generate_timestamp()

        snapshot_path = self.storage_service.build_snapshot_path(timestamp)
        video_path = self.storage_service.build_video_path(timestamp)

        try:
            print(f"\nMotion detected @ {timestamp}")

            print("Taking snapshot...")
            self.snapshot_service.capture(snapshot_path)

            print(f"Recording {VIDEO_DURATION}s clip...")
            self.video_service.record(video_path, VIDEO_DURATION)

            event = self.event_service.create_event(
                timestamp=timestamp,
                snapshot_path=str(snapshot_path),
                video_path=str(video_path)
            )

            print(f"Snapshot saved: {snapshot_path}")
            print(f"Video saved: {video_path}")
            print(f"Event created: {event['event_id']}")

        except Exception as e:
            print(f"Error during motion handling:\n{e}")

        finally:
            time.sleep(COOLDOWN_SECONDS)
            self.busy = False
            print("Re-armed. Waiting for motion...")