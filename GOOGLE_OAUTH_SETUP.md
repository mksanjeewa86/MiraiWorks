# Google OAuth Setup Instructions

## ✅ Steps Completed:
1. ✅ Backend calendar service configured
2. ✅ Database models ready
3. ✅ Frontend calendar integration ready
4. ✅ OAuth endpoints working

## 📋 Next Steps (After getting credentials):

### 1. Update .env file
Replace these lines in `backend/.env`:
```bash
GOOGLE_CALENDAR_CLIENT_ID=PASTE-YOUR-CLIENT-ID-HERE
GOOGLE_CALENDAR_CLIENT_SECRET=PASTE-YOUR-CLIENT-SECRET-HERE
```

### 2. Restart backend
```bash
docker restart miraiworks_backend
```

### 3. Test the integration
1. Login to MiraiWorks: http://localhost:3000
2. Go to Settings → Calendar
3. Click "Connect Google Calendar"
4. Should redirect to Google auth page

## 🔧 Google Cloud Console Setup:

### Project Setup:
- Project Name: MiraiWorks-Calendar
- Enable: Google Calendar API
- OAuth Consent Screen: External

### OAuth Client Configuration:
- Type: Web Application
- Name: MiraiWorks Calendar Integration
- Authorized origins: http://localhost:3000
- Redirect URIs: http://localhost:3000/settings/calendar/google/callback

### Required Scopes:
- https://www.googleapis.com/auth/calendar
- https://www.googleapis.com/auth/userinfo.email
- https://www.googleapis.com/auth/userinfo.profile

## 🎯 How it works:
1. User clicks "Connect Google Calendar"
2. Redirects to Google OAuth page
3. User logs in with their Google account
4. Google redirects back to MiraiWorks
5. User's calendar access token saved in database
6. User can now sync calendars and create meetings

Each user authenticates with their own Google account - no user credentials stored in .env!