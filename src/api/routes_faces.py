import tempfile
from pathlib import Path

from flask import Blueprint, jsonify, request

from src.camera.snapshot_service import SnapshotService
from src.services.face_db_service import FaceDatabaseService

faces_bp = Blueprint("faces", __name__)
face_db = FaceDatabaseService()
snapshot_service = SnapshotService()


@faces_bp.route("/faces", methods=["GET"])
def get_faces():
    return jsonify(face_db.get_all_faces())


@faces_bp.route("/faces", methods=["POST"])
def add_face():
    name = request.form.get("name")
    image = request.files.get("image")

    if not name or not image:
        return jsonify({"error": "name and image are required"}), 400

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        image.save(tmp.name)
        tmp_path = Path(tmp.name)

    try:
        result = face_db.add_face(name, tmp_path)
        if result is None:
            return jsonify({"error": "no face detected in image"}), 422
        return jsonify(result), 201
    finally:
        tmp_path.unlink(missing_ok=True)


@faces_bp.route("/faces/capture", methods=["POST"])
def capture_face():
    name = request.json.get("name") if request.json else None
    if not name:
        return jsonify({"error": "name is required"}), 400

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        snapshot_service.capture(tmp_path)
        result = face_db.add_face(name, tmp_path)
        if result is None:
            return jsonify({"error": "no face detected in image"}), 422
        return jsonify(result), 201
    finally:
        tmp_path.unlink(missing_ok=True)


@faces_bp.route("/faces/<face_id>", methods=["DELETE"])
def delete_face(face_id):
    deleted = face_db.delete_face(face_id)
    if not deleted:
        return jsonify({"error": "face not found"}), 404
    return jsonify({"deleted": face_id})
