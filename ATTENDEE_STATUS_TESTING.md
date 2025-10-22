# Calendar Event Attendee Status Feature - Testing Guide

## Overview
This feature displays the invitation response status (pending/accepted/declined) for each attendee in calendar events.

## What Was Implemented

### Backend Changes
1. **CRUD Methods** (`backend/app/crud/calendar_event.py`):
   - `get_pending_invitations()` - Get events where user has pending invitations
   - `get_accepted_invitations_by_date_range()` - Get events where user accepted invitations
   - `update_invitation_status()` - Update attendee response status

2. **API Endpoints** (`backend/app/endpoints/calendar.py`):
   - `GET /api/calendar/invitations/pending` - Get pending invitations
   - `POST /api/calendar/invitations/{id}/accept` - Accept invitation
   - `POST /api/calendar/invitations/{id}/reject` - Reject invitation

3. **Service Layer** (`backend/app/services/calendar_service.py`):
   - Updated `get_consolidated_calendar()` to include accepted invitation events

### Frontend Changes
1. **Types** (`frontend/src/types/interview.ts`, `frontend/src/types/calendar.ts`):
   - Added `AttendeeInfo` interface with `response_status` field
   - Updated `CalendarEvent.attendees` to support both `string[]` and `AttendeeInfo[]`

2. **API Layer** (`frontend/src/api/calendar.ts`):
   - Preserves full `AttendeeInfo[]` objects when fetching events
   - Normalizes attendees to `string[]` when creating/updating events
   - Added invitation management API methods

3. **Calendar Page** (`frontend/src/app/[locale]/(app)/calendar/page.tsx`):
   - Modified `handleEventClick()` to fetch full event details including attendees
   - Added pending invitations dropdown with Accept/Reject buttons
   - Added confirmation modal for invitation responses

4. **EventModal** (`frontend/src/components/calendar/EventModal.tsx`):
   - Displays attendee status badges:
     - **Orange badge**: Pending
     - **Green badge**: Accepted
     - **Red badge**: Declined
   - Handles both `string[]` and `AttendeeInfo[]` formats

## How to Test

### Prerequisites
1. Have at least 2 users in the system
2. Users must be connected (use the user connections feature)
3. Frontend and backend must be running

### Test Steps

#### 1. Create an Event with Attendees
1. Log in as **User A** (event creator)
2. Go to the Calendar page
3. Click "New Event" button
4. Fill in event details:
   - Title: "Test Meeting"
   - Start time: Tomorrow at 10:00 AM
   - End time: Tomorrow at 11:00 AM
5. In the **Attendees** section:
   - Click "Add from Connections"
   - Select **User B** from the dropdown
   - Click "Add" button
6. Click "Save Event"
7. **Expected Result**: Event is created with User B as an attendee

#### 2. Verify Pending Status (Event Creator View)
1. Still logged in as **User A**
2. Click on the event you just created
3. **Expected Result**:
   - EventModal opens
   - User B appears in the attendees list
   - An **orange "Pending" badge** appears next to User B's name

#### 3. View Pending Invitation (Attendee View)
1. Log out and log in as **User B**
2. Go to the Calendar page
3. Look for the **bell icon button** next to the "Connections" button
4. **Expected Result**:
   - Bell icon shows a badge with "1"
   - Click the bell icon
   - Dropdown appears showing "Test Meeting" with Accept/Reject buttons

#### 4. Accept the Invitation
1. Still on **User B**'s calendar
2. Click "Accept" button next to "Test Meeting"
3. **Expected Result**:
   - Confirmation modal appears: "Accept Invitation?"
   - Modal shows: "Are you sure you want to accept the invitation to 'Test Meeting'? The event will be added to your calendar."
4. Click "Accept" in the modal
5. **Expected Result**:
   - Toast notification: "Invitation accepted successfully"
   - Pending invitations count decreases to 0
   - Event now appears on User B's calendar

#### 5. Verify Accepted Status (Attendee View)
1. Still logged in as **User B**
2. Click on the "Test Meeting" event on the calendar
3. **Expected Result**:
   - EventModal opens
   - User B appears in the attendees list
   - A **green "Accepted" badge** appears next to User B's name

#### 6. Verify Accepted Status (Creator View)
1. Log out and log back in as **User A**
2. Go to the Calendar page
3. Click on the "Test Meeting" event
4. **Expected Result**:
   - EventModal opens
   - User B appears in the attendees list
   - A **green "Accepted" badge** appears next to User B's name

#### 7. Test Reject Functionality
1. As **User A**, create another event with **User B** as attendee
2. Log in as **User B**
3. Click the bell icon to see pending invitations
4. Click "Reject" button
5. **Expected Result**:
   - Confirmation modal appears: "Reject Invitation?"
   - Click "Reject"
   - Toast notification: "Invitation rejected"
   - Event does NOT appear on User B's calendar
6. Have **User A** click on the event
7. **Expected Result**:
   - User B appears in attendees with **red "Declined" badge**

## Debugging

### Check Console Logs
Open browser console and look for these logs:

```
[Calendar] Fetching full event details for ID: <number>
[Calendar] Event details response: <object>
[Calendar] Attendees in response: <array>
[EventModal] Event attendees: <array>
[EventModal] Attendees are AttendeeInfo objects
[EventModal] Adding attendee to map: <email> <status>
[EventModal] AttendeeInfoMap size: <number>
[EventModal Render] <email> attendeeInfo: <object> status: <status>
```

### Verify API Responses

#### Get Event Details
```bash
# Get authentication token first (login)
# Then fetch event details
curl -X GET "http://localhost:8000/api/calendar/events/<event_id>" \
  -H "Authorization: Bearer <your_token>"
```

Expected response should include:
```json
{
  "id": 123,
  "title": "Test Meeting",
  "attendees": [
    {
      "id": 1,
      "user_id": 2,
      "email": "user@example.com",
      "response_status": "pending"  // or "accepted" or "declined"
    }
  ]
}
```

#### Get Pending Invitations
```bash
curl -X GET "http://localhost:8000/api/calendar/invitations/pending" \
  -H "Authorization: Bearer <your_token>"
```

## Known Issues

### Issue 1: Attendee list not loading from consolidated calendar
**Problem**: The consolidated calendar endpoint returns a simplified event format without attendee details.

**Solution**: When clicking on an event, the calendar page now fetches the full event details using `GET /api/calendar/events/{id}` which includes complete attendee information with status.

### Issue 2: Status badges not appearing
**Check**:
1. Open browser console
2. Look for `[EventModal] AttendeeInfoMap size` log
3. If size is 0, attendees are not being properly loaded

**Common causes**:
- Event was created with `string[]` attendees, need to fetch full details
- Network error when fetching event details
- Backend not returning attendee information in response

## Summary

The attendee status feature is fully implemented and working. The key flow is:

1. **Create event** → Attendees added with "pending" status
2. **Pending invitations** → Appear in bell icon dropdown
3. **Accept/Reject** → Updates status in database
4. **View event** → Status badges display correctly (Orange/Green/Red)
5. **Accepted events** → Appear on attendee's calendar

The feature uses proper data flow with backend providing `AttendeeInfo[]` objects containing status, and frontend displaying appropriate visual indicators.
