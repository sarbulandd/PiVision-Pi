from gpiozero import MotionSensor

from src.config import PIR_GPIO_PIN


class PIRSensorService:
    def __init__(self, pin: int = PIR_GPIO_PIN):
        self.pir = MotionSensor(pin)

    def motion_detected(self) -> bool:
        return self.pir.motion_detected

    def wait_for_motion(self) -> None:
        self.pir.wait_for_motion()

    def wait_for_no_motion(self) -> None:
        self.pir.wait_for_no_motion()