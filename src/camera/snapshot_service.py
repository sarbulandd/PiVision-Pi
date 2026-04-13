import subprocess
from pathlib import Path


class SnapshotService:
    def capture(self, output_path: Path) -> Path:
        result = subprocess.run(
            [
                "rpicam-jpeg",
                "--width", "1920", "--height", "1080",
                "--denoise", "cdn_hq",
                "--metering", "average",
                "--ev", "0.5",
                "-o", str(output_path)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Snapshot capture failed.\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

        return output_path