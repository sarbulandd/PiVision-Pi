from flask import Blueprint, jsonify

from src.api.shared import event_service

events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["GET"])
def get_events():
    events = event_service.get_events()
    return jsonify({"events": events, "count": len(events)})


@events_bp.route("/events/latest", methods=["GET"])
def get_latest_event():
    events = event_service.get_events()
    if not events:
        return jsonify({"error": "no events found"}), 404
    return jsonify(events[-1])


@events_bp.route("/events/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    deleted = event_service.delete_event(event_id)
    if not deleted:
        return jsonify({"error": "event not found"}), 404
    return jsonify({"deleted": event_id})


@events_bp.route("/events", methods=["DELETE"])
def clear_events():
    event_service.clear_events()
    return jsonify({"message": "all events cleared"})
