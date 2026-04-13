import httpx
import os
import logging
import uuid
from core.signer import WebhookSigner

logger = logging.getLogger("digital-twin")


class EcosystemDispatcher:
    def __init__(self):
        self.b2b_url = os.getenv("B2B_API_URL")
        self.rpa_url = os.getenv("RPA_API_URL")
        self.api_key = os.getenv("ECOSYSTEM_API_KEY")

    def _generate_trace_context(self) -> str:
        trace_id = uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]
        return f"00-{trace_id}-{span_id}-01"

    async def dispatch_capacity_request(self, payload: dict) -> bool:
        is_legacy = payload.get("is_legacy_system", False)
        target_url = f"{self.rpa_url}/api/v1/orchestrate" if is_legacy else f"{self.b2b_url}/api/v1/bookings"

        traceparent = self._generate_trace_context()
        transaction_id = payload.get("transaction_id", uuid.uuid4().hex)

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "traceparent": traceparent,
            "Idempotency-Key": f"idem-{transaction_id}"
        }

        if is_legacy:
            headers["X-RPA-Signature"] = WebhookSigner.generate_signature(payload)

        logger.info(
            f"Dispatching [Trace: {traceparent}] [Idem: {transaction_id}] to {'Legacy RPA' if is_legacy else 'Modern B2B'} Gateway.")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(target_url, json=payload, headers=headers, timeout=10.0)
                response.raise_for_status()
                return True
            except httpx.HTTPError as e:
                logger.error(f"Ecosystem dispatch failed [Trace: {traceparent}]: {str(e)}")
                return False
