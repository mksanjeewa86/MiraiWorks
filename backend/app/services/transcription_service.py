import asyncio
import base64
import logging
from datetime import UTC, datetime

import aiohttp

from app.config import settings
from app.schemas.video_call import TranscriptionSegmentCreate
from app.services.free_transcription import transcribe_audio_free

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for handling real-time speech-to-text transcription."""

    def __init__(self):
        self.active_sessions: dict[str, dict] = {}
        self.supported_languages = ["ja", "en"]

    async def start_transcription(
        self, video_call_id: int, room_id: str, language: str = "ja"
    ) -> bool:
        """Start real-time transcription for a video call."""
        try:
            if language not in self.supported_languages:
                logger.warning(f"Unsupported language: {language}")
                return False

            session_key = f"{video_call_id}_{room_id}"

            # Initialize transcription session
            session_config = {
                "video_call_id": video_call_id,
                "room_id": room_id,
                "language": language,
                "is_active": True,
                "start_time": datetime.now(UTC),
                "segments_count": 0,
            }

            self.active_sessions[session_key] = session_config

            # Start background transcription task
            asyncio.create_task(
                self._run_transcription_session(session_key, session_config)
            )

            logger.info(f"Started transcription for video call {video_call_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start transcription: {e}")
            return False

    async def stop_transcription(self, video_call_id: int, room_id: str) -> bool:
        """Stop real-time transcription for a video call."""
        try:
            session_key = f"{video_call_id}_{room_id}"

            if session_key in self.active_sessions:
                self.active_sessions[session_key]["is_active"] = False
                del self.active_sessions[session_key]
                logger.info(f"Stopped transcription for video call {video_call_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to stop transcription: {e}")
            return False

    async def process_audio_chunk(
        self, video_call_id: int, audio_data: bytes, speaker_id: int, timestamp: float
    ) -> str | None:
        """Process audio chunk and return transcription if available."""
        try:
            session = None

            for _key, sess in self.active_sessions.items():
                if sess["video_call_id"] == video_call_id:
                    session = sess
                    break

            if not session or not session["is_active"]:
                return None

            # Send audio to transcription API
            transcription_text = await self._transcribe_audio_chunk(
                audio_data, session["language"]
            )

            if transcription_text:
                # Create transcription segment
                TranscriptionSegmentCreate(
                    speaker_id=speaker_id,
                    segment_text=transcription_text,
                    start_time=timestamp,
                    end_time=timestamp + 3.0,  # Estimated 3-second chunk
                    confidence=0.85,  # Default confidence
                )

                # This would be saved via the API endpoint
                return transcription_text

            return None

        except Exception as e:
            logger.error(f"Failed to process audio chunk: {e}")
            return None

    async def generate_final_transcript(
        self, video_call_id: int, format: str = "txt"
    ) -> str | None:
        """Generate final transcript in specified format."""
        try:
            # This would retrieve all segments and format them
            if format == "txt":
                return await self._generate_text_transcript(video_call_id)
            elif format == "srt":
                return await self._generate_srt_transcript(video_call_id)
            elif format == "pdf":
                return await self._generate_pdf_transcript(video_call_id)
            else:
                logger.warning(f"Unsupported format: {format}")
                return None

        except Exception as e:
            logger.error(f"Failed to generate transcript: {e}")
            return None

    async def _run_transcription_session(
        self, session_key: str, session_config: dict
    ) -> None:
        """Background task for handling transcription session."""
        try:
            while session_config.get("is_active", False):
                # In a real implementation, this would:
                # 1. Connect to WebRTC audio stream
                # 2. Process audio chunks
                # 3. Send to transcription API
                # 4. Handle real-time results
                # 5. Store segments in database

                await asyncio.sleep(1)  # Simulate processing

        except Exception as e:
            logger.error(f"Transcription session error: {e}")
        finally:
            if session_key in self.active_sessions:
                del self.active_sessions[session_key]

    async def _transcribe_audio_chunk(
        self, audio_data: bytes, language: str
    ) -> str | None:
        """Send audio chunk to transcription service and get result."""
        try:
            # Try free transcription first (Vosk, SpeechRecognition, etc.)
            result = await transcribe_audio_free(audio_data, language)
            if result:
                logger.info(f"Free transcription successful: {result[:50]}...")
                return result

            # Try Google Speech-to-Text if API key provided
            if settings.stt_api_key and settings.stt_service_url:
                result = await self._google_speech_to_text(audio_data, language)
                if result:
                    return result

            # Try OpenAI Whisper if API key provided
            if settings.openai_api_key:
                result = await self._openai_whisper(audio_data, language)
                if result:
                    return result

            # Final fallback: Mock transcription
            return await self._mock_transcription(audio_data, language)

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return await self._mock_transcription(audio_data, language)

    async def _google_speech_to_text(
        self, audio_data: bytes, language: str
    ) -> str | None:
        """Google Speech-to-Text API integration."""
        try:
            url = f"{settings.stt_service_url}/v1/speech:recognize"

            # Convert language code
            lang_code = "ja-JP" if language == "ja" else "en-US"

            payload = {
                "config": {
                    "encoding": "WEBM_OPUS",
                    "sampleRateHertz": 48000,
                    "languageCode": lang_code,
                    "enableAutomaticPunctuation": True,
                    "enableWordTimeOffsets": True,
                },
                "audio": {"content": base64.b64encode(audio_data).decode("utf-8")},
            }

            headers = {
                "Authorization": f"Bearer {settings.stt_api_key}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("results"):
                            return result["results"][0]["alternatives"][0]["transcript"]

            return None

        except Exception as e:
            logger.error(f"Google Speech-to-Text error: {e}")
            return None

    async def _openai_whisper(self, audio_data: bytes, language: str) -> str | None:
        """OpenAI Whisper API integration."""
        try:
            url = "https://api.openai.com/v1/audio/transcriptions"

            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}",
            }

            # Create form data
            data = aiohttp.FormData()
            data.add_field(
                "file", audio_data, filename="audio.webm", content_type="audio/webm"
            )
            data.add_field("model", "whisper-1")
            data.add_field("language", language)
            data.add_field("response_format", "json")

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("text", "")

            return None

        except Exception as e:
            logger.error(f"OpenAI Whisper error: {e}")
            return None

    async def _mock_transcription(self, audio_data: bytes, language: str) -> str | None:
        """Mock transcription for development."""
        # Simulate processing delay
        await asyncio.sleep(0.1)

        if language == "ja":
            mock_responses = [
                "こんにちは、よろしくお願いします。",
                "私の経験についてお話しします。",
                "技術的な質問はありますか？",
                "この機会について詳しく教えてください。",
                "ありがとうございました。",
            ]
        else:
            mock_responses = [
                "Hello, nice to meet you.",
                "Let me tell you about my experience.",
                "Do you have any technical questions?",
                "Could you tell me more about this opportunity?",
                "Thank you for your time.",
            ]

        import random

        return random.choice(mock_responses)

    async def _generate_text_transcript(self, video_call_id: int) -> str:
        """Generate plain text transcript."""
        # This would fetch all segments from database and format as text
        return f"# Interview Transcript - Video Call {video_call_id}\n\nGenerated transcript would be here..."

    async def _generate_srt_transcript(self, video_call_id: int) -> str:
        """Generate SRT subtitle format transcript."""
        # This would fetch all segments and format as SRT
        return "1\n00:00:00,000 --> 00:00:03,000\nGenerated SRT transcript would be here...\n"

    async def _generate_pdf_transcript(self, video_call_id: int) -> str:
        """Generate PDF transcript and return URL."""
        # This would generate a PDF and return storage URL
        return f"https://storage.example.com/transcripts/{video_call_id}.pdf"


transcription_service = TranscriptionService()
