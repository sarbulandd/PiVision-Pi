import time

import psutil
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


def _make_response(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response


def _cpu_temp() -> float | None:
    try:
        temps = psutil.sensors_temperatures()
        for key in ("cpu_thermal", "coretemp", "cpu-thermal"):
            if key in temps and temps[key]:
                return round(temps[key][0].current, 1)
    except Exception:
        pass
    return None


@health_bp.route("/health", methods=["GET"])
def get_health():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return _make_response(jsonify({
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "cpu_temp": _cpu_temp(),
        "memory_percent": round(mem.percent, 1),
        "memory_used_gb": round(mem.used / 1e9, 2),
        "memory_total_gb": round(mem.total / 1e9, 2),
        "disk_percent": round(disk.percent, 1),
        "disk_used_gb": round(disk.used / 1e9, 2),
        "disk_total_gb": round(disk.total / 1e9, 2),
        "uptime_seconds": int(time.time() - psutil.boot_time()),
    }))
