import os
import shutil
import subprocess
import threading
import time as _time
from datetime import datetime, timezone
from pathlib import Path

import cv2
from flask import Blueprint, jsonify, send_from_directory

stream_bp = Blueprint("stream", __name__)

STREAM_DIR = "/tmp/pivision_stream"
_ffmpeg_process = None
_rpicam_process = None

_detection_cache = {"result": None, "expires": 0.0}
_detection_lock = threading.Lock()
_face_service = None


def _get_face_service():
    global _face_service
    if _face_service is None:
        try:
            from src.detection.face_detection import FaceDetectionService
            _face_service = FaceDetectionService()
        except Exception:
            pass
    return _face_service


def is_streaming() -> bool:
    return _rpicam_process is not None and _rpicam_process.poll() is None


def pause_stream() -> bool:
    """Stop stream if running. Returns True if it was running."""
    global _ffmpeg_process, _rpicam_process
    if not is_streaming():
        return False
    for proc in (_ffmpeg_process, _rpicam_process):
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    _ffmpeg_process = None
    _rpicam_process = None
    if Path(STREAM_DIR).exists():
        shutil.rmtree(STREAM_DIR)
    print("Stream paused for motion capture.")
    return True


def _make_stream_response(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response


def start_stream():
    global _ffmpeg_process, _rpicam_process

    if _rpicam_process and _rpicam_process.poll() is None:
        return

    os.makedirs(STREAM_DIR, exist_ok=True)

    rpicam_cmd = [
        "rpicam-vid",
        "--width", "1280", "--height", "720",
        "--framerate", "30",
        "--codec", "h264",
        "--inline",
        "--nopreview",
        "-t", "0",
        "-o", "tcp://127.0.0.1:8888?listen"
    ]

    _rpicam_process = subprocess.Popen(
        rpicam_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-use_wallclock_as_timestamps", "1",
        "-i", "tcp://127.0.0.1:8888",
        "-c:v", "copy",
        "-hls_time", "1",
        "-hls_list_size", "4",
        "-hls_flags", "delete_segments",
        "-f", "hls",
        f"{STREAM_DIR}/live.m3u8"
    ]

    def _start_ffmpeg():
        import time
        time.sleep(1)
        global _ffmpeg_process
        _ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    import threading
    threading.Thread(target=_start_ffmpeg, daemon=True).start()


@stream_bp.route("/stream/start", methods=["POST"])
def start_stream_route():
    start_stream()
    return jsonify({"status": "started"})


@stream_bp.route("/stream/stop", methods=["POST"])
def stop_stream():
    global _ffmpeg_process, _rpicam_process

    for proc in (_ffmpeg_process, _rpicam_process):
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    _ffmpeg_process = None
    _rpicam_process = None

    if Path(STREAM_DIR).exists():
        shutil.rmtree(STREAM_DIR)

    return jsonify({"status": "stopped"})


@stream_bp.route("/stream/live.m3u8")
def serve_playlist():
    response = send_from_directory(STREAM_DIR, "live.m3u8", mimetype="application/vnd.apple.mpegurl")
    return _make_stream_response(response)


@stream_bp.route("/stream/<filename>")
def serve_segment(filename):
    mime = "video/MP2T" if filename.endswith(".ts") else "application/vnd.apple.mpegurl"
    try:
        response = send_from_directory(STREAM_DIR, filename, mimetype=mime)
        return _make_stream_response(response)
    except FileNotFoundError:
        return "", 404


@stream_bp.route("/stream/detection", methods=["GET"])
def stream_detection():
    now = _time.time()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    empty = {"detected": False, "faces": [], "timestamp": timestamp}

    with _detection_lock:
        if _detection_cache["result"] is not None and now < _detection_cache["expires"]:
            return _make_stream_response(jsonify(_detection_cache["result"]))

    try:
        segments = sorted(Path(STREAM_DIR).glob("*.ts"), key=lambda p: p.stat().st_mtime)
        if not segments:
            return _make_stream_response(jsonify(empty))

        seg = segments[-1]

        cap = cv2.VideoCapture(str(seg))
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return _make_stream_response(jsonify(empty))

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_service = _get_face_service()
        if face_service is None:
            return _make_stream_response(jsonify(empty))

        faces = face_service.scan_frame_with_confidence(rgb)
        result = {"detected": len(faces) > 0, "faces": faces, "timestamp": timestamp}

        with _detection_lock:
            _detection_cache["result"] = result
            _detection_cache["expires"] = now + 2.0

        return _make_stream_response(jsonify(result))

    except Exception:
        return _make_stream_response(jsonify(empty))
