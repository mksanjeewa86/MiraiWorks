# MiraiWorks HRMS

A modern HR & recruitment management platform built with Next.js for candidates, recruiters, and employers with real-time messaging, calendar sync, resume builder, and secure interview scheduling.

## 🚀 Technology Stack

### Frontend
- **Next.js 15** with App Router and Turbopack
- **TypeScript** for type safety
- **TailwindCSS** for styling
- **React 19** with modern hooks
- **Recharts** for data visualization
- **Lucide React** for icons
- **Radix UI** for accessible components

### Backend
- **FastAPI** with Python
- **Uvicorn** ASGI server
- **Pydantic** for data validation
- **CORS** enabled for cross-origin requests

## 🏗️ Project Structure

```
MiraiWorks/
├── frontend-nextjs/          # Next.js frontend application
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   │   ├── auth/        # Authentication pages
│   │   │   ├── dashboard/   # Dashboard pages
│   │   │   └── layout.tsx   # Root layout
│   │   ├── components/      # React components
│   │   │   ├── common/      # Shared components
│   │   │   ├── dashboard/   # Dashboard-specific components
│   │   │   └── layout/      # Layout components
│   │   ├── contexts/        # React contexts
│   │   └── types/           # TypeScript type definitions
│   ├── package.json
│   └── tailwind.config.js
├── frontend/                 # Legacy Vite frontend (deprecated)
├── backend/                 # FastAPI backend
│   ├── stub_api.py         # Demo API server
│   └── sample_data.json    # Mock data
├── docs/                   # Documentation
└── README.md
```

## 🛠️ Development Setup

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.8+ and pip

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MiraiWorks
   ```

2. **Start the backend API**
   ```bash
   cd backend
   python stub_api.py
   ```
   - API runs on: http://localhost:8001
   - API docs: http://localhost:8001/docs

3. **Start the Next.js frontend**
   ```bash
   cd frontend-nextjs
   npm install
   npm run dev
   ```
   - Frontend runs on: http://localhost:3001

## 🔐 Test Credentials

The demo API accepts any password for these email addresses:

### Test Users
- **Super Admin**: `admin@miraiworks.com`
- **Company Admin**: `admin@techcorp.jp` (Takeshi Yamamoto)
- **Recruiter**: `recruiter1@techcorp.jp` (Hiroshi Tanaka)
- **Candidate**: `john.doe@email.com` (John Doe) ← **Recommended for testing**
- **Candidate**: `jane.smith@email.com` (Jane Smith)

**Password**: Any password works in demo mode

## 🎯 Key Features

### ✅ Implemented
- **Authentication System**: Login with JWT tokens
- **Role-Based Access Control**: Different dashboards per user type
- **Responsive Design**: Mobile-first approach
- **Dashboard Analytics**: Charts and statistics
- **Modern UI**: Clean, professional interface
- **Theme Support**: Dark/light mode toggle
- **Real-time Navigation**: Dynamic sidebar based on user roles

### 🔄 In Progress
- Complete auth flow (Register, 2FA, Password Reset)
- Additional dashboard types (Recruiter, Employer, Admin)
- Feature pages (Messages, Calendar, Interviews, Resumes)

## 🎨 Design System

### Brand Colors
- **Primary**: `#6C63FF` (Brand Purple)
- **Accent**: `#22C55E` (Success Green)  
- **Muted**: `#64748B` (Neutral Gray)

### Components
- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Consistent sizing and hover states
- **Forms**: Clean input styling with focus states
- **Charts**: Recharts with custom theming

## 📱 Pages & Routes

### Public Routes
- `/` - Landing page
- `/auth/login` - User login

### Protected Routes  
- `/dashboard` - Role-based dashboard
- `/auth/*` - Authentication pages
- Feature pages (coming soon)

## 🔧 Development

### Available Scripts (frontend-nextjs)
```bash
npm run dev          # Development server with Turbopack
npm run build        # Production build
npm run start        # Production server
npm run lint         # ESLint
```

### API Development
```bash
cd backend
python stub_api.py   # Start demo API server
```

## 🚀 Migration from Vite

This project was successfully migrated from Vite to Next.js 15 for improved:
- **Stability**: No more compilation errors
- **Performance**: Turbopack for faster builds
- **Architecture**: App Router for better organization
- **Developer Experience**: Better TypeScript integration

The legacy Vite frontend is preserved in the `frontend/` directory but is deprecated.

## 🗂️ Documentation

Additional documentation is available in the `docs/` folder:
- Project structure details
- Component documentation
- Development guides
- Architecture decisions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**MiraiWorks** - Building the future of HR technology 🚀