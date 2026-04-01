import time

from src.camera.snapshot_service import SnapshotService
from src.camera.video_service import VideoService
from src.config import COOLDOWN_SECONDS, VIDEO_DURATION
from src.services.arm_service import ArmService
from src.services.event_service import EventService
from src.services.storage_service import StorageService
from src.services.upload_service import UploadService


class MotionHandler:
    def __init__(self, arm_service: ArmService = None, event_service: EventService = None):
        self.busy = False
        self.storage_service = StorageService()
        self.snapshot_service = SnapshotService()
        self.video_service = VideoService()
        self.arm_service = arm_service or ArmService()
        self.event_service = event_service or EventService()

        try:
            self.upload_service = UploadService()
        except EnvironmentError:
            print("AZURE_STORAGE_CONNECTION_STRING not set — uploads disabled.")
            self.upload_service = None

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

            final_snapshot = str(snapshot_path)
            final_video = str(video_path)

            if self.upload_service:
                print("Uploading to Azure...")
                final_snapshot = self.upload_service.upload_snapshot(snapshot_path)
                final_video = self.upload_service.upload_video(video_path)
                print(f"Uploaded snapshot: {final_snapshot}")
                print(f"Uploaded video: {final_video}")
                snapshot_path.unlink(missing_ok=True)
                video_path.unlink(missing_ok=True)
                print("Local files deleted.")

            event = self.event_service.create_event(
                timestamp=timestamp,
                snapshot_path=final_snapshot,
                video_path=final_video
            )

            print(f"Event created: {event['event_id']}")

        except Exception as e:
            print(f"Error during motion handling:\n{e}")

        finally:
            time.sleep(COOLDOWN_SECONDS)
            self.busy = False
            print("Re-armed. Waiting for motion...")