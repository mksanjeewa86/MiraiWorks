# MiraiWorks Database Setup Guide

This guide will help you set up the MySQL database for MiraiWorks and populate it with sample data.

## Prerequisites

1. **MySQL Server** - Install MySQL 8.0 or later
2. **Python Environment** - Ensure backend Python dependencies are installed

## Step 1: Install and Start MySQL

### Option A: Using Docker (Recommended)
```bash
# Run MySQL in Docker
docker run --name miraiworks-mysql \
  -e MYSQL_ROOT_PASSWORD=root123 \
  -e MYSQL_DATABASE=miraiworks \
  -e MYSQL_USER=hrms \
  -e MYSQL_PASSWORD=hrms123 \
  -p 3306:3306 \
  -d mysql:8.0

# Wait a few seconds for MySQL to start, then test connection
docker exec -it miraiworks-mysql mysql -u hrms -phrms123 miraiworks
```

### Option B: Local MySQL Installation
1. Install MySQL from https://dev.mysql.com/downloads/mysql/
2. Start MySQL service
3. Create database and user:
```sql
CREATE DATABASE miraiworks;
CREATE USER 'hrms'@'localhost' IDENTIFIED BY 'hrms123';
GRANT ALL PRIVILEGES ON miraiworks.* TO 'hrms'@'localhost';
FLUSH PRIVILEGES;
```

## Step 2: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

## Step 3: Initialize Database Tables
```bash
cd backend
python scripts/init_db.py
```

Follow the prompts to create a super admin user (or use defaults):
- Email: `admin@miraiworks.com`
- Password: `admin123!@#`

## Step 4: Populate with Sample Data
```bash
cd backend
python scripts/create_sample_data.py
```

## What Sample Data is Created

### Companies (4 total)
- **TechCorp Solutions** (Employer) - Technology solutions provider
- **Global Recruiters Inc** (Recruiter) - Premier recruitment agency  
- **StartupX** (Employer) - Fintech startup
- **Elite Talent Partners** (Recruiter) - Executive search firm

### Users (10 total)
- **Super Admin**: `admin@miraiworks.com` / `admin123!@#`
- **Company Admins**: 
  - `admin@techcorp.com` / `admin123!`
  - `admin@globalrecruiters.com` / `admin123!`
- **Recruiters**:
  - `sarah.recruiter@globalrecruiters.com` / `recruiter123!`
  - `mike.recruiter@elitetalent.com` / `recruiter123!`
- **Employers**:
  - `john.manager@techcorp.com` / `employer123!`
  - `lisa.lead@startupx.io` / `employer123!`
- **Candidates**:
  - `jane.developer@email.com` / `candidate123!`
  - `alex.engineer@email.com` / `candidate123!`
  - `emily.designer@email.com` / `candidate123!`
  - `david.analyst@email.com` / `candidate123!`

### Sample Content
- **4 Job Postings** with realistic salaries and requirements
- **Complete Resumes** for candidates with work experience, education, skills
- **Job Applications** from candidates to various positions
- **Notifications** for users across different activities

## Step 5: Start the Backend API
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## Step 6: Start the Frontend
```bash
cd frontend-nextjs
npm install
npm run dev
```

## Verification

1. **Database Connection**: Check that you can connect to MySQL
2. **API Health**: Visit http://localhost:8001/health
3. **Frontend**: Visit http://localhost:3000
4. **Login**: Use any of the sample user credentials above

## Troubleshooting

### MySQL Connection Issues
- Ensure MySQL is running on port 3306
- Verify credentials: user `hrms`, password `hrms123`
- Check database `miraiworks` exists
- For Docker: `docker logs miraiworks-mysql`

### Sample Data Issues
- Run `init_db.py` first to create tables
- Clear data and retry if needed:
```sql
DROP DATABASE miraiworks;
CREATE DATABASE miraiworks;
```

### Port Conflicts
- Backend uses port 8001
- Frontend uses port 3000
- MySQL uses port 3306
- Change ports in config files if needed

## Environment Variables

Create `.env` file in backend directory:
```bash
DB_URL=mysql+asyncmy://hrms:hrms123@localhost:3306/miraiworks
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key-here
```

## Production Notes

- Change all default passwords
- Use proper SSL certificates
- Set up database backups
- Use environment-specific configuration
- Set up proper logging and monitoring