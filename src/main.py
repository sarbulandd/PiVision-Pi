from src.camera.camera_service import CameraService
from src.config import PREVIEW_DURATION


def main() -> None:
    cam = CameraService()

    try:
        print("Starting camera preview...")
        image_path = cam.preview_and_capture(duration=PREVIEW_DURATION)
        print(f"Captured image saved to: {image_path}")
        print("Press Ctrl+C to exit if window is still open.")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        cam.stop()
        print("Camera stopped.")


if __name__ == "__main__":
    main()
