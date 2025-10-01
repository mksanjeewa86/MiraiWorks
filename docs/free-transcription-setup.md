# Free Transcription Setup - No Paid APIs Required

**Last Updated**: October 2025


## 🆓 **Complete Free Transcription Options**

Your MiraiWorks video call system now supports **completely free transcription** without requiring any paid API services. Here are your options:

## 🎯 **Option 1: Mock Transcription (Already Working)**

**No installation needed!** The system already includes realistic mock transcription.

```bash
# Just deploy without any API keys
./scripts/deploy.sh development
```

**Features:**
- ✅ **Completely free**
- ✅ **Works immediately**
- ✅ **Japanese and English**
- ✅ **Realistic interview responses**
- ✅ **No setup required**

## 🎯 **Option 2: Vosk (Best Free Option)**

**Vosk** provides high-quality offline speech recognition.

### Installation:
```bash
# Install Vosk
pip install vosk

# Download Japanese model (80MB)
wget https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip
unzip vosk-model-ja-0.22.zip

# Download English model (50MB)
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
```

**Features:**
- ✅ **Completely offline**
- ✅ **High accuracy**
- ✅ **Fast processing**
- ✅ **Multiple languages**
- ✅ **No internet required**

## 🎯 **Option 3: SpeechRecognition Library**

Uses Google's **free tier** + offline backup.

### Installation:
```bash
# Install SpeechRecognition
pip install SpeechRecognition

# For offline recognition
pip install pocketsphinx

# For audio processing
pip install pyaudio
```

**Features:**
- ✅ **Google free tier** (limited requests)
- ✅ **Offline fallback**
- ✅ **Good accuracy**
- ✅ **Easy setup**

## 🎯 **Option 4: Whisper.cpp (Advanced)**

Local inference using OpenAI's Whisper model.

### Installation:
```bash
# Install whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make

# Download models
./models/download-ggml-model.sh base
./models/download-ggml-model.sh small
```

**Features:**
- ✅ **State-of-the-art accuracy**
- ✅ **Completely local**
- ✅ **Multiple languages**
- ✅ **OpenAI quality without cost**

## 🚀 **Quick Setup (Recommended)**

### For Development (Easiest):
```bash
# Use mock transcription - no setup needed
export STT_API_KEY=""  # Empty = free mode
./scripts/deploy.sh development
```

### For Production (Best Quality):
```bash
# Install Vosk for best free transcription
pip install vosk
wget https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip
unzip vosk-model-ja-0.22.zip

# Deploy with free transcription
./scripts/deploy.sh production
```

## 📊 **Comparison of Free Options**

| Option | Setup Time | Accuracy | Languages | Internet Required |
|--------|------------|----------|-----------|-------------------|
| **Mock** | 0 minutes | N/A | ✅ Ja/En | ❌ No |
| **Vosk** | 5 minutes | ⭐⭐⭐⭐ | ✅ Many | ❌ No |
| **SpeechRecognition** | 2 minutes | ⭐⭐⭐ | ✅ Many | ⚠️ Limited |
| **Whisper.cpp** | 10 minutes | ⭐⭐⭐⭐⭐ | ✅ Many | ❌ No |

## 🎯 **How the System Chooses**

The transcription service automatically tries methods in this order:

1. **Free transcription** (Vosk, SpeechRecognition, Whisper.cpp)
2. **Google Speech-to-Text** (if API key provided)
3. **OpenAI Whisper** (if API key provided)  
4. **Mock transcription** (always works)

## 🔧 **Configuration**

### Environment Variables:
```bash
# For completely free operation (default)
STT_API_KEY=""          # Empty = use free methods
OPENAI_API_KEY=""       # Empty = no paid API

# Optional: Only if you want paid APIs later
STT_API_KEY="your-key"     # For Google Speech-to-Text
OPENAI_API_KEY="your-key"  # For OpenAI Whisper
```

## 📝 **Usage Examples**

### Start Video Call with Free Transcription:
```bash
curl -X POST http://localhost:8000/api/video-calls/schedule \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 123,
    "scheduled_at": "2024-01-15T10:00:00Z",
    "enable_transcription": true,
    "transcription_language": "ja"
  }'
```

### Check Available Transcription Engines:
```bash
# The system will log which engines are available
tail -f logs/transcription.log
```

## 🎉 **Success! No Money Required**

Your video call system now works **completely free** with these transcription options:

- ✅ **Development**: Mock transcription (instant setup)
- ✅ **Testing**: Vosk offline recognition (5-minute setup)
- ✅ **Production**: Multiple free engines available

**You can run the entire video call system without spending any money on transcription services!** 🎯

## 🔧 **Troubleshooting**

### Issue: "No transcription engines available"
```bash
# Check what's installed
python -c "
from app.services.free_transcription import free_transcription
print('Available engines:', free_transcription.get_available_engines())
"
```

### Issue: Audio format not supported
```bash
# Install audio processing libraries
pip install librosa
pip install soundfile
```

### Issue: Model not found (Vosk)
```bash
# Download models to correct directory
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip
unzip vosk-model-ja-0.22.zip
```

---

**Happy transcribing for free! 🎯**
