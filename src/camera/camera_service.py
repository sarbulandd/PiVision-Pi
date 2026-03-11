from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

from picamera2 import Picamera2, Preview

from src.config import CAMERA_RESOLUTION, PREVIEW_DURATION, CAPTURE_DIR


class CameraService:
    """
    Simple wrapper around Picamera2 that behaves a bit like the rpicam-hello / rpicam-still apps.
    """

    def __init__(self, resolution: Tuple[int, int] = CAMERA_RESOLUTION):
        self.picam2: Optional[Picamera2] = None
        self.resolution = resolution

    def start(self, with_preview: bool = True) -> None:
        """Initialise and start the camera."""
        self.picam2 = Picamera2()

        config = self.picam2.create_preview_configuration(
            main={"size": self.resolution}
        )
        self.picam2.configure(config)

        if with_preview:
            # If this crashes, try Preview.DRM instead of Preview.QT
            self.picam2.start_preview(Preview.QTGL)

        self.picam2.start()

    def stop(self) -> None:
        """Stop the camera and close resources."""
        if self.picam2 is None:
            return
        try:
            self.picam2.stop()
            self.picam2.stop_preview()
        except Exception:
            # preview might not be running; ignore
            pass
        finally:
            self.picam2.close()
            self.picam2 = None

    def capture_still(self, output_dir: Path = CAPTURE_DIR) -> Path:
        """
        Capture a single still image and return the file path.
        File is timestamped for easy sorting and history.
        """
        if self.picam2 is None:
            raise RuntimeError("Camera not started. Call start() first.")

        output_dir.mkdir(parents=True, exist_ok=True)
        filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.jpg")
        filepath = output_dir / filename

        self.picam2.capture_file(str(filepath))
        return filepath

    def preview_and_capture(self, duration: int = PREVIEW_DURATION) -> Path:
        """
        Show a live preview for <duration> seconds, then capture an image.

        This roughly mimics:  rpicam-hello --timeout <duration>
                              rpicam-still -t <duration> -o <file>
        """
        if self.picam2 is None:
            self.start(with_preview=True)

        import time
        time.sleep(duration)
        return self.capture_still()
