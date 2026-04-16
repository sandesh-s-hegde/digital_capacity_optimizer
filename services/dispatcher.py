import os
import requests
import streamlit as st
from core.signer import sign_payload
from dotenv import load_dotenv

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

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            st.success(f"Successfully dispatched to {route}!")
            return True

        except requests.exceptions.RequestException as e:
            st.error(f"Network transmission error to {route}: {str(e)}")
            return False
