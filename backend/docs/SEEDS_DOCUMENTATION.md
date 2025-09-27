# MiraiWorks Database Seeds

This directory contains comprehensive seed data for the MiraiWorks application, providing sample data for development and testing purposes.

## Overview

The seed system is organized into modular files, each handling specific aspects of the application:

### Core Seed Files

1. **`users_and_companies.py`** - Authentication data (roles, companies, users)
2. **`personality_test_questions.py`** - MBTI personality test questions
3. **`test_messages_interviews_jobs.py`** - Sample application data (messages, interviews, positions)
4. **`assessment_and_exam_system.py`** - Assessment and exam system data
5. **`resume_data.py`** - Resume system data
6. **`todo_data.py`** - Todo management system data
7. **`notification_data.py`** - Notification system data

### Main Entry Points

- **`seed_data.py`** - Main orchestrator that runs all seeds in correct order
- **`__init__.py`** - Package initialization with exported functions

## Usage

### Prerequisites

1. **Database Setup**: Ensure MySQL is running and the database exists
2. **Migrations**: Run database migrations first:
   ```bash
   cd backend
   alembic upgrade head
   ```

### Running Seeds

#### Method 1: Direct Execution

```bash
cd backend
PYTHONPATH=. python3 app/seeds/seed_data.py
```

#### Method 2: Using Docker Compose

If using Docker Compose, the seeds can be run inside the backend container:

```bash
docker-compose exec backend python app/seeds/seed_data.py
```

#### Method 3: Individual Seed Functions

You can also import and run individual seed functions in your own scripts:

```python
from app.seeds import seed_auth_data, seed_mbti_questions

async def custom_seeding():
    async with AsyncSessionLocal() as db:
        auth_result = await seed_auth_data(db)
        mbti_count = await seed_mbti_questions(db)
```

## Seed Data Overview

### Authentication System

- **4 Roles**: Admin, HR Manager, Recruiter, Candidate
- **2 Companies**: MiraiWorks (main), TechCorp (client)
- **4+ Users** with different roles and permissions
- **User Settings** with various preferences
- **Company Profiles** with complete information

### MBTI Personality Test

- **60 Questions** covering all MBTI dimensions
- Questions for Extraversion/Introversion, Sensing/Intuition, Thinking/Feeling, Judging/Perceiving
- Properly formatted for the assessment system

### Sample Application Data

- **Messages** between users (various types and statuses)
- **Interviews** scheduled with different candidates
- **Job Positions** with detailed requirements and descriptions
- **Realistic conversation flows** for testing

### Assessment & Exam System

- **Multiple Exams** for different skill areas
- **Varied Question Types** (multiple choice, coding, essay)
- **Exam Assignments** to different users
- **Scoring and evaluation data**

### Resume System

- **Complete Resumes** with all sections
- **Work Experience**, Education, Skills, Projects
- **Certifications**, Languages, References
- **Multiple Resume Formats** (chronological, functional, hybrid)

### Todo Management System

- **Todos with Different Statuses**: Pending, In Progress, Completed, Overdue
- **Priority Levels**: High, Medium, Low
- **Visibility Settings**: Private, Team, Company
- **Assignment Scenarios**: Self-assigned, manager-assigned, collaborative
- **Due Dates and Deadlines** for testing time-based features

### Notification System

- **Various Notification Types**: System, Interview, Application, Assessment, etc.
- **Read/Unread Status** for testing notification management
- **Rich Payload Data** with contextual information
- **Time-based Notifications** (recent, older, urgent)
- **User-specific Notifications** for different roles

## Login Credentials

After running seeds, you can use these credentials to test the application:

### Admin Access

- **Email**: `admin@miraiworks.com`
- **Password**: `password`
- **Permissions**: Full system access

### Recruiter Access

- **Email**: `recruiter@miraiworks.com`
- **Password**: `password`
- **Permissions**: Recruitment management

### HR Manager Access

- **Email**: `hr.manager@miraiworks.com`
- **Password**: `password`
- **Permissions**: HR operations

### Candidate Access

- **Email**: `candidate@example.com`
- **Password**: `password`
- **Permissions**: Candidate portal access

## Data Relationships

The seed data is designed with realistic relationships:

1. **Users** belong to **Companies** and have **Roles**
2. **Todos** are assigned to users with proper ownership chains
3. **Notifications** are targeted to specific users based on their roles
4. **Messages** flow between users in realistic conversation patterns
5. **Interviews** are scheduled between recruiters and candidates
6. **Exams** are assigned to candidates by recruiters/HR
7. **Resumes** belong to candidates with complete professional data

## Customization

### Adding New Seed Data

1. Create a new seed file in the `seeds/` directory
2. Follow the pattern of existing seed files:
   ```python
   async def seed_your_data(db: AsyncSession, auth_result: Dict[str, Any]) -> Dict[str, int]:
       # Your seeding logic here
       return {"created_items": count}
   ```
3. Add the import to `__init__.py`
4. Add the function call to `seed_data.py`
5. Update the cleanup function if needed

### Modifying Existing Seeds

Each seed file is self-contained and can be modified independently. The `auth_result` parameter provides user IDs and other essential data for creating relationships.

## Troubleshooting

### Common Issues

1. **Table doesn't exist**: Run `alembic upgrade head` first
2. **Connection refused**: Ensure MySQL is running
3. **Permission denied**: Check database credentials in config
4. **Foreign key constraints**: Ensure seeds run in dependency order

### Database Reset

To completely reset and reseed:

```bash
# Drop and recreate database (be careful!)
mysql -u root -p -e "DROP DATABASE miraiworks; CREATE DATABASE miraiworks;"

# Run migrations
cd backend
alembic upgrade head

# Run seeds
PYTHONPATH=. python3 app/seeds/seed_data.py
```

### Partial Seeding

If you only need specific data, you can run individual seed functions:

```python
# Example: Only seed auth data and todos
from app.seeds import seed_auth_data, seed_todo_data

async def partial_seed():
    async with AsyncSessionLocal() as db:
        auth_result = await seed_auth_data(db)
        todo_result = await seed_todo_data(db, auth_result)
```

## Development Notes

- All seed functions are **idempotent** - they clear existing data before creating new data
- The system uses **realistic sample data** rather than placeholder text
- **Relationships are properly maintained** across all entities
- **Timestamps are varied** to simulate realistic usage patterns
- **Error handling** is built into the main seed runner

## Contributing

When adding new seed data:

1. Follow existing patterns and naming conventions
2. Include proper error handling and logging
3. Update this README with new seed information
4. Test seeds both individually and as part of the full suite
5. Ensure data relationships are realistic and useful for testing

The seed system is designed to provide a comprehensive, realistic dataset that supports all aspects of the MiraiWorks application development and testing.
