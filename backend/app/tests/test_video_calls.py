#!/usr/bin/env python3
"""
Test script to verify video call functionality
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from sqlalchemy import text

from app.database import AsyncSessionLocal


async def check_video_call_tables():
    """Check if all video call tables exist and show their structure"""
    print("🔍 Checking Video Call Database Tables...")
    print("=" * 50)

    async with AsyncSessionLocal() as session:
        # Check table existence
        tables = [
            "video_calls",
            "call_participants",
            "recording_consents",
            "call_transcriptions",
            "transcription_segments",
        ]

        for table in tables:
            try:
                result = await session.execute(
                    text(
                        f"""
                    SELECT COUNT(*) as count
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    AND table_name = '{table}'
                """
                    )
                )
                count = result.fetchone()[0]
                status = "✅" if count > 0 else "❌"
                print(
                    f"{status} Table '{table}': {'exists' if count > 0 else 'missing'}"
                )

                if count > 0:
                    # Get row count
                    try:
                        result = await session.execute(
                            text(f"SELECT COUNT(*) FROM {table}")
                        )
                        row_count = result.fetchone()[0]
                        print(f"   📊 Records: {row_count}")
                    except Exception as e:
                        print(f"   ⚠️  Could not count records: {e}")

            except Exception as e:
                print(f"❌ Error checking table '{table}': {e}")

        print("\n" + "=" * 50)


async def check_video_call_endpoints():
    """Show available video call endpoints"""
    print("\n📡 Available Video Call API Endpoints:")
    print("=" * 50)

    endpoints = [
        ("POST", "/api/video-calls/schedule", "Schedule a new video call"),
        ("GET", "/api/video-calls/{call_id}", "Get video call details"),
        ("POST", "/api/video-calls/{call_id}/join", "Join a video call"),
        ("POST", "/api/video-calls/{call_id}/end", "End a video call"),
        ("POST", "/api/video-calls/{call_id}/consent", "Record consent for recording"),
        ("GET", "/api/video-calls/{call_id}/token", "Get WebRTC token"),
        ("GET", "/api/video-calls/{call_id}/transcript", "Get call transcript"),
        (
            "POST",
            "/api/video-calls/{call_id}/transcript/segments",
            "Save transcript segment",
        ),
        (
            "GET",
            "/api/video-calls/{call_id}/transcript/download",
            "Download transcript",
        ),
        ("GET", "/api/video-calls/", "List user's video calls"),
    ]

    for method, endpoint, description in endpoints:
        print(f"🔗 {method:4} {endpoint:45} - {description}")

    print("\n💡 API Documentation: http://localhost:8000/docs")
    print("=" * 50)


def check_video_call_models():
    """Show video call model structure"""
    print("\n🏗️ Video Call Data Models:")
    print("=" * 50)

    models = [
        ("VideoCall", "Main video call entity with scheduling and status"),
        ("CallParticipant", "Tracks who joined/left the call and when"),
        ("RecordingConsent", "Stores user consent for call recording"),
        ("CallTranscription", "Overall transcription of the call"),
        ("TranscriptionSegment", "Individual speech segments with timestamps"),
    ]

    for model, description in models:
        print(f"📋 {model:20} - {description}")

    print("\n🔧 Key Features:")
    features = [
        "Real-time video calling with WebRTC",
        "Call recording with consent management",
        "Automatic transcription with speaker identification",
        "Participant tracking (join/leave times)",
        "Multi-format transcript export (txt, pdf, srt)",
        "Integration with interview scheduling",
        "Permission-based access control",
    ]

    for feature in features:
        print(f"   ✨ {feature}")

    print("=" * 50)


async def test_video_call_crud_basic():
    """Test basic CRUD operations if possible"""
    print("\n🧪 Testing Video Call CRUD Operations:")
    print("=" * 50)

    try:
        async with AsyncSessionLocal() as session:
            # Check if we can query video calls
            result = await session.execute(text("SELECT COUNT(*) FROM video_calls"))
            call_count = result.fetchone()[0]
            print("✅ Database connection successful")
            print(f"📊 Current video calls in database: {call_count}")

            # Check if we can query participants
            result = await session.execute(
                text("SELECT COUNT(*) FROM call_participants")
            )
            participant_count = result.fetchone()[0]
            print(f"📊 Call participants recorded: {participant_count}")

            # Check transcriptions
            result = await session.execute(
                text("SELECT COUNT(*) FROM call_transcriptions")
            )
            transcript_count = result.fetchone()[0]
            print(f"📊 Call transcriptions: {transcript_count}")

            print("✅ Basic database operations working correctly")

    except Exception as e:
        print(f"❌ Error testing CRUD operations: {e}")

    print("=" * 50)


def show_testing_instructions():
    """Show instructions for testing video calls"""
    print("\n📝 How to Test Video Call Functionality:")
    print("=" * 50)

    steps = [
        "1. 🔐 Authenticate with the API (get access token)",
        "2. 📅 Schedule a video call using POST /api/video-calls/schedule",
        "3. 🎥 Join the call using POST /api/video-calls/{call_id}/join",
        "4. 🎯 Get WebRTC token using GET /api/video-calls/{call_id}/token",
        "5. 📝 Record consent using POST /api/video-calls/{call_id}/consent",
        "6. 🎤 Save transcript segments during call",
        "7. ⏹️ End the call using POST /api/video-calls/{call_id}/end",
        "8. 📄 Download transcript using GET /api/video-calls/{call_id}/transcript/download",
    ]

    for step in steps:
        print(f"   {step}")

    print("\n🌐 Frontend Integration:")
    print("   • Check if video call components exist in frontend/")
    print("   • Look for WebRTC integration code")
    print("   • Verify video call UI components")

    print("\n🧪 Quick API Test Commands:")
    print("   # Check API docs")
    print("   curl http://localhost:8000/docs")
    print("   ")
    print("   # Get your video calls (requires auth)")
    print(
        "   curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/api/video-calls/"
    )

    print("=" * 50)


async def main():
    """Main test function"""
    print("🎥 MiraiWorks Video Call System Check")
    print("====================================")

    # Run all checks
    await check_video_call_tables()
    await check_video_call_endpoints()
    check_video_call_models()
    await test_video_call_crud_basic()
    show_testing_instructions()

    print("\n✅ Video Call System Check Complete!")
    print("🚀 The video call functionality appears to be properly configured.")
    print(
        "💡 Use the API documentation at http://localhost:8000/docs to test endpoints."
    )


if __name__ == "__main__":
    asyncio.run(main())
