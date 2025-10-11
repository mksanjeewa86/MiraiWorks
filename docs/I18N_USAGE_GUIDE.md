# i18n Usage Guide - MiraiWorks

## ✅ What's Been Implemented

The i18n (internationalization) system is now **fully set up and working** for both frontend and backend!

### **Supported Languages**
- 🇺🇸 English (`en`) - Default
- 🇯🇵 Japanese (`ja`)

### **URL Structure**
All routes now include the locale:
- English: `/en/dashboard`, `/en/auth/login`
- Japanese: `/ja/dashboard`, `/ja/auth/login`

---

## 🎯 Frontend Usage

### **1. Using Translations in Client Components**

```tsx
'use client';

import { useTranslations } from 'next-intl';

export default function MyComponent() {
  const t = useTranslations('common'); // Load 'common' namespace

  return (
    <div>
      <h1>{t('nav.dashboard')}</h1>
      <button>{t('buttons.save')}</button>
      <p>{t('common.loading')}</p>
    </div>
  );
}
```

### **2. Using Translations in Server Components**

```tsx
import { useTranslations } from 'next-intl';
import { getTranslations } from 'next-intl/server';

export default async function ServerPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations('common');

  return (
    <div>
      <h1>{t('nav.dashboard')}</h1>
    </div>
  );
}
```

### **3. Available Translation Namespaces**

| Namespace | File | Purpose |
|-----------|------|---------|
| `common` | `common.json` | Navigation, buttons, status, pagination |
| `auth` | `auth.json` | Login, register, password reset, 2FA |
| `errors` | `errors.json` | Error messages (general, network, auth, API) |
| `validation` | `validation.json` | Form validation messages |

**Example:**
```tsx
const t = useTranslations('auth.login');

<input placeholder={t('emailPlaceholder')} />
// English: "Enter your email"
// Japanese: "メールアドレスを入力"
```

### **4. Using Multiple Namespaces**

```tsx
export default function MyPage() {
  const tCommon = useTranslations('common');
  const tAuth = useTranslations('auth.login');
  const tErrors = useTranslations('errors');

  return (
    <div>
      <h1>{tAuth('title')}</h1>
      <button>{tCommon('buttons.submit')}</button>
      <p className="error">{tErrors('general.somethingWentWrong')}</p>
    </div>
  );
}
```

### **5. Dynamic Values in Translations**

```tsx
const t = useTranslations('validation');

// Translation key: "minLength": "{field} must be at least {min} characters"
const message = t('minLength', { field: 'Password', min: 8 });
// English: "Password must be at least 8 characters"
// Japanese: "パスワードは8文字以上である必要があります"
```

---

## 🌐 Language Switching

### **Method 1: Using the LanguageSwitcher Component**

```tsx
import LanguageSwitcher from '@/components/LanguageSwitcher';

export default function Layout({ children }) {
  return (
    <div>
      <nav>
        <LanguageSwitcher />
      </nav>
      {children}
    </div>
  );
}
```

### **Method 2: Manual Language Links**

```tsx
import { useLocale } from 'next-intl';
import { usePathname } from 'next/navigation';
import Link from 'next/link';

export default function LanguageLinks() {
  const locale = useLocale();
  const pathname = usePathname();

  const switchLocale = (newLocale: string) => {
    const segments = pathname.split('/');
    segments[1] = newLocale;
    return segments.join('/');
  };

  return (
    <div>
      <Link href={switchLocale('en')}>English</Link>
      <Link href={switchLocale('ja')}>日本語</Link>
    </div>
  );
}
```

---

## 🔧 Backend Usage

### **1. Getting User's Locale**

```python
from fastapi import Header
from app.i18n import get_locale_from_header

async def my_endpoint(accept_language: str = Header(None)):
    locale = get_locale_from_header(accept_language)
    # locale will be 'en' or 'ja'
```

### **2. Translating Error Messages**

```python
from fastapi import HTTPException
from app.i18n import translator

@router.post("/login")
async def login(
    credentials: LoginRequest,
    accept_language: str = Header(None)
):
    locale = get_locale_from_header(accept_language)

    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail=translator.t("errors.invalid_credentials", locale=locale)
        )

    return {"token": generate_token(user)}
```

### **3. Success Messages with Dynamic Values**

```python
from app.i18n import translator

# Translation key: "interview_scheduled": "{datetime}に面接がスケジュールされました"
message = translator.t(
    "success.interview_scheduled",
    locale="ja",
    datetime="2025-01-15 14:30"
)
# Output: "2025-01-15 14:30に面接がスケジュールされました"
```

### **4. Getting User's Preferred Locale from Database**

```python
from app.dependencies import get_current_active_user

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    # Get locale from user settings
    locale = current_user.settings.language if current_user.settings else "en"

    message = translator.t("success.profile_updated", locale=locale)
    return {"message": message}
```

---

## 📝 Adding New Translations

### **Frontend: Adding New Translation Keys**

1. **Add to English file** (`frontend/src/i18n/locales/en/[namespace].json`):
```json
{
  "dashboard": {
    "welcome": "Welcome, {name}!",
    "stats": {
      "totalJobs": "Total Jobs",
      "activeApplications": "Active Applications"
    }
  }
}
```

2. **Add to Japanese file** (`frontend/src/i18n/locales/ja/[namespace].json`):
```json
{
  "dashboard": {
    "welcome": "{name}さん、ようこそ！",
    "stats": {
      "totalJobs": "総求人数",
      "activeApplications": "進行中の応募"
    }
  }
}
```

3. **Use in component**:
```tsx
const t = useTranslations('common.dashboard');

<h1>{t('welcome', { name: user.name })}</h1>
<div>{t('stats.totalJobs')}: {jobCount}</div>
```

### **Backend: Adding New Translation Keys**

1. **Add to `backend/app/i18n/locales/en.json`**:
```json
{
  "success": {
    "exam_completed": "Exam completed successfully! Score: {score}%"
  }
}
```

2. **Add to `backend/app/i18n/locales/ja.json`**:
```json
{
  "success": {
    "exam_completed": "試験が正常に完了しました！スコア：{score}%"
  }
}
```

3. **Use in endpoint**:
```python
message = translator.t("success.exam_completed", locale=locale, score=85)
```

---

## 🔄 Date & Time Formatting

```tsx
import { format } from 'date-fns';
import { ja, enUS } from 'date-fns/locale';
import { useLocale } from 'next-intl';

export function FormattedDate({ date }: { date: Date }) {
  const locale = useLocale();
  const dateLocale = locale === 'ja' ? ja : enUS;

  return (
    <span>
      {format(date, 'PPP', { locale: dateLocale })}
    </span>
  );
}

// Output:
// English: "January 15, 2025"
// Japanese: "2025年1月15日"
```

---

## 💰 Currency Formatting

```tsx
import { useLocale } from 'next-intl';

export function formatPrice(price: number, locale: string) {
  return new Intl.NumberFormat(locale === 'ja' ? 'ja-JP' : 'en-US', {
    style: 'currency',
    currency: locale === 'ja' ? 'JPY' : 'USD',
    minimumFractionDigits: 0,
  }).format(price);
}

export function PriceDisplay({ amount }: { amount: number }) {
  const locale = useLocale();
  return <span>{formatPrice(amount, locale)}</span>;
}

// Output:
// English: "$1,000"
// Japanese: "¥1,000"
```

---

## 🧪 Testing Translations

### **1. Test English version:**
```bash
# Visit: http://localhost:3000/en/dashboard
```

### **2. Test Japanese version:**
```bash
# Visit: http://localhost:3000/ja/dashboard
```

### **3. Test language switching:**
- Add `<LanguageSwitcher />` to your navigation
- Switch between languages and verify:
  - URL changes (e.g., `/en/` → `/ja/`)
  - Content updates
  - No page reload (smooth transition)

---

## 📦 Project Structure

```
frontend/
└── src/
    ├── i18n/
    │   ├── config.ts              # Locale configuration
    │   ├── request.ts             # Server-side i18n setup
    │   └── locales/
    │       ├── en/                # English translations
    │       │   ├── common.json
    │       │   ├── auth.json
    │       │   ├── errors.json
    │       │   └── validation.json
    │       └── ja/                # Japanese translations
    │           ├── common.json
    │           ├── auth.json
    │           ├── errors.json
    │           └── validation.json
    ├── middleware.ts              # Locale detection
    ├── components/
    │   └── LanguageSwitcher.tsx   # Language switcher component
    └── app/
        ├── layout.tsx             # Root layout
        └── [locale]/              # Locale-based routes
            ├── layout.tsx         # Locale layout with providers
            └── ...                # All app routes

backend/
└── app/
    └── i18n/
        ├── __init__.py
        ├── translate.py           # Translation utility
        └── locales/
            ├── en.json            # English backend translations
            └── ja.json            # Japanese backend translations
```

---

## 🎨 Best Practices

### ✅ **DO:**
- Always use translation keys, never hardcode strings
- Keep translation keys descriptive and hierarchical
- Test both languages when adding new features
- Use the same key structure in both language files
- Add comments for complex translations

### ❌ **DON'T:**
- Don't mix hardcoded strings with translations
- Don't translate database values (use mapping)
- Don't forget to add keys to both `en` and `ja` files
- Don't use generic keys like `text1`, `label2`

---

## 🐛 Troubleshooting

### **Issue: Translation key not found**
**Symptom:** Raw key displayed instead of translation (e.g., `common.nav.dashboard`)

**Solution:**
1. Check if the key exists in both `en` and `ja` files
2. Verify the namespace name in `useTranslations()`
3. Restart the dev server after adding new translations

### **Issue: Language doesn't switch**
**Symptom:** Language selector doesn't work

**Solution:**
1. Check that middleware is configured correctly
2. Verify the URL includes the locale (e.g., `/en/dashboard`)
3. Check browser console for errors

### **Issue: Build fails with type errors**
**Symptom:** TypeScript errors during build

**Solution:**
1. Ensure `params` are awaited in async components
2. Check that all translation files are valid JSON
3. Verify `locale` type assertions in `request.ts`

---

## 🚀 Next Steps

1. **Add translations to existing pages**:
   - Replace hardcoded English text with `t()` calls
   - Add corresponding keys to translation files

2. **Create domain-specific translation files**:
   - `jobs.json` - Job management translations
   - `interviews.json` - Interview scheduling translations
   - `candidates.json` - Candidate management translations
   - `dashboard.json` - Dashboard-specific translations

3. **Test user language persistence**:
   - Update user settings to save language preference
   - Load saved preference on login

4. **Add more languages** (future):
   - Add new locale to `src/i18n/config.ts`
   - Create translation files for new locale
   - Update backend translations

---

## 📞 Support

For questions or issues:
1. Check this documentation
2. Review the [next-intl documentation](https://next-intl-docs.vercel.app/)
3. Consult the implementation plan: `I18N_IMPLEMENTATION_PLAN.md`

---

**Last Updated:** January 2025
**Status:** ✅ Phase 1 & 2 Complete - Ready for use!
