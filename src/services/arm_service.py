from src.config import DEFAULT_ARMED


class ArmService:
    def __init__(self):
        self.armed = DEFAULT_ARMED

    def arm(self) -> None:
        self.armed = True

    def disarm(self) -> None:
        self.armed = False

    def is_armed(self) -> bool:
        return self.armed