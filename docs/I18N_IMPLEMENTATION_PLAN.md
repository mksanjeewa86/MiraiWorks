# MiraiWorks i18n Implementation Plan

**Languages**: English (en) and Japanese (ja)
**Target Completion**: 8 weeks
**Last Updated**: January 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Frontend Architecture](#frontend-architecture)
4. [Backend Architecture](#backend-architecture)
5. [Translation File Structure](#translation-file-structure)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Code Examples](#code-examples)
8. [Testing & Quality Assurance](#testing--quality-assurance)
9. [Best Practices](#best-practices)
10. [Maintenance & Updates](#maintenance--updates)

---

## 📖 Overview

### Goals
- Support English and Japanese languages across the entire application
- Provide seamless language switching without page reload
- Persist user language preferences
- Translate all UI elements, error messages, and notifications
- Maintain type safety with TypeScript
- Support both server and client components (Next.js 14 App Router)

### Current State
- ✅ User settings already include language preference field (`language: 'en' | 'es' | 'fr' | 'de' | 'ja'`)
- ✅ Database stores timezone-aware timestamps in UTC
- ✅ Settings page has language selector (lines 880-908)
- ❌ No i18n library installed yet
- ❌ All strings are hardcoded in English

---

## 🔧 Technology Stack

### Frontend
- **Library**: `next-intl` (v3.x)
- **Why**: Built specifically for Next.js 14 App Router, supports Server Components, type-safe
- **Alternative Considered**: react-i18next (rejected due to client-only focus)

### Backend
- **Library**: `babel` (Python i18n)
- **Approach**: Accept-Language header + user preferences
- **Translation Format**: JSON files

### Date/Time Formatting
- **Library**: `date-fns` with locale support
- **Formats**:
  - English: MM/DD/YYYY
  - Japanese: YYYY年MM月DD日

### Currency Formatting
- **Library**: `Intl.NumberFormat`
- **Currencies**:
  - English: USD ($)
  - Japanese: JPY (¥)

---

## 📁 Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── i18n/
│   │   ├── locales/              # Translation files
│   │   │   ├── en/
│   │   │   │   ├── common.json       # Common UI strings
│   │   │   │   ├── auth.json         # Authentication pages
│   │   │   │   ├── dashboard.json    # Dashboard content
│   │   │   │   ├── jobs.json         # Job postings
│   │   │   │   ├── interviews.json   # Interview management
│   │   │   │   ├── candidates.json   # Candidate management
│   │   │   │   ├── workflows.json    # Recruitment workflows
│   │   │   │   ├── settings.json     # Settings page
│   │   │   │   ├── calendar.json     # Calendar integration
│   │   │   │   ├── messages.json     # Messaging system
│   │   │   │   ├── exams.json        # Exam management
│   │   │   │   ├── subscription.json # Subscription plans
│   │   │   │   ├── errors.json       # Error messages
│   │   │   │   └── validation.json   # Form validation
│   │   │   └── ja/
│   │   │       ├── common.json
│   │   │       ├── auth.json
│   │   │       ├── dashboard.json
│   │   │       ├── jobs.json
│   │   │       ├── interviews.json
│   │   │       ├── candidates.json
│   │   │       ├── workflows.json
│   │   │       ├── settings.json
│   │   │       ├── calendar.json
│   │   │       ├── messages.json
│   │   │       ├── exams.json
│   │   │       ├── subscription.json
│   │   │       ├── errors.json
│   │   │       └── validation.json
│   │   ├── config.ts             # i18n configuration
│   │   └── request.ts            # Server-side i18n setup
│   ├── middleware.ts             # Locale detection middleware
│   └── app/
│       └── [locale]/             # New locale-based routing
│           ├── layout.tsx
│           └── (existing routes move here)
```

### Locale Configuration

**File**: `src/i18n/config.ts`
```typescript
export const locales = ['en', 'ja'] as const;
export type Locale = typeof locales[number];

export const defaultLocale: Locale = 'en';

export const localeNames: Record<Locale, string> = {
  en: 'English',
  ja: '日本語',
};
```

### Middleware Configuration

**File**: `src/middleware.ts`
```typescript
import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './i18n/config';

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'always', // URLs: /en/dashboard, /ja/dashboard
});

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
};
```

---

## 🔧 Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── i18n/
│   │   ├── locales/
│   │   │   ├── en.json       # English error messages, notifications
│   │   │   └── ja.json       # Japanese error messages, notifications
│   │   └── translate.py      # Translation utility
```

### Translation Utility

**File**: `backend/app/i18n/translate.py`
```python
import json
from pathlib import Path
from typing import Dict

class Translator:
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self):
        locale_dir = Path(__file__).parent / "locales"
        for locale_file in locale_dir.glob("*.json"):
            locale = locale_file.stem
            with open(locale_file, "r", encoding="utf-8") as f:
                self.translations[locale] = json.load(f)

    def t(self, key: str, locale: str = "en", **kwargs) -> str:
        """Translate a key with optional formatting"""
        translation = self.translations.get(locale, {}).get(key, key)
        return translation.format(**kwargs) if kwargs else translation

translator = Translator()
```

### Locale Detection

**File**: `backend/app/dependencies.py`
```python
from fastapi import Header, Depends
from app.models.user import User

async def get_user_locale(
    accept_language: str = Header(None, alias="Accept-Language"),
    current_user: User = Depends(get_current_active_user)
) -> str:
    """Get user's preferred language from settings or header"""
    if current_user and current_user.settings:
        return current_user.settings.language

    # Parse Accept-Language header
    if accept_language:
        # Extract first locale (e.g., "ja-JP,ja;q=0.9,en;q=0.8" -> "ja")
        locale = accept_language.split(",")[0].split("-")[0]
        return locale if locale in ["en", "ja"] else "en"

    return "en"  # Default to English
```

---

## 📝 Translation File Structure

### Frontend: `en/common.json`
```json
{
  "nav": {
    "dashboard": "Dashboard",
    "jobs": "Jobs",
    "candidates": "Candidates",
    "interviews": "Interviews",
    "calendar": "Calendar",
    "messages": "Messages",
    "settings": "Settings",
    "logout": "Logout"
  },
  "buttons": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "create": "Create",
    "search": "Search",
    "filter": "Filter",
    "export": "Export",
    "import": "Import"
  },
  "status": {
    "active": "Active",
    "inactive": "Inactive",
    "pending": "Pending",
    "completed": "Completed",
    "cancelled": "Cancelled"
  }
}
```

### Frontend: `ja/common.json`
```json
{
  "nav": {
    "dashboard": "ダッシュボード",
    "jobs": "求人",
    "candidates": "候補者",
    "interviews": "面接",
    "calendar": "カレンダー",
    "messages": "メッセージ",
    "settings": "設定",
    "logout": "ログアウト"
  },
  "buttons": {
    "save": "保存",
    "cancel": "キャンセル",
    "delete": "削除",
    "edit": "編集",
    "create": "作成",
    "search": "検索",
    "filter": "フィルター",
    "export": "エクスポート",
    "import": "インポート"
  },
  "status": {
    "active": "有効",
    "inactive": "無効",
    "pending": "保留中",
    "completed": "完了",
    "cancelled": "キャンセル済み"
  }
}
```

### Frontend: `en/auth.json`
```json
{
  "login": {
    "title": "Sign In",
    "emailLabel": "Email Address",
    "emailPlaceholder": "Enter your email",
    "passwordLabel": "Password",
    "passwordPlaceholder": "Enter your password",
    "rememberMe": "Remember me",
    "forgotPassword": "Forgot password?",
    "submitButton": "Sign In",
    "noAccount": "Don't have an account?",
    "signUpLink": "Sign up",
    "errors": {
      "invalidCredentials": "Invalid email or password",
      "requiredEmail": "Email is required",
      "requiredPassword": "Password is required"
    }
  },
  "register": {
    "title": "Create Account",
    "firstNameLabel": "First Name",
    "lastNameLabel": "Last Name",
    "emailLabel": "Email Address",
    "passwordLabel": "Password",
    "confirmPasswordLabel": "Confirm Password",
    "submitButton": "Create Account",
    "haveAccount": "Already have an account?",
    "signInLink": "Sign in"
  }
}
```

### Frontend: `ja/auth.json`
```json
{
  "login": {
    "title": "ログイン",
    "emailLabel": "メールアドレス",
    "emailPlaceholder": "メールアドレスを入力",
    "passwordLabel": "パスワード",
    "passwordPlaceholder": "パスワードを入力",
    "rememberMe": "ログイン状態を保持",
    "forgotPassword": "パスワードをお忘れですか？",
    "submitButton": "ログイン",
    "noAccount": "アカウントをお持ちでないですか？",
    "signUpLink": "新規登録",
    "errors": {
      "invalidCredentials": "メールアドレスまたはパスワードが無効です",
      "requiredEmail": "メールアドレスは必須です",
      "requiredPassword": "パスワードは必須です"
    }
  },
  "register": {
    "title": "アカウント作成",
    "firstNameLabel": "名",
    "lastNameLabel": "姓",
    "emailLabel": "メールアドレス",
    "passwordLabel": "パスワード",
    "confirmPasswordLabel": "パスワード確認",
    "submitButton": "アカウント作成",
    "haveAccount": "既にアカウントをお持ちですか？",
    "signInLink": "ログイン"
  }
}
```

### Backend: `en.json`
```json
{
  "errors": {
    "user_not_found": "User not found",
    "invalid_credentials": "Invalid email or password",
    "unauthorized": "You are not authorized to perform this action",
    "validation_failed": "Validation failed: {details}",
    "server_error": "An internal server error occurred",
    "token_expired": "Your session has expired. Please login again"
  },
  "success": {
    "user_created": "User created successfully",
    "profile_updated": "Profile updated successfully",
    "password_changed": "Password changed successfully",
    "interview_scheduled": "Interview has been scheduled for {datetime}"
  }
}
```

### Backend: `ja.json`
```json
{
  "errors": {
    "user_not_found": "ユーザーが見つかりません",
    "invalid_credentials": "メールアドレスまたはパスワードが無効です",
    "unauthorized": "この操作を実行する権限がありません",
    "validation_failed": "検証に失敗しました：{details}",
    "server_error": "内部サーバーエラーが発生しました",
    "token_expired": "セッションの有効期限が切れました。再度ログインしてください"
  },
  "success": {
    "user_created": "ユーザーが正常に作成されました",
    "profile_updated": "プロフィールが正常に更新されました",
    "password_changed": "パスワードが正常に変更されました",
    "interview_scheduled": "{datetime}に面接がスケジュールされました"
  }
}
```

---

## 🚀 Implementation Roadmap

### Phase 1: Setup & Infrastructure (Week 1)

#### 1.1 Install Dependencies
```bash
# Frontend
cd frontend
npm install next-intl

# Backend
cd backend
pip install babel
```

#### 1.2 Create Configuration Files
- [ ] Create `src/i18n/config.ts`
- [ ] Create `src/i18n/request.ts`
- [ ] Create `src/middleware.ts`
- [ ] Create backend `app/i18n/translate.py`

#### 1.3 Update App Router Structure
- [ ] Create `app/[locale]` directory
- [ ] Move existing routes under `[locale]`
- [ ] Update `app/[locale]/layout.tsx` with NextIntlClientProvider
- [ ] Test basic routing: `/en/dashboard`, `/ja/dashboard`

---

### Phase 2: Create Translation Files (Week 2)

#### 2.1 Core Translation Files
- [ ] `en/common.json` + `ja/common.json`
- [ ] `en/auth.json` + `ja/auth.json`
- [ ] `en/errors.json` + `ja/errors.json`
- [ ] `en/validation.json` + `ja/validation.json`

#### 2.2 Backend Translation Files
- [ ] `backend/app/i18n/locales/en.json`
- [ ] `backend/app/i18n/locales/ja.json`

#### 2.3 Translation Guidelines Document
- [ ] Create translation style guide
- [ ] Document key naming conventions
- [ ] List common phrases and their translations

---

### Phase 3: Update Components (Week 3-4)

#### 3.1 Authentication Pages (High Priority)
- [ ] `app/[locale]/auth/login/page.tsx`
- [ ] `app/[locale]/auth/register/page.tsx`
- [ ] `app/[locale]/auth/forgot-password/page.tsx`
- [ ] `app/[locale]/auth/two-factor/page.tsx`
- [ ] `app/[locale]/activate/[userId]/page.tsx`

#### 3.2 Navigation & Layout
- [ ] `components/layout/Sidebar.tsx`
- [ ] `components/layout/AppLayout.tsx`
- [ ] Update navigation menu items

#### 3.3 Dashboard & Core Pages
- [ ] `app/[locale]/(app)/dashboard/page.tsx`
- [ ] `app/[locale]/(app)/settings/page.tsx`
- [ ] Update status badges, buttons, common UI

#### 3.4 Create Translation Files for:
- [ ] `en/settings.json` + `ja/settings.json`
- [ ] `en/dashboard.json` + `ja/dashboard.json`

---

### Phase 4: Feature Pages (Week 5)

#### 4.1 Job Management
- [ ] `app/[locale]/(app)/jobs/page.tsx`
- [ ] `app/[locale]/(app)/positions/page.tsx`
- [ ] Create `en/jobs.json` + `ja/jobs.json`

#### 4.2 Candidate Management
- [ ] `app/[locale]/(app)/candidates/page.tsx`
- [ ] Create `en/candidates.json` + `ja/candidates.json`

#### 4.3 Interview Scheduling
- [ ] `app/[locale]/(app)/interviews/page.tsx`
- [ ] `app/[locale]/(app)/interviews/[id]/page.tsx`
- [ ] Create `en/interviews.json` + `ja/interviews.json`

#### 4.4 Calendar Integration
- [ ] `app/[locale]/(app)/calendar/page.tsx`
- [ ] Create `en/calendar.json` + `ja/calendar.json`

---

### Phase 5: Backend Translation (Week 6)

#### 5.1 Update Endpoints
- [ ] `app/endpoints/auth.py` - Add locale parameter
- [ ] `app/endpoints/users.py` - Translate error messages
- [ ] `app/endpoints/jobs.py` - Translate notifications
- [ ] `app/endpoints/interviews.py` - Translate success messages

#### 5.2 Error Handling
- [ ] Update HTTPException messages to use translator
- [ ] Add locale parameter to all endpoints
- [ ] Test error messages in both languages

---

### Phase 6: Language Switcher (Week 7)

#### 6.1 Create Language Switcher Component
- [ ] `components/LanguageSwitcher.tsx`
- [ ] Add to Sidebar
- [ ] Add to Settings page
- [ ] Update user settings API when language changes

#### 6.2 Locale Persistence
- [ ] Save language preference to database
- [ ] Load language preference on login
- [ ] Update Accept-Language header

---

### Phase 7: Testing & QA (Week 8)

#### 7.1 Functional Testing
- [ ] All pages render in both languages
- [ ] Language switcher updates URL and content
- [ ] User language preference persists after login
- [ ] API error messages display in correct language
- [ ] Form validation messages are translated

#### 7.2 Localization Testing
- [ ] Date/time formatting matches locale
- [ ] Currency formatting (USD vs JPY)
- [ ] Number formatting (1,000 vs 1.000)
- [ ] Japanese characters display correctly
- [ ] Text wrapping works for Japanese

#### 7.3 Browser Testing
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers

---

### Phase 8: Documentation & Deployment (Week 8)

#### 8.1 Documentation
- [ ] Create translator guide for adding new languages
- [ ] Document translation workflow
- [ ] Update README with i18n instructions

#### 8.2 Deployment
- [ ] Test in staging environment
- [ ] Verify both locales work correctly
- [ ] Monitor for missing translations
- [ ] Deploy to production
- [ ] Update user documentation

---

## 💻 Code Examples

### Client Component Translation

**Before (hardcoded):**
```typescript
// frontend/src/app/auth/login/page.tsx
export default function LoginPage() {
  return (
    <div>
      <h1>Sign In</h1>
      <form>
        <label>Email Address</label>
        <input type="email" placeholder="Enter your email" />
        <button type="submit">Sign In</button>
      </form>
    </div>
  );
}
```

**After (translated):**
```typescript
// frontend/src/app/[locale]/auth/login/page.tsx
'use client';

import { useTranslations } from 'next-intl';

export default function LoginPage() {
  const t = useTranslations('auth.login');

  return (
    <div>
      <h1>{t('title')}</h1>
      <form>
        <label>{t('emailLabel')}</label>
        <input type="email" placeholder={t('emailPlaceholder')} />
        <button type="submit">{t('submitButton')}</button>
      </form>
    </div>
  );
}
```

### Server Component Translation

```typescript
// frontend/src/app/[locale]/dashboard/page.tsx
import { useTranslations } from 'next-intl';
import { unstable_setRequestLocale } from 'next-intl/server';

export default function DashboardPage({
  params: { locale },
}: {
  params: { locale: string };
}) {
  unstable_setRequestLocale(locale);
  const t = useTranslations('dashboard');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('welcome')}</p>
    </div>
  );
}
```

### Language Switcher Component

```typescript
// frontend/src/components/LanguageSwitcher.tsx
'use client';

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { locales, localeNames } from '@/i18n/config';
import { userSettingsApi } from '@/api/userSettings';
import { Globe } from 'lucide-react';

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = async (newLocale: string) => {
    // Update user settings in database
    await userSettingsApi.updateSettings({ language: newLocale });

    // Navigate to new locale
    const newPath = pathname.replace(`/${locale}`, `/${newLocale}`);
    router.push(newPath);
    router.refresh();
  };

  return (
    <div className="flex items-center gap-2">
      <Globe className="h-4 w-4" />
      <select
        value={locale}
        onChange={(e) => handleChange(e.target.value)}
        className="p-2 border rounded"
      >
        {locales.map((loc) => (
          <option key={loc} value={loc}>
            {localeNames[loc]}
          </option>
        ))}
      </select>
    </div>
  );
}
```

### Backend Endpoint Translation

**Before:**
```python
# backend/app/endpoints/auth.py
@router.post("/login")
async def login(credentials: LoginRequest):
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": generate_token(user)}
```

**After:**
```python
# backend/app/endpoints/auth.py
from app.i18n.translate import translator
from app.dependencies import get_user_locale

@router.post("/login")
async def login(
    credentials: LoginRequest,
    locale: str = Depends(get_user_locale)
):
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail=translator.t("errors.invalid_credentials", locale=locale)
        )
    return {"token": generate_token(user)}
```

### Date Formatting

```typescript
// Use date-fns with locale
import { format } from 'date-fns';
import { ja, enUS } from 'date-fns/locale';
import { useLocale } from 'next-intl';

export function FormattedDate({ date }: { date: Date }) {
  const locale = useLocale();
  const dateLocale = locale === 'ja' ? ja : enUS;

  return <span>{format(date, 'PPP', { locale: dateLocale })}</span>;
}

// Output:
// English: "January 10, 2025"
// Japanese: "2025年1月10日"
```

### Currency Formatting

```typescript
// Update existing formatPrice function
const formatPrice = (price: string | number, locale: string) => {
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;

  return new Intl.NumberFormat(locale === 'ja' ? 'ja-JP' : 'en-US', {
    style: 'currency',
    currency: locale === 'ja' ? 'JPY' : 'USD',
    minimumFractionDigits: 0,
  }).format(numPrice);
};

// Usage in component:
import { useLocale } from 'next-intl';

export function PriceDisplay({ amount }: { amount: number }) {
  const locale = useLocale();
  return <span>{formatPrice(amount, locale)}</span>;
}

// Output:
// English: "$1,000"
// Japanese: "¥1,000"
```

---

## 🧪 Testing & Quality Assurance

### Testing Checklist

#### Functional Tests
- [ ] All pages render in both English and Japanese
- [ ] Language switcher updates URL correctly (`/en/...` → `/ja/...`)
- [ ] Language switcher updates content without full page reload
- [ ] User language preference persists after logout/login
- [ ] API error messages display in correct language
- [ ] Form validation messages are translated
- [ ] Toast notifications appear in correct language
- [ ] Email notifications sent in user's preferred language

#### Localization Tests
- [ ] Date formatting matches locale conventions
  - English: MM/DD/YYYY (e.g., "01/10/2025")
  - Japanese: YYYY年MM月DD日 (e.g., "2025年1月10日")
- [ ] Time formatting matches locale conventions
  - English: 12-hour (e.g., "3:30 PM")
  - Japanese: 24-hour (e.g., "15:30")
- [ ] Currency formatting correct
  - English: $1,000.00
  - Japanese: ¥1,000
- [ ] Number formatting correct
  - English: 1,000.50
  - Japanese: 1,000.50

#### Japanese-Specific Tests
- [ ] Japanese characters (Hiragana, Katakana, Kanji) display correctly
- [ ] Text wrapping works properly for Japanese text
- [ ] Form inputs accept Japanese IME input
- [ ] Search functionality works with Japanese queries
- [ ] Japanese text doesn't break UI layout
- [ ] Font rendering is clear and readable

#### Browser Compatibility
- [ ] Chrome (Windows, Mac, Android)
- [ ] Firefox (Windows, Mac)
- [ ] Safari (Mac, iOS)
- [ ] Edge (Windows)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

#### Accessibility Tests
- [ ] Screen readers announce content in correct language
- [ ] Language attribute set correctly on HTML element
- [ ] RTL support (not needed for Japanese, but document for future)

---

## 📚 Best Practices

### Translation Keys

#### Naming Convention
```json
{
  "section.subsection.element": "Translation"
}
```

#### Examples
```json
{
  "auth.login.title": "Sign In",
  "auth.login.emailLabel": "Email Address",
  "auth.login.errors.invalidCredentials": "Invalid email or password",
  "dashboard.stats.totalUsers": "Total Users",
  "settings.profile.firstName": "First Name"
}
```

### Avoid Hardcoded Strings

❌ **Bad:**
```typescript
<button>Save Changes</button>
<p>You have {count} unread messages</p>
```

✅ **Good:**
```typescript
const t = useTranslations('common');

<button>{t('buttons.save')}</button>
<p>{t('messages.unreadCount', { count })}</p>
```

### Handle Pluralization

**Translation file:**
```json
{
  "messages": {
    "unread": {
      "zero": "No unread messages",
      "one": "1 unread message",
      "other": "{count} unread messages"
    }
  }
}
```

**Component:**
```typescript
const t = useTranslations('messages');

<p>{t('unread', { count })}</p>
```

### Handle Dynamic Content

**Translation file:**
```json
{
  "interview": {
    "scheduled": "Interview scheduled for {date} at {time}",
    "withCandidate": "Interview with {candidateName}"
  }
}
```

**Component:**
```typescript
const t = useTranslations('interview');

<p>{t('scheduled', { date: formattedDate, time: formattedTime })}</p>
<p>{t('withCandidate', { candidateName: candidate.name })}</p>
```

### Keep Translations Contextual

❌ **Bad (too generic):**
```json
{
  "name": "Name",
  "email": "Email"
}
```

✅ **Good (contextual):**
```json
{
  "userProfile.fullName": "Full Name",
  "userProfile.emailAddress": "Email Address",
  "jobPosting.companyName": "Company Name",
  "jobPosting.contactEmail": "Contact Email"
}
```

### Separate UI Text from Data

❌ **Bad:**
```typescript
// Don't translate database values in frontend
const status = t(`status.${job.status}`); // job.status from database
```

✅ **Good:**
```typescript
// Use mapping for database enums
const statusMap = {
  active: t('status.active'),
  inactive: t('status.inactive'),
  pending: t('status.pending'),
};

const statusText = statusMap[job.status];
```

---

## 🔄 Maintenance & Updates

### Adding New Translations

1. **Identify the section** where translation belongs (e.g., `jobs`, `interviews`)
2. **Add to English file** first: `locales/en/[section].json`
3. **Add to Japanese file**: `locales/ja/[section].json`
4. **Use in component**: `const t = useTranslations('[section]')`
5. **Test both languages** to ensure correct rendering

### Adding a New Language (Future)

1. Add locale to `src/i18n/config.ts`:
   ```typescript
   export const locales = ['en', 'ja', 'es'] as const; // Add 'es'
   ```

2. Create translation directory:
   ```
   src/i18n/locales/es/
   ```

3. Copy all JSON files from `en/` to `es/` and translate

4. Update `localeNames`:
   ```typescript
   export const localeNames: Record<Locale, string> = {
     en: 'English',
     ja: '日本語',
     es: 'Español',
   };
   ```

5. Add backend translations: `backend/app/i18n/locales/es.json`

### Translation Workflow

#### For Developers:
1. Write code using English keys
2. Add keys to `en/[section].json`
3. Mark for translation: Add TODO comment
4. Create PR with English translations only

#### For Translators:
1. Review new keys in `en/[section].json`
2. Add translations to `ja/[section].json`
3. Test translations in UI
4. Submit PR with Japanese translations

### Missing Translation Handling

**next-intl automatically falls back to English** if a Japanese translation is missing:

```typescript
// If 'ja/auth.json' is missing a key, it will use 'en/auth.json'
const t = useTranslations('auth');
t('login.title'); // Falls back to English if Japanese missing
```

### Translation Quality Checks

- [ ] No untranslated strings in production
- [ ] Consistent terminology across files
- [ ] Proper use of formal/informal language
- [ ] Cultural appropriateness
- [ ] No machine translation artifacts
- [ ] Proper handling of gender-neutral language

---

## 📊 Progress Tracking

### Implementation Status

| Phase | Status | Start Date | End Date | Notes |
|-------|--------|------------|----------|-------|
| Phase 1: Setup & Infrastructure | ⏳ Pending | - | - | Install next-intl, configure i18n |
| Phase 2: Translation Files | ⏳ Pending | - | - | Create core JSON files |
| Phase 3: Update Components | ⏳ Pending | - | - | Convert auth & core pages |
| Phase 4: Feature Pages | ⏳ Pending | - | - | Jobs, candidates, interviews |
| Phase 5: Backend Translation | ⏳ Pending | - | - | API error messages |
| Phase 6: Language Switcher | ⏳ Pending | - | - | UI component for switching |
| Phase 7: Testing & QA | ⏳ Pending | - | - | Comprehensive testing |
| Phase 8: Documentation | ⏳ Pending | - | - | Guide for translators |

### Translation Coverage

| Section | English | Japanese | Status |
|---------|---------|----------|--------|
| Common UI | ⏳ 0% | ⏳ 0% | Not started |
| Authentication | ⏳ 0% | ⏳ 0% | Not started |
| Dashboard | ⏳ 0% | ⏳ 0% | Not started |
| Settings | ⏳ 0% | ⏳ 0% | Not started |
| Jobs | ⏳ 0% | ⏳ 0% | Not started |
| Candidates | ⏳ 0% | ⏳ 0% | Not started |
| Interviews | ⏳ 0% | ⏳ 0% | Not started |
| Calendar | ⏳ 0% | ⏳ 0% | Not started |
| Messages | ⏳ 0% | ⏳ 0% | Not started |
| Exams | ⏳ 0% | ⏳ 0% | Not started |
| Subscription | ⏳ 0% | ⏳ 0% | Not started |
| Errors | ⏳ 0% | ⏳ 0% | Not started |
| Validation | ⏳ 0% | ⏳ 0% | Not started |

---

## 🎯 Priority Implementation Order

### High Priority (Weeks 1-4)
1. ✅ Authentication pages (login, register, password reset)
2. ✅ Navigation and sidebar
3. ✅ Dashboard
4. ✅ Settings page
5. ✅ Error messages and validation
6. ✅ Common UI components (buttons, modals, alerts)

### Medium Priority (Weeks 5-6)
7. Job management
8. Candidate management
9. Interview scheduling
10. Calendar integration
11. Messaging system
12. Backend API translations

### Lower Priority (Weeks 7-8)
13. Admin panels
14. Exam system
15. Analytics and reports
16. Public landing pages
17. Documentation

---

## 📖 Additional Resources

### Official Documentation
- [next-intl Documentation](https://next-intl-docs.vercel.app/)
- [Next.js Internationalization](https://nextjs.org/docs/app/building-your-application/routing/internationalization)
- [MDN Intl API](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)
- [date-fns Locales](https://date-fns.org/docs/Locale)

### Translation Tools
- [DeepL](https://www.deepl.com/) - High-quality machine translation
- [Google Translate](https://translate.google.com/) - Quick translations
- [Gengo](https://gengo.com/) - Professional translation service

### Japanese Localization Resources
- [Japanese Date/Time Formats](https://en.wikipedia.org/wiki/Date_and_time_notation_in_Japan)
- [Japanese Typography](https://en.wikipedia.org/wiki/Japanese_typography)
- [Web Content Accessibility Guidelines - Japanese](https://waic.jp/translations/WCAG21/)

---

## 📞 Support & Feedback

For questions or issues related to i18n implementation:

1. Check this documentation first
2. Review [next-intl documentation](https://next-intl-docs.vercel.app/)
3. Open an issue in the project repository
4. Consult with the development team

---

**Last Updated**: January 2025
**Document Version**: 1.0
**Maintained by**: MiraiWorks Development Team
