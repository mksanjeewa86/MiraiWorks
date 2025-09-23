"""
Sample Application Data Seeds

Contains messages, interviews, and positions seed data.
This file creates sample data for testing application functionality.
"""

from datetime import datetime, timedelta
import hashlib
from app.models.message import Message
from app.models.interview import Interview
from app.models.position import Position
from app.utils.constants import MessageType, InterviewStatus


def get_messages_data(users):
    """Get sample messages data."""
    return [
        # テックコーポレーションとイノベートラボの採用相談
        {
            "sender_id": users[4][0].id,  # admin@techcorp.jp
            "recipient_id": users[5][0].id,  # recruiter@innovatelab.jp
            "type": MessageType.TEXT.value,
            "content": "お疲れ様です。新しいプロジェクトで優秀な開発者を探しています。候補者をご紹介いただけますでしょうか？",
        },
        {
            "sender_id": users[5][0].id,  # recruiter@innovatelab.jp
            "recipient_id": users[4][0].id,  # admin@techcorp.jp
            "type": MessageType.TEXT.value,
            "content": "もちろんです！喜んでサポートさせていただきます。どのような技術スキルをお求めでしょうか？",
        },
        {
            "sender_id": users[4][0].id,  # admin@techcorp.jp
            "recipient_id": users[5][0].id,  # recruiter@innovatelab.jp
            "type": MessageType.TEXT.value,
            "content": "ReactとNode.jsの経験を持つフルスタック開発者が必要です。3年以上の経験者を希望しています。",
        },

        # データドリブンとネクストジェンのパートナーシップ
        {
            "sender_id": users[6][0].id,  # hr@datadriven.jp
            "recipient_id": users[8][0].id,  # lead@nextgenrecruiting.jp
            "type": MessageType.TEXT.value,
            "content": "こんにちは！御社の採用サービスを拝見し、パートナーシップに興味があります。",
        },
        {
            "sender_id": users[8][0].id,  # lead@nextgenrecruiting.jp
            "recipient_id": users[6][0].id,  # hr@datadriven.jp
            "type": MessageType.TEXT.value,
            "content": "ご連絡いただきありがとうございます！弊社はデータサイエンスとアナリティクス分野の採用を専門としています。どちらのポジションをお探しでしょうか？",
        },

        # クラウドスケールチームの連携
        {
            "sender_id": users[7][0].id,  # manager@cloudscale.jp
            "recipient_id": users[5][0].id,  # recruiter@innovatelab.jp
            "type": MessageType.TEXT.value,
            "content": "協業への参加、ありがとうございます！採用活動を連携して進めましょう。",
        },
        {
            "sender_id": users[0][0].id,  # admin@miraiworks.com
            "recipient_id": users[7][0].id,  # manager@cloudscale.jp
            "type": MessageType.TEXT.value,
            "content": "MiraiWorksへようこそ！プラットフォームに関してご不明な点がございましたら、お気軽にお声かけください。",
        },
    ]


def get_interviews_data(users, companies):
    """Get sample interviews data."""
    base_time = datetime.now()

    return [
        {
            "candidate_id": users[4][0].id,  # Will use company user as mock candidate
            "recruiter_id": users[5][0].id,  # recruiter@innovatelab.jp
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
            "candidate_id": users[6][0].id,  # Will use company user as mock candidate
            "recruiter_id": users[8][0].id,  # lead@nextgenrecruiting.jp
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
            "candidate_id": users[7][0].id,  # Will use company user as mock candidate
            "recruiter_id": users[5][0].id,  # recruiter@innovatelab.jp
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


def create_slug(title: str, company_name: str) -> str:
    """Create position slug."""
    combined = f"{title}-{company_name}"
    hash_obj = hashlib.md5(combined.encode('utf-8'))
    return f"position-{hash_obj.hexdigest()[:12]}"


def get_positions_data(companies, users):
    """Get sample positions data."""
    base_time = datetime.now()

    # Base positions template - expanded for ~100 positions
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
        ("フロントエンド開発者", "technology", "full_time", "mid_level", ["React", "Vue.js", "HTML", "CSS", "TypeScript"], 5500000, 8000000),
        ("バックエンド開発者", "technology", "full_time", "senior_level", ["Node.js", "Java", "Python", "API Design"], 7000000, 10000000),
        ("DevOpsエンジニア", "technology", "full_time", "senior_level", ["Docker", "Kubernetes", "AWS", "CI/CD"], 7500000, 11000000),
        ("データサイエンティスト", "data", "full_time", "senior_level", ["Machine Learning", "Python", "R", "Statistics"], 8000000, 12000000),
        ("プロダクトマネージャー", "product", "full_time", "senior_level", ["Product Strategy", "Roadmap", "Analytics"], 7000000, 10000000),
        ("QAエンジニア", "technology", "full_time", "mid_level", ["Test Automation", "Selenium", "Quality Assurance"], 5000000, 7500000),
        ("UXデザイナー", "design", "full_time", "mid_level", ["User Research", "Prototyping", "Figma", "Design Thinking"], 5500000, 8000000),
        ("カスタマーサクセス", "support", "full_time", "mid_level", ["Customer Relations", "Onboarding", "Support"], 4500000, 6500000),
        ("人事担当", "hr", "full_time", "mid_level", ["Recruitment", "Employee Relations", "HR Policies"], 4000000, 6000000),
        ("経理・財務", "finance", "full_time", "mid_level", ["Accounting", "Financial Analysis", "Excel"], 4500000, 6500000),
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

    positions = []
    for i, (title, dept, job_type, exp_level, skills, min_sal, max_sal) in enumerate(base_positions * 5):  # Create variations
        if len(positions) >= 100:  # Create around 100 positions
            break

        company = companies[(i % 4) + 1]  # Rotate through companies 1-4 (skip MiraiWorks)
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
            "salary_min": min_sal,
            "salary_max": max_sal,
            "salary_currency": "JPY",
            "show_salary": True,
            "status": "published",
            "published_at": base_time - timedelta(days=(i % 10) + 1),
            "posted_by": users[(i % 4) + 4][0].id,  # Use company users as posters
        }
        positions.append(position)

    return positions


async def seed_sample_data(db, auth_result):
    """Create sample data."""
    print("Creating sample data...")

    users = auth_result["users_list"]
    companies = auth_result["companies_list"]

    # Create direct messages between users
    print("Creating direct messages...")
    messages_data = get_messages_data(users)
    for msg_data in messages_data:
        message = Message(**msg_data)
        db.add(message)

    await db.commit()
    print(f"   - Created {len(messages_data)} direct messages")

    # Create interviews
    print("Creating interviews...")
    interviews_data = get_interviews_data(users, companies)
    for interview_data in interviews_data:
        interview = Interview(**interview_data)
        db.add(interview)
        print(f"   - Created interview '{interview_data['title']}'")

    await db.commit()

    # Create positions
    print("Creating positions...")
    positions_data = get_positions_data(companies, users)
    created_positions = []
    for position_data in positions_data:
        # Create slug
        position_data["slug"] = create_slug(position_data["title"],
            next(c.name for c in companies if c.id == position_data["company_id"]))

        position = Position(**position_data)
        db.add(position)
        await db.flush()
        created_positions.append(position)

    await db.commit()
    print(f"   - Created {len(positions_data)} positions")

    return {
        "messages": len(messages_data),
        "interviews": len(interviews_data),
        "positions": len(positions_data)
    }