# Role-Based Color Schemes for Sidebar

This documentation explains the implementation of role-based color schemes for the MiraiWorks sidebar.

## Overview

The sidebar now dynamically changes its color scheme based on the user's role, providing visual identity and better user experience differentiation.

## Available Color Schemes

### 1. Super Admin - Deep Violet Theme
- **Primary**: Deep violet/purple colors
- **Use Case**: System administrators with highest privileges
- **Visual Identity**: Professional, authoritative

### 2. Company Admin - Deep Blue Theme
- **Primary**: Deep blue colors
- **Use Case**: Company-level administrators
- **Visual Identity**: Corporate, trustworthy

### 3. Recruiter - Deep Emerald Theme
- **Primary**: Deep emerald/green colors
- **Use Case**: Recruitment professionals
- **Visual Identity**: Growth-oriented, professional

### 4. Employer - Deep Orange Theme
- **Primary**: Deep orange/amber colors
- **Use Case**: Employers posting jobs
- **Visual Identity**: Energetic, business-focused

### 5. Candidate - Deep Cyan Theme
- **Primary**: Deep cyan/teal colors
- **Use Case**: Job seekers
- **Visual Identity**: Fresh, aspirational

## Implementation Details

### Color Scheme Structure

Each role has a comprehensive color scheme with the following properties:

```typescript
interface ColorScheme {
  // Main sidebar colors
  background: string           // Main sidebar background
  backgroundOverlay: string    // Subtle overlay for depth
  border: string              // Border colors
  headerBackground: string    // Header section background

  // Brand/logo colors
  brandBackground: string     // Logo background
  brandAccent: string        // Icon backgrounds

  // Text colors
  textPrimary: string        // Primary text color
  textSecondary: string      // Secondary text color

  // Interactive elements
  buttonBorder: string       // Button borders
  buttonHover: string        // Hover state background
  buttonActive: string       // Active state background

  // User avatar
  avatarBackground: string   // User avatar background
  avatarRing: string        // Avatar ring color

  // Indicators
  activeIndicator: string         // Active page indicators
  activeIndicatorShadow: string   // Shadow for active indicators
  statusIndicator: string         // Online status indicator
  statusIndicatorShadow: string   // Shadow for status indicator
}
```

### Usage

#### Automatic Application
The color scheme is automatically applied in the `Sidebar` component based on the authenticated user's role:

```typescript
// In Sidebar.tsx
const { user } = useAuth()
const colorScheme = getRoleColorScheme(user?.roles)
const roleDisplayName = getRoleDisplayName(user?.roles)
```

#### Utility Functions

```typescript
// Get color scheme for user roles
getRoleColorScheme(userRoles?: Array<{ role: { name: string } }>): ColorScheme

// Get formatted role display name
getRoleDisplayName(userRoles?: Array<{ role: { name: string } }>): string
```

#### Role Priority
When a user has multiple roles, the system uses this priority order:
1. `super_admin` (highest priority)
2. `company_admin`
3. `recruiter`
4. `employer`
5. `candidate` (lowest priority)

### Files Modified

1. **`/utils/roleColorSchemes.ts`** - New file containing all color definitions and utility functions
2. **`/components/layout/Sidebar.tsx`** - Updated to use dynamic color schemes
3. **`/components/demo/SidebarColorDemo.tsx`** - Demo component for testing (development only)

### CSS Classes Applied

The implementation uses Tailwind CSS classes dynamically applied based on the user's role:

- Background colors: `bg-violet-950`, `bg-blue-950`, etc.
- Border colors: `border-violet-700/30`, `border-blue-700/30`, etc.
- Text colors: `text-white`, `text-violet-200/80`, etc.
- Interactive states: hover, active, and focus states

## Testing

### Development Demo
Use the `SidebarColorDemo` component to test all color schemes:

```typescript
import SidebarColorDemo from '@/components/demo/SidebarColorDemo'

// Use in a development page to preview all schemes
<SidebarColorDemo />
```

### Role Testing
To test different roles:
1. Log in with different user roles
2. Observe the sidebar color changes
3. Verify navigation item styling
4. Check user info section colors

## Customization

### Adding New Roles
To add a new role color scheme:

1. Add the new role to `roleColorSchemes` in `/utils/roleColorSchemes.ts`:
```typescript
export const roleColorSchemes: Record<string, ColorScheme> = {
  // ... existing roles
  new_role: {
    background: 'bg-purple-950',
    backgroundOverlay: 'bg-purple-900/30',
    // ... define all required properties
  }
}
```

2. Update the role priority in `getRoleColorScheme()` if needed.

### Modifying Existing Schemes
Update the specific color properties in the `roleColorSchemes` object:

```typescript
super_admin: {
  background: 'bg-indigo-950', // Changed from violet to indigo
  // ... other properties
}
```

## Browser Support

The color schemes use modern CSS features:
- CSS Custom Properties (CSS Variables)
- CSS Gradients
- Box Shadows
- Opacity/Alpha channels

Supported in all modern browsers (Chrome 88+, Firefox 86+, Safari 14+, Edge 88+).

## Performance

- Color schemes are statically defined (no dynamic calculations)
- Minimal runtime overhead
- CSS classes are purged by Tailwind in production
- No external dependencies

## Accessibility

All color schemes maintain:
- WCAG AA contrast ratios for text
- Clear visual hierarchy
- Consistent interaction patterns
- Support for reduced motion preferences

## Future Enhancements

Potential improvements:
1. **Theme Persistence**: Save user's preferred theme
2. **Custom Themes**: Allow users to create custom color schemes
3. **Dark/Light Modes**: Extend to support system theme preferences
4. **Animation Transitions**: Smooth transitions between schemes
5. **High Contrast Mode**: Enhanced accessibility support