import threading
import time

from src.api.app import create_app
from src.api.shared import arm_service, event_service
from src.config import WARMUP_SECONDS
from src.detection.motion_handler import MotionHandler
from src.sensors.pir_sensor import PIRSensorService


def run_flask():
    from waitress import serve
    app = create_app()
    serve(app, host="0.0.0.0", port=5000)


def run_motion_loop():
    pir_sensor = PIRSensorService()
    motion_handler = MotionHandler(arm_service=arm_service, event_service=event_service)

    print("Warming up PIR... do not move in front of it.")
    time.sleep(WARMUP_SECONDS)
    print("Armed. Waiting for motion...")

    try:
        while True:
            pir_sensor.wait_for_motion()
            motion_handler.handle_motion()
            pir_sensor.wait_for_no_motion()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask API running on http://0.0.0.0:5000")

    run_motion_loop()
