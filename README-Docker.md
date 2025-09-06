# Docker Setup for MiraiWorks

This guide explains how to run the MiraiWorks application using Docker containers locally.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose v3.8 or later

## Quick Start

### 1. Development Setup (Backend + Database only)

For development, you can run just the backend services while running the frontend separately:

```bash
# Start backend services (database, redis, backend API)
docker-compose -f docker-compose.dev.yml up -d

# Check services are running
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend
```

Then run frontend separately:
```bash
cd frontend-nextjs
npm run dev
```

### 2. Full Production Setup

To run everything in containers:

```bash
# Build and start all services
docker-compose up --build -d

# Check all services are running
docker-compose ps

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Services Overview

- **Database (MySQL)**: Port 3306
- **Redis**: Port 6379  
- **Backend API**: Port 8000
- **Frontend**: Port 3000 (full setup only)

## Useful Commands

### Stop Services
```bash
# Stop development services
docker-compose -f docker-compose.dev.yml down

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: This deletes data!)
docker-compose down -v
```

### Rebuild Containers
```bash
# Rebuild backend only
docker-compose build backend

# Rebuild all services
docker-compose build

# Force rebuild without cache
docker-compose build --no-cache
```

### Database Management
```bash
# Connect to MySQL database
docker exec -it miraiworks_db mysql -u hrms -phrms miraiworks

# View database logs
docker-compose logs -f db
```

### Debugging
```bash
# Access backend container shell
docker exec -it miraiworks_backend bash

# Access frontend container shell (full setup)
docker exec -it miraiworks_frontend sh

# View container resource usage
docker stats
```

## Environment Variables

Default environment variables are set in the docker-compose files. For production, create a `.env` file:

```bash
# Database
DB_HOST=db
DB_PORT=3306
DB_USER=hrms  
DB_PASSWORD=your-secure-password
DB_NAME=miraiworks

# Redis
REDIS_URL=redis://redis:6379/0

# JWT Secret
JWT_SECRET=your-very-secure-jwt-secret-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Health Checks

All services include health checks. Check status:

```bash
# View health status
docker-compose ps

# Manual health check
curl http://localhost:8000/health
curl http://localhost:3000
```

## Troubleshooting

### Port Conflicts
If ports are already in use:
```bash
# Check what's using port 3306
netstat -an | findstr 3306

# Use different ports in docker-compose.yml
```

### Database Connection Issues
```bash
# Wait for database to be ready
docker-compose logs -f db

# Check database connection from backend
docker exec -it miraiworks_backend python -c "from app.database import engine; print('DB connected!' if engine else 'DB failed')"
```

### Build Issues
```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
```