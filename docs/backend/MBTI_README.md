# MBTI Personality Test Feature

**Last Updated**: October 2025


## Overview
The MBTI (Myers-Briggs Type Indicator) personality test feature allows candidates to take a comprehensive 60-question assessment to determine their personality type. Results are displayed in their profile with custom artwork for each type.

## 🎯 Features
- **60 Comprehensive Questions** - 15 questions per dimension (E/I, S/N, T/F, J/P)
- **Bilingual Support** - Full English and Japanese translations
- **16 Personality Types** - Complete MBTI type system
- **Custom Avatars** - Unique SVG artwork for each personality type
- **Progress Tracking** - Resume incomplete tests
- **Profile Integration** - Results displayed prominently in candidate profiles

## 🏗️ Architecture

### Backend Components
- **Models**: `MBTITest`, `MBTIQuestion`
- **Schemas**: Request/response validation with Pydantic
- **CRUD**: Database operations with scoring logic
- **Endpoints**: RESTful API for test lifecycle
- **Services**: Business logic for scoring and type determination

### Frontend Components
- **MBTITestButton**: Start/continue test button with progress
- **MBTITestModal**: Full test interface with navigation
- **MBTIResultCard**: Display results with dimension scores
- **MBTITypeAvatar**: Custom SVG icons for each type

## 🚀 Setup Instructions

### 1. Database Migration
```bash
cd backend
alembic upgrade head  # This will create the MBTI tables
```

### 2. Seed Questions Database
```bash
cd backend
python scripts/setup_mbti.py
```

Or manually run the seed:
```bash
cd backend
python app/seeds/mbti_questions_seed.py
```

### 3. Verify Setup
The setup script will:
- ✅ Create `mbti_tests` and `mbti_questions` tables
- ✅ Populate 60 questions in both languages
- ✅ Set up proper indexes for performance

## 📊 MBTI Types & Colors

### Analysts (NT) - Purple
- **INTJ** - The Architect (建築家)
- **INTP** - The Thinker (論理学者)
- **ENTJ** - The Commander (指揮官)
- **ENTP** - The Debater (討論者)

### Diplomats (NF) - Green
- **INFJ** - The Advocate (提唱者)
- **INFP** - The Mediator (仲介者)
- **ENFJ** - The Protagonist (主人公)
- **ENFP** - The Campaigner (運動家)

### Sentinels (SJ) - Blue
- **ISTJ** - The Logistician (管理者)
- **ISFJ** - The Defender (擁護者)
- **ESTJ** - The Executive (幹部)
- **ESFJ** - The Consul (領事)

### Explorers (SP) - Orange
- **ISTP** - The Virtuoso (巨匠)
- **ISFP** - The Adventurer (冒険家)
- **ESTP** - The Entrepreneur (起業家)
- **ESFP** - The Entertainer (エンターテイナー)

## 🔄 API Endpoints

### Test Lifecycle
- `POST /api/mbti/start` - Start a new test
- `GET /api/mbti/questions` - Get all questions
- `POST /api/mbti/answer` - Submit single answer
- `POST /api/mbti/submit` - Complete the test
- `GET /api/mbti/progress` - Get current progress

### Results
- `GET /api/mbti/result` - Get detailed test results
- `GET /api/mbti/summary` - Get formatted summary with type info

### Type Information
- `GET /api/mbti/types` - Get all 16 types
- `GET /api/mbti/types/{type}` - Get specific type details

## 💡 Usage Examples

### Taking the Test
1. User clicks "MBTI診断を開始" button in dashboard
2. Modal opens with language selection (JP/EN)
3. User answers 60 questions with A/B choices
4. Progress is tracked and can be resumed
5. Results are calculated and displayed

### Viewing Results
- Dashboard shows MBTI card with type and avatar
- Profile page displays detailed breakdown
- Dimension scores shown as progress bars
- Custom avatar represents personality type

## 🎨 Custom Avatars
Each MBTI type has a unique SVG icon:
- **Geometric shapes** representing type characteristics
- **Color-coded** by temperament group
- **Scalable** for different display sizes
- **Accessible** with proper labels

## 📱 Mobile Responsive
- Touch-friendly test interface
- Optimized avatar sizes for mobile
- Responsive grid layouts for results

## 🌐 Internationalization
- Question text in English and Japanese
- Type names and descriptions translated
- UI labels support both languages
- Language can be switched during test

## 🔒 Data Privacy
- Test results stored securely per user
- Only candidates can take the test (role-based)
- Results visible in own profile
- Option to make results public/private (future)

## 🧪 Testing
Run the test suite to verify MBTI functionality:
```bash
cd backend
PYTHONPATH=. python -m pytest app/tests/test_mbti.py -v
```

## 🔧 Configuration
- Default language: Japanese (`ja`)
- Test timeout: None (can be resumed)
- Questions per dimension: 15
- Total questions: 60

## 📈 Scoring Algorithm
1. **Dimension Calculation**: Count A vs B answers per dimension
2. **Percentage Scores**: Convert to strength percentages
3. **Type Determination**: Combine dominant preferences
4. **Validation**: Ensure consistent results

## 🚦 Status
- ✅ Backend implementation complete
- ✅ Frontend components ready
- ✅ Database schema created
- ✅ Question database seeded
- ✅ Integration with dashboard/profile
- ✅ Custom avatars implemented

## 🔄 Next Steps (Future Enhancements)
- [ ] Detailed career suggestions based on type
- [ ] Team compatibility analysis
- [ ] Historical test result comparison
- [ ] Export results as PDF
- [ ] Social sharing of personality type

---

*Last updated: 2025-09-22*
*Feature ready for production use!* 🎉
