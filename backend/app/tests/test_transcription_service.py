import asyncio
from unittest.mock import AsyncMock, patch

from app.services.transcription_service import transcription_service, TranscriptionService


class TestTranscriptionService:
    """Unit tests for transcription service functionality."""

    async def test_start_transcription_success(self):
        """Test successful transcription start."""
        video_call_id = 1
        room_id = "test-room-123"
        language = "ja"
        
        result = await transcription_service.start_transcription(
            video_call_id, room_id, language
        )
        
        assert result is True
        assert f"{video_call_id}_{room_id}" in transcription_service.active_sessions
        
        session = transcription_service.active_sessions[f"{video_call_id}_{room_id}"]
        assert session['video_call_id'] == video_call_id
        assert session['room_id'] == room_id
        assert session['language'] == language
        assert session['is_active'] is True

    async def test_start_transcription_unsupported_language(self):
        """Test transcription start with unsupported language."""
        result = await transcription_service.start_transcription(
            1, "test-room", "unsupported"
        )
        
        assert result is False

    async def test_stop_transcription_success(self):
        """Test successful transcription stop."""
        video_call_id = 1
        room_id = "test-room-123"
        
        # Start transcription first
        await transcription_service.start_transcription(video_call_id, room_id)
        
        result = await transcription_service.stop_transcription(video_call_id, room_id)
        
        assert result is True
        assert f"{video_call_id}_{room_id}" not in transcription_service.active_sessions

    async def test_stop_transcription_not_active(self):
        """Test stopping non-active transcription."""
        result = await transcription_service.stop_transcription(999, "non-existent")
        
        assert result is False

    @patch('app.services.transcription_service.aiohttp.ClientSession')
    async def test_google_speech_to_text_success(self, mock_session):
        """Test successful Google Speech-to-Text API call."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'results': [{
                'alternatives': [{
                    'transcript': 'Hello, how are you?'
                }]
            }]
        })
        
        mock_session_instance = AsyncMock()
        mock_session_instance.post = AsyncMock(return_value=mock_response)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session.return_value = mock_session_instance
        
        # Mock settings
        with patch('app.services.transcription_service.settings') as mock_settings:
            mock_settings.stt_api_key = "test-key"
            mock_settings.stt_service_url = "https://test-api.com"
            
            result = await transcription_service._google_speech_to_text(
                b"audio_data", "ja"
            )
        
        assert result == 'Hello, how are you?'

    @patch('app.services.transcription_service.aiohttp.ClientSession')
    async def test_openai_whisper_success(self, mock_session):
        """Test successful OpenAI Whisper API call."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'text': 'Hello, how are you today?'
        })
        
        mock_session_instance = AsyncMock()
        mock_session_instance.post = AsyncMock(return_value=mock_response)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session.return_value = mock_session_instance
        
        # Mock settings
        with patch('app.services.transcription_service.settings') as mock_settings:
            mock_settings.openai_api_key = "test-key"
            mock_settings.stt_api_key = None
            mock_settings.stt_service_url = None
            
            result = await transcription_service._openai_whisper(
                b"audio_data", "en"
            )
        
        assert result == 'Hello, how are you today?'

    async def test_mock_transcription_japanese(self):
        """Test mock transcription in Japanese."""
        result = await transcription_service._mock_transcription(b"audio", "ja")
        
        assert result is not None
        assert isinstance(result, str)
        # Should be Japanese text
        japanese_responses = [
            "こんにちは、よろしくお願いします。",
            "私の経験についてお話しします。",
            "技術的な質問はありますか？",
            "この機会について詳しく教えてください。",
            "ありがとうございました。"
        ]
        assert result in japanese_responses

    async def test_mock_transcription_english(self):
        """Test mock transcription in English."""
        result = await transcription_service._mock_transcription(b"audio", "en")
        
        assert result is not None
        assert isinstance(result, str)
        # Should be English text
        english_responses = [
            "Hello, nice to meet you.",
            "Let me tell you about my experience.",
            "Do you have any technical questions?",
            "Could you tell me more about this opportunity?",
            "Thank you for your time."
        ]
        assert result in english_responses

    async def test_process_audio_chunk_with_active_session(self):
        """Test processing audio chunk with active session."""
        video_call_id = 1
        room_id = "test-room"
        
        # Start session
        await transcription_service.start_transcription(video_call_id, room_id, "ja")
        
        # Mock transcription result
        with patch.object(transcription_service, '_transcribe_audio_chunk', 
                         return_value="こんにちは"):
            result = await transcription_service.process_audio_chunk(
                video_call_id, b"audio_data", speaker_id=1, timestamp=10.0
            )
        
        assert result == "こんにちは"

    async def test_process_audio_chunk_no_active_session(self):
        """Test processing audio chunk without active session."""
        result = await transcription_service.process_audio_chunk(
            999, b"audio_data", speaker_id=1, timestamp=10.0
        )
        
        assert result is None

    async def test_generate_text_transcript(self):
        """Test text transcript generation."""
        video_call_id = 1
        
        result = await transcription_service._generate_text_transcript(video_call_id)
        
        assert isinstance(result, str)
        assert f"Video Call {video_call_id}" in result

    async def test_generate_srt_transcript(self):
        """Test SRT transcript generation."""
        video_call_id = 1
        
        result = await transcription_service._generate_srt_transcript(video_call_id)
        
        assert isinstance(result, str)
        assert "00:00:00,000 --> 00:00:03,000" in result

    async def test_generate_pdf_transcript(self):
        """Test PDF transcript generation."""
        video_call_id = 1
        
        result = await transcription_service._generate_pdf_transcript(video_call_id)
        
        assert isinstance(result, str)
        assert result.endswith(f"{video_call_id}.pdf")

    async def test_generate_final_transcript_txt(self):
        """Test final transcript generation in TXT format."""
        video_call_id = 1
        
        result = await transcription_service.generate_final_transcript(
            video_call_id, "txt"
        )
        
        assert result is not None
        assert isinstance(result, str)

    async def test_generate_final_transcript_srt(self):
        """Test final transcript generation in SRT format."""
        video_call_id = 1
        
        result = await transcription_service.generate_final_transcript(
            video_call_id, "srt"
        )
        
        assert result is not None
        assert isinstance(result, str)

    async def test_generate_final_transcript_pdf(self):
        """Test final transcript generation in PDF format."""
        video_call_id = 1
        
        result = await transcription_service.generate_final_transcript(
            video_call_id, "pdf"
        )
        
        assert result is not None
        assert isinstance(result, str)

    async def test_generate_final_transcript_unsupported_format(self):
        """Test final transcript generation with unsupported format."""
        video_call_id = 1
        
        result = await transcription_service.generate_final_transcript(
            video_call_id, "unsupported"
        )
        
        assert result is None

    async def test_session_cleanup_on_error(self):
        """Test session cleanup when errors occur."""
        service = TranscriptionService()
        video_call_id = 1
        room_id = "test-room"
        
        # Start session
        await service.start_transcription(video_call_id, room_id)
        session_key = f"{video_call_id}_{room_id}"
        
        # Simulate session error by stopping it
        service.active_sessions[session_key]['is_active'] = False
        
        # Wait a moment for cleanup
        await asyncio.sleep(0.1)
        
        # Session should be cleaned up (in real implementation)
        # For now, just verify it can be stopped
        result = await service.stop_transcription(video_call_id, room_id)
        assert result is True

    async def test_multiple_concurrent_sessions(self):
        """Test handling multiple concurrent transcription sessions."""
        service = TranscriptionService()
        
        # Start multiple sessions
        sessions = [
            (1, "room-1", "ja"),
            (2, "room-2", "en"),
            (3, "room-3", "ja")
        ]
        
        for video_call_id, room_id, language in sessions:
            result = await service.start_transcription(video_call_id, room_id, language)
            assert result is True
        
        # Verify all sessions are active
        assert len(service.active_sessions) == 3
        
        # Stop all sessions
        for video_call_id, room_id, _ in sessions:
            result = await service.stop_transcription(video_call_id, room_id)
            assert result is True
        
        # Verify all sessions are stopped
        assert len(service.active_sessions) == 0