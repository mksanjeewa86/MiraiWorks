# MiraiWorks Frontend - Mock Data Replacement TODO

## ✅ **COMPLETED - ALL TASKS FINISHED!**

**Summary**: Successfully replaced all mock data with real API calls across 4 major components:
- 🟢 Candidates Page - Real API integration
- 🟢 Interviews Page - Real API integration
- 🟢 Dashboard Overview - Real API integration
- 🟢 Delete Operations - Real backend calls

**Total Time**: ~1 hour
**Files Modified**: 6 files
**New Files Created**: 1 API service
**Mock Data Eliminated**: 4 instances

---

## 🎯 **Priority Tasks: Replace Mock Data with Real API Calls** (COMPLETED)

### **High Priority**

#### ✅ **1. Candidates Page** - `frontend/src/app/candidates/page.tsx`
- **Lines**: 23-105 (mock data), 116-128 (fetch function), 247-256 (delete)
- **Completed**: ✅ Replaced with real API calls
- **Changes made**:
  - Added `candidatesApi.getCandidates()` for fetching with filters
  - Added `candidatesApi.deleteCandidate(id)` for delete operations
  - Added error handling and display
  - Created new `/api/candidates.ts` service
- **Status**: 🟢 **COMPLETED**

#### ✅ **2. Interviews Page** - `frontend/src/app/interviews/page.tsx`
- **Lines**: 40-87 (mock data), 98-110 (fetch function), 191-200 (delete)
- **Completed**: ✅ Replaced with real API calls
- **Changes made**:
  - Added `interviewsApi.getAll()` for fetching interviews
  - Added `interviewsApi.delete(id)` for delete operations
  - Added error handling and display
  - Used existing `/api/interviews.ts` service
- **Status**: 🟢 **COMPLETED**

### **Medium Priority**

#### ✅ **3. Dashboard CandidateOverview** - `frontend/src/components/dashboard/CandidateOverview.tsx`
- **Lines**: 28-83 (mock data and fetch function)
- **Completed**: ✅ Replaced with real API calls
- **Changes made**:
  - Added `dashboardApi.getStats()` and `dashboardApi.getRecentActivity()`
  - Mapped API responses to component state
  - Added error handling and display
  - Used existing `/api/dashboard.ts` service
- **Status**: 🟢 **COMPLETED**

#### ✅ **4. Delete Operations** - Multiple files
- **Files**:
  - `candidates/page.tsx:247-256` - handleDelete function
  - `interviews/page.tsx:191-200` - handleDelete function
- **Completed**: ✅ Implemented real DELETE API calls
- **Changes made**:
  - Both pages now call actual backend DELETE endpoints
  - Added proper error handling for failed deletes
  - Maintained optimistic UI updates on success
- **Status**: 🟢 **COMPLETED**

---

## 🔄 **Implementation Strategy**

### **Step 1: API Endpoints (Backend)**
Ensure these endpoints exist in the backend:
- `GET /api/candidates` - List all candidates
- `DELETE /api/candidates/{id}` - Delete candidate
- `GET /api/interviews` - List all interviews
- `DELETE /api/interviews/{id}` - Delete interview
- `GET /api/dashboard/candidate-stats` - Dashboard statistics
- `GET /api/dashboard/activity` - Recent activity data

### **Step 2: Frontend API Services**
Create/verify API service functions:
- `candidatesApi.getCandidates(filters?)`
- `candidatesApi.deleteCandidate(id)`
- `interviewsApi.getInterviews(filters?)`
- `interviewsApi.deleteInterview(id)`
- `dashboardApi.getCandidateStats()`
- `dashboardApi.getActivityData()`
- `dashboardApi.getRecentActivity()`

### **Step 3: Replace Mock Data**
For each component:
1. Remove hardcoded mock data arrays
2. Remove setTimeout simulations
3. Implement real async API calls
4. Add proper error handling
5. Update loading states
6. Add data validation

### **Step 4: Testing**
- Test all CRUD operations
- Verify error handling
- Check loading states
- Validate data formats

---

## 📋 **Code Pattern Examples**

### **Before (Mock Data)**
```typescript
const mockData = useMemo(() => [...], []);

useEffect(() => {
  const fetchData = async () => {
    setLoading(true);
    setTimeout(() => {
      setData(mockData);
      setLoading(false);
    }, 1000);
  };
  fetchData();
}, [mockData]);

const handleDelete = (id) => {
  // Only updates local state
  setData(data.filter(item => item.id !== id));
};
```

### **After (Real API)**
```typescript
useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await apiService.getData(filters);
      setData(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  fetchData();
}, [filters]);

const handleDelete = async (id) => {
  try {
    await apiService.deleteItem(id);
    setData(data.filter(item => item.id !== id));
  } catch (err) {
    setError(err.message);
  }
};
```

---

## ✅ **Verification Checklist**

### **For Each Replaced Component:**
- [ ] Mock data arrays removed
- [ ] setTimeout simulations removed
- [ ] Real API calls implemented
- [ ] Error handling added
- [ ] Loading states work correctly
- [ ] Delete operations call backend
- [ ] Data validation in place
- [ ] TypeScript types match API responses
- [ ] Component still renders correctly
- [ ] No console errors

---

## 🚫 **Files That DON'T Need Changes**

### **✅ Already Using Real APIs:**
- `frontend/src/app/jobs/page.tsx` - Uses `positionsApi.getPublic()`
- `frontend/src/app/positions/page.tsx` - Uses `positionsApi.getAll()`
- All files in `frontend/src/api/` - Making real HTTP requests

### **✅ Legitimate Reference Data:**
- `frontend/src/utils/prefectures.ts` - Japanese prefecture data (keep as-is)

---

## 📝 **Notes**

- **Current Status**: 4 instances of mock data identified
- **Estimated Time**: 2-4 hours for complete replacement
- **Dependencies**: Backend API endpoints must exist
- **Testing**: Verify with real backend data after replacement

---

**Last Updated**: 2025-09-20
**Priority**: High - Mock data should be replaced before production deployment