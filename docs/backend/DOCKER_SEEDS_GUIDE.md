# MiraiWorks Docker Seeds Guide

**Last Updated**: October 2025


## ✅ Seeds Successfully Applied!

The MiraiWorks database has been successfully seeded with comprehensive test data. All Docker containers are running and the backend API is healthy.

## 🚀 Quick Start

### Backend API Access

- **URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

### Database Access

- **Host**: localhost:3306
- **Database**: miraiworks
- **Username**: hrms
- **Password**: hrms

## 👥 Test User Accounts

All passwords are: `password`

### Admin User

- **Email**: admin@miraiworks.com
- **Role**: System Administrator
- **Access**: Full system access

### Recruiter User

- **Email**: recruiter@miraiworks.com
- **Role**: Senior Recruiter
- **Access**: Recruitment management

### HR Manager User

- **Email**: hr.manager@miraiworks.com
- **Role**: HR Manager
- **Access**: HR operations and employee management

### Candidate User

- **Email**: candidate@example.com
- **Role**: Job Candidate
- **Access**: Candidate portal

## 📊 Seeded Data Summary

### Core Data

- **4 Roles**: admin, hr_manager, recruiter, candidate
- **2 Companies**: MiraiWorks, TechCorp Solutions
- **4 Users**: Each with different roles and complete profiles
- **4 User Settings**: Personalized preferences for each user

### Feature Data

- **5 Todos**: Various statuses (pending, in_progress), priorities (high, medium), and visibility levels
- **5 Notifications**: Different types (system, interview, application, assessment) with read/unread status
- **10 MBTI Questions**: Sample personality test questions covering all dimensions

## 🔧 Running Seeds Again

If you need to reseed the database:

```bash
# Method 1: Main seed entry point (recommended)
docker-compose exec backend python app/seeds/seed_data.py

# Method 2: Direct docker-safe seed script
docker-compose exec backend python app/seeds/docker_safe_seed.py
```

## 🧪 Testing the System

### 1. API Health Check

```bash
curl http://localhost:8000/health
```

### 2. Login Test

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@miraiworks.com&password=password"
```

### 3. Database Verification

```bash
docker-compose exec db mysql -u hrms -phrms miraiworks -e "SHOW TABLES;"
```

## 📋 Available Features to Test

### Todo Management

- Create, update, delete todos
- Assign todos to users
- Set priorities and due dates
- Different visibility levels (private, team, company)

### Notification System

- System notifications
- Interview notifications
- Application status updates
- Assessment assignments

### User Management

- User authentication
- Role-based access control
- User settings and preferences
- Company profiles

### MBTI Personality Testing

- Personality test questions
- MBTI dimension scoring
- Assessment system integration

## 🐛 Troubleshooting

### If containers are not running:

```bash
docker-compose up -d
```

### If database connection fails:

```bash
docker-compose restart db
docker-compose logs db
```

### If backend API is not responding:

```bash
docker-compose restart backend
docker-compose logs backend
```

### To reset everything:

```bash
docker-compose down
docker-compose up -d
# Wait for containers to be healthy, then:
docker-compose exec backend python simple_seed.py
```

## 🔍 Database Schema

The seeded database includes these main tables:

- `roles` - User roles and permissions
- `companies` - Company information
- `users` - User accounts and profiles
- `user_roles` - User-role assignments
- `user_settings` - User preferences
- `todos` - Task management
- `notifications` - Notification system
- `mbti_questions` - Personality test questions

## 🎯 Next Steps

1. **Test Authentication**: Try logging in with different user accounts
2. **Explore API**: Visit http://localhost:8000/docs for interactive API documentation
3. **Test Features**: Create todos, check notifications, take MBTI tests
4. **Frontend Integration**: Connect your frontend to the seeded backend data

## 📝 Notes

- All user passwords are set to `password` for testing
- The seed data includes realistic scenarios for comprehensive testing
- JSON payloads in notifications contain rich contextual data
- Todos have varied due dates and assignment patterns
- MBTI questions cover all personality dimensions (EI, SN, TF, JP)

The system is now ready for development and testing! 🎉
