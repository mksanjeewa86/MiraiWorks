"""
Authentication and User Data Seeds

Contains roles, companies, users, and user_roles seed data.
This file creates the essential authentication system data.
"""

from app.models import Company, CompanyProfile, Role, User, UserRole, UserSettings
from app.models.user_connection import UserConnection
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType

# Roles data
ROLES_DATA = [
    {"name": "super_admin", "description": "Super administrator with full system access"},
    {"name": "company_admin", "description": "Company administrator with full company access"},
    {"name": "recruiter", "description": "Recruiter with candidate and position management access"},
    {"name": "employer", "description": "Employer with position management access"},
    {"name": "candidate", "description": "Candidate with profile and application access"},
]

# Companies data
COMPANIES_DATA = [
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


def get_users_data(companies):
    """Get users data with company IDs."""
    return [
        # Essential login accounts for testing
        {
            "company_id": companies[0].id,  # MiraiWorks システム
            "email": "admin@miraiworks.com",
            "hashed_password": auth_service.get_password_hash("password"),
            "first_name": "Admin",
            "last_name": "User",
            "phone": "+81-3-1111-1111",
            "is_active": True,
            "is_admin": True,
            "role": "super_admin",
        },
        {
            "company_id": companies[0].id,  # MiraiWorks システム
            "email": "candidate@example.com",
            "hashed_password": auth_service.get_password_hash("password"),
            "first_name": "Test",
            "last_name": "Candidate",
            "phone": "+81-3-2222-2222",
            "is_active": True,
            "is_admin": False,
            "role": "candidate",
        },
        {
            "company_id": companies[0].id,  # MiraiWorks システム
            "email": "recruiter@miraiworks.com",
            "hashed_password": auth_service.get_password_hash("password"),
            "first_name": "Test",
            "last_name": "Recruiter",
            "phone": "+81-3-3333-3333",
            "is_active": True,
            "is_admin": False,
            "role": "recruiter",
        },
        # System admin
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


def get_user_settings_data():
    """Get user settings data."""
    return [
        # Essential login accounts settings
        {
            "job_title": "System Administrator",
            "bio": "MiraiWorks system administrator with full access",
            "language": "en",
            "timezone": "Asia/Tokyo",
        },
        {
            "job_title": "Test Candidate",
            "bio": "Test candidate account for MBTI and application testing",
            "language": "en",
            "timezone": "Asia/Tokyo",
        },
        {
            "job_title": "Test Recruiter",
            "bio": "Test recruiter account for recruitment feature testing",
            "language": "en",
            "timezone": "Asia/Tokyo",
        },
        # System admin
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


def get_company_profiles_data():
    """Get company profiles data."""
    return [
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


async def create_user_connections(db, users, roles):
    """Create user connections between admin users and super admin."""
    connections_created = 0

    # Find super admin user
    super_admin_user = None
    for user, role_name in users:
        if role_name == "super_admin":
            super_admin_user = user
            break

    if not super_admin_user:
        print("   - No super admin found, skipping user connections")
        return 0

    # Connect all admin users (company_admin) to super admin
    for user, role_name in users:
        if role_name == "company_admin" and user.id != super_admin_user.id:
            connection = UserConnection(
                user_id=user.id,
                connected_user_id=super_admin_user.id,
                is_active=True,
                creation_type="automatic",
                created_by=None
            )
            db.add(connection)
            connections_created += 1
            print(f"   - Connected {user.email} (company_admin) to {super_admin_user.email} (super_admin) [AUTOMATIC]")

    # Connect recruiters to super admin as well for coordination
    for user, role_name in users:
        if role_name == "recruiter" and user.id != super_admin_user.id:
            connection = UserConnection(
                user_id=user.id,
                connected_user_id=super_admin_user.id,
                is_active=True,
                creation_type="automatic",
                created_by=None
            )
            db.add(connection)
            connections_created += 1
            print(f"   - Connected {user.email} (recruiter) to {super_admin_user.email} (super_admin) [AUTOMATIC]")

    # Connect candidate to recruiters for demonstration
    candidate_user = None
    recruiter_users = []
    for user, role_name in users:
        if role_name == "candidate":
            candidate_user = user
        elif role_name == "recruiter":
            recruiter_users.append(user)

    if candidate_user and recruiter_users:
        for recruiter_user in recruiter_users:
            connection = UserConnection(
                user_id=candidate_user.id,
                connected_user_id=recruiter_user.id,
                is_active=True,
                creation_type="automatic",
                created_by=None
            )
            db.add(connection)
            connections_created += 1
            print(f"   - Connected {candidate_user.email} (candidate) to {recruiter_user.email} (recruiter) [AUTOMATIC]")

    await db.commit()
    print(f"   - Created {connections_created} user connections")
    return connections_created


async def seed_auth_data(db):
    """Create authentication and user data."""
    print("Creating authentication data...")

    # Create roles first
    print("Creating roles...")
    roles = {}
    for role_data in ROLES_DATA:
        role = Role(**role_data)
        db.add(role)
        await db.flush()
        roles[role_data["name"]] = role
        print(f"   - Created role '{role_data['name']}'")

    await db.commit()

    # Create companies
    print("Creating companies...")
    companies = []
    for company_data in COMPANIES_DATA:
        company = Company(**company_data)
        db.add(company)
        await db.flush()
        companies.append(company)
        print(f"   - Created company '{company_data['name']}'")

    await db.commit()

    # Create users
    print("Creating users...")
    users_data = get_users_data(companies)
    users = []
    super_admin_user = None

    for i, user_data in enumerate(users_data):
        user_role = user_data.pop("role")

        # Set created_by based on user type
        if user_role == "super_admin":
            user_data["created_by"] = None  # Super admin is self-created (system user)
        elif user_role == "candidate":
            user_data["created_by"] = None  # Candidates self-register
        else:
            # Other users (company_admin, recruiter, employer) are created by super admin
            if super_admin_user:
                user_data["created_by"] = super_admin_user.id
            else:
                user_data["created_by"] = None  # Fallback if super admin not created yet

        user = User(**user_data)
        db.add(user)
        await db.flush()
        users.append((user, user_role))

        # Store reference to super admin for other users
        if user_role == "super_admin":
            super_admin_user = user

        print(f"   - Created user '{user.email}' (created_by: {user_data.get('created_by', 'None')})")

    await db.commit()

    # Create user roles
    print("Creating user roles...")
    for user, role_name in users:
        user_role = UserRole(
            user_id=user.id,
            role_id=roles[role_name].id,
            scope=f"company_{user.company_id}" if role_name != "super_admin" else "global"
        )
        db.add(user_role)
        print(f"   - Assigned role '{role_name}' to user '{user.email}'")

    await db.commit()

    # Create user settings for all users
    print("Creating user settings...")
    user_settings_data = get_user_settings_data()
    for i, (user, _) in enumerate(users):
        settings_data = user_settings_data[i].copy()
        settings_data["user_id"] = user.id
        settings = UserSettings(**settings_data)
        db.add(settings)

    await db.commit()

    # Create company profiles for all companies
    print("Creating company profiles...")
    company_profiles_data = get_company_profiles_data()
    for i, company in enumerate(companies):
        profile_data = company_profiles_data[i].copy()
        profile_data["company_id"] = company.id
        profile_data["last_updated_by"] = users[0][0].id if i == 0 else users[min(i, len(users)-1)][0].id
        profile = CompanyProfile(**profile_data)
        db.add(profile)

    await db.commit()

    # Create user connections (admin users connected to super admin)
    print("Creating user connections...")
    user_connections_count = await create_user_connections(db, users, roles)

    return {
        "roles": len(roles),
        "companies": len(companies),
        "users": len(users),
        "user_roles": len(users),
        "user_settings": len(users),
        "company_profiles": len(companies),
        "user_connections": user_connections_count,
        "users_list": users,
        "companies_list": companies
    }
