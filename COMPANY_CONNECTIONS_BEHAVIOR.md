# Company Connections - Contact List Behavior

## 📋 Overview

The company connections system controls **who appears in your contact list**. If you can't message someone, they simply won't appear - no error messages, no friction.

---

## ✅ Contact List Filtering Rules

### **Who Appears in Your Contacts:**

1. **✅ Same Company Colleagues**
   - All active users in your company
   - Automatic - no connection needed
   - Example: You and your coworkers at Company A

2. **✅ Connected Company Users**
   - All users from companies connected to yours
   - Example: Your company (Recruiter A) ↔ Company B → You see all Company B users

3. **✅ Direct Connections**
   - Users you're directly connected to via user-to-company connection
   - Example: Freelancer connected to Company A → Freelancer sees all Company A users

### **Who Does NOT Appear:**

- ❌ Users from unconnected companies
- ❌ Users without any connection to you or your company
- ❌ Inactive or deleted users

**Result:** Your contact list only shows people you can actually message.

---

## 🔧 Technical Implementation

### **Backend Endpoint:**

`GET /api/user/connections/my-connections`

**Location:** `backend/app/endpoints/user_connections.py:72-107`

```python
@router.get(API_ROUTES.USER_CONNECTIONS.MY_CONNECTIONS)
async def get_my_connections(current_user, db):
    """Get all users connected to current user via company connections."""

    # Uses company_connection_service.get_connected_users()
    connected_users = await company_connection_service.get_connected_users(
        db=db, user_id=current_user.id
    )
    # Returns ONLY users the current user can interact with
    return connected_users
```

**Logic:** `backend/app/services/company_connection_service.py:284-374`

The service automatically includes:
- Same company users (line 315-316)
- Connected companies (line 318-332)
- Direct user connections (line 334-349)

### **Frontend Usage:**

```typescript
import { userConnectionsApi } from '@/api';

// Get contacts (already filtered)
const response = await userConnectionsApi.getMyConnections();

// response.data contains ONLY users you can message
// No need to filter further!
```

---

## 🛡️ Security Layer (Backend Validation)

**Location:** `backend/app/services/message_service.py:40-49`

Even though the frontend prevents it, the backend has validation:

```python
async def send_message(db, sender_id, message_data):
    # Validate company connection
    can_interact = await company_connection_service.can_users_interact(
        db, sender_id, message_data.recipient_id
    )

    if not can_interact:
        raise HTTPException(
            status_code=403,
            detail="You cannot message this user. No company connection exists."
        )
```

**Purpose:** Prevents API manipulation - users never see this in normal usage.

---

## 📊 User Experience Flow

### **Scenario 1: Same Company Users**

```
User: Admin at MiraiWorks
Contact List Shows:
  ✅ Candidate (MiraiWorks)
  ✅ HR Manager (MiraiWorks)
  ✅ Recruiter (MiraiWorks)

Hidden:
  ❌ John Doe (Company B - no connection)
  ❌ Jane Smith (Company C - no connection)
```

### **Scenario 2: Connected Companies**

```
User: Recruiter at Agency A
Connection: Agency A ↔ Employer B

Contact List Shows:
  ✅ All colleagues at Agency A
  ✅ All active users at Employer B

Hidden:
  ❌ Users at Employer C (no connection)
```

### **Scenario 3: Freelancer with Direct Connection**

```
User: Freelancer (no company)
Connection: Freelancer → Company A

Contact List Shows:
  ✅ All active users at Company A

Hidden:
  ❌ Users at Company B (no connection)
```

---

## 🎯 Benefits

1. **Clean UX** - No error messages when trying to send
2. **Clear Expectations** - If you see them, you can message them
3. **Privacy** - Users from unconnected companies don't see each other
4. **Security** - Backend validates even if UI is bypassed

---

## 🔄 How Connections Affect Contact List

### **Creating a Connection:**

```
Before: Company A ❌ Company B
Contact List: Only Company A users visible

Admin creates: Company A ↔ Company B

After: Company A ✅ Company B
Contact List: Both Company A and Company B users visible
```

### **Deactivating a Connection:**

```
Admin deactivates: Company A ↔ Company B

Result:
- Users refresh contact list
- Company B users disappear from Company A's contacts
- Company A users disappear from Company B's contacts
- Existing conversations remain visible but new messages disabled
```

---

## ⚙️ Configuration

### **To Enable Messaging Between Companies:**

**Option 1: Company-to-Company Connection**
```bash
# Admin creates connection
POST /api/company-connections/company-to-company
{
  "source_company_id": 88,
  "target_company_id": 90,
  "can_message": true
}
```

**Option 2: User-to-Company Connection**
```bash
# Individual user connects to company
POST /api/company-connections/user-to-company
{
  "target_company_id": 90,
  "can_message": true
}
```

### **To Disable Messaging:**

```bash
# Deactivate connection
PUT /api/company-connections/{connection_id}/deactivate
```

---

## 📝 Summary

✅ **Frontend:** Only displays users you can message
✅ **Backend:** Validates as safety measure
✅ **User Experience:** No error messages - clean and simple
✅ **Security:** Prevents unauthorized messaging attempts

**Rule:** If you can't message them, you won't see them. Simple as that!

---

*Last Updated: 2025-10-11*
