import io
import os
import pickle
import uuid
from pathlib import Path

import face_recognition
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

FACES_BLOB = "faces.pkl"
FACES_CONTAINER = "faces"


class FaceDatabaseService:
    def __init__(self):
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise EnvironmentError("AZURE_STORAGE_CONNECTION_STRING is not set")
        client = BlobServiceClient.from_connection_string(connection_string)
        self.blob = client.get_blob_client(container=FACES_CONTAINER, blob=FACES_BLOB)

    def _load(self) -> list:
        try:
            data = self.blob.download_blob().readall()
            return pickle.loads(data)
        except ResourceNotFoundError:
            return []

    def _save(self, faces: list) -> None:
        data = pickle.dumps(faces)
        self.blob.upload_blob(io.BytesIO(data), overwrite=True)

    def get_all_faces(self) -> list:
        return [{"id": f["id"], "name": f["name"], "image_url": f.get("image_url")} for f in self._load()]

    def get_encodings(self) -> list:
        return [{"name": f["name"], "encoding": f["encoding"]} for f in self._load()]

    def add_face(self, name: str, image_path: Path, image_url: str = None) -> dict | None:
        image = face_recognition.load_image_file(str(image_path))
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            return None
        faces = self._load()
        entry = {"id": str(uuid.uuid4()), "name": name, "encoding": encodings[0], "image_url": image_url}
        faces.append(entry)
        self._save(faces)
        return {"id": entry["id"], "name": entry["name"], "image_url": entry["image_url"]}

    def update_image_url(self, face_id: str, image_url: str) -> None:
        faces = self._load()
        for face in faces:
            if face["id"] == face_id:
                face["image_url"] = image_url
                break
        self._save(faces)

    def delete_face(self, face_id: str) -> bool:
        faces = self._load()
        filtered = [f for f in faces if f["id"] != face_id]
        if len(filtered) == len(faces):
            return False
        self._save(filtered)
        return True
