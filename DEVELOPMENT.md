# MiraiWorks Development Guide

## 🚀 Quick Start

### Development Mode (With Hot Reloading)

**Backend Hot Reloading:** ✅ Enabled  
**Frontend Hot Reloading:** ❌ Requires rebuild (but faster than full rebuild)

## 📋 Development Commands

Use the `dev.bat` script for easy development:

```bash
# Start all services
dev.bat up

# Stop all services
dev.bat down

# Restart services
dev.bat restart

# Show logs
dev.bat logs

# Show backend logs only
dev.bat backend

# Show frontend logs only  
dev.bat frontend

# Rebuild everything (when you change dependencies)
dev.bat rebuild

# Check container status
dev.bat status
```

## 🔥 Hot Reloading Setup

### Backend (Python/FastAPI) - ✅ HOT RELOAD ENABLED
- **Volume mounting enabled:** Your local `./backend` folder is mounted into the container
- **Auto-reload enabled:** The server automatically restarts when you change Python files
- **No rebuild needed:** Just edit your Python files and see changes instantly!

### Frontend (Next.js) - ⚡ QUICK REBUILD
- **When you change frontend code:** Run `docker compose restart frontend`
- **Much faster than full rebuild:** Uses existing container with your changes
- **Only rebuild when needed:** For dependency changes, use `dev.bat rebuild`

## 🔧 Development Workflow

### For Backend Changes:
1. Edit your Python files in `./backend/`
2. Save the file
3. Changes appear automatically (hot reload)

### For Frontend Changes:
1. Edit your React/Next.js files in `./frontend-nextjs/`
2. Run: `docker compose restart frontend` (5-10 seconds)
3. Refresh your browser

### For Major Changes (Dependencies, Docker config):
1. Run: `dev.bat rebuild` (slower but complete refresh)

## 📁 Project Structure

```
MiraiWorks/
├── backend/              # Python FastAPI backend (hot reload enabled)
├── frontend-nextjs/      # Next.js frontend  
├── docker-compose.yml    # Main configuration with volume mounts
├── docker-compose.override.yml  # Development overrides
├── dev.bat              # Development helper script
└── DEVELOPMENT.md       # This file
```

## 🐛 Troubleshooting

### Backend not reloading?
```bash
# Check if volume is mounted
docker compose exec backend ls -la /app

# Check backend logs
dev.bat backend
```

### Frontend changes not appearing?
```bash
# Restart frontend container
docker compose restart frontend

# If that doesn't work, rebuild
dev.bat rebuild
```

### Ports already in use?
```bash
# Stop all containers
dev.bat down

# Check what's using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

## 🌟 Benefits of This Setup

1. **Backend changes:** Instant hot reload (0-2 seconds)
2. **Frontend changes:** Quick restart (5-10 seconds)  
3. **No full rebuilds needed:** Unless changing dependencies
4. **Same environment:** Identical to production setup
5. **Easy commands:** Use `dev.bat` for common tasks

## 📝 Normal vs Development Mode

| Task | Normal Mode | Development Mode |
|------|-------------|------------------|
| Backend change | Full rebuild (2-3 min) | Hot reload (instant) |
| Frontend change | Full rebuild (2-3 min) | Quick restart (10 sec) |
| Start services | `docker compose up` | `dev.bat up` |
| View logs | `docker compose logs` | `dev.bat logs` |

This setup gives you the best of both worlds: production-like environment with development-friendly hot reloading!