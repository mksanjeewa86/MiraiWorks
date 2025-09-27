"""
Assessment and Exam System Seeds

Creates comprehensive exam data including:
- Aptitude tests (適性検査)
- Programming skill tests
- Personality assessments
- Demo/practice exams

This file was refactored from backend/scripts/seed_exam_data.py
"""

from datetime import datetime, timedelta

from app.models.exam import (
    Exam,
    ExamAssignment,
    ExamQuestion,
    ExamStatus,
    ExamType,
    QuestionType,
)


def get_aptitude_exam_data():
    """Get aptitude test exam data."""
    return {
        "title": "適性検査 - 総合能力評価",
        "description": "論理的思考力、数値解析能力、言語理解力を総合的に評価する適性検査です。新卒採用において基礎的な能力を測定します。",
        "exam_type": ExamType.APTITUDE,
        "status": ExamStatus.ACTIVE,
        "time_limit_minutes": 45,
        "max_attempts": 2,
        "passing_score": 70.0,
        "is_randomized": True,
        "allow_web_usage": False,
        "monitor_web_usage": True,
        "require_face_verification": True,
        "face_check_interval_minutes": 10,
        "show_results_immediately": False,
        "show_correct_answers": False,
        "show_score": True,
        "instructions": """
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
    }


def get_aptitude_questions_data():
    """Get aptitude test questions."""
    return [
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


def get_programming_exam_data():
    """Get programming skill test exam data."""
    return {
        "title": "プログラミングスキル評価テスト",
        "description": "JavaScript、Python、アルゴリズムに関する技術的な知識と問題解決能力を評価します。中級エンジニア向けの技術試験です。",
        "exam_type": ExamType.SKILL,
        "status": ExamStatus.ACTIVE,
        "time_limit_minutes": 60,
        "max_attempts": 1,
        "passing_score": 75.0,
        "is_randomized": False,
        "allow_web_usage": True,
        "monitor_web_usage": True,
        "require_face_verification": False,
        "show_results_immediately": True,
        "show_correct_answers": True,
        "show_score": True,
        "instructions": """
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
    }


def get_programming_questions_data():
    """Get programming skill test questions."""
    return [
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


def get_personality_exam_data():
    """Get personality assessment exam data."""
    return {
        "title": "性格・行動特性評価",
        "description": "職場での行動特性、チームワーク、ストレス耐性、コミュニケーション能力を評価する性格診断テストです。",
        "exam_type": ExamType.PERSONALITY,
        "status": ExamStatus.ACTIVE,
        "time_limit_minutes": 25,
        "max_attempts": 1,
        "passing_score": None,  # No passing score for personality tests
        "is_randomized": True,
        "allow_web_usage": True,
        "monitor_web_usage": False,
        "require_face_verification": False,
        "show_results_immediately": False,
        "show_correct_answers": False,
        "show_score": False,
        "instructions": """
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
    }


def get_personality_questions_data():
    """Get personality assessment questions."""
    return [
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


def get_demo_exam_data():
    """Get demo/practice exam data."""
    return {
        "title": "デモ試験 - システム体験用",
        "description": "初めての方向けのデモ試験です。様々な問題形式を体験でき、システムの使い方を理解することができます。",
        "exam_type": ExamType.CUSTOM,
        "status": ExamStatus.ACTIVE,
        "time_limit_minutes": 15,
        "max_attempts": 10,  # Allow multiple attempts for demo
        "passing_score": 60.0,
        "is_randomized": False,
        "allow_web_usage": True,
        "monitor_web_usage": True,
        "require_face_verification": False,
        "show_results_immediately": True,
        "show_correct_answers": True,
        "show_score": True,
        "instructions": """
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
    }


def get_demo_questions_data():
    """Get demo exam questions."""
    return [
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


async def seed_exam_data(db, auth_result):
    """Create comprehensive exam system seed data."""
    print("Creating exam system data...")

    users_list = auth_result["users_list"]
    companies_list = auth_result["companies_list"]

    # Get first company (skip MiraiWorks) and first admin user for created_by field
    company = companies_list[1]  # Use second company (テックコーポレーション)
    admin_user = users_list[0][0]  # Use admin@miraiworks.com

    exams_created = []

    # 1. Create Aptitude Exam
    print("   Creating aptitude exam...")
    aptitude_data = get_aptitude_exam_data()
    aptitude_data.update({
        "company_id": company.id,
        "created_by": admin_user.id
    })
    aptitude_exam = Exam(**aptitude_data)
    db.add(aptitude_exam)
    await db.flush()

    # Add aptitude questions
    for i, q_data in enumerate(get_aptitude_questions_data()):
        question = ExamQuestion(
            exam_id=aptitude_exam.id,
            order_index=i,
            **q_data
        )
        db.add(question)
    exams_created.append((aptitude_exam, len(get_aptitude_questions_data())))

    # 2. Create Programming Skill Exam
    print("   Creating programming skill exam...")
    programming_data = get_programming_exam_data()
    programming_data.update({
        "company_id": company.id,
        "created_by": admin_user.id
    })
    programming_exam = Exam(**programming_data)
    db.add(programming_exam)
    await db.flush()

    # Add programming questions
    for i, q_data in enumerate(get_programming_questions_data()):
        question = ExamQuestion(
            exam_id=programming_exam.id,
            order_index=i,
            **q_data
        )
        db.add(question)
    exams_created.append((programming_exam, len(get_programming_questions_data())))

    # 3. Create Personality Assessment
    print("   Creating personality assessment...")
    personality_data = get_personality_exam_data()
    personality_data.update({
        "company_id": company.id,
        "created_by": admin_user.id
    })
    personality_exam = Exam(**personality_data)
    db.add(personality_exam)
    await db.flush()

    # Add personality questions
    for i, q_data in enumerate(get_personality_questions_data()):
        question = ExamQuestion(
            exam_id=personality_exam.id,
            order_index=i,
            **q_data
        )
        db.add(question)
    exams_created.append((personality_exam, len(get_personality_questions_data())))

    # 4. Create Demo Exam
    print("   Creating demo exam...")
    demo_data = get_demo_exam_data()
    demo_data.update({
        "company_id": company.id,
        "created_by": admin_user.id
    })
    demo_exam = Exam(**demo_data)
    db.add(demo_exam)
    await db.flush()

    # Add demo questions
    for i, q_data in enumerate(get_demo_questions_data()):
        question = ExamQuestion(
            exam_id=demo_exam.id,
            order_index=i,
            **q_data
        )
        db.add(question)
    exams_created.append((demo_exam, len(get_demo_questions_data())))

    # 5. Create sample assignments for candidate users
    print("   Creating exam assignments...")
    candidates = [user for user, role_name in users_list if role_name == "candidate"]
    assignments_created = 0

    if candidates:
        base_time = datetime.now()
        for candidate in candidates[:3]:  # Assign to first 3 candidates
            # Assign aptitude test
            assignment1 = ExamAssignment(
                exam_id=aptitude_exam.id,
                candidate_id=candidate.id,
                assigned_by=admin_user.id,
                due_date=base_time + timedelta(days=7),
                is_active=True
            )
            db.add(assignment1)
            assignments_created += 1

            # Assign demo exam
            assignment2 = ExamAssignment(
                exam_id=demo_exam.id,
                candidate_id=candidate.id,
                assigned_by=admin_user.id,
                due_date=base_time + timedelta(days=30),
                is_active=True
            )
            db.add(assignment2)
            assignments_created += 1

    await db.commit()

    total_questions = sum(count for _, count in exams_created)
    print(f"   - Created {len(exams_created)} exams with {total_questions} total questions")
    print(f"   - Created {assignments_created} exam assignments")

    return {
        "exams": len(exams_created),
        "questions": total_questions,
        "assignments": assignments_created
    }