import requests
import firebase_admin
from firebase_admin import credentials, firestore

from src.config import BASE_DIR

SERVICE_ACCOUNT_PATH = BASE_DIR / "serviceAccountKey.json"
EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


class NotificationService:
    def __init__(self):
        if not SERVICE_ACCOUNT_PATH.exists():
            raise FileNotFoundError(f"serviceAccountKey.json not found at {SERVICE_ACCOUNT_PATH}")
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def _get_push_tokens(self) -> list[str]:
        docs = self.db.collection("pushTokens").stream()
        return [doc.to_dict().get("token") for doc in docs if doc.to_dict().get("token")]

    def send_alert(self, event_id: str, face_detected: bool, recognised_person: str = None) -> None:
        tokens = self._get_push_tokens()
        if not tokens:
            print("No push tokens found — skipping notification.")
            return

        if recognised_person:
            title = f"{recognised_person} Detected"
            body = f"PiVision recognised {recognised_person} at your camera."
        elif face_detected:
            title = "Unknown Face Detected"
            body = "PiVision detected an unrecognised face at your camera."
        else:
            title = "Motion Detected"
            body = "PiVision has detected movement at your camera."

        for token in tokens:
            payload = {
                "to": token,
                "title": title,
                "body": body,
                "sound": "default",
                "channelId": "pivision-alerts",
                "data": {"alertId": event_id}
            }
            try:
                response = requests.post(EXPO_PUSH_URL, json=payload, timeout=5)
                print(f"Push notification sent to {token[:20]}... status={response.status_code}")
            except requests.RequestException as e:
                print(f"Failed to send push notification: {e}")
