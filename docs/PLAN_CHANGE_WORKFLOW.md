# Plan Change Request/Approval Workflow

## 📋 Overview

This document describes the **request/approval workflow** for changing subscription plans (upgrade/downgrade).

### **Workflow**
1. **Company Admin** → Requests plan change (with message)
2. **System Admin** → Reviews and approves/rejects the request
3. **System** → Applies the change if approved

---

## 🔄 Complete Flow

```
┌─────────────────┐
│ Company Admin   │
│ Requests Change │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Request Created     │
│ Status: PENDING     │
└────────┬────────────┘
         │
         ▼
┌─────────────────┐
│ System Admin    │
│ Reviews Request │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│ APPROVE │ │ REJECT   │
└────┬────┘ └────┬─────┘
     │           │
     ▼           ▼
┌─────────────────────┐
│ Plan Changes        │
│ OR                  │
│ Request Rejected    │
└─────────────────────┘
```

---

## 🗄️ Database Schema

### **`plan_change_requests` Table**

```sql
CREATE TABLE plan_change_requests (
    id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    subscription_id INTEGER NOT NULL,
    current_plan_id INTEGER NOT NULL,
    requested_plan_id INTEGER NOT NULL,
    request_type VARCHAR(20) NOT NULL,  -- 'upgrade', 'downgrade'
    requested_by INTEGER NOT NULL,      -- Company admin user ID
    request_message TEXT,               -- Message from company admin
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    reviewed_by INTEGER,                -- System admin user ID
    review_message TEXT,                -- Response from system admin
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Backend API Endpoints

### **1. Company Admin - Request Plan Change**

**Endpoint**: `POST /api/subscriptions/plan-change-request`

**Who can access**: Company Admin only

**Request**:
```json
{
  "requested_plan_id": 2,  // Premium plan ID
  "request_message": "We need exam management features for our recruitment process"
}
```

**Response**:
```json
{
  "id": 1,
  "company_id": 5,
  "subscription_id": 12,
  "current_plan": {
    "id": 1,
    "name": "basic",
    "display_name": "Basic Plan"
  },
  "requested_plan": {
    "id": 2,
    "name": "premium",
    "display_name": "Premium Plan"
  },
  "request_type": "upgrade",
  "requested_by": 42,
  "request_message": "We need exam management features...",
  "status": "pending",
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

### **2. Company Admin - View My Requests**

**Endpoint**: `GET /api/subscriptions/my-plan-change-requests`

**Who can access**: Company Admin

**Response**:
```json
[
  {
    "id": 1,
    "request_type": "upgrade",
    "current_plan": { "name": "basic", "display_name": "Basic Plan" },
    "requested_plan": { "name": "premium", "display_name": "Premium Plan" },
    "status": "pending",
    "request_message": "We need exam features",
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

---

### **3. System Admin - View All Pending Requests**

**Endpoint**: `GET /api/subscriptions/plan-change-requests?status=pending`

**Who can access**: System Admin only

**Response**:
```json
[
  {
    "id": 1,
    "company_id": 5,
    "company_name": "Tech Corp",
    "current_plan": { "name": "basic" },
    "requested_plan": { "name": "premium" },
    "request_type": "upgrade",
    "requested_by": 42,
    "requester_name": "John Doe",
    "request_message": "We need exam features",
    "status": "pending",
    "created_at": "2025-01-15T10:00:00Z"
  },
  {
    "id": 2,
    "company_id": 8,
    "company_name": "Small Business Inc",
    "current_plan": { "name": "premium" },
    "requested_plan": { "name": "basic" },
    "request_type": "downgrade",
    "requested_by": 88,
    "requester_name": "Jane Smith",
    "request_message": "Cost reduction needed",
    "status": "pending",
    "created_at": "2025-01-14T15:30:00Z"
  }
]
```

---

### **4. System Admin - Approve/Reject Request**

**Endpoint**: `POST /api/subscriptions/plan-change-requests/{request_id}/review`

**Who can access**: System Admin only

**Request (Approve)**:
```json
{
  "status": "approved",
  "review_message": "Approved. Welcome to Premium!"
}
```

**Request (Reject)**:
```json
{
  "status": "rejected",
  "review_message": "Please contact billing department first"
}
```

**Response**:
```json
{
  "id": 1,
  "status": "approved",
  "reviewed_by": 1,  // System admin user ID
  "review_message": "Approved. Welcome to Premium!",
  "reviewed_at": "2025-01-15T14:00:00Z"
}
```

---

## 🎨 Frontend Implementation

### **Company Admin UI - Request Plan Change**

```typescript
// frontend/src/app/subscription/upgrade/page.tsx
'use client';

import { useState } from 'react';
import { subscriptionApi } from '@/api/subscription';

export default function RequestUpgradePage() {
  const [message, setMessage] = useState('');

  const handleRequestUpgrade = async () => {
    try {
      await subscriptionApi.requestPlanChange({
        requested_plan_id: 2,  // Premium
        request_message: message
      });

      alert('Upgrade request submitted! System admin will review it.');
    } catch (error) {
      console.error('Request failed', error);
    }
  };

  return (
    <div className="p-6">
      <h1>Request Upgrade to Premium</h1>

      <div className="mt-4">
        <label>Reason for upgrade:</label>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Explain why you need Premium features..."
          className="w-full border p-2"
          rows={4}
        />
      </div>

      <button
        onClick={handleRequestUpgrade}
        className="mt-4 bg-blue-600 text-white px-4 py-2 rounded"
      >
        Submit Request
      </button>
    </div>
  );
}
```

---

### **System Admin UI - Review Requests**

```typescript
// frontend/src/app/admin/plan-change-requests/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { subscriptionApi } from '@/api/subscription';
import type { PlanChangeRequest } from '@/types/subscription';

export default function PlanChangeRequestsPage() {
  const [requests, setRequests] = useState<PlanChangeRequest[]>([]);

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    const response = await subscriptionApi.getPlanChangeRequests('pending');
    setRequests(response.data || []);
  };

  const handleReview = async (requestId: number, approved: boolean, message: string) => {
    await subscriptionApi.reviewPlanChangeRequest(requestId, {
      status: approved ? 'approved' : 'rejected',
      review_message: message
    });

    await loadRequests();  // Reload list
  };

  return (
    <div className="p-6">
      <h1>Plan Change Requests</h1>

      <div className="mt-4 space-y-4">
        {requests.map(request => (
          <div key={request.id} className="border p-4 rounded">
            <div className="flex justify-between">
              <div>
                <h3 className="font-bold">{request.company_name}</h3>
                <p className="text-sm text-gray-600">
                  {request.request_type}: {request.current_plan.display_name} → {request.requested_plan.display_name}
                </p>
                <p className="mt-2">{request.request_message}</p>
                <p className="text-xs text-gray-500 mt-1">
                  Requested by: {request.requester_name} on {new Date(request.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>

            <div className="mt-4 flex gap-2">
              <button
                onClick={() => handleReview(request.id, true, 'Approved')}
                className="bg-green-600 text-white px-4 py-2 rounded"
              >
                Approve
              </button>
              <button
                onClick={() => handleReview(request.id, false, 'Rejected')}
                className="bg-red-600 text-white px-4 py-2 rounded"
              >
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 📡 Frontend API Client

```typescript
// frontend/src/api/subscription.ts

export const subscriptionApi = {
  // ... existing methods

  // Company Admin - Request plan change
  async requestPlanChange(data: PlanChangeRequestCreate): Promise<ApiResponse<PlanChangeRequestInfo>> {
    const response = await apiClient.post<PlanChangeRequestInfo>(
      '/api/subscriptions/plan-change-request',
      data
    );
    return { data: response.data, success: true };
  },

  // Company Admin - View my requests
  async getMyPlanChangeRequests(): Promise<ApiResponse<PlanChangeRequestInfo[]>> {
    const response = await apiClient.get<PlanChangeRequestInfo[]>(
      '/api/subscriptions/my-plan-change-requests'
    );
    return { data: response.data, success: true };
  },

  // System Admin - View all requests
  async getPlanChangeRequests(status?: string): Promise<ApiResponse<PlanChangeRequestInfo[]>> {
    const params = status ? { status } : {};
    const response = await apiClient.get<PlanChangeRequestInfo[]>(
      '/api/subscriptions/plan-change-requests',
      { params }
    );
    return { data: response.data, success: true };
  },

  // System Admin - Approve/reject request
  async reviewPlanChangeRequest(
    requestId: number,
    data: PlanChangeRequestReview
  ): Promise<ApiResponse<PlanChangeRequestInfo>> {
    const response = await apiClient.post<PlanChangeRequestInfo>(
      `/api/subscriptions/plan-change-requests/${requestId}/review`,
      data
    );
    return { data: response.data, success: true };
  },
};
```

---

## 🎯 User Experience

### **Scenario 1: Company Admin Requests Upgrade**

1. Company admin navigates to **Subscription Management**
2. Sees current plan: **Basic**
3. Clicks "Request Upgrade to Premium"
4. Fills in reason: "We need exam management features for our hiring process"
5. Submits request
6. Sees message: "Request submitted! You'll be notified when reviewed."

---

### **Scenario 2: System Admin Reviews Request**

1. System admin navigates to **Admin > Plan Change Requests**
2. Sees pending request from Tech Corp
3. Reviews the reason
4. Clicks "Approve" or "Reject"
5. (Optional) Adds review message
6. Request is processed

---

### **Scenario 3: Approval - Plan Changes**

1. When system admin **approves**:
   - Company subscription is updated immediately
   - Company admin receives notification
   - All company users now have Premium features

2. When system admin **rejects**:
   - Request is marked as rejected
   - Company admin receives notification with reason
   - Plan remains unchanged

---

## 🔔 Notifications

### **Email to Company Admin (Request Submitted)**
```
Subject: Plan Change Request Submitted

Your request to upgrade to Premium has been submitted.

Request Details:
- Current Plan: Basic
- Requested Plan: Premium
- Status: Pending Review

You'll receive an email when a system administrator reviews your request.
```

### **Email to System Admin (New Request)**
```
Subject: New Plan Change Request - Tech Corp

Tech Corp has requested a plan change.

Details:
- Company: Tech Corp
- Request: Upgrade from Basic to Premium
- Reason: "We need exam management features..."
- Requested by: John Doe (john@techcorp.com)

Review at: https://app.example.com/admin/plan-change-requests
```

### **Email to Company Admin (Approved)**
```
Subject: Plan Change Request Approved!

Great news! Your plan change request has been approved.

Details:
- New Plan: Premium
- Effective: Immediately
- Review Message: "Approved. Welcome to Premium!"

You now have access to all Premium features including:
- Exam Library
- Exam Administration
- Question Banks

Start exploring: https://app.example.com/exams
```

### **Email to Company Admin (Rejected)**
```
Subject: Plan Change Request - Update Required

Your plan change request requires additional action.

Status: Rejected
Reason: "Please contact billing department first"

If you have questions, please contact our support team.
```

---

## ✅ Implementation Checklist

### **Backend**
- [ ] Create `plan_change_requests` table migration
- [ ] Create `PlanChangeRequest` model
- [ ] Create plan change request schemas
- [ ] Create plan change request CRUD
- [ ] Add `request_plan_change` endpoint (Company Admin)
- [ ] Add `get_my_plan_change_requests` endpoint (Company Admin)
- [ ] Add `get_all_plan_change_requests` endpoint (System Admin)
- [ ] Add `review_plan_change_request` endpoint (System Admin)
- [ ] Add email notifications
- [ ] Add tests

### **Frontend**
- [ ] Create plan change request types
- [ ] Add `requestPlanChange` API function
- [ ] Add `getPlanChangeRequests` API function
- [ ] Add `reviewPlanChangeRequest` API function
- [ ] Create "Request Upgrade" page (Company Admin)
- [ ] Create "Request Downgrade" page (Company Admin)
- [ ] Create "My Requests" page (Company Admin)
- [ ] Create "Review Requests" page (System Admin)
- [ ] Add request status badges
- [ ] Add notification system integration

---

## 📝 Summary

| Action | Who | Endpoint | Result |
|--------|-----|----------|--------|
| **Request upgrade** | Company Admin | `POST /plan-change-request` | Creates pending request |
| **Request downgrade** | Company Admin | `POST /plan-change-request` | Creates pending request |
| **View my requests** | Company Admin | `GET /my-plan-change-requests` | Lists company's requests |
| **View all requests** | System Admin | `GET /plan-change-requests` | Lists all pending requests |
| **Approve request** | System Admin | `POST /{id}/review` | Plan changes immediately |
| **Reject request** | System Admin | `POST /{id}/review` | Request marked rejected |

---

*This workflow ensures proper approval process for subscription changes while giving visibility to both company admins and system administrators.*
