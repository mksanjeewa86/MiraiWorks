"""
MBTI Questions Seed Data

Contains 60 MBTI personality test questions (15 per dimension).
This file creates the questions needed for the MBTI functionality.
"""

from app.models.mbti_model import MBTIQuestion

# MBTI Questions Data (60 questions total: 15 per dimension)
MBTI_QUESTIONS_DATA = [
    # Extraversion/Introversion Questions (1-15)
    {
        "question_number": 1,
        "dimension": "E_I",
        "question_text_en": "At a party, do you:",
        "question_text_ja": "パーティーでは、あなたは：",
        "option_a_en": "Interact with many, including strangers",
        "option_a_ja": "知らない人を含む多くの人と交流する",
        "option_b_en": "Interact with a few, known to you",
        "option_b_ja": "知っている少数の人と交流する",
        "scoring_key": "A"  # A = E, B = I
    },
    {
        "question_number": 2,
        "dimension": "E_I",
        "question_text_en": "Are you more:",
        "question_text_ja": "あなたはどちらかというと：",
        "option_a_en": "Realistic than speculative",
        "option_a_ja": "推測的というより現実的",
        "option_b_en": "Speculative than realistic",
        "option_b_ja": "現実的というより推測的",
        "scoring_key": "B"
    },
    {
        "question_number": 3,
        "dimension": "E_I",
        "question_text_en": "Do you prefer to work:",
        "question_text_ja": "仕事をするときは：",
        "option_a_en": "In a team",
        "option_a_ja": "チームで",
        "option_b_en": "Alone",
        "option_b_ja": "一人で",
        "scoring_key": "A"
    },
    {
        "question_number": 4,
        "dimension": "E_I",
        "question_text_en": "In company do you:",
        "question_text_ja": "人といるときは：",
        "option_a_en": "Initiate conversation",
        "option_a_ja": "自分から会話を始める",
        "option_b_en": "Wait to be approached",
        "option_b_ja": "相手から話しかけられるのを待つ",
        "scoring_key": "A"
    },
    {
        "question_number": 5,
        "dimension": "E_I",
        "question_text_en": "Are you energized more by:",
        "question_text_ja": "どちらでより元気になりますか：",
        "option_a_en": "Going out with friends",
        "option_a_ja": "友達と外出する",
        "option_b_en": "Spending quiet time alone",
        "option_b_ja": "一人で静かに過ごす",
        "scoring_key": "A"
    },
    {
        "question_number": 6,
        "dimension": "E_I",
        "question_text_en": "Do you tend to:",
        "question_text_ja": "あなたは普段：",
        "option_a_en": "Think out loud",
        "option_a_ja": "考えていることを声に出す",
        "option_b_en": "Think quietly to yourself",
        "option_b_ja": "静かに自分で考える",
        "scoring_key": "A"
    },
    {
        "question_number": 7,
        "dimension": "E_I",
        "question_text_en": "In social situations, do you:",
        "question_text_ja": "社交的な場面では：",
        "option_a_en": "Rarely feel uncomfortable",
        "option_a_ja": "不快に感じることはめったにない",
        "option_b_en": "Often feel uncomfortable",
        "option_b_ja": "よく不快に感じる",
        "scoring_key": "A"
    },
    {
        "question_number": 8,
        "dimension": "E_I",
        "question_text_en": "Do you prefer:",
        "question_text_ja": "どちらを好みますか：",
        "option_a_en": "Many friends with brief contact",
        "option_a_ja": "多くの友人と短い付き合い",
        "option_b_en": "A few friends with longer contact",
        "option_b_ja": "少数の友人と長い付き合い",
        "scoring_key": "A"
    },
    {
        "question_number": 9,
        "dimension": "E_I",
        "question_text_en": "When making decisions, do you:",
        "question_text_ja": "決定を下すときは：",
        "option_a_en": "Seek advice from others",
        "option_a_ja": "他の人にアドバイスを求める",
        "option_b_en": "Rely on your own judgment",
        "option_b_ja": "自分の判断に頼る",
        "scoring_key": "A"
    },
    {
        "question_number": 10,
        "dimension": "E_I",
        "question_text_en": "Do you find it:",
        "question_text_ja": "あなたにとって：",
        "option_a_en": "Easy to start conversations with strangers",
        "option_a_ja": "知らない人と会話を始めるのは簡単",
        "option_b_en": "Difficult to start conversations with strangers",
        "option_b_ja": "知らない人と会話を始めるのは難しい",
        "scoring_key": "A"
    },
    {
        "question_number": 11,
        "dimension": "E_I",
        "question_text_en": "Do you prefer:",
        "question_text_ja": "どちらを好みますか：",
        "option_a_en": "Being the center of attention",
        "option_a_ja": "注目の中心にいること",
        "option_b_en": "Staying in the background",
        "option_b_ja": "背景に留まること",
        "scoring_key": "A"
    },
    {
        "question_number": 12,
        "dimension": "E_I",
        "question_text_en": "Are your thoughts:",
        "question_text_ja": "あなたの考えは：",
        "option_a_en": "Easily shared with others",
        "option_a_ja": "他の人と簡単に共有できる",
        "option_b_en": "Kept mostly to yourself",
        "option_b_ja": "ほとんど自分の中に留める",
        "scoring_key": "A"
    },
    {
        "question_number": 13,
        "dimension": "E_I",
        "question_text_en": "Do you recharge by:",
        "question_text_ja": "充電するには：",
        "option_a_en": "Going out",
        "option_a_ja": "外出する",
        "option_b_en": "Having alone time",
        "option_b_ja": "一人の時間を持つ",
        "scoring_key": "A"
    },
    {
        "question_number": 14,
        "dimension": "E_I",
        "question_text_en": "In conversations, do you:",
        "question_text_ja": "会話では：",
        "option_a_en": "Do most of the talking",
        "option_a_ja": "ほとんど自分が話す",
        "option_b_en": "Do most of the listening",
        "option_b_ja": "ほとんど聞き役",
        "scoring_key": "A"
    },
    {
        "question_number": 15,
        "dimension": "E_I",
        "question_text_en": "Are you more comfortable:",
        "question_text_ja": "どちらがより快適ですか：",
        "option_a_en": "Being busy and active",
        "option_a_ja": "忙しく活動的であること",
        "option_b_en": "Having plenty of time for reflection",
        "option_b_ja": "熟考する時間がたくさんあること",
        "scoring_key": "A"
    },

    # Sensing/Intuition Questions (16-30)
    {
        "question_number": 16,
        "dimension": "S_N",
        "question_text_en": "Are you more attracted to:",
        "question_text_ja": "どちらに惹かれますか：",
        "option_a_en": "Sensible people",
        "option_a_ja": "分別のある人",
        "option_b_en": "Imaginative people",
        "option_b_ja": "想像力豊かな人",
        "scoring_key": "A"  # A = S, B = N
    },
    {
        "question_number": 17,
        "dimension": "S_N",
        "question_text_en": "Are you more interested in:",
        "question_text_ja": "どちらに興味がありますか：",
        "option_a_en": "What is actual",
        "option_a_ja": "実際にあるもの",
        "option_b_en": "What is possible",
        "option_b_ja": "可能性のあるもの",
        "scoring_key": "A"
    },
    {
        "question_number": 18,
        "dimension": "S_N",
        "question_text_en": "Do you prefer:",
        "question_text_ja": "どちらを好みますか：",
        "option_a_en": "Facts and details",
        "option_a_ja": "事実と詳細",
        "option_b_en": "Ideas and concepts",
        "option_b_ja": "アイデアと概念",
        "scoring_key": "A"
    },
    {
        "question_number": 19,
        "dimension": "S_N",
        "question_text_en": "Are you more:",
        "question_text_ja": "あなたはどちらかというと：",
        "option_a_en": "Practical",
        "option_a_ja": "実用的",
        "option_b_en": "Innovative",
        "option_b_ja": "革新的",
        "scoring_key": "A"
    },
    {
        "question_number": 20,
        "dimension": "S_N",
        "question_text_en": "Do you trust:",
        "question_text_ja": "どちらを信頼しますか：",
        "option_a_en": "Experience",
        "option_a_ja": "経験",
        "option_b_en": "Hunches",
        "option_b_ja": "直感",
        "scoring_key": "A"
    },
    {
        "question_number": 21,
        "dimension": "S_N",
        "question_text_en": "Are you more drawn to:",
        "question_text_ja": "どちらに引かれますか：",
        "option_a_en": "Fundamentals",
        "option_a_ja": "基本的なこと",
        "option_b_en": "Overtones",
        "option_b_ja": "含みのあること",
        "scoring_key": "A"
    },
    {
        "question_number": 22,
        "dimension": "S_N",
        "question_text_en": "Do you prefer to work with:",
        "question_text_ja": "どちらで働くのを好みますか：",
        "option_a_en": "Concrete facts",
        "option_a_ja": "具体的な事実",
        "option_b_en": "Abstract theories",
        "option_b_ja": "抽象的な理論",
        "scoring_key": "A"
    },
    {
        "question_number": 23,
        "dimension": "S_N",
        "question_text_en": "Are you better at:",
        "question_text_ja": "どちらが得意ですか：",
        "option_a_en": "Remembering details",
        "option_a_ja": "詳細を覚えること",
        "option_b_en": "Seeing the big picture",
        "option_b_ja": "全体像を見ること",
        "scoring_key": "A"
    },
    {
        "question_number": 24,
        "dimension": "S_N",
        "question_text_en": "Do you prefer:",
        "question_text_ja": "どちらを好みますか：",
        "option_a_en": "Traditional methods",
        "option_a_ja": "伝統的な方法",
        "option_b_en": "New approaches",
        "option_b_ja": "新しいアプローチ",
        "scoring_key": "A"
    },
    {
        "question_number": 25,
        "dimension": "S_N",
        "question_text_en": "Are you more:",
        "question_text_ja": "あなたはどちらかというと：",
        "option_a_en": "Observant",
        "option_a_ja": "観察力がある",
        "option_b_en": "Introspective",
        "option_b_ja": "内省的",
        "scoring_key": "A"
    },
    {
        "question_number": 26,
        "dimension": "S_N",
        "question_text_en": "Do you value:",
        "question_text_ja": "どちらを重視しますか：",
        "option_a_en": "Common sense",
        "option_a_ja": "常識",
        "option_b_en": "Imagination",
        "option_b_ja": "想像力",
        "scoring_key": "A"
    },
    {
        "question_number": 27,
        "dimension": "S_N",
        "question_text_en": "Are you more interested in:",
        "question_text_ja": "どちらに興味がありますか：",
        "option_a_en": "Production and distribution",
        "option_a_ja": "生産と流通",
        "option_b_en": "Design and research",
        "option_b_ja": "デザインと研究",
        "scoring_key": "A"
    },
    {
        "question_number": 28,
        "dimension": "S_N",
        "question_text_en": "Do you prefer stories that are:",
        "question_text_ja": "どんな物語を好みますか：",
        "option_a_en": "Action-packed and straightforward",
        "option_a_ja": "アクション満載で分かりやすい",
        "option_b_en": "Complex and symbolic",
        "option_b_ja": "複雑で象徴的",
        "scoring_key": "A"
    },
    {
        "question_number": 29,
        "dimension": "S_N",
        "question_text_en": "Are you better at:",
        "question_text_ja": "どちらが得意ですか：",
        "option_a_en": "Using established skills",
        "option_a_ja": "確立されたスキルを使うこと",
        "option_b_en": "Coming up with new ideas",
        "option_b_ja": "新しいアイデアを思いつくこと",
        "scoring_key": "A"
    },
    {
        "question_number": 30,
        "dimension": "S_N",
        "question_text_en": "Do you focus more on:",
        "question_text_ja": "どちらに焦点を当てますか：",
        "option_a_en": "The present",
        "option_a_ja": "現在",
        "option_b_en": "The future",
        "option_b_ja": "未来",
        "scoring_key": "A"
    },

    # Thinking/Feeling Questions (31-45)
    {
        "question_number": 31,
        "dimension": "T_F",
        "question_text_en": "Is it worse to be:",
        "question_text_ja": "どちらがより悪いですか：",
        "option_a_en": "Unjust",
        "option_a_ja": "不公平であること",
        "option_b_en": "Merciless",
        "option_b_ja": "無慈悲であること",
        "scoring_key": "B"  # A = T, B = F
    },
    {
        "question_number": 32,
        "dimension": "T_F",
        "question_text_en": "Are you more:",
        "question_text_ja": "あなたはどちらかというと：",
        "option_a_en": "Logical",
        "option_a_ja": "論理的",
        "option_b_en": "Empathetic",
        "option_b_ja": "共感的",
        "scoring_key": "A"
    },
    {
        "question_number": 33,
        "dimension": "T_F",
        "question_text_en": "Do you make decisions based on:",
        "question_text_ja": "決定を下す基準は：",
        "option_a_en": "Logic and facts",
        "option_a_ja": "論理と事実",
        "option_b_en": "Personal values",
        "option_b_ja": "個人的な価値観",
        "scoring_key": "A"
    },
    {
        "question_number": 34,
        "dimension": "T_F",
        "question_text_en": "Are you more comfortable with:",
        "question_text_ja": "どちらがより快適ですか：",
        "option_a_en": "Objective analysis",
        "option_a_ja": "客観的な分析",
        "option_b_en": "Subjective evaluation",
        "option_b_ja": "主観的な評価",
        "scoring_key": "A"
    },
    {
        "question_number": 35,
        "dimension": "T_F",
        "question_text_en": "Do you prefer to be:",
        "question_text_ja": "どちらになりたいですか：",
        "option_a_en": "Fair-minded",
        "option_a_ja": "公正な",
        "option_b_en": "Sympathetic",
        "option_b_ja": "思いやりのある",
        "scoring_key": "A"
    },
    {
        "question_number": 36,
        "dimension": "T_F",
        "question_text_en": "In arguments, are you more likely to:",
        "question_text_ja": "議論では、どちらの可能性が高いですか：",
        "option_a_en": "Stick to the facts",
        "option_a_ja": "事実にこだわる",
        "option_b_en": "Appeal to emotions",
        "option_b_ja": "感情に訴える",
        "scoring_key": "A"
    },
    {
        "question_number": 37,
        "dimension": "T_F",
        "question_text_en": "Are you governed more by:",
        "question_text_ja": "どちらに支配されていますか：",
        "option_a_en": "Your head",
        "option_a_ja": "頭（理性）",
        "option_b_en": "Your heart",
        "option_b_ja": "心（感情）",
        "scoring_key": "A"
    },
    {
        "question_number": 38,
        "dimension": "T_F",
        "question_text_en": "Do you value more:",
        "question_text_ja": "どちらをより重視しますか：",
        "option_a_en": "Competence",
        "option_a_ja": "能力",
        "option_b_en": "Compassion",
        "option_b_ja": "思いやり",
        "scoring_key": "A"
    },
    {
        "question_number": 39,
        "dimension": "T_F",
        "question_text_en": "Are you drawn more to:",
        "question_text_ja": "どちらに引かれますか：",
        "option_a_en": "Convincing reasoning",
        "option_a_ja": "説得力のある理由付け",
        "option_b_en": "Touching stories",
        "option_b_ja": "感動的な物語",
        "scoring_key": "A"
    },
    {
        "question_number": 40,
        "dimension": "T_F",
        "question_text_en": "Do you prefer:",
        "question_text_ja": "どちらを好みますか：",
        "option_a_en": "To be right",
        "option_a_ja": "正しいこと",
        "option_b_en": "To be liked",
        "option_b_ja": "好かれること",
        "scoring_key": "A"
    },
    {
        "question_number": 41,
        "dimension": "T_F",
        "question_text_en": "When giving feedback, are you more:",
        "question_text_ja": "フィードバックを与えるとき：",
        "option_a_en": "Frank and direct",
        "option_a_ja": "率直で直接的",
        "option_b_en": "Gentle and tactful",
        "option_b_ja": "優しく機転が利く",
        "scoring_key": "A"
    },
    {
        "question_number": 42,
        "dimension": "T_F",
        "question_text_en": "Are you more impressed by:",
        "question_text_ja": "どちらに感銘を受けますか：",
        "option_a_en": "Strong arguments",
        "option_a_ja": "強い論理",
        "option_b_en": "Strong emotions",
        "option_b_ja": "強い感情",
        "scoring_key": "A"
    },
    {
        "question_number": 43,
        "dimension": "T_F",
        "question_text_en": "Do you believe:",
        "question_text_ja": "どちらを信じますか：",
        "option_a_en": "The truth is more important than tact",
        "option_a_ja": "機転より真実が重要",
        "option_b_en": "Tact is more important than truth",
        "option_b_ja": "真実より機転が重要",
        "scoring_key": "A"
    },
    {
        "question_number": 44,
        "dimension": "T_F",
        "question_text_en": "Are you better at:",
        "question_text_ja": "どちらが得意ですか：",
        "option_a_en": "Analyzing problems",
        "option_a_ja": "問題を分析すること",
        "option_b_en": "Understanding people",
        "option_b_ja": "人を理解すること",
        "scoring_key": "A"
    },
    {
        "question_number": 45,
        "dimension": "T_F",
        "question_text_en": "Would you rather be seen as:",
        "question_text_ja": "どちらとして見られたいですか：",
        "option_a_en": "Reasonable",
        "option_a_ja": "理性的",
        "option_b_en": "Compassionate",
        "option_b_ja": "思いやりのある",
        "scoring_key": "A"
    },

    # Judging/Perceiving Questions (46-60)
    {
        "question_number": 46,
        "dimension": "J_P",
        "question_text_en": "Do you prefer things to be:",
        "question_text_ja": "物事はどちらを好みますか：",
        "option_a_en": "Scheduled",
        "option_a_ja": "予定通り",
        "option_b_en": "Unplanned",
        "option_b_ja": "計画なし",
        "scoring_key": "A"  # A = J, B = P
    },
    {
        "question_number": 47,
        "dimension": "J_P",
        "question_text_en": "Are you more:",
        "question_text_ja": "あなたはどちらかというと：",
        "option_a_en": "Punctual",
        "option_a_ja": "時間に正確",
        "option_b_en": "Leisurely",
        "option_b_ja": "のんびり",
        "scoring_key": "A"
    },
    {
        "question_number": 48,
        "dimension": "J_P",
        "question_text_en": "Do you prefer:",
        "question_text_ja": "どちらを好みますか：",
        "option_a_en": "Definite plans",
        "option_a_ja": "明確な計画",
        "option_b_en": "Flexible options",
        "option_b_ja": "柔軟な選択肢",
        "scoring_key": "A"
    },
    {
        "question_number": 49,
        "dimension": "J_P",
        "question_text_en": "Are you more comfortable with:",
        "question_text_ja": "どちらがより快適ですか：",
        "option_a_en": "Closure",
        "option_a_ja": "完結",
        "option_b_en": "Open options",
        "option_b_ja": "開かれた選択肢",
        "scoring_key": "A"
    },
    {
        "question_number": 50,
        "dimension": "J_P",
        "question_text_en": "Do you like to:",
        "question_text_ja": "どちらが好きですか：",
        "option_a_en": "Get things decided",
        "option_a_ja": "物事を決定する",
        "option_b_en": "Keep options open",
        "option_b_ja": "選択肢を開いておく",
        "scoring_key": "A"
    },
    {
        "question_number": 51,
        "dimension": "J_P",
        "question_text_en": "Are you more:",
        "question_text_ja": "あなたはどちらかというと：",
        "option_a_en": "Serious and determined",
        "option_a_ja": "真面目で決然とした",
        "option_b_en": "Easy-going",
        "option_b_ja": "気楽な",
        "scoring_key": "A"
    },
    {
        "question_number": 52,
        "dimension": "J_P",
        "question_text_en": "Do deadlines:",
        "question_text_ja": "締め切りは：",
        "option_a_en": "Help you focus",
        "option_a_ja": "集中するのに役立つ",
        "option_b_en": "Feel restrictive",
        "option_b_ja": "制限的に感じる",
        "scoring_key": "A"
    },
    {
        "question_number": 53,
        "dimension": "J_P",
        "question_text_en": "Do you prefer your life to be:",
        "question_text_ja": "人生はどちらを好みますか：",
        "option_a_en": "Structured",
        "option_a_ja": "構造化された",
        "option_b_en": "Spontaneous",
        "option_b_ja": "自発的な",
        "scoring_key": "A"
    },
    {
        "question_number": 54,
        "dimension": "J_P",
        "question_text_en": "Do you work better:",
        "question_text_ja": "どちらでより良く働けますか：",
        "option_a_en": "With a clear plan",
        "option_a_ja": "明確な計画がある",
        "option_b_en": "Under pressure",
        "option_b_ja": "プレッシャーの下で",
        "scoring_key": "A"
    },
    {
        "question_number": 55,
        "dimension": "J_P",
        "question_text_en": "Are you more satisfied when:",
        "question_text_ja": "どちらでより満足しますか：",
        "option_a_en": "A job is completed",
        "option_a_ja": "仕事が完了した時",
        "option_b_en": "A job is started",
        "option_b_ja": "仕事を始めた時",
        "scoring_key": "A"
    },
    {
        "question_number": 56,
        "dimension": "J_P",
        "question_text_en": "Do you prefer:",
        "question_text_ja": "どちらを好みますか：",
        "option_a_en": "Making lists",
        "option_a_ja": "リストを作る",
        "option_b_en": "Going with the flow",
        "option_b_ja": "流れに任せる",
        "scoring_key": "A"
    },
    {
        "question_number": 57,
        "dimension": "J_P",
        "question_text_en": "Are you more comfortable:",
        "question_text_ja": "どちらがより快適ですか：",
        "option_a_en": "After making a decision",
        "option_a_ja": "決定を下した後",
        "option_b_en": "Before making a decision",
        "option_b_ja": "決定を下す前",
        "scoring_key": "A"
    },
    {
        "question_number": 58,
        "dimension": "J_P",
        "question_text_en": "Do you prefer to:",
        "question_text_ja": "どちらを好みますか：",
        "option_a_en": "Settle things",
        "option_a_ja": "物事を解決する",
        "option_b_en": "Keep exploring possibilities",
        "option_b_ja": "可能性を探求し続ける",
        "scoring_key": "A"
    },
    {
        "question_number": 59,
        "dimension": "J_P",
        "question_text_en": "Is your desk usually:",
        "question_text_ja": "あなたのデスクは通常：",
        "option_a_en": "Neat and organized",
        "option_a_ja": "整理整頓されている",
        "option_b_en": "Cluttered",
        "option_b_ja": "散らかっている",
        "scoring_key": "A"
    },
    {
        "question_number": 60,
        "dimension": "J_P",
        "question_text_en": "Are you more likely to:",
        "question_text_ja": "どちらの可能性が高いですか：",
        "option_a_en": "Plan your vacations",
        "option_a_ja": "休暇を計画する",
        "option_b_en": "Be spontaneous on vacations",
        "option_b_ja": "休暇で自発的に行動する",
        "scoring_key": "A"
    }
]


def transform_mbti_question(q_data):
    """Transform seed data to match MBTIQuestion model structure."""
    # Map scoring_key to option traits
    if q_data["scoring_key"] == "A":
        # A is the first trait of the dimension
        option_a_trait = q_data["dimension"].split("_")[0]
        option_b_trait = q_data["dimension"].split("_")[1]
        direction = "+"
    else:  # scoring_key == "B"
        # B is the first trait, so A is second trait
        option_a_trait = q_data["dimension"].split("_")[1]
        option_b_trait = q_data["dimension"].split("_")[0]
        direction = "-"

    return {
        "question_number": q_data["question_number"],
        "dimension": q_data["dimension"],
        "direction": direction,
        "question_text_en": q_data["question_text_en"],
        "question_text_ja": q_data["question_text_ja"],
        "option_a_en": q_data["option_a_en"],
        "option_a_ja": q_data["option_a_ja"],
        "option_b_en": q_data["option_b_en"],
        "option_b_ja": q_data["option_b_ja"],
        "option_a_trait": option_a_trait,
        "option_b_trait": option_b_trait,
        "version": "1.0",
        "is_active": True
    }


async def seed_mbti_questions(db):
    """Create MBTI questions."""
    print("Creating MBTI questions...")

    for q_data in MBTI_QUESTIONS_DATA:
        transformed_data = transform_mbti_question(q_data)
        question = MBTIQuestion(**transformed_data)
        db.add(question)

    await db.commit()
    print(f"   - Created {len(MBTI_QUESTIONS_DATA)} MBTI questions")
    return len(MBTI_QUESTIONS_DATA)
