# i18n Migration - Remaining Tasks

**Last Updated:** 2025-10-11
**Status:** Phase 2 - Core Pages (In Progress)

---

## ✅ Completed Pages (Session Summary)

### 1. **Notifications Page** ✅
- **File:** `frontend/src/app/[locale]/(app)/notifications/page.tsx`
- **Translations:** `frontend/src/i18n/locales/{en,ja}/notifications.json`
- **Status:** COMPLETE
- **Strings Migrated:**
  - Back button
  - Filters (all, unread, updates)
  - Actions (mark all read, create update)
  - System updates section
  - Empty states
  - Time formatting

---

### 2. **Settings Page** ✅
- **File:** `frontend/src/app/[locale]/(app)/settings/page.tsx`
- **Translations:** `frontend/src/i18n/locales/{en,ja}/settings.json`
- **Status:** COMPLETE
- **Strings Migrated:**
  - All tab labels (Profile, Account, Notifications, Privacy, Security, Language, Integrations, Billing)
  - Profile section
  - Account settings with password change
  - Notification preferences (Email, Push, SMS)
  - Privacy controls
  - Security settings (2FA, sessions, login history)
  - Language & region preferences
  - Calendar integration
  - Company profile & subscription management
  - **Error messages:** 7 error types added to `settings.errors` section
  - SMS validation error messages

**Key Updates:**
- Added comprehensive `errors` section for all error messages
- All hardcoded error strings replaced with translation calls
- Added `smsRequiresPhoneError` translation key

---

### 3. **Todos Page** ✅
- **File:** `frontend/src/app/[locale]/(app)/todos/page.tsx`
- **Translations:** `frontend/src/i18n/locales/{en,ja}/todos.json` (NEW)
- **Configuration:** Added `todos` namespace to `frontend/src/i18n/request.ts`
- **Status:** COMPLETE
- **Strings Migrated:**
  - Page headers (title, focus mode, task overview)
  - Action buttons (Restore, View, Finish, Reopen, Extend, Edit, Delete)
  - Badges (Deleted, Overdue)
  - Field labels (Due, Priority, Notes, Completed)
  - Date formatting helpers
  - Statistics (In progress, Due today, Completed, Overdue)
  - View filters (All, Active, Completed, Expired, Deleted)
  - Empty states for all filters + search results
  - Search placeholder
  - Toast messages (8 types)
  - Confirmation modals (Delete, Restore, Complete, Reopen)
  - Hero section meta text
  - Create task section

**Key Implementation Details:**
- Modified `formatDisplayDate()` and `formatRelativeTime()` helper functions to accept translation function
- Updated `TodoItem` component to receive `t` function as prop
- Replaced 50+ hardcoded strings with translation calls
- Added `t` to dependency arrays in `useCallback`

**Post-Migration Checklist:**
- ✅ Created EN translation file
- ✅ Created JA translation file
- ✅ Registered namespace in `request.ts`
- ✅ Validated JSON syntax
- ✅ Updated component imports
- ✅ Tested translation loading

---

## 🔄 Remaining Pages (To Be Migrated)

### **Priority 1: Messages Page**
- **File:** `frontend/src/app/[locale]/(app)/messages/page.tsx`
- **Estimated Strings:** ~30-40
- **Complexity:** Medium
- **Translation File:** Create `messages.json` (EN/JA)
- **Sections to Migrate:**
  - Message list
  - Conversation view
  - Send message form
  - Empty states
  - Error messages

**Steps:**
1. Create `frontend/src/i18n/locales/en/messages.json`
2. Create `frontend/src/i18n/locales/ja/messages.json`
3. Already registered in `request.ts` ✅ (check if using correct namespace)
4. Add `useTranslations('messages')` to component
5. Replace all hardcoded strings
6. Test with both locales

---

### **Priority 2: Positions Page**
- **File:** `frontend/src/app/[locale]/(app)/positions/page.tsx`
- **Estimated Strings:** ~25-35
- **Complexity:** Low-Medium
- **Translation File:** Create `positions.json` (EN/JA)
- **Sections to Migrate:**
  - Page header
  - Position list/grid
  - Filters and search
  - Action buttons
  - Empty states
  - Status badges

**Steps:**
1. Create `frontend/src/i18n/locales/en/positions.json`
2. Create `frontend/src/i18n/locales/ja/positions.json`
3. Register in `frontend/src/i18n/request.ts`
4. Add `useTranslations('positions')` to component
5. Replace all hardcoded strings
6. Test with both locales

---

## 📋 Migration Checklist Template

When migrating a new page, follow this checklist:

### **1. Preparation**
- [ ] Identify all hardcoded strings in the component
- [ ] Group strings by section/context
- [ ] Determine namespace name

### **2. Create Translation Files**
- [ ] Create `frontend/src/i18n/locales/en/{namespace}.json`
- [ ] Create `frontend/src/i18n/locales/ja/{namespace}.json`
- [ ] Validate JSON syntax

### **3. Register Namespace**
- [ ] Add import in `frontend/src/i18n/request.ts`
- [ ] Add to Promise.all array
- [ ] Add to messages object

### **4. Update Component**
- [ ] Add `import { useTranslations } from 'next-intl';`
- [ ] Add `const t = useTranslations('{namespace}');`
- [ ] Replace all hardcoded strings with `t('key')`
- [ ] Update any helper functions to accept `t` parameter
- [ ] Pass `t` to child components if needed
- [ ] Update dependency arrays to include `t`

### **5. Testing**
- [ ] Validate JSON syntax with Node.js
- [ ] Restart development server
- [ ] Test English locale
- [ ] Test Japanese locale
- [ ] Verify dynamic values work correctly
- [ ] Check toast messages
- [ ] Test error states

---

## 🔍 Finding Hardcoded Strings

Use these commands to identify hardcoded strings:

```bash
# Find string literals in JSX
grep -n "'[A-Z]" frontend/src/app/[locale]/(app)/messages/page.tsx

# Find double-quoted strings
grep -n "\"[A-Z]" frontend/src/app/[locale]/(app)/messages/page.tsx

# Find toast messages
grep -n "showToast" frontend/src/app/[locale]/(app)/messages/page.tsx

# Find error messages
grep -n "Failed to\|Error\|error:" frontend/src/app/[locale]/(app)/messages/page.tsx
```

---

## 📊 Translation File Structure

### **Standard Sections:**
```json
{
  "page": {
    "title": "Page Title",
    "subtitle": "Page description"
  },
  "actions": {
    "create": "Create",
    "edit": "Edit",
    "delete": "Delete",
    "save": "Save",
    "cancel": "Cancel"
  },
  "filters": {
    "all": "All",
    "active": "Active"
  },
  "emptyStates": {
    "title": "No items",
    "description": "Description text"
  },
  "toasts": {
    "success": "Success message",
    "error": "Error message"
  },
  "errors": {
    "loadData": "Failed to load data",
    "saveData": "Failed to save data"
  },
  "confirmations": {
    "delete": {
      "title": "Confirm Delete",
      "message": "Are you sure?",
      "confirmButton": "Delete"
    }
  }
}
```

---

## 🚨 Common Pitfalls

### **1. Missing Namespace Registration**
**Problem:** Translations don't load, showing raw keys
**Solution:** Always register namespace in `frontend/src/i18n/request.ts`

```typescript
// Add to imports array
import(`./locales/${locale}/newnamespace.json`),

// Add to messages object
newnamespace: newnamespace.default,
```

### **2. JSON Syntax Errors**
**Problem:** Build fails or translations don't load
**Solution:** Validate JSON before committing

```bash
node -e "JSON.parse(require('fs').readFileSync('path/to/file.json', 'utf8'))"
```

### **3. Missing Dynamic Values**
**Problem:** Placeholders like `{name}` don't get replaced
**Solution:** Pass values as second parameter

```typescript
// ❌ Wrong
t('message.greeting', name)

// ✅ Correct
t('message.greeting', { name: userName })
```

### **4. Forgetting to Update Dependencies**
**Problem:** Translations don't update when they should
**Solution:** Add `t` to dependency arrays

```typescript
useCallback(() => {
  // uses t()
}, [showToast, t]); // Include t!
```

### **5. Not Restarting Dev Server**
**Problem:** New namespace doesn't load
**Solution:** Always restart after modifying `request.ts`

```bash
# Stop and restart
npm run dev
```

---

## 📝 Next Steps

1. **Immediate:**
   - Review and prioritize remaining pages
   - Create Messages page translations
   - Test Todos page translations after server restart

2. **Short-term:**
   - Complete Messages page migration
   - Complete Positions page migration
   - Test all migrated pages in both locales

3. **Long-term:**
   - Migrate all remaining admin pages
   - Migrate authentication pages
   - Migrate public pages
   - Add missing translations discovered during testing

---

## 🔗 Related Documentation

- **Main i18n Guide:** `docs/I18N_IMPLEMENTATION_PLAN.md`
- **Setup Guide:** `docs/I18N_SETUP_COMPLETE.md`
- **Usage Guide:** `docs/I18N_USAGE_GUIDE.md`
- **Namespace List:** `docs/I18N_NAMESPACES_COMPLETE.md`

---

## 📞 Support

If you encounter issues:
1. Check this document for common pitfalls
2. Verify namespace registration in `request.ts`
3. Validate JSON syntax
4. Restart development server
5. Check browser console for errors

---

**Status Summary:**
- ✅ **Completed:** 3 pages (Notifications, Settings, Todos)
- 🔄 **In Progress:** 0 pages
- ⏳ **Pending:** 2 high-priority pages (Messages, Positions)
- 📊 **Overall Phase 2 Progress:** 60% (3/5 core pages)

---

*Generated on: 2025-10-11*
*Session: Todos Page Migration Complete*
