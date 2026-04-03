from pathlib import Path

import cv2
import face_recognition

from src.services.face_db_service import FaceDatabaseService


class FaceDetectionService:
    def __init__(self):
        self.db = FaceDatabaseService()

    def scan_image(self, image_path: Path) -> tuple[bool, str | None]:
        image = face_recognition.load_image_file(str(image_path))
        locations = face_recognition.face_locations(image, model="hog")
        if not locations:
            return False, None
        encodings = face_recognition.face_encodings(image, locations)
        return self._match(encodings)

    def scan_video_frames(self, video_path: Path, frame_interval: int = 15) -> tuple[bool, str | None]:
        cap = cv2.VideoCapture(str(video_path))
        frame_number = 0
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_number % frame_interval == 0:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    locations = face_recognition.face_locations(rgb, model="hog")
                    if locations:
                        encodings = face_recognition.face_encodings(rgb, locations)
                        return self._match(encodings)
                frame_number += 1
        finally:
            cap.release()
        return False, None

    def _match(self, encodings: list) -> tuple[bool, str | None]:
        known = self.db.get_encodings()
        if not known:
            return True, None
        known_encodings = [k["encoding"] for k in known]
        for encoding in encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.6)
            if any(matches):
                return True, known[matches.index(True)]["name"]
        return True, None
