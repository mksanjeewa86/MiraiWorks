"""
Default seed data for MiraiWorks database initialization.

This file contains:
- 1 super admin user
- 5 company users (1 for super admin's company, 4 for other companies)
- 6 companies (1 for super admin, 5 others)
- User settings for all users
- Company profiles for all companies
- User roles and roles for all users
- 7 direct messages between users for testing messaging functionality
- 3 interviews with different statuses and scheduling details

HOW TO RUN:
    1. Navigate to the backend directory:
       cd backend

    2. Run the script:
       PYTHONPATH=. python app/seed_data.py

    3. Alternative method:
       python -m app.seed_data

REQUIREMENTS:
    - Database must exist and be accessible
    - Database tables must be created (run: alembic upgrade head)
    - Environment variables must be set (.env file)

WARNING: This script will DELETE all existing seed data and create fresh data!
         It completely refreshes the database with clean seed data every time.
         All passwords are set to: "password"
"""

import asyncio
import os

# Set environment to avoid conflicts
os.environ.setdefault("ENVIRONMENT", "development")

# Import through FastAPI app to ensure proper model loading
from app.database import AsyncSessionLocal
from app.models import User, Company, Role, UserRole, UserSettings, CompanyProfile
from app.models.message import Message
from app.models.interview import Interview
from app.models.position import Position
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType, MessageType, InterviewStatus


async def create_seed_data():
    """Create all seed data fresh (removes existing seed data first)."""
    print("Starting FRESH seed data creation...")
    print("=" * 60)
    print("WARNING: This will DELETE all existing seed data and create new data!")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import delete

            # Clear existing seed data in correct order (reverse of creation)
            print("\nClearing existing seed data...")

            # Clear messages
            await db.execute(delete(Message))
            print("   - Cleared messages")

            # Clear interviews
            await db.execute(delete(Interview))
            print("   - Cleared interviews")

            # Clear positions
            await db.execute(delete(Position))
            print("   - Cleared positions")

            # Clear company profiles
            await db.execute(delete(CompanyProfile))
            print("   - Cleared company profiles")

            # Clear user settings
            await db.execute(delete(UserSettings))
            print("   - Cleared user settings")

            # Clear user roles
            await db.execute(delete(UserRole))
            print("   - Cleared user roles")

            # Clear users
            await db.execute(delete(User))
            print("   - Cleared users")

            # Clear companies
            await db.execute(delete(Company))
            print("   - Cleared companies")

            # Clear roles
            await db.execute(delete(Role))
            print("   - Cleared roles")

            await db.commit()
            print("   > All existing seed data cleared!")

            # Create roles first
            print("\nCreating fresh roles...")
            roles_data = [
                {"name": "super_admin", "description": "Super administrator with full system access"},
                {"name": "company_admin", "description": "Company administrator with full company access"},
                {"name": "recruiter", "description": "Recruiter with candidate and position management access"},
                {"name": "employer", "description": "Employer with position management access"},
                {"name": "candidate", "description": "Candidate with profile and application access"},
            ]

            roles = {}
            for role_data in roles_data:
                role = Role(**role_data)
                db.add(role)
                await db.flush()
                roles[role_data["name"]] = role
                print(f"   - Created role '{role_data['name']}'")

            await db.commit()

            # Create companies
            print("\nCreating companies...")
            companies_data = [
                {
                    "name": "MiraiWorks システム",
                    "type": CompanyType.EMPLOYER,
                    "email": "admin@miraiworks.jp",
                    "phone": "+81-3-1234-5678",
                    "website": "https://miraiworks.jp",
                    "postal_code": "100-0001",
                    "prefecture": "Tokyo",
                    "city": "Chiyoda",
                    "description": "MiraiWorks プラットフォームシステム運営会社",
                    "is_active": "1",
                },
                {
                    "name": "テックコーポレーション",
                    "type": CompanyType.EMPLOYER,
                    "email": "hr@techcorp.jp",
                    "phone": "+81-3-2345-6789",
                    "website": "https://techcorp.jp",
                    "postal_code": "150-0001",
                    "prefecture": "Tokyo",
                    "city": "Shibuya",
                    "description": "最先端技術ソリューションプロバイダー",
                    "is_active": "1",
                },
                {
                    "name": "イノベートラボ株式会社",
                    "type": CompanyType.RECRUITER,
                    "email": "contact@innovatelab.jp",
                    "phone": "+81-6-3456-7890",
                    "website": "https://innovatelab.jp",
                    "postal_code": "530-0001",
                    "prefecture": "Osaka",
                    "city": "Kita",
                    "description": "革新的な採用支援エージェンシー",
                    "is_active": "1",
                },
                {
                    "name": "データドリブン・アナリティクス",
                    "type": CompanyType.EMPLOYER,
                    "email": "jobs@datadriven.jp",
                    "phone": "+81-45-4567-8901",
                    "website": "https://datadriven.jp",
                    "postal_code": "220-0001",
                    "prefecture": "Kanagawa",
                    "city": "Yokohama",
                    "description": "データ分析とビジネスインテリジェンス企業",
                    "is_active": "1",
                },
                {
                    "name": "クラウドスケール・システムズ",
                    "type": CompanyType.EMPLOYER,
                    "email": "careers@cloudscale.jp",
                    "phone": "+81-52-5678-9012",
                    "website": "https://cloudscale.jp",
                    "postal_code": "460-0001",
                    "prefecture": "Aichi",
                    "city": "Nagoya",
                    "description": "クラウドインフラとスケーリングソリューション",
                    "is_active": "1",
                },
                {
                    "name": "ネクストジェン・リクルーティング",
                    "type": CompanyType.RECRUITER,
                    "email": "info@nextgenrecruiting.jp",
                    "phone": "+81-92-6789-0123",
                    "website": "https://nextgenrecruiting.jp",
                    "postal_code": "810-0001",
                    "prefecture": "Fukuoka",
                    "city": "Chuo",
                    "description": "次世代採用サービス",
                    "is_active": "1",
                },
            ]

            companies = []
            for company_data in companies_data:
                company = Company(**company_data)
                db.add(company)
                await db.flush()
                companies.append(company)
                print(f"   - Created company '{company_data['name']}'")

            await db.commit()

            # Create users
            print("\nCreating users...")
            users_data = [
                {
                    "company_id": companies[0].id,  # MiraiWorks システム
                    "email": "superadmin@miraiworks.jp",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "スーパー",
                    "last_name": "管理者",
                    "phone": "+81-3-1111-2222",
                    "is_active": True,
                    "is_admin": True,
                    "role": "super_admin",
                },
                {
                    "company_id": companies[1].id,  # テックコーポレーション
                    "email": "admin@techcorp.jp",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "田中",
                    "last_name": "太郎",
                    "phone": "+81-3-2222-3333",
                    "is_active": True,
                    "is_admin": False,
                    "role": "company_admin",
                },
                {
                    "company_id": companies[2].id,  # イノベートラボ株式会社
                    "email": "recruiter@innovatelab.jp",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "佐藤",
                    "last_name": "花子",
                    "phone": "+81-6-3333-4444",
                    "is_active": True,
                    "is_admin": False,
                    "role": "recruiter",
                },
                {
                    "company_id": companies[3].id,  # データドリブン・アナリティクス
                    "email": "hr@datadriven.jp",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "鈴木",
                    "last_name": "一郎",
                    "phone": "+81-45-4444-5555",
                    "is_active": True,
                    "is_admin": False,
                    "role": "employer",
                },
                {
                    "company_id": companies[4].id,  # クラウドスケール・システムズ
                    "email": "manager@cloudscale.jp",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "高橋",
                    "last_name": "美咲",
                    "phone": "+81-52-5555-6666",
                    "is_active": True,
                    "is_admin": False,
                    "role": "company_admin",
                },
                {
                    "company_id": companies[5].id,  # ネクストジェン・リクルーティング
                    "email": "lead@nextgenrecruiting.jp",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "伊藤",
                    "last_name": "健太",
                    "phone": "+81-92-6666-7777",
                    "is_active": True,
                    "is_admin": False,
                    "role": "recruiter",
                },
            ]

            users = []
            for user_data in users_data:
                user_role = user_data.pop("role")
                user = User(**user_data)
                db.add(user)
                await db.flush()
                users.append((user, user_role))
                print(f"   - Created user '{user_data['email']}'")

            await db.commit()

            # Create user roles
            for user, role_name in users:
                user_role = UserRole(
                    user_id=user.id,
                    role_id=roles[role_name].id,
                    scope=f"company_{user.company_id}" if role_name != "super_admin" else "global"
                )
                db.add(user_role)

            # Create user settings for all users
            user_settings_data = [
                {
                    "job_title": "システム管理者",
                    "bio": "MiraiWorksプラットフォームの管理運営を担当するスーパー管理者",
                    "language": "ja",
                    "timezone": "Asia/Tokyo",
                },
                {
                    "job_title": "人事部長",
                    "bio": "テックコーポレーションの人材獲得と人事業務を統括",
                    "language": "ja",
                    "timezone": "Asia/Tokyo",
                },
                {
                    "job_title": "シニアリクルーター",
                    "bio": "IT技術者採用と人材開拓の専門家",
                    "language": "ja",
                    "timezone": "Asia/Tokyo",
                },
                {
                    "job_title": "人材獲得マネージャー",
                    "bio": "データ分析を活用した最適な人材発掘",
                    "language": "ja",
                    "timezone": "Asia/Tokyo",
                },
                {
                    "job_title": "人事オペレーション責任者",
                    "bio": "クラウドスケールソリューションのための優秀なチーム構築",
                    "language": "ja",
                    "timezone": "Asia/Tokyo",
                },
                {
                    "job_title": "リクルートメントコンサルタント主任",
                    "bio": "次世代採用戦略とソリューションの企画・実行",
                    "language": "ja",
                    "timezone": "Asia/Tokyo",
                },
            ]

            for i, (user, _) in enumerate(users):
                settings_data = user_settings_data[i].copy()
                settings_data["user_id"] = user.id
                settings = UserSettings(**settings_data)
                db.add(settings)

            # Create company profiles for all companies
            company_profiles_data = [
                {
                    "tagline": "未来の採用を支えるプラットフォーム",
                    "mission": "革新的なテクノロジーで企業と人材の最適なマッチングを実現する",
                    "values": '["革新性", "透明性", "卓越性", "協働"]',
                    "culture": "継続的な改善とユーザー満足度を重視する、ダイナミックでテクノロジー主導の環境",
                    "employee_count": "11-50",
                    "headquarters": "東京都千代田区",
                    "founded_year": 2024,
                    "benefits_summary": "包括的な健康保険、フレックス勤務、専門能力開発支援",
                    "perks_highlights": '["リモートワーク対応", "教育研修費補助", "健康・ウェルネスプログラム"]',
                },
                {
                    "tagline": "価値ある技術ソリューション",
                    "mission": "ビジネス成功を推進する最先端技術ソリューションの提供",
                    "values": '["革新性", "品質", "顧客成功", "誠実性"]',
                    "culture": "創造性と技術的卓越性が活かされる、革新的でペースの早い環境",
                    "employee_count": "201-500",
                    "headquarters": "東京都渋谷区",
                    "founded_year": 2018,
                    "benefits_summary": "完全健康保険、株式参加、無制限有給休暇",
                    "perks_highlights": '["ストックオプション", "無制限有給", "最高級機器支給", "学習支援金"]',
                },
                {
                    "tagline": "革新と人材の出会い",
                    "mission": "戦略的採用により革新的企業と優秀な人材を結ぶ",
                    "values": '["卓越性", "パートナーシップ", "革新性", "信頼"]',
                    "culture": "長期的なパートナーシップ構築に焦点を当てた、協調的で成果重視の環境",
                    "employee_count": "51-100",
                    "headquarters": "大阪府大阪市北区",
                    "founded_year": 2020,
                    "benefits_summary": "競争力のある給与、健康保険、柔軟な勤務スケジュール",
                    "perks_highlights": '["フレックスタイム", "業界ネットワーキング", "成果ボーナス"]',
                },
                {
                    "tagline": "データ駆動の意思決定、人間中心の結果",
                    "mission": "データを実用的な洞察に変換し、ビジネス成長を促進する",
                    "values": '["データ整合性", "革新性", "協働", "インパクト"]',
                    "culture": "データと創造性が融合する、分析的で協調的な環境",
                    "employee_count": "101-200",
                    "headquarters": "神奈川県横浜市",
                    "founded_year": 2019,
                    "benefits_summary": "包括的福利厚生、専門能力開発、ワークライフバランス",
                    "perks_highlights": '["データサイエンス研修", "学会参加支援", "ウェルネスプログラム"]',
                },
                {
                    "tagline": "クラウドで可能性を拡げる",
                    "mission": "クラウドインフラソリューションで企業のシームレスなスケーリングを支援",
                    "values": '["拡張性", "信頼性", "革新性", "卓越性"]',
                    "culture": "信頼性と継続的改善に焦点を当てた高性能文化",
                    "employee_count": "51-100",
                    "headquarters": "愛知県名古屋市",
                    "founded_year": 2021,
                    "benefits_summary": "完全福利厚生パッケージ、株式オプション、専門成長支援",
                    "perks_highlights": '["クラウド認定取得支援", "技術会議参加", "チームビルディングイベント"]',
                },
                {
                    "tagline": "採用の未来がここに",
                    "mission": "テクノロジーと個別化サービスで採用業界を革新する",
                    "values": '["革新性", "個別化", "成果", "パートナーシップ"]',
                    "culture": "新技術と手法を取り入れた、先進的でクライアント重視の環境",
                    "employee_count": "11-50",
                    "headquarters": "福岡県福岡市中央区",
                    "founded_year": 2022,
                    "benefits_summary": "競争力のあるパッケージ、専門能力開発、柔軟な働き方",
                    "perks_highlights": '["リモート柔軟性", "業界研修", "成果インセンティブ"]',
                },
            ]

            for i, company in enumerate(companies):
                profile_data = company_profiles_data[i].copy()
                profile_data["company_id"] = company.id
                profile_data["last_updated_by"] = users[0][0].id if i == 0 else users[min(i, len(users)-1)][0].id
                profile = CompanyProfile(**profile_data)
                db.add(profile)

            # Create direct messages between users
            print("\nCreating direct messages...")
            messages_data = [
                # テックコーポレーションとイノベートラボの採用相談
                {
                    "sender_id": users[1][0].id,  # admin@techcorp.jp
                    "recipient_id": users[2][0].id,  # recruiter@innovatelab.jp
                    "type": MessageType.TEXT.value,
                    "content": "お疲れ様です。新しいプロジェクトで優秀な開発者を探しています。候補者をご紹介いただけますでしょうか？",
                },
                {
                    "sender_id": users[2][0].id,  # recruiter@innovatelab.jp
                    "recipient_id": users[1][0].id,  # admin@techcorp.jp
                    "type": MessageType.TEXT.value,
                    "content": "もちろんです！喜んでサポートさせていただきます。どのような技術スキルをお求めでしょうか？",
                },
                {
                    "sender_id": users[1][0].id,  # admin@techcorp.jp
                    "recipient_id": users[2][0].id,  # recruiter@innovatelab.jp
                    "type": MessageType.TEXT.value,
                    "content": "ReactとNode.jsの経験を持つフルスタック開発者が必要です。3年以上の経験者を希望しています。",
                },

                # データドリブンとネクストジェンのパートナーシップ
                {
                    "sender_id": users[3][0].id,  # hr@datadriven.jp
                    "recipient_id": users[5][0].id,  # lead@nextgenrecruiting.jp
                    "type": MessageType.TEXT.value,
                    "content": "こんにちは！御社の採用サービスを拝見し、パートナーシップに興味があります。",
                },
                {
                    "sender_id": users[5][0].id,  # lead@nextgenrecruiting.jp
                    "recipient_id": users[3][0].id,  # hr@datadriven.jp
                    "type": MessageType.TEXT.value,
                    "content": "ご連絡いただきありがとうございます！弊社はデータサイエンスとアナリティクス分野の採用を専門としています。どちらのポジションをお探しでしょうか？",
                },

                # クラウドスケールチームの連携
                {
                    "sender_id": users[4][0].id,  # manager@cloudscale.jp
                    "recipient_id": users[2][0].id,  # recruiter@innovatelab.jp
                    "type": MessageType.TEXT.value,
                    "content": "協業への参加、ありがとうございます！採用活動を連携して進めましょう。",
                },
                {
                    "sender_id": users[0][0].id,  # superadmin@miraiworks.jp
                    "recipient_id": users[4][0].id,  # manager@cloudscale.jp
                    "type": MessageType.TEXT.value,
                    "content": "MiraiWorksへようこそ！プラットフォームに関してご不明な点がございましたら、お気軽にお声かけください。",
                },
            ]

            for msg_data in messages_data:
                message = Message(**msg_data)
                db.add(message)

            print(f"   - Created {len(messages_data)} direct messages")

            # Create interviews
            print("\nCreating interviews...")

            from datetime import datetime, timedelta
            base_time = datetime.now()

            interviews_data = [
                {
                    "candidate_id": users[1][0].id,  # Will use company user as mock candidate
                    "recruiter_id": users[2][0].id,  # recruiter@innovatelab.jp
                    "employer_company_id": companies[1].id,  # テックコーポレーション
                    "recruiter_company_id": companies[2].id,  # イノベートラボ株式会社
                    "title": "シニアフルスタック開発者面接",
                    "description": "ReactとNode.jsに重点を置いたシニアフルスタック開発者ポジションの技術面接",
                    "position_title": "シニアフルスタック開発者",
                    "status": InterviewStatus.SCHEDULED.value,
                    "interview_type": "video",
                    "scheduled_start": base_time + timedelta(days=3, hours=10),
                    "scheduled_end": base_time + timedelta(days=3, hours=11),
                    "timezone": "Asia/Tokyo",
                    "meeting_url": "https://meet.techcorp.jp/interview-001",
                    "meeting_id": "tcorp-001",
                },
                {
                    "candidate_id": users[3][0].id,  # Will use company user as mock candidate
                    "recruiter_id": users[5][0].id,  # lead@nextgenrecruiting.jp
                    "employer_company_id": companies[3].id,  # データドリブン・アナリティクス
                    "recruiter_company_id": companies[5].id,  # ネクストジェン・リクルーティング
                    "title": "データサイエンティストポジション面接",
                    "description": "機械学習とアナリティクスに焦点を当てたデータサイエンティスト職の面接",
                    "position_title": "シニアデータサイエンティスト",
                    "status": InterviewStatus.CONFIRMED.value,
                    "interview_type": "video",
                    "scheduled_start": base_time + timedelta(days=5, hours=14),
                    "scheduled_end": base_time + timedelta(days=5, hours=15, minutes=30),
                    "timezone": "Asia/Tokyo",
                    "meeting_url": "https://zoom.us/j/datadriven123",
                    "meeting_id": "zoom-dd-123",
                },
                {
                    "candidate_id": users[4][0].id,  # Will use company user as mock candidate
                    "recruiter_id": users[2][0].id,  # recruiter@innovatelab.jp
                    "employer_company_id": companies[4].id,  # クラウドスケール・システムズ
                    "recruiter_company_id": companies[2].id,  # イノベートラボ株式会社
                    "title": "DevOpsエンジニア面接",
                    "description": "クラウドインフラに重点を置いたDevOpsエンジニアポジションの技術面接",
                    "position_title": "シニアDevOpsエンジニア",
                    "status": InterviewStatus.PENDING_SCHEDULE.value,
                    "interview_type": "video",
                    "timezone": "Asia/Tokyo",
                },
            ]

            for interview_data in interviews_data:
                interview = Interview(**interview_data)
                db.add(interview)
                print(f"   - Created interview '{interview_data['title']}'")

            # Create positions (sample jobs)
            print("\nCreating positions...")

            # Helper function to create position slug
            def create_slug(title: str, company_name: str) -> str:
                import hashlib
                # For Japanese titles, create a hash-based slug
                combined = f"{title}-{company_name}"
                # Create a hash for Japanese characters
                hash_obj = hashlib.md5(combined.encode('utf-8'))
                return f"position-{hash_obj.hexdigest()[:12]}"

            positions_data = [
                # All positions will be generated automatically with Japanese content
            ]

            # Add more positions to reach approximately 100 total
            additional_positions = []

            # Create variations of existing positions for different companies and locations
            base_positions = [
                ("ソフトウェアエンジニア", "technology", "full_time", "mid_level", ["Python", "JavaScript", "SQL", "Git"], 6000000, 9000000),
                ("データアナリスト", "data", "full_time", "mid_level", ["SQL", "Excel", "Python", "Tableau"], 5000000, 7000000),
                ("マーケティングコーディネーター", "marketing", "full_time", "entry_level", ["Social Media", "Content Creation", "Email Marketing"], 3500000, 4500000),
                ("営業担当", "sales", "full_time", "mid_level", ["Sales", "CRM", "Account Management"], 4500000, 7000000),
                ("UIデザイナー", "design", "full_time", "mid_level", ["UI Design", "Figma", "Adobe Creative Suite"], 5000000, 7500000),
                ("ビジネスアナリスト", "business", "full_time", "mid_level", ["Business Analysis", "Requirements Gathering", "SQL"], 5500000, 7500000),
                ("テクニカルサポートエンジニア", "support", "full_time", "entry_level", ["Technical Support", "Troubleshooting", "Customer Service"], 4000000, 5500000),
                ("サイバーセキュリティアナリスト", "security", "full_time", "mid_level", ["Security Analysis", "Risk Assessment", "Incident Response"], 6000000, 8500000),
                ("システム管理者", "technology", "full_time", "mid_level", ["Linux", "Windows Server", "Network Administration"], 5000000, 7000000),
                ("プロジェクトマネージャー", "project_management", "full_time", "senior_level", ["Project Management", "Agile", "Scrum", "PMP"], 6500000, 9000000),
            ]

            locations = [
                ("東京都千代田区", "Japan", "千代田区"),
                ("東京都渋谷区", "Japan", "渋谷区"),
                ("東京都新宿区", "Japan", "新宿区"),
                ("大阪府大阪市北区", "Japan", "大阪市北区"),
                ("神奈川県横浜市", "Japan", "横浜市"),
                ("愛知県名古屋市", "Japan", "名古屋市"),
                ("福岡県福岡市中央区", "Japan", "福岡市中央区"),
                ("リモート", "Japan", None),
            ]

            remote_types = ["on_site", "remote", "hybrid"]
            job_types = ["full_time", "part_time", "contract"]

            for i, (title, dept, job_type, exp_level, skills, min_sal, max_sal) in enumerate(base_positions * 7):  # Multiply to get more variations
                if len(additional_positions) >= 70:  # Limit to avoid too many
                    break

                company = companies[(i % 4) + 1]  # Rotate through companies 1-4
                location, country, city = locations[i % len(locations)]
                remote_type = remote_types[i % len(remote_types)]
                job_type_var = job_types[i % len(job_types)]

                # Adjust salary for part-time and contract
                if job_type_var == "part_time":
                    min_sal = int(min_sal * 0.6)
                    max_sal = int(max_sal * 0.6)
                elif job_type_var == "contract":
                    min_sal = int(min_sal * 1.2)
                    max_sal = int(max_sal * 1.2)

                position = {
                    "title": f"{title} {i+1}" if i > 0 else title,
                    "company_id": company.id,
                    "department": dept,
                    "job_type": job_type_var,
                    "experience_level": exp_level,
                    "remote_type": remote_type,
                    "location": location,
                    "country": country,
                    "city": city,
                    "description": f"{title}として私たちのチームに参加し、あなたの専門知識と献身で会社の成功を支援してください。",
                    "summary": f"{title}のポジションで成長機会あり",
                    "requirements": f"{', '.join(skills[:3])}の経験と強力な問題解決スキルが必要です。",
                    "required_skills": '[' + ', '.join([f'"{skill}"' for skill in skills]) + ']',
                    "preferred_skills": '[' + ', '.join([f'"{skill} Advanced"' for skill in skills[:2]]) + ']',
                    "salary_min": min_sal,  # Already in yen
                    "salary_max": max_sal,  # Already in yen
                    "salary_currency": "JPY",
                    "show_salary": True,
                    "status": "published",
                    "published_at": base_time - timedelta(days=(i % 10) + 1),
                    "posted_by": users[(i % 4) + 1][0].id,
                }
                additional_positions.append(position)

            # Combine all positions
            all_positions = positions_data + additional_positions

            # Create position records
            created_positions = []
            for position_data in all_positions:
                # Create slug
                position_data["slug"] = create_slug(position_data["title"],
                    next(c.name for c in companies if c.id == position_data["company_id"]))

                position = Position(**position_data)
                db.add(position)
                await db.flush()
                created_positions.append(position)

            print(f"   - Created {len(all_positions)} positions")

            # Commit all changes
            await db.commit()

            print("SUCCESS: Fresh seed data created successfully!")
            print("=" * 50)
            print("FRESH DATA SUMMARY:")
            print(f"   - {len(roles_data)} roles")
            print(f"   - {len(companies)} companies")
            print(f"   - {len(users)} users")
            print(f"   - {len(users)} user roles")
            print(f"   - {len(users)} user settings")
            print(f"   - {len(companies)} company profiles")
            print(f"   - {len(messages_data)} messages")
            print(f"   - {len(interviews_data)} interviews")
            print(f"   - {len(all_positions)} positions")

            print("\nLOGIN CREDENTIALS (All passwords: 'password'):")
            print("=" * 50)
            print("Super Admin:")
            print("   Email: superadmin@miraiworks.jp")
            print("   Password: password")

            print("\nCompany Users:")
            for user, role_name in users[1:]:
                company_name = next(c.name for c in companies if c.id == user.company_id)
                print(f"   - {user.email} (password) - {role_name} at {company_name}")

            print("\n> Database has been refreshed with clean seed data!")

        except Exception as e:
            await db.rollback()
            print(f"ERROR: Error creating seed data: {e}")
            print("\nTroubleshooting:")
            print("1. Ensure database tables exist (run migrations)")
            print("2. Check database connection settings")
            print("3. Verify all required dependencies are installed")
            raise


async def main():
    """Main function to run seed data creation."""
    await create_seed_data()


if __name__ == "__main__":
    asyncio.run(main())

