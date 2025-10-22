#!/usr/bin/env python3
"""
Test script for calendar event attendee status feature.

This script tests:
1. Creating an event with attendees
2. Fetching event details to verify attendees have status
3. Accepting/rejecting invitations
4. Verifying status updates
"""

import asyncio
import sys
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.calendar_event import CalendarEvent
from app.models.calendar_event_attendee import CalendarEventAttendee
from app.models.user import User
from app.schemas.calendar_event import CalendarEventCreate
from app.services.calendar_service import calendar_service
from app.crud.calendar_event import calendar_event


async def test_attendee_status():
    """Test the attendee status feature."""
    print("=" * 60)
    print("Testing Calendar Event Attendee Status Feature")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get two test users
        result = await db.execute(select(User).limit(2))
        users = result.scalars().all()

        if len(users) < 2:
            print("❌ Error: Need at least 2 users in the database to test")
            return False

        creator = users[0]
        attendee = users[1]

        print(f"\n✓ Creator: {creator.email} (ID: {creator.id})")
        print(f"✓ Attendee: {attendee.email} (ID: {attendee.id})")

        # Step 1: Create an event with attendees
        print("\n" + "-" * 60)
        print("Step 1: Creating event with attendee")
        print("-" * 60)

        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)

        event_data = CalendarEventCreate(
            title="Test Event - Attendee Status",
            description="Testing attendee status display",
            start_datetime=start_time,
            end_datetime=end_time,
            is_all_day=False,
            location="Test Location",
            timezone="UTC",
            attendees=[attendee.email]
        )

        created_event = await calendar_service.create_event(
            db, event_in=event_data, creator_id=creator.id
        )

        print(f"✓ Created event ID: {created_event.id}")
        print(f"  Title: {created_event.title}")

        # Step 2: Fetch event with relationships to verify attendees
        print("\n" + "-" * 60)
        print("Step 2: Fetching event with attendee details")
        print("-" * 60)

        event_with_attendees = await calendar_event.get_with_relationships(
            db, event_id=created_event.id
        )

        if not event_with_attendees:
            print("❌ Error: Could not fetch event")
            return False

        if not event_with_attendees.attendees:
            print("❌ Error: Event has no attendees")
            return False

        print(f"✓ Event has {len(event_with_attendees.attendees)} attendee(s)")

        for att in event_with_attendees.attendees:
            print(f"  - Email: {att.email}")
            print(f"    User ID: {att.user_id}")
            print(f"    Status: {att.response_status}")
            print(f"    Attendee ID: {att.id}")

            if att.response_status != "pending":
                print(f"    ❌ Error: Initial status should be 'pending', got '{att.response_status}'")
                return False

        print("✓ All attendees have 'pending' status")

        # Step 3: Get pending invitations for the attendee
        print("\n" + "-" * 60)
        print("Step 3: Getting pending invitations for attendee")
        print("-" * 60)

        pending_events = await calendar_event.get_pending_invitations(
            db, user_id=attendee.id
        )

        print(f"✓ Found {len(pending_events)} pending invitation(s)")

        found_our_event = False
        for event in pending_events:
            if event.id == created_event.id:
                found_our_event = True
                print(f"✓ Found our test event: {event.title}")

        if not found_our_event:
            print("❌ Error: Test event not in pending invitations")
            return False

        # Step 4: Accept the invitation
        print("\n" + "-" * 60)
        print("Step 4: Accepting invitation")
        print("-" * 60)

        success = await calendar_event.update_invitation_status(
            db, event_id=created_event.id, user_id=attendee.id, status="accepted"
        )

        if not success:
            print("❌ Error: Failed to accept invitation")
            return False

        print("✓ Invitation accepted")

        # Step 5: Verify status was updated
        print("\n" + "-" * 60)
        print("Step 5: Verifying status update")
        print("-" * 60)

        updated_event = await calendar_event.get_with_relationships(
            db, event_id=created_event.id
        )

        for att in updated_event.attendees:
            print(f"  - Email: {att.email}")
            print(f"    Status: {att.response_status}")

            if att.email == attendee.email:
                if att.response_status != "accepted":
                    print(f"    ❌ Error: Status should be 'accepted', got '{att.response_status}'")
                    return False
                print("    ✓ Status updated to 'accepted'")

        # Step 6: Verify event appears in accepted invitations
        print("\n" + "-" * 60)
        print("Step 6: Checking accepted invitations")
        print("-" * 60)

        accepted_events = await calendar_event.get_accepted_invitations_by_date_range(
            db,
            user_id=attendee.id,
            start_date=start_time - timedelta(days=1),
            end_date=end_time + timedelta(days=1)
        )

        print(f"✓ Found {len(accepted_events)} accepted invitation(s)")

        found_accepted = False
        for event in accepted_events:
            if event.id == created_event.id:
                found_accepted = True
                print(f"✓ Test event appears in accepted invitations")

        if not found_accepted:
            print("❌ Error: Test event not in accepted invitations")
            return False

        # Step 7: Test declining invitation (change status)
        print("\n" + "-" * 60)
        print("Step 7: Declining invitation")
        print("-" * 60)

        success = await calendar_event.update_invitation_status(
            db, event_id=created_event.id, user_id=attendee.id, status="declined"
        )

        if not success:
            print("❌ Error: Failed to decline invitation")
            return False

        print("✓ Invitation declined")

        # Verify declined status
        declined_event = await calendar_event.get_with_relationships(
            db, event_id=created_event.id
        )

        for att in declined_event.attendees:
            if att.email == attendee.email:
                if att.response_status != "declined":
                    print(f"    ❌ Error: Status should be 'declined', got '{att.response_status}'")
                    return False
                print("    ✓ Status updated to 'declined'")

        # Cleanup: Delete the test event
        print("\n" + "-" * 60)
        print("Cleanup: Deleting test event")
        print("-" * 60)

        await calendar_event.remove(db, id=created_event.id)
        print("✓ Test event deleted")

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_attendee_status())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
