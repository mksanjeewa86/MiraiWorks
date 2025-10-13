# ATS Rule-Based Algorithms (Non-AI Implementation)

**Document Version**: 1.0
**Created**: 2025-10-13
**Approach**: Rule-Based / Statistical (No AI/ML)
**Status**: Implementation Guide

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Scoring Algorithms](#scoring-algorithms)
3. [Keyword Extraction](#keyword-extraction)
4. [Skills Detection](#skills-detection)
5. [Optimization Suggestions](#optimization-suggestions)
6. [ATS Compatibility Checks](#ats-compatibility-checks)
7. [Job Matching Logic](#job-matching-logic)
8. [Implementation Code](#implementation-code)
9. [Data Dictionaries](#data-dictionaries)

---

## 📖 Overview

### Rule-Based Approach Benefits

**Advantages**:
- ✅ No external API dependencies or costs
- ✅ Fast processing (< 500ms per resume)
- ✅ Deterministic and predictable results
- ✅ Easy to debug and tune
- ✅ Complete control over logic
- ✅ No rate limits or API quotas
- ✅ Privacy-friendly (no data sent externally)

**Approach**:
- Use keyword dictionaries and pattern matching
- Statistical analysis of resume content
- Rule-based scoring with weighted factors
- Predefined suggestion templates
- Regex patterns for data extraction

---

## 🎯 Scoring Algorithms

### 1. Overall Resume Score (0-100)

**Formula**:
```python
overall_score = (
    content_quality_score * 0.25 +
    completeness_score * 0.20 +
    experience_score * 0.20 +
    skills_score * 0.15 +
    ats_compatibility_score * 0.15 +
    keyword_density_score * 0.05
)
```

---

### 2. Content Quality Score

**Factors** (each 0-100):

#### A. Professional Summary Quality (30%)
```python
def score_professional_summary(summary: str) -> int:
    """Score professional summary quality."""
    if not summary:
        return 0

    score = 50  # Base score for having a summary

    # Length check (150-300 words is ideal)
    word_count = len(summary.split())
    if 150 <= word_count <= 300:
        score += 20
    elif 100 <= word_count < 150 or 300 < word_count <= 400:
        score += 10

    # Contains action verbs
    action_verbs = ['led', 'managed', 'developed', 'created', 'implemented',
                    'designed', 'architected', 'optimized', 'established', 'launched']
    action_count = sum(1 for verb in action_verbs if verb.lower() in summary.lower())
    score += min(action_count * 3, 15)

    # Contains metrics/numbers
    import re
    numbers = re.findall(r'\d+[%+]?', summary)
    if numbers:
        score += min(len(numbers) * 5, 15)

    return min(score, 100)
```

#### B. Experience Descriptions Quality (40%)
```python
def score_experience_quality(experiences: list) -> int:
    """Score work experience descriptions."""
    if not experiences:
        return 0

    total_score = 0

    for exp in experiences:
        exp_score = 0
        description = exp.description or ""

        # Has description
        if description:
            exp_score += 20

        # Description length (100-500 words per job)
        word_count = len(description.split())
        if 100 <= word_count <= 500:
            exp_score += 20
        elif 50 <= word_count < 100:
            exp_score += 10

        # Bullet points or structured format
        if '•' in description or '\n-' in description or '\n*' in description:
            exp_score += 10

        # Contains action verbs
        action_count = sum(1 for verb in ACTION_VERBS if verb.lower() in description.lower())
        exp_score += min(action_count * 2, 20)

        # Contains achievements/metrics
        import re
        achievements = re.findall(r'(increased|decreased|improved|reduced|achieved|delivered|saved).*?(\d+%?)',
                                 description, re.IGNORECASE)
        exp_score += min(len(achievements) * 10, 30)

        total_score += exp_score

    # Average across experiences
    return min(total_score // len(experiences), 100)
```

#### C. Grammar and Spelling (30%)
```python
def check_grammar_and_spelling(text: str) -> int:
    """Basic grammar and spelling check."""
    score = 100

    # Check for common issues
    issues = 0

    # Double spaces
    if '  ' in text:
        issues += text.count('  ')

    # Missing punctuation at sentence ends
    import re
    sentences = re.split(r'[.!?]\s', text)
    for sentence in sentences:
        if sentence and not sentence.strip().endswith(('.', '!', '?')):
            issues += 1

    # Inconsistent capitalization after periods
    bad_caps = re.findall(r'\.\s+[a-z]', text)
    issues += len(bad_caps)

    # Basic word repetition (same word 3+ times in a row)
    words = text.lower().split()
    for i in range(len(words) - 2):
        if words[i] == words[i+1] == words[i+2]:
            issues += 1

    # Deduct points for issues
    score -= min(issues * 5, 50)

    return max(score, 0)
```

---

### 3. Completeness Score

```python
def calculate_completeness_score(resume: Resume) -> int:
    """Calculate how complete the resume is."""
    score = 0
    max_score = 100

    # Required sections (60 points total)
    sections = {
        'contact_info': 10,      # Name, email, phone
        'professional_summary': 10,
        'work_experience': 15,
        'education': 10,
        'skills': 15,
    }

    # Contact info
    if resume.full_name and resume.email and resume.phone:
        score += sections['contact_info']
    elif resume.full_name and resume.email:
        score += 7

    # Professional summary
    if resume.professional_summary and len(resume.professional_summary) >= 100:
        score += sections['professional_summary']
    elif resume.professional_summary:
        score += 5

    # Work experience
    if len(resume.experiences) >= 3:
        score += sections['work_experience']
    elif len(resume.experiences) >= 1:
        score += sections['work_experience'] * len(resume.experiences) / 3

    # Education
    if len(resume.educations) >= 1:
        score += sections['education']

    # Skills
    if len(resume.skills) >= 10:
        score += sections['skills']
    elif len(resume.skills) >= 5:
        score += sections['skills'] * 0.7
    elif len(resume.skills) >= 1:
        score += sections['skills'] * 0.4

    # Optional sections (40 points total)
    optional = {
        'projects': 10,
        'certifications': 10,
        'languages': 10,
        'references': 5,
        'linkedin': 5,
    }

    if len(resume.projects) >= 2:
        score += optional['projects']
    elif len(resume.projects) == 1:
        score += optional['projects'] * 0.5

    if len(resume.certifications) >= 2:
        score += optional['certifications']
    elif len(resume.certifications) == 1:
        score += optional['certifications'] * 0.5

    if len(resume.languages) >= 2:
        score += optional['languages']
    elif len(resume.languages) == 1:
        score += optional['languages'] * 0.5

    if resume.references and len(resume.references) >= 2:
        score += optional['references']

    if resume.linkedin_url:
        score += optional['linkedin']

    return min(int(score), max_score)
```

---

### 4. Experience Relevance Score

```python
def calculate_experience_score(experiences: list, target_role: str = None) -> int:
    """Calculate experience relevance and quality."""
    if not experiences:
        return 0

    score = 0

    # Years of experience (40 points)
    total_months = 0
    for exp in experiences:
        start = exp.start_date
        end = exp.end_date or datetime.now()
        months = (end.year - start.year) * 12 + (end.month - start.month)
        total_months += max(months, 0)

    years = total_months / 12
    if years >= 10:
        score += 40
    elif years >= 5:
        score += 30
    elif years >= 3:
        score += 20
    elif years >= 1:
        score += 10

    # Job progression/career growth (30 points)
    # Check for seniority in titles
    seniority_keywords = {
        'senior': 3,
        'lead': 3,
        'principal': 4,
        'staff': 3,
        'director': 4,
        'head': 4,
        'chief': 5,
        'vp': 5,
        'manager': 3,
    }

    max_seniority = 0
    for exp in experiences:
        title_lower = exp.position_title.lower()
        for keyword, level in seniority_keywords.items():
            if keyword in title_lower:
                max_seniority = max(max_seniority, level)

    score += min(max_seniority * 6, 30)

    # Relevance to target role (30 points)
    if target_role:
        target_lower = target_role.lower()
        relevance = 0

        for exp in experiences:
            title_lower = exp.position_title.lower()
            # Check for keyword overlap
            target_words = set(target_lower.split())
            title_words = set(title_lower.split())
            overlap = len(target_words & title_words)

            if overlap >= 2:
                relevance += 15
            elif overlap >= 1:
                relevance += 8

        score += min(relevance, 30)
    else:
        score += 15  # Base score if no target role specified

    return min(score, 100)
```

---

### 5. Skills Match Score

```python
def calculate_skills_score(resume: Resume, required_skills: list = None) -> int:
    """Calculate skills coverage and relevance."""
    if not resume.skills:
        return 0

    score = 0

    # Number of skills (40 points)
    skill_count = len(resume.skills)
    if skill_count >= 20:
        score += 40
    elif skill_count >= 15:
        score += 32
    elif skill_count >= 10:
        score += 24
    elif skill_count >= 5:
        score += 16
    else:
        score += skill_count * 3

    # Skill categorization (30 points)
    categories = set()
    for skill in resume.skills:
        if skill.category:
            categories.add(skill.category.lower())

    # More categories = more diverse skill set
    category_count = len(categories)
    if category_count >= 4:
        score += 30
    elif category_count >= 3:
        score += 20
    elif category_count >= 2:
        score += 10

    # Proficiency levels specified (30 points)
    with_proficiency = sum(1 for skill in resume.skills if skill.proficiency_level)
    if with_proficiency == skill_count:
        score += 30
    else:
        score += int((with_proficiency / skill_count) * 30)

    # Match with required skills (bonus if provided)
    if required_skills:
        matched = 0
        resume_skill_names = [s.name.lower() for s in resume.skills]

        for req_skill in required_skills:
            if req_skill.lower() in resume_skill_names:
                matched += 1

        match_rate = matched / len(required_skills)
        score = int(score * (0.5 + match_rate * 0.5))  # Adjust score based on match

    return min(score, 100)
```

---

### 6. ATS Compatibility Score

```python
def calculate_ats_compatibility_score(resume: Resume) -> int:
    """Check ATS parsing compatibility."""
    score = 100
    issues = []

    # File format check (if PDF path exists)
    # Assume we're checking the structured data, not PDF parsing

    # Contact information placement (critical)
    if not resume.full_name or not resume.email:
        score -= 20
        issues.append("Missing critical contact information")

    # Phone number format
    if resume.phone:
        import re
        # Check if phone has proper format
        if not re.match(r'^[\d\s\-\+\(\)]+$', resume.phone):
            score -= 5
            issues.append("Phone number has unusual characters")

    # Section organization
    sections_present = 0
    if resume.professional_summary:
        sections_present += 1
    if resume.experiences:
        sections_present += 1
    if resume.educations:
        sections_present += 1
    if resume.skills:
        sections_present += 1

    if sections_present < 3:
        score -= 15
        issues.append("Missing essential resume sections")

    # Date formatting in experiences
    for exp in resume.experiences:
        if exp.is_current and exp.end_date:
            score -= 5
            issues.append("Current job has end date (conflicting data)")

    # URL formatting
    urls = [resume.website, resume.linkedin_url, resume.github_url]
    for url in urls:
        if url:
            if not (url.startswith('http://') or url.startswith('https://')):
                score -= 3
                issues.append("URLs should start with http:// or https://")

    # Email validation
    if resume.email and '@' not in resume.email:
        score -= 10
        issues.append("Invalid email format")

    # Skills without proficiency (minor issue)
    skills_without_prof = sum(1 for s in resume.skills if not s.proficiency_level)
    if skills_without_prof > len(resume.skills) * 0.5:
        score -= 5
        issues.append("Many skills lack proficiency levels")

    # Custom CSS might break ATS parsing
    if resume.custom_css and len(resume.custom_css) > 100:
        score -= 10
        issues.append("Excessive custom styling may affect ATS parsing")

    return max(score, 0)
```

---

### 7. Keyword Density Score

```python
def calculate_keyword_density(resume: Resume, target_keywords: list = None) -> int:
    """Calculate keyword optimization score."""
    # Combine all text from resume
    text_parts = []

    if resume.professional_summary:
        text_parts.append(resume.professional_summary)

    for exp in resume.experiences:
        if exp.description:
            text_parts.append(exp.description)

    for edu in resume.educations:
        if edu.description:
            text_parts.append(edu.description)

    full_text = ' '.join(text_parts).lower()
    word_count = len(full_text.split())

    if word_count < 100:
        return 20  # Not enough content

    score = 50  # Base score

    # Industry keywords (if target keywords provided)
    if target_keywords:
        found_keywords = sum(1 for kw in target_keywords if kw.lower() in full_text)
        keyword_rate = found_keywords / len(target_keywords)
        score += int(keyword_rate * 50)
    else:
        # General keyword analysis
        important_terms = [
            'developed', 'managed', 'led', 'created', 'implemented',
            'designed', 'optimized', 'achieved', 'increased', 'improved'
        ]
        found = sum(1 for term in important_terms if term in full_text)
        score += min(found * 5, 50)

    return min(score, 100)
```

---

## 🔍 Keyword Extraction

### Extract Keywords from Resume

```python
import re
from collections import Counter

def extract_keywords(resume: Resume) -> dict:
    """Extract keywords from resume using pattern matching."""

    # Combine all text
    text_parts = []
    if resume.professional_summary:
        text_parts.append(resume.professional_summary)
    for exp in resume.experiences:
        if exp.description:
            text_parts.append(exp.description)

    full_text = ' '.join(text_parts)

    # Extract different types of keywords
    keywords = {
        'technical_skills': [],
        'soft_skills': [],
        'action_verbs': [],
        'technologies': [],
        'certifications': [],
    }

    # Technical skills (from predefined list)
    for skill in TECHNICAL_SKILLS_DATABASE:
        if skill.lower() in full_text.lower():
            keywords['technical_skills'].append(skill)

    # Soft skills
    for skill in SOFT_SKILLS_DATABASE:
        if skill.lower() in full_text.lower():
            keywords['soft_skills'].append(skill)

    # Action verbs
    words = full_text.lower().split()
    for verb in ACTION_VERBS:
        if verb in words:
            keywords['action_verbs'].append(verb)

    # Extract technologies (programming languages, frameworks)
    for tech in TECHNOLOGY_DATABASE:
        pattern = r'\b' + re.escape(tech) + r'\b'
        if re.search(pattern, full_text, re.IGNORECASE):
            keywords['technologies'].append(tech)

    # Extract certifications from certification models
    for cert in resume.certifications:
        keywords['certifications'].append(cert.name)

    # Count frequency
    for category in keywords:
        keywords[category] = list(set(keywords[category]))  # Remove duplicates

    return keywords


def calculate_keyword_relevance(keyword: str, context: str, target_role: str = None) -> int:
    """Calculate relevance score for a keyword (0-100)."""
    score = 50  # Base relevance

    # Frequency in context
    frequency = context.lower().count(keyword.lower())
    score += min(frequency * 5, 25)

    # Proximity to target role keywords
    if target_role:
        target_words = target_role.lower().split()
        keyword_lower = keyword.lower()

        # Check if keyword appears in target role
        if keyword_lower in target_role.lower():
            score += 25
        # Check for related words
        elif any(word in keyword_lower or keyword_lower in word for word in target_words):
            score += 15

    return min(score, 100)
```

---

## 💡 Optimization Suggestions

### Generate Suggestions Based on Rules

```python
def generate_optimization_suggestions(resume: Resume, target_role: str = None) -> list:
    """Generate improvement suggestions using rule-based analysis."""
    suggestions = []

    # 1. Professional Summary Suggestions
    if not resume.professional_summary:
        suggestions.append({
            'category': 'content',
            'section': 'summary',
            'priority': 'critical',
            'title': 'Add Professional Summary',
            'description': 'Your resume lacks a professional summary. This is often the first thing recruiters read.',
            'suggested_action': 'Write a 3-4 sentence summary highlighting your experience, key skills, and career objectives.',
            'example_text': f'Experienced {target_role or "professional"} with X years of expertise in [key skills]. Proven track record of [major achievement]. Seeking to leverage [skills] to drive success at [company type].',
            'potential_score_improvement': 15,
            'difficulty': 'easy'
        })
    elif len(resume.professional_summary.split()) < 50:
        suggestions.append({
            'category': 'content',
            'section': 'summary',
            'priority': 'high',
            'title': 'Expand Professional Summary',
            'description': 'Your professional summary is too brief. Aim for 150-300 words.',
            'suggested_action': 'Add more details about your experience, key achievements, and unique value proposition.',
            'example_text': None,
            'potential_score_improvement': 8,
            'difficulty': 'easy'
        })

    # 2. Work Experience Suggestions
    if not resume.experiences:
        suggestions.append({
            'category': 'experience',
            'section': 'experience',
            'priority': 'critical',
            'title': 'Add Work Experience',
            'description': 'Your resume has no work experience listed.',
            'suggested_action': 'Add your employment history with job titles, companies, dates, and responsibilities.',
            'example_text': None,
            'potential_score_improvement': 25,
            'difficulty': 'medium'
        })
    else:
        # Check for action verbs in experience descriptions
        for exp in resume.experiences:
            if exp.description:
                desc_lower = exp.description.lower()
                action_count = sum(1 for verb in ACTION_VERBS if verb in desc_lower)

                if action_count < 3:
                    suggestions.append({
                        'category': 'experience',
                        'section': 'experience',
                        'priority': 'high',
                        'title': f'Use More Action Verbs in {exp.position_title}',
                        'description': 'Your job descriptions lack strong action verbs that demonstrate impact.',
                        'suggested_action': 'Start bullet points with action verbs like "Led", "Developed", "Implemented", "Managed", "Optimized".',
                        'example_text': '• Led a team of 5 developers to implement new features\n• Optimized database queries, reducing load time by 40%',
                        'potential_score_improvement': 5,
                        'difficulty': 'easy'
                    })

                # Check for metrics/achievements
                import re
                metrics = re.findall(r'\d+[%$]?', exp.description)
                if len(metrics) < 2:
                    suggestions.append({
                        'category': 'experience',
                        'section': 'experience',
                        'priority': 'high',
                        'title': f'Add Quantifiable Achievements to {exp.position_title}',
                        'description': 'Include specific numbers, percentages, or metrics to demonstrate impact.',
                        'suggested_action': 'Add metrics like: team size managed, revenue generated, efficiency improvements, cost savings, user growth, etc.',
                        'example_text': '• Increased sales by 35% through implementation of new CRM system\n• Managed a team of 8 engineers and delivered projects 20% faster',
                        'potential_score_improvement': 8,
                        'difficulty': 'medium'
                    })

    # 3. Skills Suggestions
    if len(resume.skills) < 10:
        suggestions.append({
            'category': 'skills',
            'section': 'skills',
            'priority': 'high',
            'title': 'Add More Skills',
            'description': f'You only have {len(resume.skills)} skills listed. Aim for at least 10-15.',
            'suggested_action': 'List both technical and soft skills relevant to your field. Include programming languages, tools, methodologies, and interpersonal skills.',
            'example_text': None,
            'potential_score_improvement': 10,
            'difficulty': 'easy'
        })

    # Check for proficiency levels
    without_proficiency = sum(1 for s in resume.skills if not s.proficiency_level)
    if without_proficiency > len(resume.skills) * 0.7:
        suggestions.append({
            'category': 'skills',
            'section': 'skills',
            'priority': 'medium',
            'title': 'Add Skill Proficiency Levels',
            'description': 'Most of your skills lack proficiency indicators.',
            'suggested_action': 'Rate your skills on a scale (e.g., Beginner, Intermediate, Advanced, Expert) or use a 1-5 scale.',
            'example_text': None,
            'potential_score_improvement': 5,
            'difficulty': 'easy'
        })

    # 4. Education Suggestions
    if not resume.educations:
        suggestions.append({
            'category': 'education',
            'section': 'education',
            'priority': 'medium',
            'title': 'Add Education Information',
            'description': 'Your resume lacks education details.',
            'suggested_action': 'Include your highest degree, institution, graduation date, and any relevant coursework or honors.',
            'example_text': None,
            'potential_score_improvement': 12,
            'difficulty': 'easy'
        })

    # 5. Contact Information
    if not resume.phone:
        suggestions.append({
            'category': 'contact',
            'section': 'contact',
            'priority': 'high',
            'title': 'Add Phone Number',
            'description': 'Missing phone number makes it harder for recruiters to contact you.',
            'suggested_action': 'Add a phone number where you can be reached.',
            'example_text': None,
            'potential_score_improvement': 5,
            'difficulty': 'easy'
        })

    if not resume.linkedin_url:
        suggestions.append({
            'category': 'contact',
            'section': 'contact',
            'priority': 'low',
            'title': 'Add LinkedIn Profile',
            'description': 'Including your LinkedIn URL provides additional context for recruiters.',
            'suggested_action': 'Add your LinkedIn profile URL to your resume.',
            'example_text': None,
            'potential_score_improvement': 3,
            'difficulty': 'easy'
        })

    # 6. Keyword Optimization
    if target_role:
        # Check if target role keywords appear in resume
        target_keywords = extract_role_keywords(target_role)
        resume_text = get_resume_text(resume).lower()

        missing_keywords = [kw for kw in target_keywords if kw.lower() not in resume_text]

        if missing_keywords:
            suggestions.append({
                'category': 'keywords',
                'section': 'all',
                'priority': 'high',
                'title': f'Add Keywords for {target_role}',
                'description': f'Your resume is missing key terms commonly found in {target_role} job descriptions.',
                'suggested_action': f'Incorporate these keywords naturally: {", ".join(missing_keywords[:5])}',
                'example_text': None,
                'potential_score_improvement': 12,
                'difficulty': 'medium'
            })

    # 7. Certifications
    if not resume.certifications and target_role:
        suggestions.append({
            'category': 'certifications',
            'section': 'certifications',
            'priority': 'low',
            'title': 'Consider Adding Certifications',
            'description': 'Professional certifications can make your resume stand out.',
            'suggested_action': 'If you have relevant certifications, add them. If not, consider pursuing certifications relevant to your field.',
            'example_text': None,
            'potential_score_improvement': 7,
            'difficulty': 'hard'
        })

    # 8. Projects (for technical roles)
    if len(resume.projects) < 2 and target_role and is_technical_role(target_role):
        suggestions.append({
            'category': 'projects',
            'section': 'projects',
            'priority': 'medium',
            'title': 'Add Personal or Professional Projects',
            'description': 'Including projects demonstrates hands-on experience and passion.',
            'suggested_action': 'List 2-3 projects with descriptions, technologies used, and links to code or demos.',
            'example_text': None,
            'potential_score_improvement': 8,
            'difficulty': 'medium'
        })

    return suggestions


def extract_role_keywords(role: str) -> list:
    """Extract common keywords for a role."""
    role_lower = role.lower()

    # Define role-specific keywords
    role_keywords_map = {
        'developer': ['programming', 'coding', 'software', 'development', 'debugging', 'testing', 'agile'],
        'engineer': ['engineering', 'design', 'architecture', 'implementation', 'optimization', 'scalability'],
        'manager': ['management', 'leadership', 'team', 'project', 'planning', 'strategy', 'budget'],
        'designer': ['design', 'ui', 'ux', 'wireframes', 'prototypes', 'user experience', 'visual'],
        'analyst': ['analysis', 'data', 'research', 'reporting', 'metrics', 'insights', 'sql'],
        'marketing': ['marketing', 'campaign', 'social media', 'seo', 'content', 'branding', 'analytics'],
    }

    keywords = []
    for key, values in role_keywords_map.items():
        if key in role_lower:
            keywords.extend(values)

    # Add specific technology keywords based on role
    if 'full stack' in role_lower or 'full-stack' in role_lower:
        keywords.extend(['frontend', 'backend', 'database', 'api', 'react', 'node', 'javascript'])
    elif 'frontend' in role_lower or 'front-end' in role_lower:
        keywords.extend(['html', 'css', 'javascript', 'react', 'vue', 'angular', 'responsive'])
    elif 'backend' in role_lower or 'back-end' in role_lower:
        keywords.extend(['api', 'database', 'server', 'python', 'java', 'node', 'microservices'])
    elif 'data' in role_lower:
        keywords.extend(['sql', 'python', 'analysis', 'visualization', 'statistics', 'machine learning'])

    return list(set(keywords))


def is_technical_role(role: str) -> bool:
    """Check if role is technical."""
    technical_keywords = ['developer', 'engineer', 'programmer', 'architect', 'devops', 'data scientist']
    return any(kw in role.lower() for kw in technical_keywords)


def get_resume_text(resume: Resume) -> str:
    """Get all text content from resume."""
    parts = []

    if resume.professional_summary:
        parts.append(resume.professional_summary)

    for exp in resume.experiences:
        parts.append(exp.position_title)
        if exp.description:
            parts.append(exp.description)

    for skill in resume.skills:
        parts.append(skill.name)

    return ' '.join(parts)
```

---

## 🔍 ATS Compatibility Checks

```python
def perform_ats_compatibility_checks(resume: Resume) -> list:
    """Perform comprehensive ATS compatibility checks."""
    checks = []

    # 1. Contact Information Checks
    checks.append({
        'check_type': 'structure',
        'check_name': 'Contact information completeness',
        'passed': bool(resume.full_name and resume.email and resume.phone),
        'severity': 'critical' if not (resume.full_name and resume.email) else 'warning',
        'issue_description': 'Missing essential contact details' if not (resume.full_name and resume.email and resume.phone) else None,
        'fix_suggestion': 'Add full name, email, and phone number to contact section',
        'impact_on_ats_parsing': 'high' if not resume.email else 'medium'
    })

    # 2. Email Format Check
    import re
    email_valid = bool(resume.email and re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', resume.email))
    checks.append({
        'check_type': 'formatting',
        'check_name': 'Email format validation',
        'passed': email_valid,
        'severity': 'critical' if not email_valid else 'info',
        'issue_description': 'Invalid email format' if not email_valid else None,
        'fix_suggestion': 'Use a standard email format: name@domain.com',
        'impact_on_ats_parsing': 'high' if not email_valid else 'none'
    })

    # 3. Section Organization
    has_essential_sections = bool(resume.experiences and resume.educations and resume.skills)
    checks.append({
        'check_type': 'structure',
        'check_name': 'Essential sections present',
        'passed': has_essential_sections,
        'severity': 'critical' if not has_essential_sections else 'info',
        'issue_description': 'Missing one or more essential resume sections (Experience, Education, Skills)' if not has_essential_sections else None,
        'fix_suggestion': 'Include Work Experience, Education, and Skills sections',
        'impact_on_ats_parsing': 'high' if not has_essential_sections else 'none'
    })

    # 4. Date Format Consistency
    date_issues = []
    for exp in resume.experiences:
        if exp.is_current and exp.end_date:
            date_issues.append(f'{exp.position_title}: marked as current but has end date')
        if exp.end_date and exp.start_date and exp.end_date < exp.start_date:
            date_issues.append(f'{exp.position_title}: end date before start date')

    checks.append({
        'check_type': 'formatting',
        'check_name': 'Date consistency',
        'passed': len(date_issues) == 0,
        'severity': 'warning' if date_issues else 'info',
        'issue_description': '; '.join(date_issues) if date_issues else None,
        'fix_suggestion': 'Fix date inconsistencies in work experience',
        'impact_on_ats_parsing': 'medium' if date_issues else 'none'
    })

    # 5. URL Formatting
    url_issues = []
    if resume.website and not resume.website.startswith(('http://', 'https://')):
        url_issues.append('Website URL')
    if resume.linkedin_url and not resume.linkedin_url.startswith(('http://', 'https://')):
        url_issues.append('LinkedIn URL')
    if resume.github_url and not resume.github_url.startswith(('http://', 'https://')):
        url_issues.append('GitHub URL')

    checks.append({
        'check_type': 'formatting',
        'check_name': 'URL formatting',
        'passed': len(url_issues) == 0,
        'severity': 'warning' if url_issues else 'info',
        'issue_description': f'URLs missing protocol: {", ".join(url_issues)}' if url_issues else None,
        'fix_suggestion': 'Add https:// prefix to all URLs',
        'impact_on_ats_parsing': 'low'
    })

    # 6. Phone Number Format
    phone_valid = True
    if resume.phone:
        # Basic phone validation - should contain digits
        digits = re.sub(r'\D', '', resume.phone)
        if len(digits) < 10 or len(digits) > 15:
            phone_valid = False

    checks.append({
        'check_type': 'formatting',
        'check_name': 'Phone number format',
        'passed': phone_valid,
        'severity': 'warning' if not phone_valid else 'info',
        'issue_description': 'Phone number appears to be invalid' if not phone_valid else None,
        'fix_suggestion': 'Use a standard phone format with 10-15 digits',
        'impact_on_ats_parsing': 'medium' if not phone_valid else 'none'
    })

    # 7. Content Length Check
    total_words = 0
    if resume.professional_summary:
        total_words += len(resume.professional_summary.split())
    for exp in resume.experiences:
        if exp.description:
            total_words += len(exp.description.split())

    sufficient_content = total_words >= 200
    checks.append({
        'check_type': 'structure',
        'check_name': 'Sufficient content',
        'passed': sufficient_content,
        'severity': 'warning' if not sufficient_content else 'info',
        'issue_description': f'Resume content is too brief ({total_words} words). Aim for at least 200 words.' if not sufficient_content else None,
        'fix_suggestion': 'Add more details to your professional summary and job descriptions',
        'impact_on_ats_parsing': 'low'
    })

    # 8. File Format (check template/format settings)
    uses_simple_format = resume.resume_format in ['INTERNATIONAL', 'MODERN']  # Enum values
    checks.append({
        'check_type': 'formatting',
        'check_name': 'ATS-friendly format',
        'passed': uses_simple_format,
        'severity': 'info',
        'issue_description': 'Complex resume formats may have parsing issues with some ATS' if not uses_simple_format else None,
        'fix_suggestion': 'Consider using a simpler, more ATS-friendly template',
        'impact_on_ats_parsing': 'low'
    })

    # 9. Custom CSS Check
    has_complex_styling = bool(resume.custom_css and len(resume.custom_css) > 100)
    checks.append({
        'check_type': 'formatting',
        'check_name': 'Minimal custom styling',
        'passed': not has_complex_styling,
        'severity': 'warning' if has_complex_styling else 'info',
        'issue_description': 'Excessive custom styling may interfere with ATS parsing' if has_complex_styling else None,
        'fix_suggestion': 'Reduce custom CSS to ensure proper parsing',
        'impact_on_ats_parsing': 'medium' if has_complex_styling else 'none'
    })

    # 10. Skills Formatting
    skill_names_clean = all(
        re.match(r'^[a-zA-Z0-9\s\+\-\.\#]+$', skill.name)
        for skill in resume.skills
    )
    checks.append({
        'check_type': 'formatting',
        'check_name': 'Skill names formatting',
        'passed': skill_names_clean,
        'severity': 'info',
        'issue_description': 'Some skill names contain special characters that may not parse well' if not skill_names_clean else None,
        'fix_suggestion': 'Use standard characters in skill names',
        'impact_on_ats_parsing': 'low'
    })

    return checks
```

---

## 🎯 Job Matching Logic

```python
def match_resume_to_job(resume: Resume, job_data: dict) -> dict:
    """Match resume to job requirements."""

    required_skills = job_data.get('required_skills', [])
    preferred_skills = job_data.get('preferred_skills', [])
    min_years = job_data.get('min_years_experience', 0)
    job_description = job_data.get('job_description', '')

    # Extract resume data
    resume_skills = [s.name.lower() for s in resume.skills]
    resume_text = get_resume_text(resume).lower()

    # Calculate years of experience
    total_months = 0
    for exp in resume.experiences:
        from datetime import datetime
        start = exp.start_date
        end = exp.end_date or datetime.now()
        months = (end.year - start.year) * 12 + (end.month - start.month)
        total_months += max(months, 0)

    years_experience = total_months / 12

    # 1. Required Skills Match (40% weight)
    matched_required = []
    missing_required = []

    for skill in required_skills:
        skill_lower = skill.lower()
        if skill_lower in resume_skills or skill_lower in resume_text:
            matched_required.append(skill)
        else:
            missing_required.append(skill)

    required_match_rate = len(matched_required) / len(required_skills) if required_skills else 1.0
    required_score = int(required_match_rate * 100)

    # 2. Preferred Skills Match (20% weight)
    matched_preferred = []

    for skill in preferred_skills:
        skill_lower = skill.lower()
        if skill_lower in resume_skills or skill_lower in resume_text:
            matched_preferred.append(skill)

    preferred_match_rate = len(matched_preferred) / len(preferred_skills) if preferred_skills else 0.5
    preferred_score = int(preferred_match_rate * 100)

    # 3. Experience Match (25% weight)
    if years_experience >= min_years:
        if years_experience >= min_years * 1.5:
            experience_score = 100
        else:
            experience_score = 80
    else:
        experience_score = int((years_experience / min_years) * 60)

    # 4. Education Match (15% weight)
    # Simple check: has degree
    education_score = 100 if resume.educations else 50

    # Calculate overall match score
    match_score = int(
        required_score * 0.40 +
        preferred_score * 0.20 +
        experience_score * 0.25 +
        education_score * 0.15
    )

    # Determine recommendation
    if match_score >= 85:
        recommendation = 'strong_match'
    elif match_score >= 70:
        recommendation = 'good_match'
    elif match_score >= 50:
        recommendation = 'partial_match'
    else:
        recommendation = 'weak_match'

    # Generate notes
    notes = []
    if required_match_rate == 1.0:
        notes.append('Has all required skills.')
    elif required_match_rate >= 0.75:
        notes.append(f'Has most required skills ({len(matched_required)}/{len(required_skills)}).')
    else:
        notes.append(f'Missing {len(missing_required)} required skills.')

    if years_experience >= min_years:
        notes.append(f'Meets experience requirement ({years_experience:.1f} years).')
    else:
        notes.append(f'Below experience requirement (has {years_experience:.1f}, needs {min_years}).')

    if matched_preferred:
        notes.append(f'Has {len(matched_preferred)} preferred skills.')

    return {
        'match_score': match_score,
        'match_breakdown': {
            'required_skills_match': required_score,
            'preferred_skills_match': preferred_score,
            'experience_match': experience_score,
            'education_match': education_score,
        },
        'matched_skills': matched_required + matched_preferred,
        'missing_skills': missing_required,
        'years_experience': round(years_experience, 1),
        'recommendation': recommendation,
        'notes': ' '.join(notes)
    }
```

---

## 📚 Data Dictionaries

### Technical Skills Database

```python
TECHNICAL_SKILLS_DATABASE = [
    # Programming Languages
    'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin',
    'Go', 'Rust', 'TypeScript', 'Scala', 'R', 'MATLAB', 'Perl', 'Objective-C',

    # Web Technologies
    'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django',
    'Flask', 'Spring', 'ASP.NET', 'Laravel', 'Rails', 'jQuery', 'Bootstrap',
    'Tailwind', 'Next.js', 'Nuxt.js', 'Svelte', 'Webpack', 'Vite',

    # Databases
    'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Oracle', 'SQLite',
    'Cassandra', 'DynamoDB', 'Elasticsearch', 'Neo4j', 'MariaDB',

    # Cloud & DevOps
    'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
    'CI/CD', 'Terraform', 'Ansible', 'Linux', 'Bash', 'PowerShell',

    # Data Science & ML
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'scikit-learn',
    'Pandas', 'NumPy', 'Jupyter', 'Tableau', 'Power BI', 'Data Analysis',

    # Mobile
    'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin',

    # Other
    'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'JIRA',
    'Testing', 'Unit Testing', 'Integration Testing', 'Selenium', 'Jest',
]

SOFT_SKILLS_DATABASE = [
    'Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking',
    'Time Management', 'Adaptability', 'Creativity', 'Attention to Detail',
    'Collaboration', 'Project Management', 'Analytical Skills', 'Decision Making',
    'Conflict Resolution', 'Mentoring', 'Presentation', 'Negotiation',
    'Customer Service', 'Strategic Planning', 'Multitasking',
]

ACTION_VERBS = [
    'achieved', 'administered', 'analyzed', 'architected', 'built', 'collaborated',
    'created', 'decreased', 'delivered', 'demonstrated', 'designed', 'developed',
    'directed', 'established', 'executed', 'expanded', 'generated', 'implemented',
    'improved', 'increased', 'initiated', 'launched', 'led', 'managed', 'optimized',
    'organized', 'performed', 'planned', 'produced', 'reduced', 'redesigned',
    'resolved', 'streamlined', 'strengthened', 'supervised', 'trained', 'transformed',
]

TECHNOLOGY_DATABASE = TECHNICAL_SKILLS_DATABASE  # Same as technical skills
```

---

## 🔧 Complete Implementation Example

```python
# backend/app/services/resume_ats_service.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resume import Resume
from app.models.resume_ats import (
    ResumeAnalysis,
    ResumeOptimizationSuggestion,
    ResumeKeyword,
    ATSCompatibilityCheck
)
from app.utils.datetime_utils import get_utc_now
import logging

logger = logging.getLogger(__name__)


class ResumeATSService:
    """Rule-based ATS service (no AI/ML dependencies)."""

    async def analyze_resume(
        self,
        db: AsyncSession,
        resume_id: int,
        user_id: int,
        analysis_type: str,
        target_role: Optional[str] = None,
        job_description: Optional[str] = None,
        job_position_id: Optional[int] = None,
    ) -> ResumeAnalysis:
        """Perform comprehensive resume analysis."""

        # Get resume
        resume = await self._get_resume(db, resume_id, user_id)

        # Calculate scores
        overall_score = self._calculate_overall_score(resume, target_role)
        content_quality = self._calculate_content_quality(resume)
        skills_score = calculate_skills_score(resume)
        experience_score = calculate_experience_score(resume.experiences, target_role)
        ats_score = calculate_ats_compatibility_score(resume)
        keyword_score = calculate_keyword_density(resume)

        # Extract data
        extracted_skills = extract_keywords(resume)

        # Create analysis record
        analysis = ResumeAnalysis(
            resume_id=resume_id,
            analyzed_by_user_id=user_id,
            job_position_id=job_position_id,
            analysis_type=analysis_type,
            target_role=target_role,
            job_description=job_description,
            overall_score=overall_score,
            content_quality_score=content_quality,
            skills_match_score=skills_score,
            experience_relevance_score=experience_score,
            ats_compatibility_score=ats_score,
            keyword_optimization_score=keyword_score,
            extracted_skills=extracted_skills,
            status='completed'
        )

        db.add(analysis)
        await db.flush()

        # Generate suggestions
        suggestions = generate_optimization_suggestions(resume, target_role)
        for sug in suggestions:
            suggestion = ResumeOptimizationSuggestion(
                analysis_id=analysis.id,
                **sug
            )
            db.add(suggestion)

        # Perform ATS checks
        checks = perform_ats_compatibility_checks(resume)
        for check in checks:
            ats_check = ATSCompatibilityCheck(
                analysis_id=analysis.id,
                **check
            )
            db.add(ats_check)

        await db.commit()
        await db.refresh(analysis)

        return analysis

    def _calculate_overall_score(self, resume: Resume, target_role: Optional[str]) -> int:
        """Calculate overall resume score."""
        content = self._calculate_content_quality(resume)
        completeness = calculate_completeness_score(resume)
        experience = calculate_experience_score(resume.experiences, target_role)
        skills = calculate_skills_score(resume)
        ats = calculate_ats_compatibility_score(resume)
        keywords = calculate_keyword_density(resume)

        overall = int(
            content * 0.25 +
            completeness * 0.20 +
            experience * 0.20 +
            skills * 0.15 +
            ats * 0.15 +
            keywords * 0.05
        )

        return min(overall, 100)

    def _calculate_content_quality(self, resume: Resume) -> int:
        """Calculate content quality score."""
        summary_score = score_professional_summary(resume.professional_summary or "")
        exp_score = score_experience_quality(resume.experiences)

        # Combine scores
        return int(summary_score * 0.4 + exp_score * 0.6)

    async def _get_resume(self, db: AsyncSession, resume_id: int, user_id: int) -> Resume:
        """Get resume with all relationships."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        result = await db.execute(
            select(Resume)
            .where(Resume.id == resume_id, Resume.user_id == user_id)
            .options(
                selectinload(Resume.experiences),
                selectinload(Resume.educations),
                selectinload(Resume.skills),
                selectinload(Resume.projects),
                selectinload(Resume.certifications),
            )
        )
        resume = result.scalar_one_or_none()

        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        return resume


# Create singleton instance
resume_ats_service = ResumeATSService()
```

---

## ⚡ Performance Considerations

**Expected Performance**:
- Resume analysis: < 500ms
- Keyword extraction: < 100ms
- Suggestion generation: < 200ms
- ATS compatibility check: < 100ms
- Job matching: < 300ms

**Optimization Tips**:
1. Cache skill dictionaries in memory
2. Pre-compile regex patterns
3. Use database indexes properly
4. Batch database operations
5. Consider caching analysis results

---

## 🎯 Advantages of Rule-Based Approach

1. **Cost**: No AI API costs
2. **Speed**: Faster than AI (< 500ms vs 2-5s)
3. **Privacy**: All processing done locally
4. **Reliability**: No external dependencies
5. **Predictability**: Deterministic results
6. **Debuggability**: Easy to trace and fix
7. **Customization**: Full control over logic
8. **Scalability**: No API rate limits

---

**Implementation Status**: ✅ Ready for Development
**Estimated Development Time**: 4-5 weeks (reduced from 6 weeks - no AI integration needed)
**Dependencies**: None (all rule-based)
