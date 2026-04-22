import os
import requests
import streamlit as st
import logging
from core.signer import sign_payload
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("WebhookDispatcher")

load_dotenv()

class EcosystemDispatcher:
    def __init__(self):
        self.b2b_api_url = os.getenv("B2B_API_URL")
        self.rpa_bridge_url = os.getenv("RPA_BRIDGE_URL")

    def dispatch_sync(self, payload: dict) -> bool:
        route = payload.get("Target Ecosystem Route")

        try:
            signed_payload = sign_payload(payload)

            if route == "Modern B2B (API)":
                return self._send_request(self.b2b_api_url, signed_payload, route)
            elif route == "Legacy Carrier (RPA)":
                return self._send_request(self.rpa_bridge_url, signed_payload, route)
            else:
                st.error("Unknown routing destination.")
                return False

        except Exception as e:
            st.error(f"Dispatch preparation failed: {str(e)}")
            return False

    def _send_request(self, url: str, payload: dict, route: str) -> bool:
        if not url:
            st.error(f"URL configuration missing for {route}.")
            return False

        logger.info(f"Dispatching payload to {target_url}...")

        try:
            # Enforce a strict 10-second timeout to prevent UI thread locking
            response = requests.post(target_url, json=secure_payload, headers=headers, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Success! Server responded with HTTP {response.status_code}")
            return True
        except requests.exceptions.Timeout:
            logger.error("Dispatch Failed: The external API timed out after 10 seconds.")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Dispatch Failed: Network exception occurred - {str(e)}")
            return False

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            st.success(f"Successfully dispatched to {route}!")
            return True

        except requests.exceptions.RequestException as e:
            st.error(f"Network transmission error to {route}: {str(e)}")
            return False
