import os
import requests
import time
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
            if route == "Modern B2B (API)":
                signed_payload = sign_payload(payload)
                return self._send_request(self.b2b_api_url, signed_payload, route)

            elif route == "Legacy Carrier (RPA)":
                # Intercept and transform the payload for rigid legacy bot consumption
                rpa_payload = self._format_for_legacy_rpa(payload)
                signed_rpa_payload = sign_payload(rpa_payload)
                return self._send_request(self.rpa_bridge_url, signed_rpa_payload, route)

            else:
                logger.error("Unknown routing destination.")
                st.error("Unknown routing destination.")
                return False

        except Exception as e:
            logger.error(f"Dispatch preparation failed: {str(e)}")
            st.error(f"Dispatch preparation failed: {str(e)}")
            return False

    def _format_for_legacy_rpa(self, payload: dict) -> dict:
        """
        Flattens complex nested JSON payloads into a strict, single-level
        dictionary required by legacy RPA queue managers.
        """
        logger.info("Transforming payload schema for legacy RPA bot compatibility...")
        return {
            "RPA_Task_ID": f"JOB-{int(time.time())}",
            "Action": "PROCURE_CAPACITY",
            "Target_SKU": payload.get("Target Ecosystem Route", "GENERAL_FREIGHT"),
            "Volume_Required": payload.get("Assets to Procure", 1),
            "Urgency_Flag": "HIGH",
            "System_Source": "LSP_DIGITAL_TWIN_V5"
        }

    def _send_request(self, url: str, payload: dict, route: str) -> bool:
        if not url:
            logger.error(f"URL configuration missing for {route}.")
            st.error(f"URL configuration missing for {route}.")
            return False

        logger.info(f"Dispatching payload to {url}...")

        try:
            # Enforce a strict 10-second timeout to prevent UI thread locking
            response = requests.post(url, json=payload, timeout=10.0)
            response.raise_for_status()

            logger.info(f"Success! Server responded with HTTP {response.status_code}")
            return True

        except requests.exceptions.Timeout:
            logger.error("Dispatch Failed: The external API timed out after 10 seconds.")
            st.error(f"Network timeout: {route} did not respond in time.")
            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Dispatch Failed: Network exception occurred - {str(e)}")
            st.error(f"Network transmission error to {route}: {str(e)}")
            return False
