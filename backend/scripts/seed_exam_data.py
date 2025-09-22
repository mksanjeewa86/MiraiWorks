#!/usr/bin/env python3
"""
Seed script to create sample exam data for demonstration purposes.
Run this script to populate the database with realistic exam examples.
"""

import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models.exam import (
    Exam, ExamQuestion, ExamAssignment, 
    ExamType, ExamStatus, QuestionType
)
from app.models.user import User
from app.models.company import Company
from app.utils.constants import UserRole

async def create_sample_exams():
    """Create sample exams with questions for demonstration."""
    
    async with get_db_session() as db:
        # Get a sample company (assuming one exists)
        company = await db.execute(
            "SELECT * FROM companies WHERE is_active = '1' AND is_deleted = false LIMIT 1"
        )
        company = company.first()
        
        if not company:
            print("No active company found. Please create a company first.")
            return
        
        company_id = company.id
        print(f"Using company: {company.name} (ID: {company_id})")
        
        # Get a sample admin user from the company
        admin_user = await db.execute(
            """
            SELECT u.* FROM users u 
            JOIN user_roles ur ON u.id = ur.user_id 
            JOIN roles r ON ur.role_id = r.id 
            WHERE u.company_id = :company_id 
            AND r.name IN ('company_admin', 'company_recruiter')
            AND u.is_active = true 
            LIMIT 1
            """,
            {"company_id": company_id}
        )
        admin_user = admin_user.first()
        
        if not admin_user:
            print("No admin user found for the company. Please create an admin user first.")
            return
        
        admin_user_id = admin_user.id
        print(f"Using admin user: {admin_user.email} (ID: {admin_user_id})")

        # Sample Exam 1: 適性検査 (Aptitude Test)
        aptitude_exam = Exam(
            title="適性検査 - 総合能力評価",
            description="論理的思考力、数値解析能力、言語理解力を総合的に評価する適性検査です。新卒採用において基礎的な能力を測定します。",
            exam_type=ExamType.APTITUDE,
            status=ExamStatus.ACTIVE,
            company_id=company_id,
            created_by=admin_user_id,
            time_limit_minutes=45,
            max_attempts=2,
            passing_score=70.0,
            is_randomized=True,
            allow_web_usage=False,
            monitor_web_usage=True,
            require_face_verification=True,
            face_check_interval_minutes=10,
            show_results_immediately=False,
            show_correct_answers=False,
            show_score=True,
            instructions="""
【適性検査について】

この検査は45分間で実施され、あなたの基礎的な能力を多角的に評価します。

【注意事項】
• 制限時間内にできるだけ多くの問題に回答してください
• 分からない問題は飛ばして、後で戻ることができます
• 電卓の使用は禁止されています
• 途中でブラウザを閉じたり、他のタブに移動しないでください
• 定期的に本人確認のため写真撮影が行われます

【評価項目】
• 論理的思考力
• 数値解析能力
• 言語理解力
• 問題解決能力

頑張ってください！
            """.strip()
        )
        
        db.add(aptitude_exam)
        await db.flush()
        
        # Aptitude exam questions
        aptitude_questions = [
            {
                "question_text": "次の数列の規則性を見つけて、?に入る数字を選んでください。\n\n2, 6, 18, 54, ?",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 2.0,
                "options": {"A": "108", "B": "162", "C": "216", "D": "270"},
                "correct_answers": ["B"],
                "explanation": "各項に3を掛けることで次の項が得られます。54 × 3 = 162"
            },
            {
                "question_text": "「すべての鳥は飛ぶことができる」という文が偽であることを示すためには、どのような例を示せばよいですか？",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 2.0,
                "options": {
                    "A": "空を飛んでいる鳥の例",
                    "B": "飛ばない鳥の例",
                    "C": "飛ぶ動物で鳥でないものの例",
                    "D": "鳥でない動物の例"
                },
                "correct_answers": ["B"],
                "explanation": "全称命題を偽にするには、反例を一つ示せば十分です。飛ばない鳥（ペンギンなど）の例を示せば、この命題は偽になります。"
            },
            {
                "question_text": "ある会社の売上が昨年比120%となりました。これは昨年と比べて何%の増加を意味しますか？",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 2.0,
                "options": {"A": "20%", "B": "120%", "C": "220%", "D": "1.2%"},
                "correct_answers": ["A"],
                "explanation": "120% = 100% + 20%なので、20%の増加を意味します。"
            },
            {
                "question_text": "次の文章の要旨として最も適切なものを選んでください。\n\n「AI技術の発展により、多くの業務が自動化される一方で、新たな職種や業務も生まれている。重要なのは技術の進歩に適応し、継続的に学習する姿勢を持つことである。」",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 2.0,
                "options": {
                    "A": "AI技術により全ての仕事がなくなる",
                    "B": "AI技術の発展に適応するための継続学習が重要",
                    "C": "新しい職種は技術者のみに限られる",
                    "D": "自動化により労働者は不要になる"
                },
                "correct_answers": ["B"],
                "explanation": "文章の主旨は、AI技術の発展による変化に適応するため、継続的な学習が重要であることです。"
            },
            {
                "question_text": "図形の面積に関する問題です。\n\n正方形の一辺が6cmの時、その正方形に内接する円の面積は何cm²ですか？（円周率πは3.14として計算）",
                "question_type": QuestionType.TEXT_INPUT,
                "points": 3.0,
                "max_length": 50,
                "explanation": "正方形の一辺が6cmなので、内接する円の直径は6cm、半径は3cmです。面積 = π × 3² = 3.14 × 9 = 28.26cm²"
            },
            {
                "question_text": "以下の状況について、あなたならどのように対応しますか？論理的に説明してください。\n\n「チームプロジェクトで意見が対立し、期限が迫っている状況で、リーダーとして決断を下す必要があります。」",
                "question_type": QuestionType.ESSAY,
                "points": 5.0,
                "min_length": 100,
                "max_length": 500,
                "explanation": "この問題では、問題解決能力、リーダーシップ、コミュニケーション能力を評価します。"
            },
            {
                "question_text": "次の推理において、論理的に正しいものはどれですか？",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "points": 3.0,
                "options": {
                    "A": "すべてのAはBである。CはBである。よってCはAである。",
                    "B": "すべてのAはBである。CはAである。よってCはBである。",
                    "C": "AはBである。BはCである。よってAはCである。",
                    "D": "いくつかのAはBである。CはAである。よってCはBである。"
                },
                "correct_answers": ["B", "C"],
                "explanation": "B: 三段論法の正しい形。C: 推移律の正しい適用。A、Dは論理的に誤りです。"
            },
            {
                "question_text": "効率的な学習方法として、最も重要だと思う要素はどれですか？",
                "question_type": QuestionType.RATING,
                "points": 1.0,
                "rating_scale": 5,
                "explanation": "学習に対する価値観や優先順位を評価します。"
            }
        ]
        
        for i, q_data in enumerate(aptitude_questions):
            question = ExamQuestion(
                exam_id=aptitude_exam.id,
                order_index=i,
                **q_data
            )
            db.add(question)

        # Sample Exam 2: Programming Skill Test
        skill_exam = Exam(
            title="プログラミングスキル評価テスト",
            description="JavaScript、Python、アルゴリズムに関する技術的な知識と問題解決能力を評価します。中級エンジニア向けの技術試験です。",
            exam_type=ExamType.SKILL,
            status=ExamStatus.ACTIVE,
            company_id=company_id,
            created_by=admin_user_id,
            time_limit_minutes=60,
            max_attempts=1,
            passing_score=75.0,
            is_randomized=False,
            allow_web_usage=True,
            monitor_web_usage=True,
            require_face_verification=False,
            show_results_immediately=True,
            show_correct_answers=True,
            show_score=True,
            instructions="""
【プログラミングスキル評価について】

この試験では、実際の開発現場で必要となる技術的な知識と問題解決能力を評価します。

【試験内容】
• JavaScript/TypeScript
• Python
• アルゴリズムとデータ構造
• システム設計の基礎
• コードレビュー

【注意事項】
• 制限時間は60分です
• 資料の参照は許可されていますが、他者との相談は禁止です
• コードを書く問題では、可読性も評価対象となります
• 分からない問題は部分点も考慮されるため、思考過程を記述してください

【評価基準】
• 技術的な正確性
• コードの可読性
• 問題解決のアプローチ
• 効率性の考慮

頑張ってください！
            """.strip()
        )
        
        db.add(skill_exam)
        await db.flush()
        
        # Programming skill questions
        skill_questions = [
            {
                "question_text": "次のJavaScriptコードの実行結果はどうなりますか？\n\n```javascript\nconsole.log(typeof null);\nconsole.log(typeof undefined);\nconsole.log(typeof []);\nconsole.log(typeof {});\n```",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 3.0,
                "options": {
                    "A": "null, undefined, array, object",
                    "B": "object, undefined, object, object",
                    "C": "null, undefined, object, object",
                    "D": "object, undefined, array, object"
                },
                "correct_answers": ["B"],
                "explanation": "JavaScriptでは、typeof null は 'object'、typeof [] も 'object' を返します。これは言語仕様の特徴です。"
            },
            {
                "question_text": "Pythonで以下のリスト内包表記と同じ結果を得るfor文を書いてください。\n\n```python\nresult = [x**2 for x in range(10) if x % 2 == 0]\n```",
                "question_type": QuestionType.TEXT_INPUT,
                "points": 4.0,
                "max_length": 200,
                "explanation": "正解例:\nresult = []\nfor x in range(10):\n    if x % 2 == 0:\n        result.append(x**2)"
            },
            {
                "question_text": "バブルソートアルゴリズムの時間計算量として正しいものはどれですか？",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 2.0,
                "options": {
                    "A": "O(n)",
                    "B": "O(n log n)",
                    "C": "O(n²)",
                    "D": "O(2^n)"
                },
                "correct_answers": ["C"],
                "explanation": "バブルソートは最悪の場合、すべての要素のペアを比較するため、時間計算量はO(n²)です。"
            },
            {
                "question_text": "RESTful APIの設計原則として適切なものを選んでください。",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "points": 3.0,
                "options": {
                    "A": "ステートレスであること",
                    "B": "HTTPメソッドを適切に使用すること",
                    "C": "URLにリソースを表現すること",
                    "D": "JSONのみを使用すること"
                },
                "correct_answers": ["A", "B", "C"],
                "explanation": "RESTの原則には、ステートレス性、適切なHTTPメソッドの使用、リソース指向のURL設計が含まれます。JSONは一般的ですが必須ではありません。"
            },
            {
                "question_text": "以下のシナリオに対して、適切なデータベース設計とAPIエンドポイントを提案してください。\n\n「ブログシステムで、ユーザーが記事を投稿し、他のユーザーがコメントできる機能」",
                "question_type": QuestionType.ESSAY,
                "points": 8.0,
                "min_length": 200,
                "max_length": 1000,
                "explanation": "データベース設計、REST API設計、リレーション設定などの技術的な理解度を評価します。"
            },
            {
                "question_text": "GitHubでのコード管理において、以下のうち適切なプラクティスはどれですか？",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "points": 2.0,
                "options": {
                    "A": "直接mainブランチにpushする",
                    "B": "機能ごとにブランチを作成する",
                    "C": "コミットメッセージは簡潔に書く",
                    "D": "プルリクエストでコードレビューを行う"
                },
                "correct_answers": ["B", "C", "D"],
                "explanation": "適切なGitワークフローには、機能ブランチの使用、明確なコミットメッセージ、コードレビューが含まれます。"
            }
        ]
        
        for i, q_data in enumerate(skill_questions):
            question = ExamQuestion(
                exam_id=skill_exam.id,
                order_index=i,
                **q_data
            )
            db.add(question)

        # Sample Exam 3: Personality Assessment
        personality_exam = Exam(
            title="性格・行動特性評価",
            description="職場での行動特性、チームワーク、ストレス耐性、コミュニケーション能力を評価する性格診断テストです。",
            exam_type=ExamType.PERSONALITY,
            status=ExamStatus.ACTIVE,
            company_id=company_id,
            created_by=admin_user_id,
            time_limit_minutes=25,
            max_attempts=1,
            passing_score=None,  # No passing score for personality tests
            is_randomized=True,
            allow_web_usage=True,
            monitor_web_usage=False,
            require_face_verification=False,
            show_results_immediately=False,
            show_correct_answers=False,
            show_score=False,
            instructions="""
【性格・行動特性評価について】

この評価では、あなたの職場での行動特性や価値観を理解することが目的です。
正解・不正解はありませんので、素直にお答えください。

【評価項目】
• コミュニケーションスタイル
• チームワーク志向
• ストレス対処法
• 意思決定スタイル
• 学習・成長への姿勢

【回答のコツ】
• 理想ではなく、実際の自分の行動に基づいて回答してください
• 深く考えすぎず、直感的に答えてください
• 全ての質問に回答してください

この評価結果は、あなたにとって最適な職場環境や役割を検討するために活用されます。
            """.strip()
        )
        
        db.add(personality_exam)
        await db.flush()
        
        # Personality assessment questions
        personality_questions = [
            {
                "question_text": "チームでプロジェクトを進める際、あなたはどのような役割を好みますか？",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 1.0,
                "options": {
                    "A": "リーダーとして全体をまとめる",
                    "B": "専門知識を活かしてサポートする",
                    "C": "アイデアを出して創造性を発揮する",
                    "D": "確実に作業を遂行する"
                },
                "correct_answers": ["A"],  # No actual correct answer for personality
                "tags": ["leadership", "teamwork"]
            },
            {
                "question_text": "新しい技術や知識を学ぶことについて、どの程度重要だと思いますか？",
                "question_type": QuestionType.RATING,
                "points": 1.0,
                "rating_scale": 5,
                "tags": ["learning", "growth_mindset"]
            },
            {
                "question_text": "ストレスを感じる状況での対処法として、あなたに当てはまるものを選んでください。",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "points": 1.0,
                "options": {
                    "A": "同僚に相談する",
                    "B": "一人で解決策を考える",
                    "C": "休憩を取ってリフレッシュする",
                    "D": "タスクを整理して優先順位をつける"
                },
                "correct_answers": ["A"],
                "tags": ["stress_management", "coping_strategies"]
            },
            {
                "question_text": "重要な意思決定をする際、あなたが最も重視するのは何ですか？",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 1.0,
                "options": {
                    "A": "データと論理的分析",
                    "B": "過去の経験と直感",
                    "C": "チームメンバーの意見",
                    "D": "リスクと利益のバランス"
                },
                "correct_answers": ["A"],
                "tags": ["decision_making", "analytical_thinking"]
            },
            {
                "question_text": "困難な課題に直面した時の、あなたの一般的な反応を教えてください。",
                "question_type": QuestionType.ESSAY,
                "points": 2.0,
                "min_length": 50,
                "max_length": 300,
                "tags": ["problem_solving", "resilience"]
            },
            {
                "question_text": "コミュニケーションにおいて、以下のうちあなたが得意とするものはどれですか？",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "points": 1.0,
                "options": {
                    "A": "プレゼンテーション",
                    "B": "1対1での対話",
                    "C": "書面でのコミュニケーション",
                    "D": "グループディスカッション"
                },
                "correct_answers": ["A"],
                "tags": ["communication", "presentation"]
            },
            {
                "question_text": "職場での人間関係について、どの程度重要だと思いますか？",
                "question_type": QuestionType.RATING,
                "points": 1.0,
                "rating_scale": 5,
                "tags": ["relationships", "workplace_culture"]
            },
            {
                "question_text": "変化に対するあなたの態度として最も近いものはどれですか？",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 1.0,
                "options": {
                    "A": "変化を歓迎し、積極的に適応する",
                    "B": "慎重に検討してから適応する",
                    "C": "必要に応じて適応する",
                    "D": "安定した環境を好む"
                },
                "correct_answers": ["A"],
                "tags": ["adaptability", "change_management"]
            },
            {
                "question_text": "フィードバックを受ける際のあなたの反応について教えてください。",
                "question_type": QuestionType.ESSAY,
                "points": 2.0,
                "min_length": 50,
                "max_length": 200,
                "tags": ["feedback", "growth_mindset"]
            },
            {
                "question_text": "仕事でのモチベーションの源泉として、最も重要なものはどれですか？",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 1.0,
                "options": {
                    "A": "達成感と成長実感",
                    "B": "認められることと評価",
                    "C": "安定した環境と待遇",
                    "D": "自由度と創造性"
                },
                "correct_answers": ["A"],
                "tags": ["motivation", "values"]
            }
        ]
        
        for i, q_data in enumerate(personality_questions):
            question = ExamQuestion(
                exam_id=personality_exam.id,
                order_index=i,
                **q_data
            )
            db.add(question)

        # Sample Exam 4: Demo/Practice Exam
        demo_exam = Exam(
            title="デモ試験 - システム体験用",
            description="初めての方向けのデモ試験です。様々な問題形式を体験でき、システムの使い方を理解することができます。",
            exam_type=ExamType.CUSTOM,
            status=ExamStatus.ACTIVE,
            company_id=company_id,
            created_by=admin_user_id,
            time_limit_minutes=15,
            max_attempts=10,  # Allow multiple attempts for demo
            passing_score=60.0,
            is_randomized=False,
            allow_web_usage=True,
            monitor_web_usage=True,
            require_face_verification=False,
            show_results_immediately=True,
            show_correct_answers=True,
            show_score=True,
            instructions="""
【デモ試験について】

このデモ試験では、実際の試験で使用される様々な問題形式を体験できます。

【体験できる機能】
• 選択問題（単一・複数選択）
• テキスト入力問題
• 評価スケール問題
• リアルタイムタイマー
• 自動保存機能

【注意事項】
• この試験の結果は評価には使用されません
• 何度でも受験可能です
• 操作に慣れるまで自由に試してください

システムの使い方を理解して、本番の試験に備えましょう！
            """.strip()
        )
        
        db.add(demo_exam)
        await db.flush()
        
        # Demo exam questions
        demo_questions = [
            {
                "question_text": "このシステムの使い方は理解できましたか？",
                "question_type": QuestionType.SINGLE_CHOICE,
                "points": 1.0,
                "options": {
                    "A": "はい、よく理解できました",
                    "B": "だいたい理解できました",
                    "C": "少し分からない部分があります",
                    "D": "よく分かりません"
                },
                "correct_answers": ["A"],
                "explanation": "このようにシステムが動作します。実際の試験でも同じインターフェースを使用します。"
            },
            {
                "question_text": "簡単な計算問題です。12 + 8 × 3 = ?",
                "question_type": QuestionType.TEXT_INPUT,
                "points": 2.0,
                "max_length": 10,
                "explanation": "正解は36です。8 × 3 = 24、24 + 12 = 36（掛け算を先に計算）"
            },
            {
                "question_text": "このデモ試験の満足度を5段階で評価してください。",
                "question_type": QuestionType.RATING,
                "points": 1.0,
                "rating_scale": 5,
                "explanation": "5段階評価の問題では、スライダーを使用して回答します。"
            },
            {
                "question_text": "以下のうち、日本の都道府県として正しいものを選んでください。",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "points": 2.0,
                "options": {
                    "A": "東京都",
                    "B": "大阪府",
                    "C": "愛知市",
                    "D": "北海道"
                },
                "correct_answers": ["A", "B", "D"],
                "explanation": "東京都、大阪府、北海道は都道府県ですが、愛知市は存在しません（正しくは愛知県）。"
            },
            {
                "question_text": "このシステムについてのご意見やコメントがあれば自由に記入してください。",
                "question_type": QuestionType.ESSAY,
                "points": 1.0,
                "min_length": 10,
                "max_length": 500,
                "explanation": "自由記述問題では、長文での回答が可能です。"
            }
        ]
        
        for i, q_data in enumerate(demo_questions):
            question = ExamQuestion(
                exam_id=demo_exam.id,
                order_index=i,
                **q_data
            )
            db.add(question)

        # Create some sample assignments (optional)
        # Get some candidate users
        candidates = await db.execute(
            """
            SELECT u.* FROM users u 
            JOIN user_roles ur ON u.id = ur.user_id 
            JOIN roles r ON ur.role_id = r.id 
            WHERE r.name = 'candidate'
            AND u.is_active = true 
            LIMIT 3
            """
        )
        candidates = candidates.fetchall()
        
        if candidates:
            print(f"Creating sample assignments for {len(candidates)} candidates...")
            
            for candidate in candidates:
                # Assign aptitude test
                assignment1 = ExamAssignment(
                    exam_id=aptitude_exam.id,
                    candidate_id=candidate.id,
                    assigned_by=admin_user_id,
                    due_date=datetime.utcnow() + timedelta(days=7),
                    is_active=True
                )
                db.add(assignment1)
                
                # Assign demo exam
                assignment2 = ExamAssignment(
                    exam_id=demo_exam.id,
                    candidate_id=candidate.id,
                    assigned_by=admin_user_id,
                    due_date=datetime.utcnow() + timedelta(days=30),
                    is_active=True
                )
                db.add(assignment2)

        await db.commit()
        print("\n✅ Sample exam data created successfully!")
        print(f"Created exams:")
        print(f"  1. {aptitude_exam.title} (ID: {aptitude_exam.id}) - {len(aptitude_questions)} questions")
        print(f"  2. {skill_exam.title} (ID: {skill_exam.id}) - {len(skill_questions)} questions")  
        print(f"  3. {personality_exam.title} (ID: {personality_exam.id}) - {len(personality_questions)} questions")
        print(f"  4. {demo_exam.title} (ID: {demo_exam.id}) - {len(demo_questions)} questions")
        
        if candidates:
            print(f"\nAssigned exams to {len(candidates)} candidates")

async def main():
    """Main function to run the seed script."""
    print("🌱 Seeding exam data...")
    try:
        await create_sample_exams()
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())