from flask import Blueprint, jsonify

from src.api.shared import arm_service

control_bp = Blueprint("control", __name__)


@control_bp.route("/arm", methods=["POST"])
def arm():
    arm_service.arm()
    return jsonify({"status": "armed"})


@control_bp.route("/disarm", methods=["POST"])
def disarm():
    arm_service.disarm()
    return jsonify({"status": "disarmed"})
