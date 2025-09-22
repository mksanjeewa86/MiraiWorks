# Video Call Feature Plan for Interviews

## Overview
This document outlines the implementation plan for adding video call functionality to MiraiWorks, specifically designed for conducting remote interviews between recruiters/employers and candidates.

---

## 🎯 Feature Requirements

### Core Functionality
- One-on-one video calls between interviewer and candidate
- Screen sharing capability for technical interviews
- In-call chat for sharing links/code snippets
- Call recording with consent management
- Real-time transcription and post-call transcript generation
- Interview scheduling integration
- Call quality monitoring and fallback options

### User Roles
- **Interviewer**: Recruiter or hiring manager initiating the call
- **Candidate**: Job applicant joining the scheduled interview

---

## 🏗️ Backend Implementation Plan

### 1. Database Schema Updates

#### New Tables
```sql
-- Video call sessions
CREATE TABLE video_calls (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    interviewer_id INTEGER REFERENCES users(id),
    candidate_id INTEGER REFERENCES users(id),
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(20), -- scheduled, in_progress, completed, cancelled
    room_id VARCHAR(255) UNIQUE,
    recording_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Call participants tracking
CREATE TABLE call_participants (
    id SERIAL PRIMARY KEY,
    video_call_id INTEGER REFERENCES video_calls(id),
    user_id INTEGER REFERENCES users(id),
    joined_at TIMESTAMP,
    left_at TIMESTAMP,
    connection_quality VARCHAR(20), -- excellent, good, fair, poor
    device_info JSONB
);

-- Recording consent
CREATE TABLE recording_consents (
    id SERIAL PRIMARY KEY,
    video_call_id INTEGER REFERENCES video_calls(id),
    user_id INTEGER REFERENCES users(id),
    consented BOOLEAN DEFAULT FALSE,
    consented_at TIMESTAMP
);

-- Transcription data
CREATE TABLE call_transcriptions (
    id SERIAL PRIMARY KEY,
    video_call_id INTEGER REFERENCES video_calls(id),
    transcript_url VARCHAR(255),
    transcript_text TEXT,
    language VARCHAR(10) DEFAULT 'ja',
    processing_status VARCHAR(20), -- pending, processing, completed, failed
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Real-time transcription segments
CREATE TABLE transcription_segments (
    id SERIAL PRIMARY KEY,
    video_call_id INTEGER REFERENCES video_calls(id),
    speaker_id INTEGER REFERENCES users(id),
    segment_text TEXT,
    start_time FLOAT,
    end_time FLOAT,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. API Endpoints (Following MiraiWorks Architecture)

#### `app/schemas/video_call.py`
```python
from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class VideoCallStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ConnectionQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class TranscriptionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoCallCreate(BaseModel):
    job_id: int
    candidate_id: int
    scheduled_at: datetime
    enable_transcription: bool = True

class VideoCallInfo(BaseModel):
    id: int
    room_id: str
    status: VideoCallStatus
    scheduled_at: datetime
    transcription_enabled: bool
    # ... other fields

class TranscriptionSegment(BaseModel):
    speaker_id: int
    segment_text: str
    start_time: float
    end_time: float
    confidence: float
```

#### `app/crud/video_call.py`
```python
# CRUD operations for video calls
- create_video_call()
- get_video_call_by_room_id()
- update_call_status()
- get_user_video_calls()
- save_transcription_segment()
- get_call_transcription()
- update_transcription_status()
```

#### `app/endpoints/video_calls.py`
```python
# POST /api/video-calls/schedule - Schedule interview call
# GET /api/video-calls/{call_id} - Get call details
# POST /api/video-calls/{call_id}/join - Join video call
# POST /api/video-calls/{call_id}/end - End video call
# POST /api/video-calls/{call_id}/consent - Record consent
# GET /api/video-calls/{call_id}/token - Get WebRTC token
# GET /api/video-calls/{call_id}/transcript - Get call transcript
# POST /api/video-calls/{call_id}/transcript/segments - Save real-time segment
# GET /api/video-calls/{call_id}/transcript/download - Download transcript file
```

### 3. WebRTC Integration Service

#### `app/services/video_service.py`
- WebRTC signaling server integration (using Socket.IO)
- STUN/TURN server configuration
- Room management
- Token generation for secure connections
- Recording service integration
- Real-time transcription streaming

#### `app/services/transcription_service.py`
- Speech-to-text integration (Google Speech-to-Text, AWS Transcribe, or Azure)
- Real-time audio stream processing
- Language detection and support (Japanese/English)
- Speaker diarization (identify who is speaking)
- Post-processing for accuracy improvement
- Transcript formatting and export

#### Technology Stack
- **WebRTC Library**: Consider Twilio Video, Daily.co, or Agora SDK
- **Signaling**: Socket.IO with Redis adapter
- **TURN Server**: Coturn or cloud provider solution
- **Recording**: Cloud storage integration (S3/GCS)
- **Transcription**: Google Speech-to-Text API, AWS Transcribe, or Azure Speech Services
- **Audio Processing**: WebRTC audio processing pipeline

### 4. Notification Service Updates

#### `app/services/notification_service.py`
- Interview reminder emails (24h, 1h before)
- Call link sharing
- Post-interview follow-up
- Technical issue alerts

---

## 💻 Frontend Implementation Plan

### 1. Video Call UI Components

#### Core Components
```
src/components/video/
├── VideoCallRoom.tsx        # Main video call container
├── VideoControls.tsx        # Mute/unmute, camera on/off
├── ParticipantVideo.tsx     # Individual video feed
├── ScreenShare.tsx          # Screen sharing view
├── ChatPanel.tsx            # In-call messaging
├── ConnectionStatus.tsx     # Network quality indicator
├── RecordingConsent.tsx     # Consent modal
├── TranscriptionPanel.tsx   # Real-time transcript display
├── TranscriptDownload.tsx   # Export transcript options
└── LanguageSelector.tsx     # Japanese/English toggle
```

#### Features to Implement
- Grid/Speaker view toggle
- Picture-in-picture mode
- Virtual backgrounds (optional)
- Noise suppression controls
- Bandwidth adaptation
- Real-time transcription display with speaker labels
- Transcription search and highlight
- Export transcript in multiple formats (TXT, PDF, SRT)

### 2. Interview Scheduling Integration

#### Components
```
src/components/interview/
├── ScheduleInterview.tsx    # Calendar integration
├── InterviewDetails.tsx     # Call details & join button
├── InterviewList.tsx        # Upcoming interviews
└── InterviewReminder.tsx    # Notification component
```

### 3. State Management

#### Redux Slices
```typescript
// videoCallSlice.ts
interface VideoCallState {
    currentCall: VideoCall | null
    participants: Participant[]
    connectionQuality: ConnectionQuality
    isRecording: boolean
    isMuted: boolean
    isVideoOn: boolean
    isScreenSharing: boolean
    messages: ChatMessage[]
    transcriptionEnabled: boolean
    transcriptionLanguage: 'ja' | 'en'
    transcriptionSegments: TranscriptionSegment[]
}

// Actions
- joinCall
- leaveCall
- toggleAudio
- toggleVideo
- startScreenShare
- sendMessage
- toggleTranscription
- addTranscriptionSegment
- setTranscriptionLanguage

// transcriptionSlice.ts
interface TranscriptionState {
    segments: TranscriptionSegment[]
    isProcessing: boolean
    currentSpeaker: number | null
    searchQuery: string
    highlightedSegments: number[]
}

// Actions
- addSegment
- updateSegment
- searchTranscript
- highlightSegment
- exportTranscript
```

### 4. WebRTC Client Implementation

```typescript
// services/webrtc.service.ts
class WebRTCService {
    - initializeConnection()
    - createOffer()
    - handleAnswer()
    - addIceCandidate()
    - getLocalStream()
    - addRemoteStream()
    - handleDisconnect()
    - setupAudioProcessor()
    - startTranscriptionStream()
}

// services/transcription.service.ts
class TranscriptionService {
    - initializeTranscription()
    - processAudioStream()
    - handleTranscriptionResult()
    - switchLanguage()
    - exportTranscript()
    - searchInTranscript()
}
```

---

## 🧪 Testing Strategy

### Backend Tests

#### 1. Unit Tests (`tests/unit/`)
```python
# test_video_call_crud.py
- test_create_video_call()
- test_get_video_call_by_room_id()
- test_update_call_status()
- test_concurrent_call_limit()
- test_save_transcription_segment()
- test_get_call_transcription()

# test_video_service.py
- test_token_generation()
- test_room_creation()
- test_participant_limit()

# test_transcription_service.py
- test_audio_stream_processing()
- test_language_detection()
- test_speaker_diarization()
- test_transcript_export_formats()
- test_real_time_segment_processing()
```

#### 2. Integration Tests (`tests/integration/`)
```python
# test_video_call_endpoints.py
- test_schedule_interview_success()
- test_schedule_interview_unauthorized()
- test_join_call_valid_participant()
- test_join_call_invalid_participant()
- test_recording_consent_flow()
- test_concurrent_calls_prevention()
- test_get_transcript_success()
- test_save_transcription_segment()
- test_download_transcript_formats()
```

#### 3. End-to-End Tests
```python
# test_interview_flow.py
- test_complete_interview_workflow()
- test_missed_interview_rescheduling()
- test_technical_issue_handling()
- test_interview_with_transcription()
- test_transcript_post_processing()
```

### Frontend Tests

#### 1. Component Tests
```typescript
// VideoCallRoom.test.tsx
- renders video feeds correctly
- handles connection states
- manages device permissions
- displays transcription panel

// VideoControls.test.tsx
- toggles audio/video
- handles device switching
- shows correct control states

// TranscriptionPanel.test.tsx
- displays real-time segments
- handles language switching
- shows speaker labels
- search functionality works
```

#### 2. Integration Tests
```typescript
// videoCall.integration.test.ts
- full call flow simulation
- reconnection handling
- quality degradation scenarios
```

#### 3. E2E Tests (Cypress/Playwright)
```typescript
// interview-call.e2e.ts
- schedule and join interview
- test all call controls
- verify recording consent
- test chat functionality
- verify transcription display
- test transcript download
```

---

## 🚀 Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Database schema implementation (including transcription tables)
- [ ] Basic CRUD operations
- [ ] WebRTC service setup
- [ ] Simple 1-on-1 calling
- [ ] Audio stream capture setup

### Phase 2: Interview Features (Week 3-4)
- [ ] Scheduling integration
- [ ] Calendar UI components
- [ ] Email notifications
- [ ] Basic video call UI

### Phase 3: Advanced Features (Week 5-6)
- [ ] Screen sharing
- [ ] In-call chat
- [ ] Recording with consent
- [ ] Real-time transcription implementation
- [ ] Transcription UI components
- [ ] Connection quality monitoring

### Phase 4: Polish & Testing (Week 7-8)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Error handling & fallbacks
- [ ] Transcription accuracy tuning
- [ ] Multi-language support testing
- [ ] Documentation

---

## 🔧 Technical Considerations

### Security
- End-to-end encryption for calls
- Secure token generation
- Rate limiting on API endpoints
- Recording access control
- Transcript access permissions
- Audio stream encryption

### Performance
- Adaptive bitrate streaming
- Lazy loading of video components
- Connection pooling for signaling
- CDN for static assets
- Efficient audio buffering for transcription
- Transcript segment caching

### Scalability
- Horizontal scaling for signaling servers
- Load balancing for TURN servers
- Database connection pooling
- Caching strategy for tokens
- Transcription service auto-scaling
- Queue management for transcript processing

### Monitoring
- Call quality metrics
- Error tracking (Sentry)
- Performance monitoring
- User analytics
- Transcription accuracy metrics
- Language usage statistics

---

## 📋 Deployment Checklist

### Infrastructure Requirements
- [ ] WebRTC-compatible hosting
- [ ] TURN/STUN servers
- [ ] Redis for Socket.IO
- [ ] Storage for recordings and transcripts
- [ ] SSL certificates
- [ ] Speech-to-text API access
- [ ] Message queue for transcript processing

### Environment Variables
```env
# WebRTC Configuration
TURN_SERVER_URL=
TURN_USERNAME=
TURN_PASSWORD=
STUN_SERVER_URL=

# Video Service Provider (if using third-party)
VIDEO_API_KEY=
VIDEO_API_SECRET=

# Recording Storage
RECORDING_BUCKET=
RECORDING_CDN_URL=

# Transcription Service
TRANSCRIPTION_API_KEY=
TRANSCRIPTION_API_ENDPOINT=
TRANSCRIPTION_LANGUAGE_DEFAULT=ja
TRANSCRIPTION_CONFIDENCE_THRESHOLD=0.8
```

### Pre-deployment Testing
- [ ] Load testing with multiple concurrent calls
- [ ] Network failure simulation
- [ ] Cross-browser compatibility
- [ ] Mobile device testing
- [ ] Bandwidth constraint testing
- [ ] Transcription accuracy testing (Japanese/English)
- [ ] Audio quality impact testing
- [ ] Real-time performance benchmarking

---

## 📚 Documentation Needs

### Developer Documentation
- API endpoint documentation
- WebRTC integration guide
- State management flow
- Error handling patterns
- Transcription service integration guide
- Audio processing pipeline documentation

### User Documentation
- Interview scheduling guide
- Video call troubleshooting
- System requirements
- Best practices for interviews
- Transcription feature guide
- Language switching instructions
- Transcript export tutorials

---

## 🎯 Success Metrics

### Technical Metrics
- Call connection success rate > 95%
- Average call quality rating > 4/5
- Call setup time < 3 seconds
- Recording processing time < 5 minutes
- Transcription accuracy > 90% (Japanese)
- Transcription accuracy > 95% (English)
- Real-time transcription delay < 2 seconds

### Business Metrics
- Interview completion rate
- User satisfaction scores
- Time-to-hire reduction
- Technical issue reports < 5%
- Transcript usage rate
- Post-interview review efficiency

---

## 🚨 Risk Mitigation

### Technical Risks
- **WebRTC compatibility**: Provide fallback options
- **Network issues**: Implement reconnection logic
- **Scaling challenges**: Plan for load balancing
- **Recording storage**: Set retention policies
- **Transcription accuracy**: Multiple speech recognition providers
- **Language detection**: Manual language selection backup
- **Audio quality**: Noise suppression and enhancement

### User Experience Risks
- **Device permissions**: Clear onboarding flow
- **Connection issues**: Helpful error messages
- **Audio/video quality**: Bandwidth detection
- **Transcription errors**: Edit capability post-call
- **Speaker identification**: Manual correction option
- **Language switching**: Clear UI indicators

---

## 📅 Timeline

**Total Duration**: 8 weeks

- **Weeks 1-2**: Backend infrastructure & basic calling
- **Weeks 3-4**: Frontend UI & scheduling
- **Weeks 5-6**: Advanced features, recording & transcription
- **Weeks 7-8**: Testing, optimization & deployment

### Transcription Feature Breakdown (Week 5-6)
- **Week 5, Days 1-2**: Transcription service integration
- **Week 5, Days 3-4**: Real-time audio streaming setup
- **Week 5, Day 5**: Database and API implementation
- **Week 6, Days 1-2**: Frontend transcription components
- **Week 6, Days 3-4**: Language support and testing
- **Week 6, Day 5**: Export functionality and optimization

---

*Last updated: December 2024*
*Feature Owner: Development Team*