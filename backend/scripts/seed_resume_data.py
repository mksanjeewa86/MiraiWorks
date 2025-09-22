#!/usr/bin/env python3
"""
Resume System Seed Data
Creates sample resume data with Japanese formats for testing
Includes fallback handling for database connection issues
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Optional
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.database import get_db
    from app.models.user import User
    from app.models.company import Company
    from app.models.resume import (
        Resume,
        WorkExperience,
        Education,
        Skill,
        Project,
        Certification,
        Language,
        Reference,
        ResumeSection
    )
    from app.utils.constants import (
        ResumeStatus,
        ResumeVisibility,
        ResumeFormat,
        ResumeLanguage,
        SectionType
    )
    from app.crud.resume import resume as resume_crud, generate_slug, generate_share_token
    
    DB_AVAILABLE = True
except ImportError as e:
    print(f"Database dependencies not available: {e}")
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)


class ResumeSeeder:
    """Seed data creator for resume system"""
    
    def __init__(self):
        self.created_resumes = []
        self.fallback_data = {}
    
    async def seed_all(self):
        """Main seeding function"""
        if not DB_AVAILABLE:
            return self.create_fallback_data()
        
        try:
            async for db in get_db():
                # Check if we have users to create resumes for
                users = await self.get_sample_users(db)
                if not users:
                    print("No users found. Creating sample user first...")
                    users = [await self.create_sample_user(db)]
                
                print(f"Creating resumes for {len(users)} users...")
                
                for user in users:
                    await self.create_resumes_for_user(db, user)
                
                await db.commit()
                print(f"✅ Created {len(self.created_resumes)} sample resumes")
                return True
                
        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            print(f"❌ Database seeding failed: {e}")
            print("Creating fallback data instead...")
            return self.create_fallback_data()
    
    async def get_sample_users(self, db: AsyncSession):
        """Get existing users for resume creation"""
        from sqlalchemy import select
        
        result = await db.execute(
            select(User).limit(3)
        )
        return result.scalars().all()
    
    async def create_sample_user(self, db: AsyncSession):
        """Create a sample user if none exist"""
        from app.schemas.user import UserCreate
        from app.crud.user import user as user_crud
        from werkzeug.security import generate_password_hash
        
        user_data = {
            "email": "resume.demo@miraiworks.com",
            "hashed_password": generate_password_hash("demo123"),
            "full_name": "田中太郎",
            "is_active": True,
            "is_verified": True
        }
        
        user = User(**user_data)
        db.add(user)
        await db.flush()
        return user
    
    async def create_resumes_for_user(self, db: AsyncSession, user: User):
        """Create multiple resume formats for a user"""
        
        # 1. Create Japanese 履歴書 (Rirekisho)
        rirekisho = await self.create_rirekisho_resume(db, user)
        self.created_resumes.append(rirekisho)
        
        # 2. Create Japanese 職務経歴書 (Shokumu Keirekisho)
        shokumu = await self.create_shokumu_resume(db, user)
        self.created_resumes.append(shokumu)
        
        # 3. Create International Resume
        international = await self.create_international_resume(db, user)
        self.created_resumes.append(international)
        
        # 4. Create Modern Format Resume
        modern = await self.create_modern_resume(db, user)
        self.created_resumes.append(modern)
    
    async def create_rirekisho_resume(self, db: AsyncSession, user: User) -> Resume:
        """Create Japanese 履歴書 format resume"""
        
        resume_data = {
            "user_id": user.id,
            "title": "履歴書 - 田中太郎",
            "description": "正社員採用用の履歴書です",
            "full_name": "田中太郎",
            "furigana_name": "タナカタロウ",
            "email": "tanaka.taro@example.com",
            "phone": "090-1234-5678",
            "location": "〒100-0001 東京都千代田区千代田1-1-1",
            "birth_date": datetime(1990, 4, 15),
            "gender": "男性",
            "nationality": "日本",
            "marital_status": "既婚",
            "emergency_contact": {
                "name": "田中花子",
                "relationship": "配偶者",
                "phone": "090-8765-4321",
                "commute_time": "45",
                "dependents": "1"
            },
            "professional_summary": """
新卒でIT企業に入社し、5年間Webアプリケーション開発に従事してまいりました。
特にPythonとReactを使用したフルスタック開発が得意で、要件定義から
運用まで一貫して携わった経験があります。チームリーダーとして
後輩指導も行い、プロジェクト管理能力も身につけました。
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
            "is_primary": True,
            "public_url_slug": generate_slug("履歴書 田中太郎"),
            "share_token": generate_share_token(),
            "is_public": False,
            "can_download_pdf": True,
            "can_edit": True,
            "can_delete": True
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
                "start_date": datetime(2008, 4, 1),
                "end_date": datetime(2012, 3, 31),
                "is_current": False,
                "gpa": "3.7/4.0",
                "honors": "優秀賞",
                "display_order": 1,
                "is_visible": True
            },
            {
                "resume_id": resume.id,
                "institution_name": "東京都立○○高等学校",
                "degree": "高等学校卒業",
                "field_of_study": "普通科",
                "location": "東京都",
                "start_date": datetime(2005, 4, 1),
                "end_date": datetime(2008, 3, 31),
                "is_current": False,
                "display_order": 2,
                "is_visible": True
            }
        ]
        
        for edu_data in educations:
            education = Education(**edu_data)
            db.add(education)
        
        # Add work experience
        experiences = [
            {
                "resume_id": resume.id,
                "company_name": "株式会社テックイノベーション",
                "position_title": "システムエンジニア",
                "location": "東京都渋谷区",
                "start_date": datetime(2012, 4, 1),
                "end_date": datetime(2017, 3, 31),
                "is_current": False,
                "description": "Webアプリケーションの開発・保守業務に従事。主にPython(Django)とJavaScriptを使用したシステム開発を担当。",
                "achievements": [
                    "社内システムの開発チームリーダーとして3名のメンバーを指導",
                    "既存システムのパフォーマンス改善により処理速度を30%向上",
                    "新人研修プログラムの立案・実施"
                ],
                "technologies": ["Python", "Django", "JavaScript", "PostgreSQL", "Git"],
                "display_order": 1,
                "is_visible": True
            },
            {
                "resume_id": resume.id,
                "company_name": "株式会社ウェブソリューションズ",
                "position_title": "シニアエンジニア",
                "location": "東京都新宿区",
                "start_date": datetime(2017, 4, 1),
                "is_current": True,
                "description": "フルスタック開発者として、React/TypeScript、Python/FastAPIを使用したSaaS製品の開発を担当。",
                "achievements": [
                    "新規SaaS製品の技術選定・アーキテクチャ設計を主導",
                    "開発効率化のためのCI/CDパイプライン構築",
                    "お客様からの満足度向上に貢献（NPS 8.5/10達成）"
                ],
                "technologies": ["React", "TypeScript", "Python", "FastAPI", "AWS", "Docker"],
                "display_order": 2,
                "is_visible": True
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
                "issue_date": datetime(2013, 10, 15),
                "does_not_expire": True,
                "display_order": 1,
                "is_visible": True
            },
            {
                "resume_id": resume.id,
                "name": "TOEIC 850点",
                "issuing_organization": "国際ビジネスコミュニケーション協会",
                "issue_date": datetime(2020, 1, 20),
                "expiration_date": datetime(2022, 1, 20),
                "does_not_expire": False,
                "display_order": 2,
                "is_visible": True
            }
        ]
        
        for cert_data in certifications:
            certification = Certification(**cert_data)
            db.add(certification)
        
        return resume
    
    async def create_shokumu_resume(self, db: AsyncSession, user: User) -> Resume:
        """Create Japanese 職務経歴書 format resume"""
        
        resume_data = {
            "user_id": user.id,
            "title": "職務経歴書 - システムエンジニア",
            "description": "技術職向けの詳細な職務経歴書",
            "full_name": "田中太郎",
            "email": "tanaka.taro@example.com",
            "phone": "090-1234-5678",
            "professional_summary": """
【職務要約】
新卒で入社後、5年間でWebアプリケーション開発の幅広い経験を積んでまいりました。
バックエンドからフロントエンドまでのフルスタック開発が可能で、特にPython/Django、
React/TypeScriptを使用した開発が得意です。要件定義から設計、実装、テスト、
運用まで一貫して担当できる技術力を有しています。

現職では、新規SaaS製品の技術選定・アーキテクチャ設計を主導し、開発チームの
生産性向上とプロダクトの品質向上に貢献してきました。また、チームリーダーとして
後輩エンジニアの指導・育成も行い、技術力だけでなくマネジメント能力も身につけました。

今後は、より大規模なシステム開発や上流工程に携わることで、さらなる技術的成長を
目指したいと考えております。
            """.strip(),
            "objective": """
【自己PR】
■ 技術への探究心
新しい技術やフレームワークに対する学習意欲が高く、業務に活かせる技術は
積極的に検証・導入を提案しています。最近では、コンテナ技術（Docker/Kubernetes）や
クラウドネイティブな開発手法を学び、開発効率化に貢献しました。

■ チームワーク・コミュニケーション能力
チームリーダーとして、メンバーのスキルレベルに合わせた指導を行い、
チーム全体のレベルアップを図ってきました。また、非エンジニアのステークホルダーとも
円滑にコミュニケーションを取り、要件定義から運用まで成功に導いています。

■ 問題解決能力
システムの性能問題や障害対応において、根本原因を特定し、持続可能な解決策を
提案・実装してきました。特に、データベースクエリの最適化やアーキテクチャの改善に
より、大幅な性能向上を実現した経験があります。
            """.strip(),
            "template_id": "shokumu_detailed",
            "resume_format": ResumeFormat.SHOKUMU_KEIREKISHO,
            "resume_language": ResumeLanguage.JAPANESE,
            "status": ResumeStatus.PUBLISHED,
            "visibility": ResumeVisibility.PRIVATE,
            "theme_color": "#059669",
            "font_family": "Yu Gothic",
            "is_primary": False,
            "public_url_slug": generate_slug("職務経歴書 システムエンジニア"),
            "share_token": generate_share_token(),
            "is_public": False,
            "can_download_pdf": True,
            "can_edit": True,
            "can_delete": True
        }
        
        resume = Resume(**resume_data)
        db.add(resume)
        await db.flush()
        
        # Add detailed work experience
        experiences = [
            {
                "resume_id": resume.id,
                "company_name": "株式会社ウェブソリューションズ",
                "position_title": "シニアエンジニア（チームリーダー）",
                "location": "東京都新宿区",
                "start_date": datetime(2017, 4, 1),
                "is_current": True,
                "description": """
【事業内容】SaaS型の業務管理システムの開発・運営
【従業員数】約200名（エンジニア50名）
【担当業務】
・新規プロダクトの技術選定・アーキテクチャ設計（技術リード）
・フルスタック開発（React/TypeScript, Python/FastAPI）
・開発チームマネジメント（メンバー5名）
・コードレビュー、技術面接、新人研修の実施
・DevOps環境の構築・運用（AWS, Docker, GitHub Actions）
                """.strip(),
                "achievements": [
                    "新規SaaS製品の立ち上げプロジェクトで技術リードを担当し、月間アクティブユーザー1万人超の成長に貢献",
                    "マイクロサービスアーキテクチャの導入により、開発チームの並行開発効率を40%向上",
                    "CI/CDパイプラインの構築により、デプロイ時間を従来の1/3に短縮",
                    "API設計ガイドラインとコーディング規約の策定により、コード品質を標準化",
                    "チームメンバーの技術力向上により、3名が昇格・昇進を達成"
                ],
                "technologies": [
                    "React", "TypeScript", "Python", "FastAPI", "PostgreSQL", 
                    "Redis", "AWS", "Docker", "Kubernetes", "GitHub Actions"
                ],
                "display_order": 1,
                "is_visible": True
            },
            {
                "resume_id": resume.id,
                "company_name": "株式会社テックイノベーション",
                "position_title": "システムエンジニア",
                "location": "東京都渋谷区",
                "start_date": datetime(2012, 4, 1),
                "end_date": datetime(2017, 3, 31),
                "is_current": False,
                "description": """
【事業内容】企業向けWebシステムの受託開発
【従業員数】約50名（エンジニア30名）
【担当業務】
・Python/Djangoを使用したWebアプリケーション開発
・フロントエンド開発（jQuery, Bootstrap）
・データベース設計・最適化（MySQL, PostgreSQL）
・顧客要件のヒアリング・要件定義
・結合テスト・受入テストの実施
                """.strip(),
                "achievements": [
                    "ECサイト構築プロジェクトで、要件定義から運用開始まで一貫して担当し、予定通りリリースを達成",
                    "レガシーシステムのモダナイゼーション案件で、既存機能を100%移行しつつ処理速度を3倍向上",
                    "社内開発ツールの作成により、テスト工数を50%削減",
                    "新人教育プログラムの立案・実施により、新人の戦力化期間を2ヶ月短縮"
                ],
                "technologies": [
                    "Python", "Django", "JavaScript", "jQuery", "HTML/CSS", 
                    "MySQL", "PostgreSQL", "Linux", "Apache", "Git"
                ],
                "display_order": 2,
                "is_visible": True
            }
        ]
        
        for exp_data in experiences:
            experience = WorkExperience(**exp_data)
            db.add(experience)
        
        # Add technical skills
        skills = [
            {"resume_id": resume.id, "name": "Python", "category": "プログラミング言語", "proficiency_level": 5, "proficiency_label": "エキスパート", "display_order": 1},
            {"resume_id": resume.id, "name": "JavaScript", "category": "プログラミング言語", "proficiency_level": 5, "proficiency_label": "エキスパート", "display_order": 2},
            {"resume_id": resume.id, "name": "TypeScript", "category": "プログラミング言語", "proficiency_level": 4, "proficiency_label": "上級", "display_order": 3},
            {"resume_id": resume.id, "name": "Java", "category": "プログラミング言語", "proficiency_level": 3, "proficiency_label": "中級", "display_order": 4},
            {"resume_id": resume.id, "name": "React", "category": "フレームワーク", "proficiency_level": 5, "proficiency_label": "エキスパート", "display_order": 5},
            {"resume_id": resume.id, "name": "Django", "category": "フレームワーク", "proficiency_level": 5, "proficiency_label": "エキスパート", "display_order": 6},
            {"resume_id": resume.id, "name": "FastAPI", "category": "フレームワーク", "proficiency_level": 4, "proficiency_label": "上級", "display_order": 7},
            {"resume_id": resume.id, "name": "PostgreSQL", "category": "データベース", "proficiency_level": 4, "proficiency_label": "上級", "display_order": 8},
            {"resume_id": resume.id, "name": "AWS", "category": "クラウド", "proficiency_level": 4, "proficiency_label": "上級", "display_order": 9},
            {"resume_id": resume.id, "name": "Docker", "category": "インフラ", "proficiency_level": 4, "proficiency_label": "上級", "display_order": 10},
        ]
        
        for skill_data in skills:
            skill = Skill(**skill_data)
            db.add(skill)
        
        # Add projects
        projects = [
            {
                "resume_id": resume.id,
                "name": "SaaS型プロジェクト管理システム",
                "description": """
チーム向けのプロジェクト管理・タスク管理を行うWebアプリケーション。
リアルタイム通知、ガントチャート表示、レポート機能などを実装。
マイクロサービスアーキテクチャを採用し、高いスケーラビリティを実現。
                """.strip(),
                "start_date": datetime(2020, 1, 1),
                "end_date": datetime(2022, 12, 31),
                "is_ongoing": False,
                "role": "技術リード",
                "technologies": ["React", "TypeScript", "Python", "FastAPI", "PostgreSQL", "Redis", "AWS"],
                "project_url": "https://example-pm.com",
                "display_order": 1,
                "is_visible": True
            },
            {
                "resume_id": resume.id,
                "name": "ECサイト リニューアルプロジェクト",
                "description": """
レガシーなECサイトのフルリニューアル案件。
既存の売上データを分析し、ユーザビリティを大幅に改善。
レスポンシブデザイン対応、決済システムの更新、管理画面の刷新を実施。
                """.strip(),
                "start_date": datetime(2015, 6, 1),
                "end_date": datetime(2016, 3, 31),
                "is_ongoing": False,
                "role": "フルスタック開発者",
                "technologies": ["Python", "Django", "JavaScript", "Bootstrap", "MySQL"],
                "display_order": 2,
                "is_visible": True
            }
        ]
        
        for project_data in projects:
            project = Project(**project_data)
            db.add(project)
        
        return resume
    
    async def create_international_resume(self, db: AsyncSession, user: User) -> Resume:
        """Create international format resume"""
        
        resume_data = {
            "user_id": user.id,
            "title": "Software Engineer Resume",
            "description": "International format resume for global opportunities",
            "full_name": "Taro Tanaka",
            "email": "taro.tanaka@example.com",
            "phone": "+81-90-1234-5678",
            "location": "Tokyo, Japan",
            "website": "https://tarotanaka.dev",
            "linkedin_url": "https://linkedin.com/in/tarotanaka",
            "github_url": "https://github.com/tarotanaka",
            "professional_summary": """
Experienced Full-Stack Software Engineer with 5+ years of expertise in web application development. 
Skilled in Python, React, and cloud technologies with a proven track record of leading development teams 
and delivering scalable solutions. Passionate about clean code, performance optimization, and mentoring 
junior developers. Seeking opportunities to contribute to innovative products in a global environment.
            """.strip(),
            "template_id": "international_modern",
            "resume_format": ResumeFormat.INTERNATIONAL,
            "resume_language": ResumeLanguage.ENGLISH,
            "status": ResumeStatus.PUBLISHED,
            "visibility": ResumeVisibility.PUBLIC,
            "theme_color": "#7c3aed",
            "font_family": "Inter",
            "is_primary": False,
            "public_url_slug": generate_slug("Software Engineer Resume"),
            "share_token": generate_share_token(),
            "is_public": True,
            "can_download_pdf": True,
            "can_edit": True,
            "can_delete": True
        }
        
        resume = Resume(**resume_data)
        db.add(resume)
        await db.flush()
        
        # Add international work experience
        experiences = [
            {
                "resume_id": resume.id,
                "company_name": "Web Solutions Inc.",
                "position_title": "Senior Software Engineer",
                "location": "Tokyo, Japan",
                "company_website": "https://websolutions.co.jp",
                "start_date": datetime(2017, 4, 1),
                "is_current": True,
                "description": """
Led development of SaaS products using React/TypeScript and Python/FastAPI. 
Responsible for architecture design, team leadership, and DevOps implementation.
                """.strip(),
                "achievements": [
                    "Architected and led development of SaaS platform serving 10,000+ monthly active users",
                    "Improved deployment efficiency by 60% through CI/CD pipeline implementation",
                    "Mentored 5 junior developers, with 3 receiving promotions",
                    "Reduced API response time by 40% through performance optimization"
                ],
                "technologies": ["React", "TypeScript", "Python", "FastAPI", "AWS", "Docker"],
                "display_order": 1,
                "is_visible": True
            },
            {
                "resume_id": resume.id,
                "company_name": "Tech Innovation Co.",
                "position_title": "Software Engineer",
                "location": "Tokyo, Japan",
                "start_date": datetime(2012, 4, 1),
                "end_date": datetime(2017, 3, 31),
                "is_current": False,
                "description": """
Developed web applications using Python/Django and JavaScript. 
Handled full-stack development from requirements gathering to deployment.
                """.strip(),
                "achievements": [
                    "Successfully delivered 10+ client projects on time and within budget",
                    "Improved legacy system performance by 200% through optimization",
                    "Created internal development tools that reduced testing time by 50%"
                ],
                "technologies": ["Python", "Django", "JavaScript", "PostgreSQL", "Linux"],
                "display_order": 2,
                "is_visible": True
            }
        ]
        
        for exp_data in experiences:
            experience = WorkExperience(**exp_data)
            db.add(experience)
        
        # Add international education
        educations = [
            {
                "resume_id": resume.id,
                "institution_name": "University of Tokyo",
                "degree": "Bachelor of Engineering",
                "field_of_study": "Information and Communication Engineering",
                "location": "Tokyo, Japan",
                "start_date": datetime(2008, 4, 1),
                "end_date": datetime(2012, 3, 31),
                "is_current": False,
                "gpa": "3.7/4.0",
                "honors": "Dean's List",
                "display_order": 1,
                "is_visible": True
            }
        ]
        
        for edu_data in educations:
            education = Education(**edu_data)
            db.add(education)
        
        # Add languages
        languages = [
            {
                "resume_id": resume.id,
                "name": "Japanese",
                "proficiency": "Native",
                "display_order": 1,
                "is_visible": True
            },
            {
                "resume_id": resume.id,
                "name": "English",
                "proficiency": "Professional Working Proficiency (TOEIC 850)",
                "display_order": 2,
                "is_visible": True
            }
        ]
        
        for lang_data in languages:
            language = Language(**lang_data)
            db.add(language)
        
        return resume
    
    async def create_modern_resume(self, db: AsyncSession, user: User) -> Resume:
        """Create modern format resume"""
        
        resume_data = {
            "user_id": user.id,
            "title": "Creative Developer Portfolio",
            "description": "Modern creative resume showcasing design and development skills",
            "full_name": "Taro Tanaka",
            "email": "hello@tarotanaka.design",
            "phone": "090-1234-5678",
            "location": "Tokyo, Japan",
            "website": "https://tarotanaka.design",
            "linkedin_url": "https://linkedin.com/in/tarotanaka",
            "github_url": "https://github.com/tarotanaka",
            "professional_summary": """
Creative Full-Stack Developer with a passion for building beautiful, functional web experiences. 
Combining technical expertise with design sensibility to create user-centered solutions that drive business value.
            """.strip(),
            "template_id": "modern_creative",
            "resume_format": ResumeFormat.MODERN,
            "resume_language": ResumeLanguage.BILINGUAL,
            "status": ResumeStatus.DRAFT,
            "visibility": ResumeVisibility.PRIVATE,
            "theme_color": "#f59e0b",
            "font_family": "Poppins",
            "is_primary": False,
            "public_url_slug": generate_slug("Creative Developer Portfolio"),
            "share_token": generate_share_token(),
            "is_public": False,
            "can_download_pdf": True,
            "can_edit": True,
            "can_delete": True
        }
        
        resume = Resume(**resume_data)
        db.add(resume)
        await db.flush()
        
        # Add creative projects
        projects = [
            {
                "resume_id": resume.id,
                "name": "Interactive Data Visualization Platform",
                "description": "Built an interactive dashboard for data visualization using D3.js and React",
                "start_date": datetime(2021, 1, 1),
                "end_date": datetime(2021, 6, 30),
                "is_ongoing": False,
                "role": "Lead Developer & Designer",
                "technologies": ["React", "D3.js", "TypeScript", "Node.js"],
                "project_url": "https://dataviz.example.com",
                "github_url": "https://github.com/tarotanaka/dataviz-platform",
                "demo_url": "https://demo.dataviz.example.com",
                "display_order": 1,
                "is_visible": True
            }
        ]
        
        for project_data in projects:
            project = Project(**project_data)
            db.add(project)
        
        return resume
    
    def create_fallback_data(self):
        """Create fallback JSON data when database is not available"""
        self.fallback_data = {
            "message": "Database not available. Resume seed data created as JSON.",
            "timestamp": datetime.now().isoformat(),
            "sample_resumes": [
                {
                    "title": "履歴書 - 田中太郎",
                    "format": "rirekisho",
                    "language": "ja",
                    "description": "Traditional Japanese resume format with all required fields",
                    "features": [
                        "Personal information with furigana",
                        "Educational background",
                        "Work history",
                        "Certifications and qualifications",
                        "Photo section"
                    ]
                },
                {
                    "title": "職務経歴書 - システムエンジニア",
                    "format": "shokumu_keirekisho",
                    "language": "ja",
                    "description": "Detailed career history document for technical positions",
                    "features": [
                        "Career summary",
                        "Detailed work experience",
                        "Technical skills",
                        "Project history",
                        "Self-PR section"
                    ]
                },
                {
                    "title": "Software Engineer Resume",
                    "format": "international",
                    "language": "en",
                    "description": "International format resume for global opportunities",
                    "features": [
                        "Professional summary",
                        "Work experience",
                        "Education",
                        "Skills and technologies",
                        "Achievements"
                    ]
                },
                {
                    "title": "Creative Developer Portfolio",
                    "format": "modern",
                    "language": "bilingual",
                    "description": "Modern creative resume with design focus",
                    "features": [
                        "Creative layout",
                        "Project portfolio",
                        "Design skills",
                        "Technical abilities",
                        "Visual elements"
                    ]
                }
            ],
            "instructions": {
                "database_setup": "Set up your database connection to enable full seeding",
                "manual_creation": "Use the API endpoints to create resumes manually",
                "sample_data": "Use the structure above as a template for resume creation"
            }
        }
        
        # Save fallback data to file
        import json
        fallback_file = os.path.join(project_root, "scripts", "resume_seed_fallback.json")
        with open(fallback_file, "w", encoding="utf-8") as f:
            json.dump(self.fallback_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Fallback data saved to: {fallback_file}")
        return True


async def main():
    """Main execution function"""
    print("🚀 Starting Resume System Seeding...")
    print("=" * 50)
    
    seeder = ResumeSeeder()
    success = await seeder.seed_all()
    
    print("=" * 50)
    if success:
        print("✅ Resume seeding completed successfully!")
        if seeder.created_resumes:
            print(f"📋 Created {len(seeder.created_resumes)} sample resumes:")
            for resume in seeder.created_resumes:
                print(f"  • {resume.title} ({resume.resume_format.value})")
        else:
            print("📋 Fallback data created due to database unavailability")
    else:
        print("❌ Resume seeding failed")
        return False
    
    print("\n📖 Sample resumes include:")
    print("  🇯🇵 履歴書 (Traditional Japanese resume)")
    print("  🇯🇵 職務経歴書 (Japanese career history)")
    print("  🌍 International format resume")
    print("  🎨 Modern creative portfolio")
    
    print("\n🔧 Next steps:")
    print("  • Test resume creation via API")
    print("  • Generate PDF exports")
    print("  • Set up public sharing")
    print("  • Configure email integration")
    
    return True


if __name__ == "__main__":
    asyncio.run(main())