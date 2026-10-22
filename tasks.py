import asyncio
from datetime import datetime, timezone

from sqlalchemy import delete

from database import SessionLocal
from models import PendingOwner


def delete_expired_pending_users():
    """Delete unverified users whose verification has expired."""

    with SessionLocal() as db:
        now = datetime.now(timezone.utc)

        statement = delete(PendingOwner).where(
            PendingOwner.expires_at <= now,
        )

        result = db.execute(statement)
        db.commit()

        return result.rowcount or 0


async def cleanup_expired_users():
    while True:
        try:
            # Run synchronous database work without blocking
            # the async event loop.
            deleted_count = await asyncio.to_thread(
                delete_expired_pending_users
            )

            if deleted_count:
                print(
                    f"Deleted {deleted_count} expired pending users."
                )

        except Exception as exc:
            print(f"Pending-user cleanup failed: {exc}")

        # Check again in 60 seconds.
        await asyncio.sleep(60)
