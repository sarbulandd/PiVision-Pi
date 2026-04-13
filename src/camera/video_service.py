import subprocess
from pathlib import Path


class VideoService:
    def record(self, output_path: Path, duration: int) -> Path:
        result = subprocess.run(
            [
                "rpicam-vid",
                "--width", "1920", "--height", "1080",
                "--denoise", "cdn_fast",
                "--metering", "average",
                "--ev", "0.5",
                "-t", str(duration * 1000),
                "-o", str(output_path)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Video recording failed.\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

        return output_path