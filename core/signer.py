import os
import hmac
import hashlib
import json


def sign_payload(payload: dict) -> dict:
    secret_key = os.getenv("API_SECRET_KEY", "fallback_dev_secret_key_123").encode("utf-8")

    payload_string = json.dumps(payload, sort_keys=True).encode("utf-8")
    signature = hmac.new(secret_key, payload_string, hashlib.sha256).hexdigest()

    return {
        "security_signature": signature,
        "payload": payload
    }
