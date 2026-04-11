import time
from pathlib import Path

import cv2
import face_recognition

from src.services.face_db_service import FaceDatabaseService

_ENCODINGS_TTL = 30  # seconds before re-fetching from Azure


class FaceDetectionService:
    def __init__(self):
        self.db = FaceDatabaseService()
        self._encodings_cache: list = []
        self._encodings_cache_ts: float = 0.0

    def _get_known(self) -> list:
        if time.time() - self._encodings_cache_ts < _ENCODINGS_TTL:
            return self._encodings_cache
        self._encodings_cache = self.db.get_encodings()
        self._encodings_cache_ts = time.time()
        return self._encodings_cache

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

    def scan_frame_with_confidence(self, frame_rgb) -> list[dict]:
        """Scan an RGB numpy frame and return per-face results with confidence."""
        locations = face_recognition.face_locations(frame_rgb, model="hog")
        if not locations:
            return []
        encodings = face_recognition.face_encodings(frame_rgb, locations)
        known = self._get_known()
        results = []
        for encoding in encodings:
            if not known:
                results.append({"name": "Unknown", "confidence": None})
                continue
            known_encodings = [k["encoding"] for k in known]
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_index = int(distances.argmin())
            if distances[best_index] < 0.5:
                results.append({
                    "name": known[best_index]["name"],
                    "confidence": round(float(1 - distances[best_index]), 2)
                })
            else:
                results.append({"name": "Unknown", "confidence": None})
        return results

    def _match(self, encodings: list) -> tuple[bool, str | None]:
        known = self.db.get_encodings()
        if not known:
            return True, None
        known_encodings = [k["encoding"] for k in known]
        for encoding in encodings:
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_index = int(distances.argmin())
            if distances[best_index] < 0.5:
                return True, known[best_index]["name"]
        return True, None
