# Docker on Windows - Troubleshooting Guide

## Common Issue: Watchfiles I/O Error on First Startup

### Symptoms
When you start Docker for the first time each day, you see this error:

```
_rust_notify.WatchfilesRustInternalError: error in underlying watcher: Input/output error (os error 5)
```

### Root Cause
This is a known issue with Docker Desktop on Windows:
- Docker uses a virtual file system layer (WSL2 or Hyper-V)
- On first startup, file watching events may not be properly initialized
- The `watchfiles` library (used by uvicorn's `--reload`) can't establish file watchers
- This typically happens due to Windows file system notification limits or timing issues

### Why It Happens "First Time Every Day"
- When Docker Desktop starts fresh, the file system virtualization layer needs time to initialize
- File watching requires kernel-level file system notifications
- Windows may not have the notification system ready when containers start immediately

---

## Solutions

### Quick Fix: Restart the Backend Container
The easiest solution is to simply restart the backend container:

```bash
# Option 1: Use the helper script (Windows)
fix-backend-watcher.bat

# Option 2: Restart manually
docker-compose restart backend

# Option 3: Check logs after restart
docker-compose logs --tail=50 --follow backend
```

The restart usually works because by then, the file system layer is fully initialized.

---

### Permanent Solutions

#### Solution 1: Use Polling Mode (Current Configuration)
The project is already configured to use polling mode:

```yaml
# docker-compose.override.yml
environment:
  - WATCHFILES_FORCE_POLLING=true      # Use polling instead of native watchers
  - WATCHFILES_RUST_TIMEOUT=10000      # 10 second timeout for initialization
command:
  - --reload-delay
  - "3"                                # Wait 3 seconds before reloading
```

**Pros:**
- Works reliably on Windows Docker
- Automatically recovers from watcher failures
- No manual intervention needed after first restart

**Cons:**
- Slightly higher CPU usage (polling every few seconds)
- Reload may be 1-2 seconds slower

---

#### Solution 2: Disable Auto-Reload (Production Mode)
If you don't need auto-reload during development:

```bash
# Start without the override file (disables auto-reload)
docker-compose -f docker-compose.yml up

# Or temporarily disable auto-reload
docker-compose up backend --no-deps -d --force-recreate \
  --entrypoint "uvicorn app.main:app --host 0.0.0.0 --port 8000 --noreload"
```

**Pros:**
- No file watcher issues
- Lower resource usage
- Faster startup

**Cons:**
- Must manually restart container after code changes
- Less convenient for active development

---

#### Solution 3: Use Docker Desktop Settings
Optimize Docker Desktop for better file system performance:

1. **Open Docker Desktop Settings**
2. **Go to Resources → WSL Integration** (if using WSL2)
3. **Enable integration** with your WSL2 distro
4. **Increase resource limits:**
   - Memory: At least 4GB
   - CPUs: At least 2
   - Disk: At least 20GB

5. **Go to General**
   - Enable "Use the WSL 2 based engine"
   - Disable "Use Docker Compose V2" (if you have issues)

6. **Apply & Restart Docker Desktop**

---

#### Solution 4: Wait for File System to Initialize
Add a startup delay to the backend:

```yaml
# docker-compose.override.yml
backend:
  command:
    - sh
    - -c
    - "sleep 5 && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload ..."
```

**Pros:**
- Gives file system time to initialize
- May prevent the error entirely

**Cons:**
- Delays every startup (even when not needed)
- Not guaranteed to fix the issue

---

## Recommended Workflow

For daily development on Windows:

1. **Start Docker Desktop and containers:**
   ```bash
   docker-compose up -d
   ```

2. **If you see the watchfiles error:**
   ```bash
   # Quick fix - just restart backend
   docker-compose restart backend
   ```

3. **Verify backend is running:**
   ```bash
   # Check logs
   docker-compose logs --tail=20 backend

   # Check health
   curl http://localhost:8000/health
   ```

4. **Continue development** - auto-reload should work normally after restart

---

## Alternative: Use Native Python Development

If Docker file watching is too problematic, consider running the backend natively:

```bash
# 1. Install Python 3.11+
# 2. Create virtual environment
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (create .env file)
# 5. Run backend natively
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Pros:**
- No Docker file watching issues
- Faster reloads
- Better IDE integration
- Easier debugging

**Cons:**
- Need to install MySQL, Redis, MinIO locally
- Environment differences from production
- More complex setup

---

## When to Worry

**DON'T worry if:**
- ✅ Error happens only on first startup
- ✅ Backend works after restarting container
- ✅ Auto-reload works after restart
- ✅ No errors in subsequent startups

**DO investigate if:**
- ❌ Error persists after multiple restarts
- ❌ Backend crashes or becomes unresponsive
- ❌ Auto-reload stops working entirely
- ❌ You see file system corruption errors
- ❌ Other containers also show I/O errors

---

## Related Issues & References

- [watchfiles Issue #242](https://github.com/samuelcolvin/watchfiles/issues/242) - Windows Docker I/O errors
- [Docker Desktop Known Issues](https://docs.docker.com/desktop/troubleshoot/known-issues/)
- [WSL2 File System Performance](https://learn.microsoft.com/en-us/windows/wsl/filesystems)

---

## Summary

The watchfiles error on Windows Docker is:
- **Common** - affects many developers using Docker on Windows
- **Harmless** - doesn't indicate actual file system corruption
- **Temporary** - usually resolves after one container restart
- **Expected** - due to Windows file system virtualization timing

**The fix is simple: restart the backend container when you see the error.**

```bash
docker-compose restart backend
```

That's it! 🎉
