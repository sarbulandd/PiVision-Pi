import threading
import time
from pathlib import Path

from src.camera.snapshot_service import SnapshotService
from src.camera.video_service import VideoService
from src.config import COOLDOWN_SECONDS, VIDEO_DURATION, VIDEO_FRAME_INTERVAL
from src.detection.face_detection import FaceDetectionService
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
        self.face_service = FaceDetectionService()
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

            print("Scanning snapshot for faces...")
            face_detected, recognised_person = self.face_service.scan_image(snapshot_path)
            print(f"Face detected: {face_detected}, Recognised: {recognised_person}")

            final_snapshot = str(snapshot_path)
            final_video = str(video_path)

            if self.upload_service:
                print("Uploading to Azure...")
                final_snapshot = self.upload_service.upload_snapshot(snapshot_path)
                final_video = self.upload_service.upload_video(video_path)
                print(f"Uploaded snapshot: {final_snapshot}")
                print(f"Uploaded video: {final_video}")
                snapshot_path.unlink(missing_ok=True)

            event = self.event_service.create_event(
                timestamp=timestamp,
                snapshot_path=final_snapshot,
                video_path=final_video,
                face_detected=face_detected,
                recognised_person=recognised_person
            )

            print(f"Event created: {event['event_id']}")

            if not face_detected:
                threading.Thread(
                    target=self._scan_video_background,
                    args=(video_path, event["event_id"]),
                    daemon=True
                ).start()
            else:
                video_path.unlink(missing_ok=True)

        except Exception as e:
            print(f"Error during motion handling:\n{e}")

        finally:
            time.sleep(COOLDOWN_SECONDS)
            self.busy = False
            print("Re-armed. Waiting for motion...")

    def _scan_video_background(self, video_path: Path, event_id: str) -> None:
        try:
            print(f"Background scan started for {event_id}...")
            face_detected, recognised_person = self.face_service.scan_video_frames(
                video_path, frame_interval=VIDEO_FRAME_INTERVAL
            )
            if face_detected:
                self.event_service.update_event(
                    event_id,
                    face_detected=True,
                    recognised_person=recognised_person
                )
                print(f"Background scan updated event {event_id}: recognised={recognised_person}")
            else:
                print(f"Background scan complete — no face found in video for {event_id}")
        finally:
            video_path.unlink(missing_ok=True)
