"""
Migration script to convert user_connections to company_connections.

This script reads existing user_connections and creates corresponding
company_connections based on the users' companies.

Migration Logic:
1. If both users have companies:
   - Create company-to-company connection (bidirectional)
2. If one user has no company:
   - Create user-to-company connection
3. If neither user has a company:
   - Skip (cannot create company connection)

Usage:
    PYTHONPATH=. python scripts/migrate_user_connections.py [--dry-run]
"""

import argparse
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, init_db
from app.models.company_connection import CompanyConnection
from app.models.user import User
from app.models.user_connection import UserConnection
from app.utils.datetime_utils import get_utc_now
from app.utils.logging import configure_structlog, get_logger

configure_structlog(log_level="INFO", json_logs=False)
logger = get_logger(__name__)


class MigrationStats:
    """Track migration statistics."""

    def __init__(self):
        self.total_user_connections = 0
        self.company_to_company_created = 0
        self.user_to_company_created = 0
        self.skipped_no_company = 0
        self.skipped_duplicate = 0
        self.errors = 0


async def migrate_connection(
    db: AsyncSession,
    user_conn: UserConnection,
    user_map: dict[int, User],
    stats: MigrationStats,
    dry_run: bool = False,
) -> None:
    """
    Migrate a single user_connection to company_connection.

    Args:
        db: Database session
        user_conn: UserConnection to migrate
        user_map: Map of user_id to User object
        stats: Migration statistics
        dry_run: If True, don't actually create connections
    """
    user1 = user_map.get(user_conn.user_id)
    user2 = user_map.get(user_conn.connected_user_id)

    if not user1 or not user2:
        logger.warning(
            f"Skipping connection {user_conn.id}: User not found",
            user1_id=user_conn.user_id,
            user2_id=user_conn.connected_user_id,
        )
        stats.skipped_no_company += 1
        return

    # Determine connection type based on companies
    if user1.company_id and user2.company_id:
        # Both have companies
        if user1.company_id == user2.company_id:
            # Same company - users can interact by default, no connection needed
            logger.info(
                f"Skipping connection {user_conn.id}: Both users in same company",
                user1_id=user_conn.user_id,
                user2_id=user_conn.connected_user_id,
                company_id=user1.company_id,
            )
            stats.skipped_no_company += 1
        else:
            # Different companies → company-to-company connection
            await create_company_to_company_connection(
                db, user1, user2, user_conn, stats, dry_run
            )
    elif user1.company_id:
        # Only user1 has company → user2-to-company1 connection
        await create_user_to_company_connection(
            db, user2, user1.company_id, user_conn, stats, dry_run
        )
    elif user2.company_id:
        # Only user2 has company → user1-to-company2 connection
        await create_user_to_company_connection(
            db, user1, user2.company_id, user_conn, stats, dry_run
        )
    else:
        # Neither has company → cannot create connection
        logger.info(
            f"Skipping connection {user_conn.id}: Neither user has a company",
            user1_id=user_conn.user_id,
            user2_id=user_conn.connected_user_id,
        )
        stats.skipped_no_company += 1


async def create_company_to_company_connection(
    db: AsyncSession,
    user1: User,
    user2: User,
    user_conn: UserConnection,
    stats: MigrationStats,
    dry_run: bool,
) -> None:
    """Create bidirectional company-to-company connections."""
    # Create connection from company1 to company2
    await create_single_company_connection(
        db,
        source_type="company",
        source_company_id=user1.company_id,
        target_company_id=user2.company_id,
        created_by=user_conn.created_by,
        creation_type=user_conn.creation_type or "manual",
        stats=stats,
        dry_run=dry_run,
        label=f"Company {user1.company_id} → Company {user2.company_id}",
    )

    # Create reverse connection from company2 to company1 (if different)
    if user1.company_id != user2.company_id:
        await create_single_company_connection(
            db,
            source_type="company",
            source_company_id=user2.company_id,
            target_company_id=user1.company_id,
            created_by=user_conn.created_by,
            creation_type=user_conn.creation_type or "manual",
            stats=stats,
            dry_run=dry_run,
            label=f"Company {user2.company_id} → Company {user1.company_id}",
        )

    stats.company_to_company_created += 1


async def create_user_to_company_connection(
    db: AsyncSession,
    user: User,
    target_company_id: int,
    user_conn: UserConnection,
    stats: MigrationStats,
    dry_run: bool,
) -> None:
    """Create user-to-company connection."""
    await create_single_company_connection(
        db,
        source_type="user",
        source_user_id=user.id,
        target_company_id=target_company_id,
        created_by=user_conn.created_by,
        creation_type=user_conn.creation_type or "manual",
        stats=stats,
        dry_run=dry_run,
        label=f"User {user.id} → Company {target_company_id}",
    )

    stats.user_to_company_created += 1


async def create_single_company_connection(
    db: AsyncSession,
    source_type: str,
    target_company_id: int,
    created_by: int | None,
    creation_type: str,
    stats: MigrationStats,
    dry_run: bool,
    label: str,
    source_user_id: int | None = None,
    source_company_id: int | None = None,
) -> None:
    """Create a single company connection if it doesn't exist."""
    # Check if connection already exists
    if source_type == "user":
        result = await db.execute(
            select(CompanyConnection).where(
                CompanyConnection.source_type == "user",
                CompanyConnection.source_user_id == source_user_id,
                CompanyConnection.target_company_id == target_company_id,
            )
        )
    else:
        result = await db.execute(
            select(CompanyConnection).where(
                CompanyConnection.source_type == "company",
                CompanyConnection.source_company_id == source_company_id,
                CompanyConnection.target_company_id == target_company_id,
            )
        )

    existing = result.scalar_one_or_none()

    if existing:
        logger.debug(f"Connection already exists: {label}")
        stats.skipped_duplicate += 1
        return

    if dry_run:
        logger.info(f"[DRY RUN] Would create: {label}")
        return

    # Create the connection
    connection = CompanyConnection(
        source_type=source_type,
        source_user_id=source_user_id,
        source_company_id=source_company_id,
        target_company_id=target_company_id,
        is_active=True,
        connection_type="standard",
        can_message=True,
        can_view_profile=True,
        can_assign_tasks=False,
        creation_type=creation_type,
        created_by=created_by,
        created_at=get_utc_now(),
    )

    db.add(connection)
    logger.info(f"Created: {label}")


async def load_users(db: AsyncSession) -> dict[int, User]:
    """Load all users with their companies."""
    result = await db.execute(select(User))
    users = result.scalars().all()

    return {user.id: user for user in users}


async def migrate_all_connections(dry_run: bool = False) -> MigrationStats:
    """
    Migrate all user_connections to company_connections.

    Args:
        dry_run: If True, don't actually create connections

    Returns:
        Migration statistics
    """
    stats = MigrationStats()

    async with AsyncSessionLocal() as db:
        try:
            # Load all users
            logger.info("Loading users...")
            user_map = await load_users(db)
            logger.info(f"Loaded {len(user_map)} users")

            # Load all user connections
            logger.info("Loading user connections...")
            result = await db.execute(select(UserConnection))
            user_connections = result.scalars().all()
            stats.total_user_connections = len(user_connections)
            logger.info(f"Found {stats.total_user_connections} user connections")

            # Migrate each connection
            logger.info("Starting migration...")
            for idx, user_conn in enumerate(user_connections, 1):
                try:
                    await migrate_connection(db, user_conn, user_map, stats, dry_run)

                    if idx % 10 == 0:
                        logger.info(f"Progress: {idx}/{stats.total_user_connections}")

                except Exception as e:
                    logger.error(
                        f"Error migrating connection {user_conn.id}",
                        error=str(e),
                        user1_id=user_conn.user_id,
                        user2_id=user_conn.connected_user_id,
                    )
                    stats.errors += 1

            if not dry_run:
                await db.commit()
                logger.info("Migration committed to database")

        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            await db.rollback()
            raise

    return stats


def print_stats(stats: MigrationStats, dry_run: bool) -> None:
    """Print migration statistics."""
    mode = "DRY RUN" if dry_run else "COMPLETED"

    print(f"\n{'=' * 60}")
    print(f"Migration {mode}")
    print(f"{'=' * 60}")
    print(f"Total user_connections:           {stats.total_user_connections}")
    print(f"Company-to-company created:       {stats.company_to_company_created}")
    print(f"User-to-company created:          {stats.user_to_company_created}")
    print(f"Skipped (no company):             {stats.skipped_no_company}")
    print(f"Skipped (duplicate):              {stats.skipped_duplicate}")
    print(f"Errors:                           {stats.errors}")
    print(f"{'=' * 60}\n")

    if dry_run:
        print("[!] This was a DRY RUN - no changes were made to the database")
        print("Run without --dry-run to perform the actual migration\n")
    else:
        print("[OK] Migration completed successfully!")
        print(
            f"Created {stats.company_to_company_created + stats.user_to_company_created} new company connections\n"
        )


async def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(
        description="Migrate user_connections to company_connections"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run migration without making changes to database",
    )
    args = parser.parse_args()

    logger.info("Starting user_connections migration")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")

    # Initialize database
    await init_db()

    # Run migration
    stats = await migrate_all_connections(dry_run=args.dry_run)

    # Print results
    print_stats(stats, args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
