from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def index():
        return {"message": "PiVision API is running"}, 200


    from src.api.routes_status import status_bp
    from src.api.routes_control import control_bp
    from src.api.routes_events import events_bp
    from src.api.routes_faces import faces_bp

    app.register_blueprint(status_bp)
    app.register_blueprint(control_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(faces_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
