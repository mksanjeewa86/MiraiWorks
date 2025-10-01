# 📝 MiraiWorks Exam System (適性検査システム)

**Last Updated**: October 2025


A comprehensive recruitment exam system with advanced security features, real-time monitoring, and flexible question types.

## 🎯 Features

### **For Employers**
- **Exam Creation & Management** - Create custom exams with multiple question types
- **Organization-wise Questions** - Company-specific question banks
- **Security Monitoring** - Web usage tracking and face verification
- **Real-time Analytics** - Comprehensive statistics and reporting
- **Result Control** - Configure what candidates can see
- **Test Mode** - Preview exams before deployment

### **For Candidates**
- **Intuitive Interface** - Easy-to-use exam taking experience
- **Real-time Timer** - Clear time management with warnings
- **Auto-save** - Answers saved automatically
- **Practice Mode** - Demo exams to familiarize with the system
- **Detailed Results** - Question-by-question breakdown (if enabled)

### **Security Features**
- **Web Usage Monitoring** - Track tab switching and focus changes
- **Face Recognition** - Periodic identity verification
- **Fullscreen Mode** - Secure exam environment
- **Session Tracking** - Comprehensive event logging
- **Anti-cheating** - Multiple security measures

## 🚀 Quick Start

### 1. Database Setup
```bash
# Run database migrations
cd backend
PYTHONPATH=. python3 -m alembic upgrade head
```

### 2. Create Sample Data
```bash
# Create sample exams and questions
cd backend
make seed-exam-data
```

### 3. Access the System
- **Admin Dashboard**: `/admin/exams`
- **Candidate Portal**: `/exams`
- **Demo Exams**: `/exams/demo`

## 📋 Sample Exams Created

The seed script creates 4 comprehensive sample exams:

### 1. 適性検査 - 総合能力評価 (Aptitude Test)
- **Type**: Aptitude Assessment  
- **Duration**: 45 minutes
- **Questions**: 8 comprehensive questions
- **Features**: Face verification, web monitoring, randomized order
- **Content**: Logical reasoning, numerical analysis, language comprehension

**Question Types Included:**
- Number sequence analysis
- Logical deduction problems
- Percentage calculations
- Reading comprehension
- Geometry problems
- Essay responses on problem-solving
- Multiple choice reasoning
- Rating scale assessments

### 2. プログラミングスキル評価テスト (Programming Skill Test)
- **Type**: Technical Skill Assessment
- **Duration**: 60 minutes  
- **Questions**: 6 technical questions
- **Features**: Web usage allowed, detailed explanations
- **Content**: JavaScript, Python, algorithms, system design

**Question Types Included:**
- JavaScript typeof behavior
- Python list comprehensions
- Algorithm complexity analysis
- RESTful API design principles
- System design scenarios
- Git workflow best practices

### 3. 性格・行動特性評価 (Personality Assessment)
- **Type**: Behavioral Assessment
- **Duration**: 25 minutes
- **Questions**: 10 personality questions
- **Features**: No time pressure, no correct answers
- **Content**: Work style, teamwork, stress management, communication

**Assessment Areas:**
- Leadership preferences
- Learning orientation
- Stress coping strategies
- Decision-making style
- Communication skills
- Adaptability to change
- Motivation factors
- Feedback receptiveness

### 4. デモ試験 - システム体験用 (Demo Exam)
- **Type**: System Demonstration
- **Duration**: 15 minutes
- **Questions**: 5 sample questions
- **Features**: Multiple attempts, immediate results
- **Content**: System tutorial and feature demonstration

## 🔧 Configuration Options

### Exam Settings
- **Time Limits**: Configurable per exam and per question
- **Attempt Limits**: Control how many times candidates can take the exam
- **Passing Score**: Set minimum score requirements
- **Question Order**: Fixed or randomized
- **Result Visibility**: Control what candidates see after completion

### Security Settings
- **Web Usage**: Allow/block tab switching and web browsing
- **Web Monitoring**: Track and log web usage events
- **Face Verification**: Periodic identity checks with camera
- **Face Check Interval**: Configure frequency of face verification

### Display Settings
- **Show Results**: Immediate or manual release
- **Show Correct Answers**: Include explanations and correct responses
- **Show Score**: Display numerical scores and percentages

## 📊 Question Types Supported

### 1. Single Choice
- Radio button selection
- One correct answer
- Automatic grading

### 2. Multiple Choice  
- Checkbox selection
- Multiple correct answers
- Automatic grading

### 3. True/False
- Binary choice questions
- Quick assessment format
- Automatic grading

### 4. Text Input
- Short text responses
- Character limits configurable
- Manual or automatic grading

### 5. Essay
- Long-form responses
- Word count requirements
- Manual grading required

### 6. Rating Scale
- Slider-based responses
- Configurable scale (1-3, 1-5, 1-7, 1-10)
- Subjective assessments

## 🛡️ Security Features

### Web Usage Monitoring
- **Tab Switching Detection** - Alert when candidates switch tabs
- **Window Focus Tracking** - Monitor when exam window loses focus
- **Keyboard Shortcuts** - Block common shortcuts (Ctrl+T, Alt+Tab, etc.)
- **Right-click Disable** - Prevent context menu access
- **Print Prevention** - Block printing attempts
- **Copy/Paste Tracking** - Monitor clipboard usage

### Face Recognition System
- **Initial Verification** - Confirm identity at exam start
- **Periodic Checks** - Regular identity verification during exam
- **Automatic Capture** - Photo taken at configured intervals
- **Suspicious Activity** - Additional photos when issues detected
- **Manual Review** - Flag sessions requiring human verification

### Session Security
- **IP Address Logging** - Track candidate location
- **Browser Fingerprinting** - Record user agent and screen resolution
- **Session Monitoring** - Comprehensive event logging
- **Time Tracking** - Monitor time spent per question
- **Automatic Submission** - Prevent overtime attempts

## 📈 Analytics & Reporting

### Exam Statistics
- **Completion Rates** - Track how many candidates complete exams
- **Average Scores** - Calculate mean performance across candidates
- **Time Analysis** - Monitor time spent on exams and questions
- **Pass/Fail Rates** - Measure success rates against passing scores

### Question Analysis
- **Difficulty Assessment** - Identify challenging questions
- **Response Patterns** - Analyze common answer choices
- **Time Per Question** - Optimize question complexity
- **Success Rates** - Track question-level performance

### Security Reports
- **Monitoring Events** - Detailed security incident logs
- **Violation Tracking** - Monitor policy violations
- **Risk Assessment** - Identify high-risk sessions
- **Compliance Reports** - Generate audit trails

## 🧪 Testing the System

### For Employers
1. **Login as Admin** - Access the admin dashboard
2. **View Sample Exams** - Explore created exam content
3. **Preview Mode** - Use exam preview to test interface
4. **Test Mode** - Take exams in test mode (doesn't count)
5. **Review Analytics** - Check statistics and reports

### For Candidates  
1. **Demo Exams** - Start with practice exams at `/exams/demo`
2. **Assigned Exams** - Check for actual assignments at `/exams`
3. **Test Features** - Experience monitoring and security features
4. **View Results** - See detailed results (if enabled)

## 💻 Technical Architecture

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM with async support
- **PostgreSQL** - Primary database
- **Redis** - Session storage and caching
- **Alembic** - Database migrations

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Shadcn/ui** - Component library

### Security
- **JWT Authentication** - Secure API access
- **Role-based Access** - Granular permissions
- **CORS Protection** - Cross-origin request security
- **Input Validation** - Comprehensive data validation

## 🔄 Development Workflow

### Running the Seed Script
```bash
# Method 1: Using Make
cd backend
make seed-exam-data

# Method 2: Direct Python
cd backend
PYTHONPATH=. python scripts/run_seed.py

# Method 3: Using the runner
cd backend
python scripts/run_seed.py
```

### Customizing Sample Data
Edit `backend/scripts/seed_exam_data.py` to:
- Add more exam types
- Modify question content
- Adjust exam settings
- Include additional test data

### Database Management
```bash
# Create new migration
PYTHONPATH=. python3 -m alembic revision --autogenerate -m "Description"

# Apply migrations
PYTHONPATH=. python3 -m alembic upgrade head

# Check migration status
PYTHONPATH=. python3 -m alembic current
```

## 📚 API Documentation

### Key Endpoints
- `GET /api/exam/exams` - List company exams
- `POST /api/exam/exams` - Create new exam
- `POST /api/exam/exams/take` - Start exam session
- `POST /api/exam/sessions/{id}/answers` - Submit answers
- `GET /api/exam/sessions/{id}/results` - Get exam results

### Authentication
All API endpoints require JWT authentication:
```bash
curl -H "Authorization: Bearer <token>" https://api.example.com/api/exam/exams
```

## 🚨 Troubleshooting

### Common Issues
1. **Database Connection** - Ensure PostgreSQL is running
2. **Redis Connection** - Verify Redis server is accessible  
3. **Migration Errors** - Check database permissions
4. **Seed Data Fails** - Ensure company and users exist
5. **Face Recognition** - Requires HTTPS in production

### Debug Mode
Set environment variables for debugging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
export ENVIRONMENT=development
```

## 🎓 Best Practices

### For Employers
- **Test First** - Always preview exams before deployment
- **Clear Instructions** - Provide detailed candidate instructions
- **Appropriate Timing** - Set realistic time limits
- **Fair Assessment** - Ensure questions match job requirements
- **Privacy Compliance** - Follow data protection regulations

### For System Administrators
- **Regular Backups** - Backup exam data and results
- **Security Updates** - Keep system dependencies updated
- **Performance Monitoring** - Monitor system performance during exams
- **Capacity Planning** - Ensure adequate resources for concurrent users

---

## 📞 Support

For technical issues or questions about the exam system:

1. **Check Documentation** - Review this README and code comments
2. **Search Issues** - Look for similar problems in the issue tracker
3. **Create Ticket** - Submit detailed bug reports or feature requests
4. **Contact Admin** - Reach out to system administrators

---

**Built with ❤️ for modern recruitment processes**
