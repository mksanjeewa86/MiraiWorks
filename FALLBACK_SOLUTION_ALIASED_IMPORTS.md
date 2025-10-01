# Fallback Solution: Aliased Imports

## Issue: Potential Name Conflicts

If component names like `Card`, `Button`, `Badge` conflict with other types or components, we can use aliased imports.

## Solution Options

### Option 1: Prefix with UI
```typescript
import {
  Card as UICard,
  CardContent as UICardContent,
  CardHeader as UICardHeader,
  CardTitle as UICardTitle,
  Button as UIButton,
  Badge as UIBadge,
} from '@/components/ui';

// Usage:
<UICard>
  <UICardHeader>
    <UICardTitle>Title</UICardTitle>
  </UICardHeader>
  <UICardContent>
    <UIButton>Click</UIButton>
    <UIBadge>New</UIBadge>
  </UICardContent>
</UICard>
```

### Option 2: Use Original Direct Imports with Extensions

If the issue is path resolution, try adding explicit `.tsx` extensions:

```typescript
import { Card } from '@/components/ui/card.tsx';
import { Button } from '@/components/ui/button.tsx';
import { Badge } from '@/components/ui/badge.tsx';
```

### Option 3: Use Relative Imports

Bypass path aliases completely:

```typescript
// From: src/app/admin/exams/[id]/preview/page.tsx
import { Card, CardContent, CardHeader, CardTitle } from '../../../../../components/ui/card';
import { Button } from '../../../../../components/ui/button';
import { Badge } from '../../../../../components/ui/badge';
```

### Option 4: Update tsconfig for Better Module Resolution

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/components/ui": ["./src/components/ui/index.ts"],
      "@/components/ui/*": ["./src/components/ui/*"],
      "@/*": ["./src/*"]
    },
    "moduleResolution": "node",
    "resolveJsonModule": true
  }
}
```

### Option 5: Create Named Exports Namespace

Update `index.ts` to export as namespace:

```typescript
// src/components/ui/index.ts
import { Alert, AlertDescription } from './alert';
import { Badge } from './badge';
import { Button } from './button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
// ... all other imports

export const UI = {
  Alert,
  AlertDescription,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  // ... all other components
};

export * from './alert';
export * from './badge';
export * from './button';
export * from './card';
// ... all other exports
```

Usage:
```typescript
import { UI } from '@/components/ui';

<UI.Card>
  <UI.CardHeader>
    <UI.CardTitle>Title</UI.CardTitle>
  </UI.CardHeader>
</UI.Card>
```

## Current Status

✅ **Build works locally** with current approach
✅ **No name conflicts detected**
✅ **TypeScript validates successfully**

The barrel export with direct component names should work in CI. If it doesn't, we'll implement one of the fallback options above.

## Quick Test for Name Conflicts

```bash
# Search for potential conflicts
cd frontend
grep -r "^export.*Card\b\|^export.*Button\b\|^export.*Badge\b" src/ --include="*.tsx" --include="*.ts"

# Check global types
npx tsc --showConfig | grep -i "types"
```

## Recommended Approach

1. **First**: Try current solution (barrel export with direct names) ✅ DONE
2. **If fails**: Add UI prefix (Option 1)
3. **If still fails**: Use relative imports (Option 3)
4. **Last resort**: Update all component names to be more specific (e.g., `UICard`, `UIButton`)

---

**Current Implementation**: Using barrel export with direct component names
**Status**: Works locally, waiting for CI test
**Fallback Ready**: Multiple options available if needed
