"""
Resume System Seed Data

Creates sample resume data with Japanese formats for testing.
This module creates comprehensive resume examples including 履歴書 (rirekisho),
職務経歴書 (shokumu keirekisho), international, and modern creative formats.
"""

from datetime import datetime

from app.crud.resume import generate_share_token, generate_slug
from app.models.resume import (
    Certification,
    Education,
    Language,
    Project,
    Resume,
    Skill,
    WorkExperience,
)
from app.utils.constants import (
    ResumeFormat,
    ResumeLanguage,
    ResumeStatus,
    ResumeVisibility,
)


async def seed_resume_data(db, auth_result):
    """Create comprehensive resume seed data."""
    print("Creating resume system data...")

    users_list = auth_result["users_list"]
    auth_result["companies_list"]

    # Use first few users for resume creation
    candidate_users = [
        users_list[1][0],
        users_list[2][0],
        users_list[3][0],
    ]  # Skip admin
    created_resumes = []

    for i, user in enumerate(candidate_users):
        # Create 4 different resume formats for each user
        resumes = await create_resumes_for_user(db, user, i)
        created_resumes.extend(resumes)

    await db.commit()
    print(f"   - Created {len(created_resumes)} sample resumes")
    print("   - Formats: 履歴書, 職務経歴書, International, Modern")

    return {
        "resumes": len(created_resumes),
        "formats": ["rirekisho", "shokumu_keirekisho", "international", "modern"],
    }


async def create_resumes_for_user(db, user, user_index):
    """Create multiple resume formats for a user."""
    resumes = []

    # 1. Create Japanese 履歴書 (Rirekisho)
    rirekisho = await create_rirekisho_resume(db, user, user_index)
    resumes.append(rirekisho)

    # 2. Create Japanese 職務経歴書 (Shokumu Keirekisho)
    shokumu = await create_shokumu_resume(db, user, user_index)
    resumes.append(shokumu)

    # 3. Create International Resume
    international = await create_international_resume(db, user, user_index)
    resumes.append(international)

    # 4. Create Modern Format Resume
    modern = await create_modern_resume(db, user, user_index)
    resumes.append(modern)

    return resumes


async def create_rirekisho_resume(db, user, user_index):
    """Create Japanese 履歴書 format resume."""
    names = ["田中太郎", "佐藤花子", "鈴木次郎"]
    furigana_names = ["タナカタロウ", "サトウハナコ", "スズキジロウ"]

    resume_data = {
        "user_id": user.id,
        "title": f"履歴書 - {names[user_index]}",
        "description": "正社員採用用の履歴書です",
        "full_name": names[user_index],
        "furigana_name": furigana_names[user_index],
        "email": f"{names[user_index].lower().replace(' ', '.')}@example.com",
        "phone": f"090-{1234 + user_index}-5678",
        "location": f"〒100-000{user_index + 1} 東京都千代田区千代田{user_index + 1}-1-1",
        "birth_date": datetime(1990 + user_index, 4, 15),
        "gender": "男性" if user_index % 2 == 0 else "女性",
        "nationality": "日本",
        "marital_status": "既婚" if user_index == 0 else "未婚",
        "emergency_contact": {
            "name": f"{names[user_index]}の家族",
            "relationship": "配偶者" if user_index == 0 else "親",
            "phone": f"090-{8765 + user_index}-4321",
            "commute_time": str(30 + user_index * 15),
            "dependents": str(user_index),
        },
        "professional_summary": f"""
新卒でIT企業に入社し、{3 + user_index}年間Webアプリケーション開発に従事してまいりました。
特にPythonとReactを使用したフルスタック開発が得意で、要件定義から
運用まで一貫して携わった経験があります。
この度は、より上流工程に関われる環境で、技術力を活かして
貴社の事業成長に貢献したいと考えております。
        """.strip(),
        "template_id": "rirekisho_standard",
        "resume_format": ResumeFormat.RIREKISHO,
        "resume_language": ResumeLanguage.JAPANESE,
        "status": ResumeStatus.PUBLISHED,
        "visibility": ResumeVisibility.PRIVATE,
        "theme_color": "#2563eb",
        "font_family": "MS Gothic",
        "is_primary": user_index == 0,
        "public_url_slug": generate_slug(f"履歴書 {names[user_index]}"),
        "share_token": generate_share_token(),
        "is_public": False,
        "can_download_pdf": True,
        "can_edit": True,
        "can_delete": True,
    }

    resume = Resume(**resume_data)
    db.add(resume)
    await db.flush()

    # Add education history
    educations = [
        {
            "resume_id": resume.id,
            "institution_name": "東京大学工学部情報理工学科",
            "degree": "学士",
            "field_of_study": "情報工学",
            "location": "東京都",
            "start_date": datetime(2008 + user_index, 4, 1),
            "end_date": datetime(2012 + user_index, 3, 31),
            "is_current": False,
            "gpa": f"{3.5 + user_index * 0.1:.1f}/4.0",
            "honors": "優秀賞" if user_index == 0 else None,
            "display_order": 1,
            "is_visible": True,
        }
    ]

    for edu_data in educations:
        education = Education(**edu_data)
        db.add(education)

    # Add work experience
    companies = [
        "株式会社テックイノベーション",
        "株式会社ウェブソリューションズ",
        "株式会社デジタルクリエイト",
    ]
    experiences = [
        {
            "resume_id": resume.id,
            "company_name": companies[user_index],
            "position_title": "システムエンジニア",
            "location": "東京都渋谷区",
            "start_date": datetime(2012 + user_index, 4, 1),
            "is_current": True,
            "description": "Webアプリケーションの開発・保守業務に従事。主にPython(Django)とJavaScriptを使用したシステム開発を担当。",
            "achievements": [
                "社内システムの開発チームリーダーとして3名のメンバーを指導",
                "既存システムのパフォーマンス改善により処理速度を30%向上",
                "新人研修プログラムの立案・実施",
            ],
            "technologies": ["Python", "Django", "JavaScript", "PostgreSQL", "Git"],
            "display_order": 1,
            "is_visible": True,
        }
    ]

    for exp_data in experiences:
        experience = WorkExperience(**exp_data)
        db.add(experience)

    # Add certifications
    certifications = [
        {
            "resume_id": resume.id,
            "name": "応用情報技術者試験",
            "issuing_organization": "独立行政法人情報処理推進機構",
            "issue_date": datetime(2013 + user_index, 10, 15),
            "does_not_expire": True,
            "display_order": 1,
            "is_visible": True,
        }
    ]

    for cert_data in certifications:
        certification = Certification(**cert_data)
        db.add(certification)

    return resume


async def create_shokumu_resume(db, user, user_index):
    """Create Japanese 職務経歴書 format resume."""
    names = ["田中太郎", "佐藤花子", "鈴木次郎"]

    resume_data = {
        "user_id": user.id,
        "title": f"職務経歴書 - システムエンジニア ({names[user_index]})",
        "description": "技術職向けの詳細な職務経歴書",
        "full_name": names[user_index],
        "email": f"{names[user_index].lower().replace(' ', '.')}@example.com",
        "phone": f"090-{1234 + user_index}-5678",
        "professional_summary": f"""
【職務要約】
新卒で入社後、{3 + user_index}年間でWebアプリケーション開発の幅広い経験を積んでまいりました。
バックエンドからフロントエンドまでのフルスタック開発が可能で、特にPython/Django、
React/TypeScriptを使用した開発が得意です。

現職では、新規SaaS製品の技術選定・アーキテクチャ設計を主導し、開発チームの
生産性向上とプロダクトの品質向上に貢献してきました。
        """.strip(),
        "template_id": "shokumu_detailed",
        "resume_format": ResumeFormat.SHOKUMU_KEIREKISHO,
        "resume_language": ResumeLanguage.JAPANESE,
        "status": ResumeStatus.PUBLISHED,
        "visibility": ResumeVisibility.PRIVATE,
        "theme_color": "#059669",
        "font_family": "Yu Gothic",
        "is_primary": False,
        "public_url_slug": generate_slug(
            f"職務経歴書 システムエンジニア {names[user_index]}"
        ),
        "share_token": generate_share_token(),
        "is_public": False,
        "can_download_pdf": True,
        "can_edit": True,
        "can_delete": True,
    }

    resume = Resume(**resume_data)
    db.add(resume)
    await db.flush()

    # Add technical skills
    skills = [
        {
            "resume_id": resume.id,
            "name": "Python",
            "category": "プログラミング言語",
            "proficiency_level": 5,
            "proficiency_label": "エキスパート",
            "display_order": 1,
        },
        {
            "resume_id": resume.id,
            "name": "JavaScript",
            "category": "プログラミング言語",
            "proficiency_level": 4,
            "proficiency_label": "上級",
            "display_order": 2,
        },
        {
            "resume_id": resume.id,
            "name": "React",
            "category": "フレームワーク",
            "proficiency_level": 4,
            "proficiency_label": "上級",
            "display_order": 3,
        },
        {
            "resume_id": resume.id,
            "name": "Django",
            "category": "フレームワーク",
            "proficiency_level": 5,
            "proficiency_label": "エキスパート",
            "display_order": 4,
        },
        {
            "resume_id": resume.id,
            "name": "PostgreSQL",
            "category": "データベース",
            "proficiency_level": 4,
            "proficiency_label": "上級",
            "display_order": 5,
        },
    ]

    for skill_data in skills:
        skill = Skill(**skill_data)
        db.add(skill)

    return resume


async def create_international_resume(db, user, user_index):
    """Create international format resume."""
    english_names = ["Taro Tanaka", "Hanako Sato", "Jiro Suzuki"]

    resume_data = {
        "user_id": user.id,
        "title": f"Software Engineer Resume - {english_names[user_index]}",
        "description": "International format resume for global opportunities",
        "full_name": english_names[user_index],
        "email": f"{english_names[user_index].lower().replace(' ', '.')}@example.com",
        "phone": f"+81-90-{1234 + user_index}-5678",
        "location": "Tokyo, Japan",
        "website": f"https://{english_names[user_index].lower().replace(' ', '')}.dev",
        "linkedin_url": f"https://linkedin.com/in/{english_names[user_index].lower().replace(' ', '')}",
        "github_url": f"https://github.com/{english_names[user_index].lower().replace(' ', '')}",
        "professional_summary": f"""
Experienced Full-Stack Software Engineer with {3 + user_index}+ years of expertise in web application development.
Skilled in Python, React, and cloud technologies with a proven track record of delivering scalable solutions.
Passionate about clean code, performance optimization, and continuous learning.
        """.strip(),
        "template_id": "international_modern",
        "resume_format": ResumeFormat.INTERNATIONAL,
        "resume_language": ResumeLanguage.ENGLISH,
        "status": ResumeStatus.PUBLISHED,
        "visibility": ResumeVisibility.PUBLIC
        if user_index == 0
        else ResumeVisibility.PRIVATE,
        "theme_color": "#7c3aed",
        "font_family": "Inter",
        "is_primary": False,
        "public_url_slug": generate_slug(
            f"Software Engineer Resume {english_names[user_index]}"
        ),
        "share_token": generate_share_token(),
        "is_public": user_index == 0,
        "can_download_pdf": True,
        "can_edit": True,
        "can_delete": True,
    }

    resume = Resume(**resume_data)
    db.add(resume)
    await db.flush()

    # Add languages
    languages = [
        {
            "resume_id": resume.id,
            "name": "Japanese",
            "proficiency": "Native",
            "display_order": 1,
            "is_visible": True,
        },
        {
            "resume_id": resume.id,
            "name": "English",
            "proficiency": f"Professional Working Proficiency (TOEIC {800 + user_index * 25})",
            "display_order": 2,
            "is_visible": True,
        },
    ]

    for lang_data in languages:
        language = Language(**lang_data)
        db.add(language)

    return resume


async def create_modern_resume(db, user, user_index):
    """Create modern format resume."""
    creative_names = ["Taro Tanaka", "Hanako Sato", "Jiro Suzuki"]

    resume_data = {
        "user_id": user.id,
        "title": f"Creative Developer Portfolio - {creative_names[user_index]}",
        "description": "Modern creative resume showcasing design and development skills",
        "full_name": creative_names[user_index],
        "email": f"hello@{creative_names[user_index].lower().replace(' ', '')}.design",
        "phone": f"090-{1234 + user_index}-5678",
        "location": "Tokyo, Japan",
        "website": f"https://{creative_names[user_index].lower().replace(' ', '')}.design",
        "linkedin_url": f"https://linkedin.com/in/{creative_names[user_index].lower().replace(' ', '')}",
        "github_url": f"https://github.com/{creative_names[user_index].lower().replace(' ', '')}",
        "professional_summary": """
Creative Full-Stack Developer with a passion for building beautiful, functional web experiences.
Combining technical expertise with design sensibility to create user-centered solutions.
        """.strip(),
        "template_id": "modern_creative",
        "resume_format": ResumeFormat.MODERN,
        "resume_language": ResumeLanguage.BILINGUAL,
        "status": ResumeStatus.DRAFT if user_index == 2 else ResumeStatus.PUBLISHED,
        "visibility": ResumeVisibility.PRIVATE,
        "theme_color": "#f59e0b",
        "font_family": "Poppins",
        "is_primary": False,
        "public_url_slug": generate_slug(
            f"Creative Developer Portfolio {creative_names[user_index]}"
        ),
        "share_token": generate_share_token(),
        "is_public": False,
        "can_download_pdf": True,
        "can_edit": True,
        "can_delete": True,
    }

    resume = Resume(**resume_data)
    db.add(resume)
    await db.flush()

    # Add creative projects
    projects = [
        {
            "resume_id": resume.id,
            "name": f"Interactive Dashboard Platform {user_index + 1}",
            "description": "Built an interactive dashboard for data visualization using React and D3.js",
            "start_date": datetime(2021 + user_index, 1, 1),
            "end_date": datetime(2022 + user_index, 6, 30),
            "is_ongoing": False,
            "role": "Lead Developer & Designer",
            "technologies": ["React", "D3.js", "TypeScript", "Node.js"],
            "project_url": f"https://project{user_index + 1}.example.com",
            "github_url": f"https://github.com/{creative_names[user_index].lower().replace(' ', '')}/project{user_index + 1}",
            "display_order": 1,
            "is_visible": True,
        }
    ]

    for project_data in projects:
        project = Project(**project_data)
        db.add(project)

    return resume
