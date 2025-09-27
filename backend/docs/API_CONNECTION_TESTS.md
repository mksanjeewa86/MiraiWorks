# API Connection Test

Open the browser console (F12 → Console) and run these commands one by one:

## 1. Test basic backend connectivity:
```javascript
fetch('http://localhost:8000/')
  .then(response => response.json())
  .then(data => console.log('Backend reachable:', data))
  .catch(error => console.error('Backend connection failed:', error));
```

## 2. Check if auth token exists:
```javascript
console.log('Auth token:', localStorage.getItem('accessToken'));
```

## 3. Test authenticated API call:
```javascript
const token = localStorage.getItem('accessToken');
if (token) {
  fetch('http://localhost:8000/api/interviews', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => console.log('Auth API response:', data))
  .catch(error => console.error('Auth API failed:', error));
} else {
  console.log('No auth token found - user not logged in');
}
```

## 4. Test video call API specifically:
```javascript
const token = localStorage.getItem('accessToken');
const interviewId = 22; // Replace with actual interview ID
if (token) {
  fetch(`http://localhost:8000/api/interviews/${interviewId}/video-call`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
  .then(data => console.log('Video call API response:', data))
  .catch(error => console.error('Video call API failed:', error));
} else {
  console.log('No auth token found - user not logged in');
}
```

Run these tests and tell me what output you get for each one.