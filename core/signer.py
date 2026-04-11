import hmac
import hashlib
import os
import json


class WebhookSigner:
    @staticmethod
    def generate_signature(payload: dict) -> str:
        """
        Generates an HMAC-SHA256 signature for outgoing webhook verification.
        Ensures downstream APIs trust the Digital Twin's execution commands.
        """
        secret = os.getenv("WEBHOOK_SECRET_KEY", "dev_secret_key").encode("utf-8")

        body = json.dumps(payload, separators=(',', ':')).encode("utf-8")

        return hmac.new(secret, body, hashlib.sha256).hexdigest()
