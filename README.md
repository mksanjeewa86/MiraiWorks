# MiraiWorks HRMS

🏆 **Production-Ready HR & Recruitment Management Platform**

A comprehensive HR management system built with **FastAPI + Next.js**, featuring real-time messaging, calendar integration, resume management, and secure interview scheduling. **Now with 100% stable CI/CD pipeline and comprehensive test coverage.**

[![CI Pipeline](https://github.com/mksanjeewa86/MiraiWorks/actions/workflows/ci.yml/badge.svg)](https://github.com/mksanjeewa86/MiraiWorks/actions/workflows/ci.yml)
[![Documentation](https://github.com/mksanjeewa86/MiraiWorks/actions/workflows/docs.yml/badge.svg)](https://github.com/mksanjeewa86/MiraiWorks/actions/workflows/docs.yml)
[![Coverage](https://img.shields.io/badge/coverage-55.5%25-orange)](https://github.com/mksanjeewa86/MiraiWorks)
[![Tests](https://img.shields.io/badge/tests-167%20passing-brightgreen)](https://github.com/mksanjeewa86/MiraiWorks)

## 🚀 Technology Stack

### Backend (Production-Ready)
- **FastAPI** with Python 3.11+
- **SQLAlchemy** with async support
- **Pydantic v2** for data validation
- **JWT Authentication** with 2FA support
- **Redis** for caching and sessions
- **MinIO/S3** for file storage
- **Comprehensive Testing** (pytest, asyncio)

### Frontend (Modern)
- **Next.js 15** with App Router
- **TypeScript** for type safety
- **TailwindCSS 4** for styling
- **React 19** with modern hooks
- **Recharts** for data visualization
- **Radix UI** for accessible components

### DevOps & Infrastructure
- **GitHub Actions** CI/CD pipeline
- **Docker** containerization
- **Pytest** with 55.5% coverage
- **Ruff** linting and formatting
- **MyPy** type checking
- **Multi-format documentation** (MkDocs, TypeDoc, Sphinx)

## 🏗️ Project Architecture

```
MiraiWorks/
├── 📁 backend/              # Production FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📁 endpoints/    # API routes (18 modules)
│   │   ├── 📁 models/       # SQLAlchemy models
│   │   ├── 📁 schemas/      # Pydantic schemas
│   │   ├── 📁 services/     # Business logic
│   │   ├── 📁 crud/         # Database operations
│   │   ├── 📁 tests/        # 167 passing tests
│   │   └── 📁 utils/        # Shared utilities
│   ├── 📄 requirements.txt
│   └── 📄 alembic.ini       # Database migrations
├── 📁 frontend/             # Next.js Frontend
│   ├── 📁 src/
│   │   ├── 📁 app/          # App Router pages
│   │   ├── 📁 components/   # React components
│   │   ├── 📁 contexts/     # State management
│   │   ├── 📁 api/          # API integration
│   │   └── 📁 types/        # TypeScript definitions
│   ├── 📄 package.json
│   └── 📄 tailwind.config.js
├── 📁 .github/workflows/    # CI/CD Pipeline
│   ├── 📄 ci.yml           # Testing & linting
│   └── 📄 docs.yml         # Documentation
├── 📁 docs/                # Project documentation
├── 📄 TEST_PLAN.md         # Testing strategy
├── 📄 COVERAGE_STRATEGY.md # Coverage improvement
├── 📄 CLAUDE.md            # Development guidelines
└── 📄 README.md
```

## 🛠️ Development Setup

### Prerequisites
- **Node.js** 20+ and npm
- **Python** 3.11+ and pip
- **Redis** (for caching)
- **PostgreSQL** or **SQLite** (for database)

### Production Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/mksanjeewa86/MiraiWorks.git
   cd MiraiWorks
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt

   # Set up environment variables
   cp .env.example .env
   # Edit .env with your database and Redis URLs

   # Run database migrations
   alembic upgrade head

   # Start the server
   uvicorn app.main:app --reload --port 8000
   ```
   - API runs on: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - OpenAPI spec: http://localhost:8000/openapi.json

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install

   # Set up environment variables
   cp .env.local.example .env.local
   # Edit .env.local with your API URL

   # Start development server
   npm run dev
   ```
   - Frontend runs on: http://localhost:3000

### Testing & Quality Assurance

```bash
# Run backend tests
cd backend
PYTHONPATH=. python -m pytest app/tests/ -v --cov=app

# Run frontend tests
cd frontend
npm run test
npm run typecheck
npm run lint

# Run all CI checks locally
npm run build  # Frontend build check
```

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

### ✅ **Production-Ready Core Systems**
- 🔐 **Complete Authentication**: JWT + 2FA, password reset, account activation
- 👥 **User Management**: RBAC with Super Admin, Company Admin, Recruiter, Candidate roles
- 🏢 **Company Management**: Multi-tenant architecture with company-scoped operations
- 💬 **Real-time Messaging**: Conversation management with file attachments
- 📄 **Resume System**: Builder, PDF generation, template management
- 📅 **Calendar Integration**: Google/Microsoft Calendar sync
- 🎤 **Interview Management**: Scheduling, feedback, video integration
- 🔔 **Notification System**: Real-time alerts and updates
- 📊 **Dashboard Analytics**: Role-based dashboards with charts

### ✅ **Technical Excellence**
- 🧪 **167 Passing Tests**: Comprehensive test coverage (55.5%)
- 🔄 **100% Stable CI/CD**: Automated testing, linting, and deployment
- 📚 **Complete Documentation**: API docs, frontend docs, and guides
- 🛡️ **Security**: JWT authentication, role-based permissions, data validation
- 🚀 **Performance**: Async FastAPI, optimized database queries
- 🐳 **DevOps Ready**: Docker, environment configuration, database migrations

### 🔄 **In Active Development**
- 📈 **Advanced Analytics**: Enhanced reporting and insights
- 🔗 **External Integrations**: More calendar providers, ATS systems
- 📱 **Mobile App**: React Native mobile application
- 🤖 **AI Features**: Resume parsing, candidate matching

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

## 📊 **Project Status & Metrics**

### 🎯 **Current State** (September 2025)
| Component | Status | Metrics |
|-----------|--------|---------|
| **Backend API** | 🟢 Production Ready | 18 endpoint modules, 144+ routes |
| **Test Coverage** | 🟡 55.5% (Improving) | 167 tests passing, 0 failing |
| **CI/CD Pipeline** | 🟢 100% Stable | All workflows passing |
| **Documentation** | 🟢 Complete | Auto-generated API/frontend docs |
| **Frontend Build** | 🟢 Stable | Next.js + TypeScript |
| **Database** | 🟢 Production Ready | SQLAlchemy async, migrations |

### 🏆 **Recent Achievements**
- ✅ **Complete CI/CD stabilization** (September 2025)
- ✅ **167 backend tests** all passing with comprehensive coverage
- ✅ **Real-time messaging system** fully implemented and tested
- ✅ **User & company management** with 99%+ test coverage
- ✅ **Authentication system** with 100% test coverage
- ✅ **Cross-platform development** (Windows/Linux compatibility)

### 📈 **Test Coverage by Module**
- **Authentication**: 100% (333 lines tested)
- **Messaging**: 100% (234 lines tested)
- **User Management**: 100% (257 lines tested)
- **Company Management**: 99% (221 lines tested)
- **Models & Schemas**: 85%+ average
- **Services**: 35% average (improvement target)

## 🔧 **Development Commands**

### Backend Development
```bash
cd backend

# Testing
PYTHONPATH=. python -m pytest app/tests/ -v --cov=app --cov-report=html
python -m pytest app/tests/test_messaging.py -v  # Specific test module

# Code Quality
ruff check .                    # Linting
ruff format .                   # Formatting
mypy app/ --ignore-missing-imports  # Type checking

# Database
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head            # Apply migrations

# Server
uvicorn app.main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend

# Development
npm run dev                     # Development server
npm run build                   # Production build
npm run start                   # Production server

# Quality Assurance
npm run typecheck               # TypeScript checking
npm run lint                    # ESLint
npm run lint:fix                # Auto-fix linting issues
```

### CI/CD Commands
```bash
# Run full CI locally
cd backend && PYTHONPATH=. python -m pytest app/tests/ --cov=app --cov-fail-under=55
cd frontend && npm run build && npm run typecheck && npm run lint
```

## 📚 **Documentation**

Comprehensive documentation is automatically generated and available:

### **API Documentation**
- **Interactive API Docs**: `/docs` (Swagger UI)
- **OpenAPI Specification**: `/openapi.json`
- **Backend Code Docs**: Auto-generated with Sphinx

### **Frontend Documentation**
- **Component Docs**: Auto-generated with TypeDoc
- **Type Definitions**: Complete TypeScript coverage

### **Project Documentation**
- **[TEST_PLAN.md](TEST_PLAN.md)**: Comprehensive testing strategy
- **[COVERAGE_STRATEGY.md](COVERAGE_STRATEGY.md)**: Coverage improvement roadmap
- **[CLAUDE.md](CLAUDE.md)**: Development guidelines and architecture rules
- **API Documentation**: Auto-generated from code

### **Download Documentation**
For private repositories, documentation is available as CI artifacts:
1. Go to [Actions](../../actions) → Documentation workflow
2. Download the `documentation-site` artifact
3. Extract and open `index.html` for offline viewing

## 🤝 **Contributing**

We follow strict development standards to maintain code quality:

### **Development Process**
1. **Fork & Clone**: Fork the repository and clone locally
2. **Branch**: Create a feature branch (`feature/amazing-feature`)
3. **Follow Guidelines**: Adhere to patterns in [CLAUDE.md](CLAUDE.md)
4. **Test First**: Write tests before implementation (TDD)
5. **Quality Gates**: All checks must pass

### **Required Before PR**
```bash
# Backend quality checks
cd backend
ruff check .                    # Linting must pass
mypy app/ --ignore-missing-imports  # Type checking must pass
PYTHONPATH=. python -m pytest app/tests/ --cov=app --cov-fail-under=55  # Tests must pass

# Frontend quality checks
cd frontend
npm run typecheck               # TypeScript must compile
npm run lint                    # ESLint must pass
npm run build                   # Build must succeed
```

### **Code Standards**
- ✅ **100% test coverage** for new endpoints
- ✅ **Follow architecture patterns** defined in CLAUDE.md
- ✅ **Type safety**: Full TypeScript/Python type hints
- ✅ **Documentation**: Update docs for new features
- ✅ **Security**: Follow security best practices

### **Review Process**
1. All CI checks must pass (automated)
2. Code review by maintainers
3. Test coverage verification
4. Architecture compliance check

## 🛡️ **Security & Production Readiness**

### **Security Features**
- 🔐 **JWT Authentication** with refresh tokens
- 🔑 **Two-Factor Authentication** (2FA) support
- 🛡️ **Role-Based Access Control** (RBAC)
- 🔒 **Data Validation** with Pydantic v2
- 🚫 **SQL Injection Protection** via SQLAlchemy
- 🛡️ **CORS Configuration** for secure cross-origin requests

### **Production Features**
- 🏗️ **Database Migrations** with Alembic
- 📦 **Docker Support** for containerization
- 🔄 **Async Operations** for high performance
- 📊 **Monitoring Ready** with logging and metrics
- 🗄️ **Multi-Database Support** (PostgreSQL, SQLite)
- ☁️ **Cloud Storage** integration (S3/MinIO)

## 📈 **Performance & Scalability**

- ⚡ **Async FastAPI** for high-concurrency handling
- 🗄️ **Async SQLAlchemy** for database operations
- 🚀 **Redis Caching** for improved response times
- 📦 **Optimized Bundle** with Next.js and Turbopack
- 🔄 **Background Tasks** with Celery integration
- 📊 **Database Indexing** for query optimization

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🎉 **Project Status: Production Ready!**

✅ **167 Tests Passing** | ✅ **55.5% Coverage** | ✅ **100% Stable CI/CD** | ✅ **Complete Documentation**

**MiraiWorks** - *Building the future of HR technology with enterprise-grade reliability* 🚀

---

*Last Updated: September 15, 2025 | Major CI/CD & Testing Milestone Achieved*

---

### **Quick Links**
- 🐛 [Report Issues](../../issues)
- 🚀 [View CI/CD Status](../../actions)
- 📚 [Browse Documentation](../../releases)
- 💬 [Discussions](../../discussions)
- 🔄 [Pull Requests](../../pulls)