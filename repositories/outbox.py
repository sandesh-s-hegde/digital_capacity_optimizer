import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class OutboxRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def stage_event(self, event_type: str, payload: dict) -> None:
        """
        Implements the Transactional Outbox Pattern.
        Guarantees that the AI's internal state update and the webhook generation
        are committed atomically to prevent phantom data drops.
        """
        stmt = text("""
            INSERT INTO system_outbox (event_type, payload, status)
            VALUES (:event_type, :payload, 'pending')
        """)

        await self.db.execute(stmt, {
            "event_type": event_type,
            "payload": json.dumps(payload)
        })
