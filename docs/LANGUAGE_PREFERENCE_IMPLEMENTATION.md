# Language Preference Implementation

## Summary

Implemented user-based language preference system for MiraiWorks platform, moving language selection from a standalone UI component to the user settings page.

## Changes Made

### 1. Removed Language Switcher from Navigation

**Files Modified:**
- `frontend/src/components/layout/Topbar.tsx`
- `frontend/src/components/layout/Sidebar.tsx`

**Changes:**
- Removed `LanguageSwitcher` component import
- Removed `LanguageSwitcher` component usage from both Topbar and Sidebar
- Language selection is now exclusively in Settings page

### 2. Updated Settings Page Language Options

**File:** `frontend/src/app/[locale]/(app)/settings/page.tsx`

**Changes:**
- Updated language dropdown to only show English (en) and Japanese (ja)
- Removed Spanish, French, and German options
- Added automatic locale switching when user changes language preference
- Integrated with `useLocaleRouter` for seamless locale navigation

**Implementation:**
```typescript
const updatePreferences = async (field: string, value: string) => {
  setState((prev) => ({
    ...prev,
    settings: prev.settings ? { ...prev.settings, [field]: value } : null,
  }));

  // Auto-save preference setting
  await autoSaveSettings(field, value);

  // If language changed, also update the UI locale
  if (field === 'language' && value !== locale) {
    // Get current pathname and replace locale
    const pathname = window.location.pathname;
    const segments = pathname.split('/');
    segments[1] = value; // Replace locale segment
    const newPath = segments.join('/');

    // Navigate to new locale
    router.push(newPath);
  }
};
```

### 3. Backend Support (Already Exists)

**File:** `backend/app/models/user_settings.py`

The backend already has full support for language preferences:
```python
# UI preferences
language = Column(String(10), nullable=False, default="en")
timezone = Column(String(50), nullable=False, default="America/New_York")
date_format = Column(String(20), nullable=False, default="MM/DD/YYYY")
```

**File:** `backend/app/schemas/user_settings.py`

Schemas already support language field:
```python
class UserSettingsResponse(BaseModel):
    language: str = "en"
    # ...

class UserSettingsUpdate(BaseModel):
    language: Optional[str] = None
    # ...
```

### 4. LanguageSwitcher Component (Retained)

**File:** `frontend/src/components/LanguageSwitcher.tsx`

**Status:** Kept intact for potential future use
- Component still exists and is functional
- Only supports EN and JA locales (from i18n config)
- Can be reused if needed in other parts of the application

## User Flow

### Current Implementation

1. **User logs in** → Sees application in their current locale (browser default or last used)

2. **User navigates to Settings** (`/[locale]/settings`)
   - Clicks on "Preferences" tab
   - Sees "Localization" section with Language dropdown
   - Dropdown shows: English and 日本語 (Japanese)

3. **User changes language**
   - Selects new language from dropdown
   - Language preference is saved to backend automatically (via `autoSaveSettings`)
   - UI immediately switches to new locale
   - URL changes from `/en/settings` to `/ja/settings` (or vice versa)
   - All translations update instantly

4. **User continues browsing**
   - All navigation preserves the selected locale
   - Language preference is persisted in user settings

### Language Preference Persistence

- **Storage:** User's language preference is stored in the `user_settings` table in the database
- **Default:** New users default to English (en)
- **Auto-save:** Changes are saved automatically when user selects a language
- **Immediate effect:** UI switches to new language without page refresh

## Supported Locales

| Locale Code | Language | Native Name |
|-------------|----------|-------------|
| `en` | English | English |
| `ja` | Japanese | 日本語 |

## Configuration

### i18n Configuration

**File:** `frontend/src/i18n/config.ts`

```typescript
export const locales = ['en', 'ja'] as const;
export const defaultLocale: Locale = 'en';

export const localeNames: Record<Locale, string> = {
  en: 'English',
  ja: '日本語',
};

export const routing = defineRouting({
  locales: locales,
  defaultLocale: defaultLocale,
  localePrefix: 'always',
});
```

### Middleware

**File:** `frontend/src/middleware.ts`

The middleware handles locale routing automatically:
- Matches all paths except API routes, static files, and assets
- Applies internationalization to all matching routes
- Enforces locale prefix in URLs (e.g., `/en/dashboard`, `/ja/settings`)

## API Endpoints

### Get User Settings
```
GET /api/user-settings
Response: {
  language: "en" | "ja",
  timezone: string,
  date_format: string,
  // ... other settings
}
```

### Update User Settings
```
PUT /api/user-settings
Body: {
  language: "en" | "ja",
  // ... other settings
}
Response: {
  success: true,
  data: { ... }
}
```

## Testing

### Manual Testing Steps

1. **Test Language Change in Settings**
   ```
   1. Login to the application
   2. Navigate to Settings → Preferences
   3. Change Language dropdown from English to 日本語
   4. Verify:
      - URL changes to /ja/settings
      - All UI text changes to Japanese
      - No page refresh occurs
   5. Change back to English
   6. Verify URL changes to /en/settings and UI updates
   ```

2. **Test Language Persistence**
   ```
   1. Login to the application
   2. Change language to Japanese in Settings
   3. Navigate to Dashboard
   4. Verify dashboard is in Japanese
   5. Navigate to other pages
   6. Verify all pages use Japanese
   7. Logout and login again
   8. Check if language preference persists (currently uses last URL locale)
   ```

3. **Test API Persistence**
   ```
   1. Open browser DevTools → Network tab
   2. Navigate to Settings → Preferences
   3. Change language
   4. Verify PUT request to /api/user-settings
   5. Verify request body contains: { language: "ja" }
   6. Verify response is successful
   ```

## Future Enhancements

### Recommended Improvements

1. **Login-time Locale Detection**
   - On successful login, check user's stored language preference
   - Redirect to user's preferred locale automatically
   - Implementation location: `frontend/src/contexts/AuthContext.tsx` in the `login` function

2. **Profile-level Language Display**
   - Show current language in user profile dropdown
   - Quick language switch option in user menu

3. **Language-specific Welcome Messages**
   - Display different welcome messages based on user's language
   - Use translation keys in dashboard components

4. **Additional Locales**
   - Add more languages as needed (Korean, Chinese, etc.)
   - Update i18n config and create translation files
   - Update settings dropdown options

## Files Modified

```
frontend/src/components/layout/Topbar.tsx          - Removed LanguageSwitcher
frontend/src/components/layout/Sidebar.tsx         - Removed LanguageSwitcher
frontend/src/app/[locale]/(app)/settings/page.tsx  - Updated language dropdown
frontend/src/components/LanguageSwitcher.tsx       - No changes (retained)
backend/app/models/user_settings.py                - No changes (already supported)
backend/app/schemas/user_settings.py               - No changes (already supported)
frontend/src/i18n/config.ts                        - No changes (already configured)
frontend/src/middleware.ts                         - No changes (already configured)
```

## Architecture Decisions

### Why Settings-Only Language Selection?

1. **Cleaner UI:** Removes clutter from navigation bars
2. **Intentional Changes:** Users make deliberate language changes rather than accidental clicks
3. **Persistent Preference:** Encourages users to set their preference once and forget
4. **Standard Pattern:** Many applications follow this pattern (e.g., Gmail, GitHub)

### Why Only EN and JA?

1. **Initial Launch:** Starting with two well-supported languages
2. **Translation Coverage:** Both languages have complete translation namespaces
3. **Target Market:** Primary markets are English and Japanese speakers
4. **Easy Expansion:** Architecture supports adding more languages in the future

### Why Immediate Locale Switching?

1. **Better UX:** Users see changes immediately without reloading
2. **Modern Approach:** Single-page application behavior
3. **Seamless Transition:** URL and UI update together
4. **Validation:** Users can immediately verify their selection

## Troubleshooting

### Language doesn't change when selected

**Solution:** Check browser console for errors. Verify:
- `useLocaleRouter` hook is properly imported
- Router navigation is not blocked
- URL pattern matches locale-first routing (`/[locale]/path`)

### Language resets after page reload

**Solution:** This is expected behavior currently. To implement persistence:
1. Update AuthContext to redirect to user's preferred locale on login
2. Add locale detection in middleware based on user session
3. Store locale preference in localStorage as backup

### Settings page not saving language

**Solution:** Check:
- Network tab shows PUT request to `/api/user-settings`
- Backend user_settings endpoint is accessible
- User is authenticated
- Database has `language` column in `user_settings` table

## Related Documentation

- [I18N Implementation Summary](./I18N_IMPLEMENTATION_SUMMARY.md)
- [I18N Setup Complete](./I18N_SETUP_COMPLETE.md)
- [Locale Routing Fix](./LOCALE_ROUTING_FIX.md)
- [Routes Update Summary](../ROUTES_UPDATE_SUMMARY.md)

---

**Last Updated:** 2025-10-10
**Status:** ✅ Complete
**Version:** 1.0
