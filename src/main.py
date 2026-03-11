import time

from src.config import WARMUP_SECONDS
from src.detection.motion_handler import MotionHandler
from src.sensors.pir_sensor import PIRSensorService


def main() -> None:
    pir_sensor = PIRSensorService()
    motion_handler = MotionHandler()

    print("Warming up PIR... do not move in front of it.")
    time.sleep(WARMUP_SECONDS)
    print("Armed. Waiting for motion...")

    try:
        while True:
            pir_sensor.wait_for_motion()
            motion_handler.handle_motion()
            pir_sensor.wait_for_no_motion()

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")


if __name__ == "__main__":
    main()