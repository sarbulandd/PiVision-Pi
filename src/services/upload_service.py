import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient


class UploadService:
    def __init__(self):
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise EnvironmentError("AZURE_STORAGE_CONNECTION_STRING is not set")
        self.client = BlobServiceClient.from_connection_string(connection_string)

    def upload_snapshot(self, file_path: Path) -> str:
        return self._upload(file_path, container="snapshots")

    def upload_video(self, file_path: Path) -> str:
        return self._upload(file_path, container="clips")

    def upload_face_image(self, file_path: Path, face_id: str) -> str:
        blob_name = f"face_{face_id}.jpg"
        blob_client = self.client.get_blob_client(container="faces", blob=blob_name)
        with open(file_path, "rb") as f:
            blob_client.upload_blob(f, overwrite=True)
        return blob_client.url

    def _upload(self, file_path: Path, container: str) -> str:
        blob_client = self.client.get_blob_client(container=container, blob=file_path.name)
        with open(file_path, "rb") as f:
            blob_client.upload_blob(f, overwrite=True)
        return blob_client.url
