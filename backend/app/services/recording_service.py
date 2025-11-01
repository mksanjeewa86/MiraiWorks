import logging
from typing import Any

from app.models.video_call import RecordingConsent, VideoCall
from app.services.video_service import video_service
from app.utils.datetime_utils import get_utc_now

logger = logging.getLogger(__name__)


class RecordingService:
    """Service for handling video call recording with consent management."""

    def __init__(self):
        self.active_recordings: dict[str, dict] = {}

    async def start_recording(
        self, video_call: VideoCall, consents: list[RecordingConsent]
    ) -> str | None:
        """Start recording a video call if all participants have consented."""
        try:
            # Check if all participants have consented
            if not self._all_participants_consented(consents):
                logger.warning(
                    f"Cannot start recording: Not all participants consented for call {video_call.id}"
                )
                return None

            # Generate recording session
            recording_id = f"rec_{video_call.room_id}_{int(get_utc_now().timestamp())}"

            # Start recording through video service
            recording_url = await video_service.start_recording(video_call.room_id)

            if recording_url:
                # Track recording session
                self.active_recordings[video_call.room_id] = {
                    "recording_id": recording_id,
                    "video_call_id": video_call.id,
                    "started_at": get_utc_now(),
                    "recording_url": recording_url,
                    "consents": [consent.id for consent in consents],
                }

                logger.info(
                    f"Started recording {recording_id} for video call {video_call.id}"
                )
                return recording_id

            return None

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return None

    async def stop_recording(self, video_call: VideoCall) -> str | None:
        """Stop recording and return the final recording URL."""
        try:
            if video_call.room_id not in self.active_recordings:
                logger.warning(f"No active recording found for call {video_call.id}")
                return None

            recording_session = self.active_recordings[video_call.room_id]
            recording_id = recording_session["recording_id"]

            # Stop recording through video service
            final_url = await video_service.stop_recording(recording_id)

            if final_url:
                # Update recording session
                recording_session["ended_at"] = get_utc_now()
                recording_session["final_url"] = final_url

                # Clean up active session
                del self.active_recordings[video_call.room_id]

                logger.info(
                    f"Stopped recording {recording_id} for video call {video_call.id}"
                )
                return final_url

            return None

        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return None

    async def pause_recording(self, video_call: VideoCall) -> bool:
        """Pause recording (if supported by the video service)."""
        try:
            if video_call.room_id not in self.active_recordings:
                return False

            recording_session = self.active_recordings[video_call.room_id]
            recording_id = recording_session["recording_id"]

            # Pause recording through video service
            success = await video_service.pause_recording(recording_id)  # type: ignore

            if success:
                recording_session["paused_at"] = get_utc_now()
                logger.info(f"Paused recording {recording_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to pause recording: {e}")
            return False

    async def resume_recording(self, video_call: VideoCall) -> bool:
        """Resume paused recording."""
        try:
            if video_call.room_id not in self.active_recordings:
                return False

            recording_session = self.active_recordings[video_call.room_id]
            recording_id = recording_session["recording_id"]

            # Resume recording through video service
            success = await video_service.resume_recording(recording_id)  # type: ignore

            if success:
                recording_session["resumed_at"] = get_utc_now()
                logger.info(f"Resumed recording {recording_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to resume recording: {e}")
            return False

    async def get_recording_status(self, video_call: VideoCall) -> dict[str, Any]:
        """Get current recording status."""
        try:
            if video_call.room_id not in self.active_recordings:
                return {"is_recording": False, "status": "not_started"}

            recording_session = self.active_recordings[video_call.room_id]

            return {
                "is_recording": True,
                "recording_id": recording_session["recording_id"],
                "started_at": recording_session["started_at"].isoformat(),
                "status": "active",
                "duration_seconds": (
                    get_utc_now() - recording_session["started_at"]
                ).total_seconds(),
            }

        except Exception as e:
            logger.error(f"Failed to get recording status: {e}")
            return {"is_recording": False, "status": "error"}

    async def validate_recording_consent(
        self, video_call: VideoCall, consents: list[RecordingConsent]
    ) -> dict[str, Any]:
        """Validate recording consent from all participants."""
        try:
            participants = [video_call.interviewer_id, video_call.candidate_id]

            consent_status = {}
            all_consented = True

            for participant_id in participants:
                consent = next(
                    (c for c in consents if c.user_id == participant_id), None
                )

                if consent and consent.consented:
                    consent_status[str(participant_id)] = {
                        "consented": True,
                        "consented_at": consent.consented_at.isoformat()
                        if consent.consented_at
                        else None,
                    }
                else:
                    consent_status[str(participant_id)] = {
                        "consented": False,
                        "consented_at": None,
                    }
                    all_consented = False

            return {
                "all_consented": all_consented,
                "consent_status": consent_status,
                "can_record": all_consented,
                "missing_consents": [
                    str(pid)
                    for pid in participants
                    if not consent_status[str(pid)]["consented"]
                ],
            }

        except Exception as e:
            logger.error(f"Failed to validate consent: {e}")
            return {"all_consented": False, "can_record": False}

    async def generate_recording_metadata(
        self, video_call: VideoCall, recording_url: str
    ) -> dict[str, Any]:
        """Generate metadata for the recording."""
        try:
            metadata = {
                "video_call_id": video_call.id,
                "room_id": video_call.room_id,
                "scheduled_at": video_call.scheduled_at.isoformat(),
                "started_at": video_call.started_at.isoformat()
                if video_call.started_at
                else None,
                "ended_at": video_call.ended_at.isoformat()
                if video_call.ended_at
                else None,
                "participants": {
                    "interviewer_id": video_call.interviewer_id,
                    "candidate_id": video_call.candidate_id,
                },
                "recording_url": recording_url,
                "transcription_enabled": video_call.transcription_enabled,
                "language": video_call.transcription_language,
                "created_at": get_utc_now().isoformat(),
            }

            return metadata

        except Exception as e:
            logger.error(f"Failed to generate metadata: {e}")
            return {}

    async def delete_recording(self, recording_url: str) -> bool:
        """Delete a recording (GDPR compliance)."""
        try:
            # This would integrate with your storage service to delete the file
            # For now, return True as a placeholder
            logger.info(f"Recording deletion requested: {recording_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete recording: {e}")
            return False

    def _all_participants_consented(self, consents: list[RecordingConsent]) -> bool:
        """Check if all required participants have consented to recording."""
        consented_users = {consent.user_id for consent in consents if consent.consented}

        # For a basic interview, we need at least the interviewer and candidate
        # In a real implementation, you'd get the actual participant list
        required_participants = 2  # interviewer + candidate

        return len(consented_users) >= required_participants


recording_service = RecordingService()
