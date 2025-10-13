# ATS (Applicant Tracking System) Implementation Plan

**Document Version**: 1.1
**Created**: 2025-10-13
**Updated**: 2025-10-13
**Status**: Planning Phase - Rule-Based Implementation
**Priority**: High
**Implementation Approach**: ⚡ **RULE-BASED (No AI/ML)**

---

## 🚀 **IMPORTANT: Implementation Approach**

**This system uses RULE-BASED algorithms (NO AI/ML dependencies)**

For detailed scoring algorithms, keyword extraction, and suggestion logic, see:
📘 **[ATS_RULE_BASED_ALGORITHMS.md](./ATS_RULE_BASED_ALGORITHMS.md)**

**Benefits**:
- ✅ No external API costs (OpenAI, etc.)
- ✅ Fast processing (< 500ms per resume)
- ✅ Privacy-friendly (no data sent externally)
- ✅ Predictable and deterministic results
- ✅ No rate limits or API quotas
- ✅ Complete control over logic

**Estimated Timeline**: 4-5 weeks (reduced from 6 weeks)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Feature Requirements](#feature-requirements)
3. [Database Schema](#database-schema)
4. [API Specifications](#api-specifications)
5. [Service Layer Architecture](#service-layer-architecture)
6. [Premium Features Configuration](#premium-features-configuration)
7. [Frontend Implementation](#frontend-implementation)
8. [Implementation Checklist](#implementation-checklist)
9. [Testing Requirements](#testing-requirements)
10. [Migration Steps](#migration-steps)

---

## 📖 Overview

### Goal
Add ATS (Applicant Tracking System) functionality to MiraiWorks to provide:
1. **Resume analysis and screening** for employers (premium)
2. **Resume optimization suggestions** for candidates (premium)

### Business Value
- **For Employers**: Rule-based candidate screening, skills extraction, ranking system
- **For Candidates**: Resume quality improvement, ATS compatibility checks, keyword optimization
- **For Platform**: Premium revenue stream through feature gating

### Technical Approach
- Follow MiraiWorks architecture pattern (models → schemas → crud → services → endpoints)
- Use **rule-based algorithms** for analysis (pattern matching, statistical analysis, predefined dictionaries)
- Store analysis results in database for history tracking
- Gate features using existing subscription system
- **NO AI/ML dependencies** - all processing done locally

---

## 🎯 Feature Requirements

### Feature 1: Resume Analysis & Screening (Employers)

**Feature Name**: `resume_ats_screening`
**User Type**: Employers/Recruiters
**Premium**: Yes

**Capabilities**:
- ✅ Analyze resume completeness and quality
- ✅ Extract skills automatically from resume content
- ✅ Score resume against job requirements
- ✅ Match keywords with job descriptions
- ✅ Check ATS compatibility (formatting, structure)
- ✅ Rank multiple candidates
- ✅ Generate analysis reports
- ✅ Track analysis history

**Key Metrics**:
- Overall quality score (0-100)
- Skills match percentage
- Experience relevance score
- ATS compatibility rating
- Keyword density
- Section completeness

---

### Feature 2: Resume Optimization (Candidates)

**Feature Name**: `resume_ats_optimization`
**User Type**: Candidates/Job Seekers
**Premium**: Yes

**Capabilities**:
- ✅ Calculate resume quality score
- ✅ Provide actionable improvement suggestions
- ✅ Suggest missing keywords for target roles
- ✅ Check ATS compatibility (formatting issues)
- ✅ Recommend content improvements per section
- ✅ Compare with industry standards
- ✅ Track optimization progress over time

**Suggestion Categories**:
- Content quality
- Skills representation
- Experience descriptions
- Keyword optimization
- Formatting issues
- Section completeness
- ATS compatibility

---

## 🗄️ Database Schema

### 1. ResumeAnalysis Model

**File**: `backend/app/models/resume_ats.py`

```python
class ResumeAnalysis(BaseModel):
    """
    Stores comprehensive analysis results for a resume.
    Supports both employer screening and candidate optimization use cases.
    """
    __tablename__ = "resume_analyses"

    # Foreign keys
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    analyzed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_position_id = Column(Integer, ForeignKey("positions.id"), nullable=True, index=True)  # Optional job matching

    # Analysis type and context
    analysis_type = Column(String(50), nullable=False, index=True)  # 'employer_screening', 'candidate_optimization', 'job_matching'
    target_role = Column(String(200), nullable=True)  # Target job title for analysis
    job_description = Column(Text, nullable=True)  # Job description for matching

    # Overall scores (0-100 scale)
    overall_score = Column(Integer, nullable=False, default=0)  # Overall quality/match score
    content_quality_score = Column(Integer, nullable=False, default=0)
    skills_match_score = Column(Integer, nullable=False, default=0)
    experience_relevance_score = Column(Integer, nullable=False, default=0)
    ats_compatibility_score = Column(Integer, nullable=False, default=0)
    keyword_optimization_score = Column(Integer, nullable=False, default=0)

    # Extracted data (JSON fields)
    extracted_skills = Column(JSON, nullable=True)  # {"technical": [...], "soft": [...], "domain": [...]}
    extracted_keywords = Column(JSON, nullable=True)  # {"primary": [...], "secondary": [...]}
    missing_keywords = Column(JSON, nullable=True)  # Keywords that should be added
    section_scores = Column(JSON, nullable=True)  # Scores per section: {"summary": 85, "experience": 90, ...}

    # Analysis metadata
    analysis_version = Column(String(20), nullable=False, default="1.0")  # Track analysis algorithm version
    processing_time_ms = Column(Integer, nullable=True)  # Analysis processing time

    # Status
    status = Column(String(20), nullable=False, default="completed")  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(Text, nullable=True)

    # Relationships
    resume = relationship("Resume", back_populates="analyses")
    analyzed_by = relationship("User", foreign_keys=[analyzed_by_user_id])
    job_position = relationship("Position", back_populates="resume_analyses")
    suggestions = relationship("ResumeOptimizationSuggestion", back_populates="analysis", cascade="all, delete-orphan")
    keywords = relationship("ResumeKeyword", back_populates="analysis", cascade="all, delete-orphan")
    compatibility_checks = relationship("ATSCompatibilityCheck", back_populates="analysis", cascade="all, delete-orphan")
```

---

### 2. ResumeOptimizationSuggestion Model

```python
class ResumeOptimizationSuggestion(BaseModel):
    """
    Stores individual optimization suggestions for resume improvement.
    """
    __tablename__ = "resume_optimization_suggestions"

    # Foreign key
    analysis_id = Column(Integer, ForeignKey("resume_analyses.id"), nullable=False, index=True)

    # Suggestion details
    category = Column(String(50), nullable=False, index=True)  # 'content', 'skills', 'experience', 'keywords', 'formatting', 'ats_compatibility'
    section = Column(String(50), nullable=True)  # Which resume section: 'summary', 'experience', 'education', etc.
    priority = Column(String(20), nullable=False, default="medium")  # 'critical', 'high', 'medium', 'low'

    # Suggestion content
    title = Column(String(200), nullable=False)  # Short title
    description = Column(Text, nullable=False)  # Detailed explanation
    suggested_action = Column(Text, nullable=False)  # Specific action to take
    example_text = Column(Text, nullable=True)  # Example of improved text

    # Impact metrics
    potential_score_improvement = Column(Integer, nullable=True)  # Estimated score gain (0-100)
    difficulty = Column(String(20), nullable=False, default="medium")  # 'easy', 'medium', 'hard'

    # Implementation tracking
    is_applied = Column(Boolean, nullable=False, default=False)
    applied_at = Column(DateTime, nullable=True)
    dismissed = Column(Boolean, nullable=False, default=False)
    dismissed_at = Column(DateTime, nullable=True)

    # Relationships
    analysis = relationship("ResumeAnalysis", back_populates="suggestions")
```

---

### 3. ResumeKeyword Model

```python
class ResumeKeyword(BaseModel):
    """
    Stores extracted keywords from resume and keyword optimization data.
    """
    __tablename__ = "resume_keywords"

    # Foreign key
    analysis_id = Column(Integer, ForeignKey("resume_analyses.id"), nullable=False, index=True)

    # Keyword details
    keyword = Column(String(100), nullable=False, index=True)
    keyword_type = Column(String(50), nullable=False, index=True)  # 'skill', 'technology', 'industry_term', 'action_verb', 'certification'

    # Context and source
    source_section = Column(String(50), nullable=True)  # Where keyword was found
    context = Column(Text, nullable=True)  # Surrounding text context

    # Relevance metrics
    relevance_score = Column(Integer, nullable=False, default=0)  # 0-100 scale
    frequency = Column(Integer, nullable=False, default=1)  # How many times it appears
    is_present_in_resume = Column(Boolean, nullable=False, default=True)
    is_suggested = Column(Boolean, nullable=False, default=False)  # True if this is a suggested keyword to add

    # Job matching
    appears_in_job_description = Column(Boolean, nullable=False, default=False)
    importance_for_role = Column(String(20), nullable=True)  # 'critical', 'important', 'beneficial', 'optional'

    # Relationships
    analysis = relationship("ResumeAnalysis", back_populates="keywords")
```

---

### 4. ATSCompatibilityCheck Model

```python
class ATSCompatibilityCheck(BaseModel):
    """
    Stores ATS compatibility check results (formatting, structure, etc.).
    """
    __tablename__ = "ats_compatibility_checks"

    # Foreign key
    analysis_id = Column(Integer, ForeignKey("resume_analyses.id"), nullable=False, index=True)

    # Check details
    check_type = Column(String(50), nullable=False, index=True)  # 'formatting', 'structure', 'file_type', 'parsing', 'readability'
    check_name = Column(String(100), nullable=False)

    # Result
    passed = Column(Boolean, nullable=False, default=True)
    severity = Column(String(20), nullable=False, default="info")  # 'critical', 'warning', 'info'

    # Issue details
    issue_description = Column(Text, nullable=True)
    fix_suggestion = Column(Text, nullable=True)
    affected_sections = Column(JSON, nullable=True)  # List of affected sections

    # Impact
    impact_on_ats_parsing = Column(String(20), nullable=True)  # 'high', 'medium', 'low', 'none'

    # Relationships
    analysis = relationship("ResumeAnalysis", back_populates="compatibility_checks")
```

---

### 5. Model Relationships Updates

**Add to `Resume` model** (`backend/app/models/resume.py`):
```python
# Add relationship
analyses = relationship("ResumeAnalysis", back_populates="resume", cascade="all, delete-orphan")
```

**Add to `Position` model** (`backend/app/models/position.py`):
```python
# Add relationship
resume_analyses = relationship("ResumeAnalysis", back_populates="job_position")
```

**Add to `User` model** (`backend/app/models/user.py`):
```python
# Add relationship (if not exists)
resume_analyses = relationship("ResumeAnalysis", foreign_keys="ResumeAnalysis.analyzed_by_user_id")
```

---

## 🔌 API Specifications

### Endpoint Structure

**File**: `backend/app/endpoints/resume_ats.py`

All endpoints should be added to `backend/app/config/endpoints.py` following alphabetical ordering:

```python
class ResumeATSRoutes:
    """ATS (Applicant Tracking System) endpoints for resume analysis and optimization."""
    ANALYZE = "/resumes/{resume_id}/analyze"
    ANALYSIS_BY_ID = "/resumes/analyses/{analysis_id}"
    ANALYSIS_HISTORY = "/resumes/{resume_id}/analyses"
    ATS_CHECK = "/resumes/{resume_id}/ats-check"
    BATCH_ANALYZE = "/resumes/batch-analyze"
    MATCH_JOB = "/resumes/{resume_id}/match-job"
    OPTIMIZE = "/resumes/{resume_id}/optimize"
    SCORE = "/resumes/{resume_id}/score"
    SUGGEST_KEYWORDS = "/resumes/{resume_id}/suggest-keywords"
    SUGGESTIONS = "/resumes/analyses/{analysis_id}/suggestions"
```

---

### 1. Analyze Resume (Comprehensive)

**Endpoint**: `POST /api/resumes/{resume_id}/analyze`
**Permission**: `resume_ats_screening` (employers) OR `resume_ats_optimization` (candidates)
**Rate Limit**: 20 requests/hour

**Request**:
```json
{
  "analysis_type": "employer_screening",  // or "candidate_optimization"
  "target_role": "Senior Full Stack Developer",
  "job_description": "We are looking for a senior developer with 5+ years...",
  "job_position_id": 123,  // Optional: link to specific job posting
  "include_suggestions": true,
  "include_keywords": true,
  "include_ats_check": true
}
```

**Response**:
```json
{
  "id": 456,
  "resume_id": 789,
  "analysis_type": "employer_screening",
  "overall_score": 87,
  "scores": {
    "content_quality": 85,
    "skills_match": 90,
    "experience_relevance": 88,
    "ats_compatibility": 95,
    "keyword_optimization": 82
  },
  "extracted_skills": {
    "technical": ["Python", "React", "PostgreSQL", "AWS"],
    "soft": ["Leadership", "Communication", "Problem Solving"],
    "domain": ["E-commerce", "Fintech"]
  },
  "section_scores": {
    "professional_summary": 90,
    "work_experience": 85,
    "education": 80,
    "skills": 95,
    "projects": 88
  },
  "suggestions_count": 8,
  "critical_issues_count": 2,
  "status": "completed",
  "processing_time_ms": 2340,
  "created_at": "2025-10-13T10:30:00Z"
}
```

---

### 2. Get Resume Score (Quick)

**Endpoint**: `GET /api/resumes/{resume_id}/score`
**Permission**: Owner OR `resume_ats_screening`
**Rate Limit**: 50 requests/hour

**Response**:
```json
{
  "resume_id": 789,
  "overall_score": 87,
  "scores": {
    "content_quality": 85,
    "completeness": 90,
    "ats_compatibility": 95,
    "keyword_density": 82
  },
  "grade": "B+",  // A, A-, B+, B, B-, C+, C, D, F
  "percentile": 78,  // Compared to other resumes
  "last_calculated": "2025-10-13T10:30:00Z"
}
```

---

### 3. Get Optimization Suggestions

**Endpoint**: `POST /api/resumes/{resume_id}/optimize`
**Permission**: Owner OR `resume_ats_optimization`
**Rate Limit**: 20 requests/hour

**Request**:
```json
{
  "target_role": "Senior Full Stack Developer",
  "focus_areas": ["skills", "experience", "keywords"],  // Optional filter
  "priority_threshold": "medium"  // Only return medium+ priority suggestions
}
```

**Response**:
```json
{
  "resume_id": 789,
  "analysis_id": 456,
  "current_score": 87,
  "potential_score": 94,
  "suggestions": [
    {
      "id": 101,
      "category": "keywords",
      "section": "experience",
      "priority": "high",
      "title": "Add more action verbs in experience section",
      "description": "Your experience descriptions lack strong action verbs that demonstrate impact.",
      "suggested_action": "Replace passive language with action verbs like 'Led', 'Architected', 'Implemented', 'Optimized'",
      "example_text": "Led a team of 5 developers to architect and implement a microservices platform, reducing deployment time by 40%",
      "potential_score_improvement": 5,
      "difficulty": "easy",
      "is_applied": false
    },
    {
      "id": 102,
      "category": "skills",
      "section": "skills",
      "priority": "critical",
      "title": "Missing key technologies from job requirements",
      "description": "Your resume is missing several technologies commonly required for Senior Full Stack Developer roles.",
      "suggested_action": "Add experience with Docker, Kubernetes, and CI/CD pipelines if you have it",
      "potential_score_improvement": 8,
      "difficulty": "medium",
      "is_applied": false
    }
  ],
  "total_suggestions": 8,
  "by_priority": {
    "critical": 2,
    "high": 3,
    "medium": 2,
    "low": 1
  }
}
```

---

### 4. Suggest Keywords

**Endpoint**: `POST /api/resumes/{resume_id}/suggest-keywords`
**Permission**: Owner OR `resume_ats_optimization`
**Rate Limit**: 30 requests/hour

**Request**:
```json
{
  "target_role": "Senior Full Stack Developer",
  "industry": "fintech",
  "job_description": "Optional job description to match against"
}
```

**Response**:
```json
{
  "resume_id": 789,
  "target_role": "Senior Full Stack Developer",
  "current_keywords": [
    {
      "keyword": "Python",
      "type": "skill",
      "relevance_score": 95,
      "frequency": 8
    }
  ],
  "suggested_keywords": [
    {
      "keyword": "Microservices",
      "type": "technology",
      "importance": "critical",
      "relevance_score": 90,
      "reason": "Highly relevant for senior full-stack roles in your industry"
    },
    {
      "keyword": "CI/CD",
      "type": "technology",
      "importance": "important",
      "relevance_score": 85,
      "reason": "Common requirement for senior developer positions"
    }
  ],
  "missing_critical_keywords": 3,
  "keyword_optimization_score": 82
}
```

---

### 5. Check ATS Compatibility

**Endpoint**: `GET /api/resumes/{resume_id}/ats-check`
**Permission**: Owner OR `resume_ats_optimization`
**Rate Limit**: 30 requests/hour

**Response**:
```json
{
  "resume_id": 789,
  "overall_compatibility": 95,
  "passed": true,
  "checks": [
    {
      "check_type": "formatting",
      "check_name": "Font consistency",
      "passed": true,
      "severity": "info"
    },
    {
      "check_type": "structure",
      "check_name": "Contact information placement",
      "passed": false,
      "severity": "warning",
      "issue_description": "Contact information is embedded in a header that may not be parsed by all ATS systems",
      "fix_suggestion": "Move contact information to the main body of the resume",
      "impact_on_ats_parsing": "medium"
    }
  ],
  "critical_issues": 0,
  "warnings": 2,
  "info": 5,
  "last_checked": "2025-10-13T10:30:00Z"
}
```

---

### 6. Match Resume to Job

**Endpoint**: `POST /api/resumes/{resume_id}/match-job`
**Permission**: `resume_ats_screening`
**Rate Limit**: 30 requests/hour

**Request**:
```json
{
  "job_position_id": 123,
  "job_title": "Senior Full Stack Developer",
  "job_description": "Required: 5+ years experience with React, Node.js...",
  "required_skills": ["React", "Node.js", "PostgreSQL"],
  "preferred_skills": ["AWS", "Docker", "TypeScript"],
  "min_years_experience": 5
}
```

**Response**:
```json
{
  "resume_id": 789,
  "job_position_id": 123,
  "match_score": 87,
  "match_breakdown": {
    "required_skills_match": 90,
    "preferred_skills_match": 75,
    "experience_match": 85,
    "education_match": 100,
    "cultural_fit": 80
  },
  "matched_skills": ["React", "Node.js", "PostgreSQL", "AWS"],
  "missing_skills": ["Docker"],
  "years_experience": 6,
  "recommendation": "strong_match",  // "strong_match", "good_match", "partial_match", "weak_match"
  "notes": "Candidate has all required skills and exceeds experience requirement. Missing Docker experience.",
  "created_at": "2025-10-13T10:30:00Z"
}
```

---

### 7. Batch Analyze Resumes

**Endpoint**: `POST /api/resumes/batch-analyze`
**Permission**: `resume_ats_screening`
**Rate Limit**: 5 requests/hour

**Request**:
```json
{
  "resume_ids": [789, 790, 791, 792],
  "job_position_id": 123,
  "analysis_criteria": {
    "target_role": "Senior Full Stack Developer",
    "required_skills": ["React", "Node.js"],
    "min_years_experience": 5
  },
  "sort_by": "match_score",  // or "overall_score", "experience", "created_at"
  "limit": 20
}
```

**Response**:
```json
{
  "total_analyzed": 4,
  "job_position_id": 123,
  "results": [
    {
      "resume_id": 789,
      "candidate_name": "John Doe",
      "overall_score": 87,
      "match_score": 90,
      "ranking": 1,
      "recommendation": "strong_match",
      "analysis_id": 456
    },
    {
      "resume_id": 791,
      "candidate_name": "Jane Smith",
      "overall_score": 85,
      "match_score": 85,
      "ranking": 2,
      "recommendation": "good_match",
      "analysis_id": 457
    }
  ],
  "processing_time_ms": 5670,
  "created_at": "2025-10-13T10:30:00Z"
}
```

---

### 8. Get Analysis History

**Endpoint**: `GET /api/resumes/{resume_id}/analyses`
**Permission**: Owner OR `resume_ats_screening`
**Rate Limit**: 100 requests/hour

**Query Parameters**:
- `limit` (default: 10)
- `offset` (default: 0)
- `analysis_type` (filter by type)

**Response**:
```json
{
  "resume_id": 789,
  "total_analyses": 15,
  "analyses": [
    {
      "id": 456,
      "analysis_type": "employer_screening",
      "overall_score": 87,
      "target_role": "Senior Full Stack Developer",
      "analyzed_by": {
        "id": 12,
        "name": "Jane Recruiter",
        "company": "Tech Corp"
      },
      "created_at": "2025-10-13T10:30:00Z"
    }
  ],
  "score_trend": {
    "current": 87,
    "previous": 82,
    "change": +5
  }
}
```

---

### 9. Get Analysis Details

**Endpoint**: `GET /api/resumes/analyses/{analysis_id}`
**Permission**: Owner OR Analyzer
**Rate Limit**: 100 requests/hour

**Response**: Full analysis object with all suggestions, keywords, and compatibility checks

---

### 10. Apply/Dismiss Suggestion

**Endpoint**: `PATCH /api/resumes/analyses/{analysis_id}/suggestions/{suggestion_id}`
**Permission**: Owner
**Rate Limit**: 100 requests/hour

**Request**:
```json
{
  "action": "apply",  // or "dismiss"
  "notes": "Applied suggestion to experience section"
}
```

---

## 🔧 Service Layer Architecture

### File: `backend/app/services/resume_ats_service.py`

**Key Components**:

```python
class ResumeATSService:
    """
    Service for ATS analysis and optimization functionality.
    """

    # Core analysis methods
    async def analyze_resume(self, db: AsyncSession, resume_id: int, user_id: int,
                           analysis_request: AnalysisRequest) -> ResumeAnalysis

    async def calculate_resume_score(self, resume: Resume, target_role: str = None) -> dict

    async def generate_optimization_suggestions(self, resume: Resume,
                                              target_role: str = None) -> list[OptimizationSuggestion]

    # Keyword extraction and analysis
    async def extract_keywords(self, resume: Resume) -> dict

    async def suggest_keywords(self, resume: Resume, target_role: str,
                              industry: str = None) -> list[KeywordSuggestion]

    # Job matching
    async def match_resume_to_job(self, resume: Resume, job_data: dict) -> JobMatchResult

    # ATS compatibility
    async def check_ats_compatibility(self, resume: Resume) -> ATSCompatibilityResult

    # Batch operations
    async def batch_analyze_resumes(self, db: AsyncSession, resume_ids: list[int],
                                   criteria: dict) -> list[AnalysisResult]

    # AI/ML integration methods
    def _analyze_content_quality(self, text: str) -> int
    def _extract_skills_with_nlp(self, text: str) -> dict
    def _calculate_keyword_relevance(self, keyword: str, context: str) -> int
    def _generate_improvement_suggestions(self, section: str, content: str) -> list
```

**Rule-Based Implementation**:

All algorithms use pattern matching, statistical analysis, and predefined dictionaries:

1. **Scoring Algorithms**: Weighted formulas based on content analysis
   - Professional summary scoring
   - Experience quality scoring
   - Skills coverage scoring
   - Completeness scoring

2. **Keyword Extraction**: Pattern matching with predefined skill dictionaries
   - Technical skills database (200+ skills)
   - Soft skills database (20+ skills)
   - Action verbs database (40+ verbs)
   - Technology keywords

3. **Suggestion Generation**: Rule-based templates
   - Content quality checks
   - Section completeness checks
   - Keyword density analysis
   - ATS compatibility checks

See **[ATS_RULE_BASED_ALGORITHMS.md](./ATS_RULE_BASED_ALGORITHMS.md)** for complete implementation details.

---

## 🔒 Premium Features Configuration

### Feature Catalog Setup

**Database Seed**: `backend/app/seeds/features.py`

Add two new features:

```python
# Feature 1: Employer Resume Screening
{
    "name": "resume_ats_screening",
    "display_name": "ATS Resume Screening",
    "description": "Automated resume analysis, candidate screening, and ranking system for employers using rule-based algorithms",
    "category": "premium",
    "permission_key": "ats.screening",
    "is_active": True
}

# Feature 2: Candidate Resume Optimization
{
    "name": "resume_ats_optimization",
    "display_name": "Resume Optimization",
    "description": "Automated resume optimization with quality scoring, ATS compatibility checks, and improvement suggestions using rule-based algorithms",
    "category": "premium",
    "permission_key": "ats.optimization",
    "is_active": True
}
```

### Subscription Plan Assignment

**Recommended Plan Structure**:

1. **Free Plan**: No ATS features
2. **Basic Plan**: 5 optimizations/month (candidate)
3. **Professional Plan**:
   - Unlimited optimizations (candidate)
   - 20 screenings/month (employer)
4. **Enterprise Plan**:
   - Unlimited everything
   - Batch analysis
   - Advanced reporting

### Permission Checks

**Middleware**: `backend/app/middleware/feature_check.py`

```python
@router.post("/resumes/{resume_id}/analyze")
async def analyze_resume(
    resume_id: int,
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Check permission based on analysis type
    required_feature = (
        "resume_ats_screening" if request.analysis_type == "employer_screening"
        else "resume_ats_optimization"
    )

    # Check if user has access to feature
    if not await has_feature_access(db, current_user, required_feature):
        raise HTTPException(
            status_code=403,
            detail=f"This feature requires '{required_feature}'. Please upgrade your subscription."
        )

    # Proceed with analysis...
```

---

## 💻 Frontend Implementation

### TypeScript Types

**File**: `frontend/src/types/resume-ats.ts`

```typescript
// Enums
export enum AnalysisType {
  EMPLOYER_SCREENING = 'employer_screening',
  CANDIDATE_OPTIMIZATION = 'candidate_optimization',
  JOB_MATCHING = 'job_matching',
}

export enum SuggestionCategory {
  CONTENT = 'content',
  SKILLS = 'skills',
  EXPERIENCE = 'experience',
  KEYWORDS = 'keywords',
  FORMATTING = 'formatting',
  ATS_COMPATIBILITY = 'ats_compatibility',
}

export enum Priority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

// Main interfaces
export interface ResumeAnalysis {
  id: number;
  resume_id: number;
  analysis_type: AnalysisType;
  overall_score: number;
  scores: ScoreBreakdown;
  extracted_skills: ExtractedSkills;
  section_scores: Record<string, number>;
  suggestions_count: number;
  critical_issues_count: number;
  status: string;
  processing_time_ms: number;
  created_at: string;
}

export interface ScoreBreakdown {
  content_quality: number;
  skills_match: number;
  experience_relevance: number;
  ats_compatibility: number;
  keyword_optimization: number;
}

export interface OptimizationSuggestion {
  id: number;
  category: SuggestionCategory;
  section: string | null;
  priority: Priority;
  title: string;
  description: string;
  suggested_action: string;
  example_text: string | null;
  potential_score_improvement: number | null;
  difficulty: string;
  is_applied: boolean;
  dismissed: boolean;
}

export interface KeywordSuggestion {
  keyword: string;
  type: string;
  importance: string;
  relevance_score: number;
  reason: string;
}

export interface ATSCompatibilityCheck {
  check_type: string;
  check_name: string;
  passed: boolean;
  severity: string;
  issue_description?: string;
  fix_suggestion?: string;
  impact_on_ats_parsing?: string;
}

// Request types
export interface AnalyzeResumeRequest {
  analysis_type: AnalysisType;
  target_role?: string;
  job_description?: string;
  job_position_id?: number;
  include_suggestions?: boolean;
  include_keywords?: boolean;
  include_ats_check?: boolean;
}

export interface OptimizeResumeRequest {
  target_role?: string;
  focus_areas?: string[];
  priority_threshold?: string;
}

export interface SuggestKeywordsRequest {
  target_role: string;
  industry?: string;
  job_description?: string;
}

export interface JobMatchRequest {
  job_position_id?: number;
  job_title: string;
  job_description: string;
  required_skills: string[];
  preferred_skills?: string[];
  min_years_experience?: number;
}
```

---

### API Client Functions

**File**: `frontend/src/api/resume-ats.ts`

```typescript
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type {
  ResumeAnalysis,
  AnalyzeResumeRequest,
  OptimizeResumeRequest,
  OptimizationSuggestion,
  KeywordSuggestion,
  SuggestKeywordsRequest,
  ATSCompatibilityCheck,
  JobMatchRequest,
} from '@/types/resume-ats';

export const resumeATSApi = {
  // Analyze resume
  async analyzeResume(
    resumeId: number,
    request: AnalyzeResumeRequest
  ): Promise<ApiResponse<ResumeAnalysis>> {
    const response = await apiClient.post<ResumeAnalysis>(
      `/api/resumes/${resumeId}/analyze`,
      request
    );
    return { data: response.data, success: true };
  },

  // Get resume score
  async getResumeScore(resumeId: number): Promise<ApiResponse<any>> {
    const response = await apiClient.get<any>(`/api/resumes/${resumeId}/score`);
    return { data: response.data, success: true };
  },

  // Get optimization suggestions
  async optimizeResume(
    resumeId: number,
    request: OptimizeResumeRequest
  ): Promise<ApiResponse<{ suggestions: OptimizationSuggestion[] }>> {
    const response = await apiClient.post(
      `/api/resumes/${resumeId}/optimize`,
      request
    );
    return { data: response.data, success: true };
  },

  // Suggest keywords
  async suggestKeywords(
    resumeId: number,
    request: SuggestKeywordsRequest
  ): Promise<ApiResponse<{ suggested_keywords: KeywordSuggestion[] }>> {
    const response = await apiClient.post(
      `/api/resumes/${resumeId}/suggest-keywords`,
      request
    );
    return { data: response.data, success: true };
  },

  // Check ATS compatibility
  async checkATSCompatibility(
    resumeId: number
  ): Promise<ApiResponse<{ checks: ATSCompatibilityCheck[] }>> {
    const response = await apiClient.get(`/api/resumes/${resumeId}/ats-check`);
    return { data: response.data, success: true };
  },

  // Match resume to job
  async matchResumeToJob(
    resumeId: number,
    request: JobMatchRequest
  ): Promise<ApiResponse<any>> {
    const response = await apiClient.post(
      `/api/resumes/${resumeId}/match-job`,
      request
    );
    return { data: response.data, success: true };
  },

  // Get analysis history
  async getAnalysisHistory(
    resumeId: number,
    params?: { limit?: number; offset?: number; analysis_type?: string }
  ): Promise<ApiResponse<{ analyses: ResumeAnalysis[] }>> {
    const response = await apiClient.get(
      `/api/resumes/${resumeId}/analyses`,
      { params }
    );
    return { data: response.data, success: true };
  },

  // Get analysis details
  async getAnalysisDetails(
    analysisId: number
  ): Promise<ApiResponse<ResumeAnalysis>> {
    const response = await apiClient.get<ResumeAnalysis>(
      `/api/resumes/analyses/${analysisId}`
    );
    return { data: response.data, success: true };
  },

  // Apply/dismiss suggestion
  async updateSuggestion(
    analysisId: number,
    suggestionId: number,
    action: 'apply' | 'dismiss',
    notes?: string
  ): Promise<ApiResponse<OptimizationSuggestion>> {
    const response = await apiClient.patch(
      `/api/resumes/analyses/${analysisId}/suggestions/${suggestionId}`,
      { action, notes }
    );
    return { data: response.data, success: true };
  },

  // Batch analyze resumes
  async batchAnalyzeResumes(request: {
    resume_ids: number[];
    job_position_id?: number;
    analysis_criteria: any;
  }): Promise<ApiResponse<any>> {
    const response = await apiClient.post('/api/resumes/batch-analyze', request);
    return { data: response.data, success: true };
  },
};
```

**Update API Config** (`frontend/src/api/config.ts`):

```typescript
export const API_ENDPOINTS = {
  // ... existing endpoints ...

  RESUME_ATS: {
    ANALYZE: (id: number) => `/api/resumes/${id}/analyze`,
    ATS_CHECK: (id: number) => `/api/resumes/${id}/ats-check`,
    BATCH_ANALYZE: '/api/resumes/batch-analyze',
    MATCH_JOB: (id: number) => `/api/resumes/${id}/match-job`,
    OPTIMIZE: (id: number) => `/api/resumes/${id}/optimize`,
    SCORE: (id: number) => `/api/resumes/${id}/score`,
    SUGGEST_KEYWORDS: (id: number) => `/api/resumes/${id}/suggest-keywords`,
  },
} as const;
```

---

## ✅ Implementation Checklist

### Phase 1: Backend Foundation (Week 1)

- [ ] Create database models (`resume_ats.py`)
  - [ ] `ResumeAnalysis` model
  - [ ] `ResumeOptimizationSuggestion` model
  - [ ] `ResumeKeyword` model
  - [ ] `ATSCompatibilityCheck` model
  - [ ] Update relationships in existing models

- [ ] Create Alembic migration
  - [ ] Generate migration file
  - [ ] Test migration up/down
  - [ ] Verify foreign key constraints

- [ ] Create schemas (`resume_ats.py`)
  - [ ] All request schemas
  - [ ] All response schemas
  - [ ] Enums (AnalysisType, Priority, etc.)
  - [ ] Validation rules

- [ ] Create CRUD operations (`crud/resume_ats.py`)
  - [ ] Create analysis
  - [ ] Get analysis by ID
  - [ ] Get analysis history
  - [ ] Create/update suggestions
  - [ ] Keyword operations
  - [ ] Compatibility check operations

---

### Phase 2: Service Layer (Week 2)

- [ ] Implement `ResumeATSService` base structure
  - [ ] Initialize service class
  - [ ] Add error handling
  - [ ] Add logging

- [ ] Implement scoring algorithms
  - [ ] Content quality scoring
  - [ ] Skills match scoring
  - [ ] Experience relevance scoring
  - [ ] ATS compatibility scoring
  - [ ] Keyword optimization scoring

- [ ] Implement keyword extraction
  - [ ] Basic keyword extraction
  - [ ] NLP-based skill extraction
  - [ ] Keyword relevance calculation
  - [ ] Missing keyword detection

- [ ] Implement optimization suggestions
  - [ ] Content improvement suggestions
  - [ ] Skills gap analysis
  - [ ] Experience enhancement suggestions
  - [ ] Keyword optimization suggestions
  - [ ] Formatting recommendations

- [ ] Implement ATS compatibility checks
  - [ ] Formatting checks
  - [ ] Structure validation
  - [ ] Parsing simulation
  - [ ] Issue detection

- [ ] Implement job matching logic
  - [ ] Skills matching
  - [ ] Experience matching
  - [ ] Requirement scoring
  - [ ] Match recommendation

---

### Phase 3: API Layer (Week 3)

- [ ] Create endpoint file (`endpoints/resume_ats.py`)
- [ ] Implement all endpoints (10 endpoints)
  - [ ] POST `/analyze` - Comprehensive analysis
  - [ ] GET `/score` - Quick score
  - [ ] POST `/optimize` - Get suggestions
  - [ ] POST `/suggest-keywords` - Keyword suggestions
  - [ ] GET `/ats-check` - ATS compatibility
  - [ ] POST `/match-job` - Job matching
  - [ ] POST `/batch-analyze` - Batch operations
  - [ ] GET `/analyses` - History
  - [ ] GET `/analyses/{id}` - Details
  - [ ] PATCH `/suggestions/{id}` - Apply/dismiss

- [ ] Add to `config/endpoints.py` (alphabetically)
- [ ] Add permission checks (feature gating)
- [ ] Add rate limiting
- [ ] Add request validation
- [ ] Add error handling
- [ ] Add API documentation (docstrings)

---

### Phase 4: Premium Features (Week 3)

- [ ] Create feature catalog entries
  - [ ] `resume_ats_screening` feature
  - [ ] `resume_ats_optimization` feature
  - [ ] Add to database seed

- [ ] Implement permission middleware
  - [ ] Feature access check function
  - [ ] User subscription verification
  - [ ] Usage tracking/limits

- [ ] Update subscription plans
  - [ ] Assign features to plans
  - [ ] Set usage limits
  - [ ] Configure pricing

---

### Phase 5: Frontend (Week 4)

- [ ] Create TypeScript types (`types/resume-ats.ts`)
  - [ ] All interfaces
  - [ ] Enums
  - [ ] Request/response types

- [ ] Create API client (`api/resume-ats.ts`)
  - [ ] All API functions
  - [ ] Error handling
  - [ ] Type safety

- [ ] Update API config
  - [ ] Add ATS endpoints
  - [ ] Alphabetical ordering

- [ ] Create React components
  - [ ] Resume score dashboard
  - [ ] Suggestions list component
  - [ ] Keyword analysis component
  - [ ] ATS compatibility report
  - [ ] Analysis history view

- [ ] Create custom hooks
  - [ ] `useResumeAnalysis`
  - [ ] `useOptimizationSuggestions`
  - [ ] `useATSCheck`
  - [ ] `useResumeScore`

---

### Phase 6: Testing (Week 5)

- [ ] Backend unit tests
  - [ ] Service layer tests
  - [ ] CRUD tests
  - [ ] Scoring algorithm tests

- [ ] Backend integration tests
  - [ ] API endpoint tests
  - [ ] Permission tests
  - [ ] Database operations

- [ ] Frontend tests
  - [ ] Component tests
  - [ ] Hook tests
  - [ ] API client tests

- [ ] End-to-end tests
  - [ ] Full analysis flow
  - [ ] Optimization flow
  - [ ] Job matching flow

---

### Phase 7: AI/ML Integration (Week 6)

- [ ] Choose AI/ML approach
  - [ ] Evaluate options (OpenAI, spaCy, custom)
  - [ ] Set up API credentials
  - [ ] Create integration layer

- [ ] Implement AI features
  - [ ] Content analysis with AI
  - [ ] Suggestion generation
  - [ ] Skill extraction
  - [ ] Keyword relevance

- [ ] Fine-tune algorithms
  - [ ] Test with sample resumes
  - [ ] Adjust scoring weights
  - [ ] Improve accuracy

- [ ] Add caching layer
  - [ ] Cache analysis results
  - [ ] Cache AI responses
  - [ ] Optimize performance

---

## 🧪 Testing Requirements

### Unit Tests

**Backend**:
```python
# test_resume_ats_service.py
def test_calculate_resume_score():
    """Test resume scoring algorithm"""

def test_extract_keywords():
    """Test keyword extraction"""

def test_generate_suggestions():
    """Test suggestion generation"""

def test_check_ats_compatibility():
    """Test ATS compatibility checks"""

def test_match_resume_to_job():
    """Test job matching algorithm"""
```

### Integration Tests

```python
# test_resume_ats_endpoints.py
async def test_analyze_resume_endpoint():
    """Test resume analysis endpoint"""

async def test_optimize_resume_endpoint():
    """Test optimization endpoint"""

async def test_permission_checks():
    """Test feature gating"""

async def test_rate_limiting():
    """Test rate limit enforcement"""
```

### E2E Tests

```typescript
// resume-ats.e2e.test.ts
describe('Resume ATS Flow', () => {
  it('should analyze resume and show results', async () => {
    // Test full analysis flow
  });

  it('should display optimization suggestions', async () => {
    // Test optimization flow
  });

  it('should enforce premium feature access', async () => {
    // Test permission checks
  });
});
```

---

## 📊 Migration Steps

### Database Migration

```bash
# 1. Create migration
cd backend
alembic revision --autogenerate -m "Add ATS resume analysis tables"

# 2. Review migration file
# backend/alembic/versions/XXXX_add_ats_resume_analysis_tables.py

# 3. Apply migration
alembic upgrade head

# 4. Verify tables created
# Check: resume_analyses, resume_optimization_suggestions,
#        resume_keywords, ats_compatibility_checks
```

### Feature Seeding

```bash
# Run feature seed to add ATS features
python -m app.seeds.features
```

### Testing

```bash
# Run tests
pytest backend/tests/test_resume_ats*.py -v

# Run integration tests
pytest backend/tests/integration/test_resume_ats*.py -v
```

### Deployment

```bash
# 1. Deploy backend (staging)
docker-compose -f docker-compose.staging.yml up -d backend

# 2. Run migrations on staging
docker exec miraiworks_backend alembic upgrade head

# 3. Test on staging
# Run smoke tests

# 4. Deploy to production
docker-compose -f docker-compose.prod.yml up -d backend

# 5. Run migrations on production
docker exec miraiworks_backend_prod alembic upgrade head

# 6. Monitor logs
docker logs -f miraiworks_backend_prod
```

---

## 📈 Success Metrics

### Technical Metrics
- ✅ All endpoints respond in < 2 seconds
- ✅ Analysis accuracy > 85%
- ✅ ATS compatibility detection accuracy > 90%
- ✅ 99.9% uptime for ATS services
- ✅ Rate limit violations < 1%

### Business Metrics
- ✅ Premium conversion rate > 15%
- ✅ User engagement with suggestions > 70%
- ✅ Suggestion application rate > 40%
- ✅ Customer satisfaction score > 4.5/5

---

## 🔜 Future Enhancements

### Phase 2 Features (Post-MVP)
- [ ] Resume comparison tool
- [ ] Industry benchmarking
- [ ] Historical score tracking with charts
- [ ] AI-powered resume rewriting
- [ ] Cover letter analysis
- [ ] LinkedIn profile integration
- [ ] Video resume analysis
- [ ] Batch export capabilities
- [ ] White-label reports for agencies
- [ ] Custom scoring weights

---

## 📚 References

### Architecture Documents
- `CLAUDE.md` - Project architecture rules
- `docs/COMPANY_CONNECTIONS_BEHAVIOR.md` - Connection patterns
- `backend/app/models/base.py` - BaseModel pattern

### Existing Resume Implementation
- `backend/app/models/resume.py` - Resume models
- `backend/app/services/resume_service.py` - Resume service
- `backend/app/endpoints/resumes.py` - Resume endpoints

### Subscription System
- `backend/app/models/feature.py` - Feature model
- `backend/app/models/subscription_plan.py` - Plans
- `backend/app/services/subscription_service.py` - Subscription logic

---

## 👥 Implementation Team

**Backend Developer**: Database models, service layer, API endpoints
**AI/ML Engineer**: Scoring algorithms, NLP integration
**Frontend Developer**: UI components, TypeScript types, API integration
**QA Engineer**: Test planning, test execution, quality assurance

**Estimated Timeline**: 6 weeks for MVP

---

**Document Status**: ✅ Ready for Implementation
**Next Action**: Begin Phase 1 - Backend Foundation
**Owner**: Development Team
**Review Date**: 2025-10-20
