from flask import Blueprint, jsonify

from src.api.shared import arm_service

status_bp = Blueprint("status", __name__)


@status_bp.route("/status", methods=["GET"])
def get_status():
    armed = arm_service.is_armed()
    return jsonify({
        "system_name": "PiVision",
        "health": "ok",
        "armed": armed,
        "status": "armed" if armed else "disarmed"
    })
