# Temporary Password Troubleshooting Guide

## 🚨 Issue: "Invalid temporary password" Error

If you're getting "Invalid temporary password" when trying to activate your account, here are the most common causes and solutions:

---

## ✅ **Quick Checklist**

### **1. Copy-Paste Issues**
- **Problem**: Extra spaces, line breaks, or hidden characters
- **Solution**:
  - Use the eye icon 👁️ to show the password and verify what you typed
  - Copy the password character by character from the email
  - Don't copy from email previews - open the full email

### **2. Case Sensitivity**
- **Problem**: Passwords are case-sensitive (A ≠ a)
- **Solution**:
  - Make sure capitalization matches exactly
  - Use the show password feature to verify each character

### **3. Email Client Issues**
- **Problem**: Email client might modify the password display
- **Solution**:
  - Try viewing the email in a different client
  - Check both HTML and plain text versions
  - Look for the password in a `<code>` or monospace section

### **4. Browser Auto-Fill Interference**
- **Problem**: Browser might auto-fill wrong password
- **Solution**:
  - Clear the password field completely
  - Type manually (autocomplete is now disabled)
  - Use incognito/private browsing mode

---

## 🔍 **Detailed Troubleshooting Steps**

### **Step 1: Verify the Email**

Check your activation email for these elements:
```
Subject: Activate your MiraiWorks Account
Content should include:
- Your name
- Activation URL (like: /activate/123)
- Temporary password (usually 12 characters, mixed case + numbers)
```

### **Step 2: Test Password Characters**

**Valid temporary password characters:**
- ✅ Uppercase letters: A-Z
- ✅ Lowercase letters: a-z
- ✅ Numbers: 0-9
- ❌ Special symbols: NOT included in temporary passwords

**Example valid temporary password:** `aB3cD4eF5gH6`

### **Step 3: Manual Entry Process**

1. **Clear the field completely**
2. **Click the eye icon 👁️ to show password**
3. **Type each character carefully**
4. **Compare with email character by character**
5. **Ensure no trailing spaces**

### **Step 4: Check User Account Status**

The user account must be in the correct state:
- ✅ Account created but not yet activated (`is_active = False`)
- ✅ Temporary password recently generated
- ❌ Account already activated
- ❌ Account suspended or deleted

---

## 🛠 **Advanced Debugging**

### **If You're Still Having Issues:**

#### **Option 1: Request New Temporary Password**
Ask your administrator to:
1. Reset your temporary password
2. Send a new activation email
3. Verify the email delivery

#### **Option 2: Check Database (Admin Only)**
```sql
-- Check user status
SELECT id, email, is_active, created_at, updated_at
FROM users
WHERE email = 'your-email@domain.com';

-- Verify password was set recently
SELECT id, email, updated_at
FROM users
WHERE email = 'your-email@domain.com'
AND updated_at > NOW() - INTERVAL 1 DAY;
```

#### **Option 3: Backend Logs (Admin Only)**
Check for these log entries:
```
"Invalid temporary password" - means password verification failed
"User not found" - means email/user ID mismatch
"Account already activated" - means user is already active
```

---

## 🔧 **Common Fixes**

### **Fix 1: Email Display Issues**

**If your email shows the password like this:**
```
Password: abc123XYZ (but looks weird or truncated)
```

**Try:**
- View source of the email
- Copy from plain text version
- Contact admin for password via different method

### **Fix 2: Browser Issues**

**If browser seems to interfere:**
```javascript
// Clear browser storage (in console)
localStorage.clear();
sessionStorage.clear();
```

**Or use incognito mode**

### **Fix 3: Mobile/App Issues**

**If using mobile or email app:**
- Switch to desktop browser
- Open email in web browser instead of app
- Zoom in to see password clearly

---

## 📧 **Email Template Issues**

### **What to Look For in Your Email:**

```html
<!-- Good email format -->
<p>Your temporary password is: <strong>aB3cD4eF5gH6</strong></p>

<!-- Or in plain text -->
Temporary Password: aB3cD4eF5gH6
```

### **Red Flags:**
- Password shown as: `[HIDDEN]` or `****`
- Password with unusual characters: `@#$%^&*`
- Password shorter than 12 characters
- Password with spaces in the middle

---

## 🎯 **Prevention Tips**

### **For Users:**
1. **Check email immediately** after account creation
2. **Use copy-paste carefully** - prefer manual typing for passwords
3. **Activate quickly** - don't wait days/weeks
4. **Use desktop browser** for activation when possible

### **For Administrators:**
1. **Test activation process** regularly
2. **Monitor failed activation attempts**
3. **Provide alternative contact method** for password issues
4. **Consider SMS/phone backup** for critical accounts

---

## ⚡ **Quick Resolution**

**Most Common Solution (90% of cases):**
1. Open the activation email
2. Find the temporary password (usually bold or in code format)
3. Clear the password field on activation page
4. Click the eye icon to show password
5. Type the password manually, character by character
6. Double-check each character matches the email
7. Submit the form

**If this doesn't work, contact your system administrator for a new temporary password.**

---

## 📞 **When to Contact Support**

Contact your administrator if:
- ✅ You've tried manual entry multiple times
- ✅ You've verified the password character by character
- ✅ You're using the correct email and user ID
- ✅ The account was created recently (within 24 hours)
- ✅ You've tried different browsers/devices

**Include in your support request:**
- Your email address
- Time you received the activation email
- Screenshot of the email (blur sensitive info)
- Error message you're seeing
- Browser/device you're using