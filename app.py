import streamlit as st
from datetime import datetime
import random

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="오늘의 라이프스타일 운세",
    page_icon="✨",
    layout="centered"
)

# -----------------------------
# DATA
# -----------------------------
FORTUNE_MESSAGES = [
    "새로운 스타일 변화가 행운을 부르는 하루예요.",
    "오늘은 작은 소비가 큰 만족으로 이어질 수 있어요.",
    "사람들과의 대화에서 좋은 기회가 생길 가능성이 높아요.",
    "감각적인 선택이 당신의 분위기를 더욱 빛내줄 거예요.",
    "오늘은 자신을 위한 작은 선물이 필요한 날이에요.",
]

LUCKY_COLORS = [
    "Pink",
    "Gold",
    "Lavender",
    "Sky Blue",
    "Emerald",
    "Black"
]

LUCKY_ITEMS = [
    "액세서리",
    "향수",
    "가방",
    "스니커즈",
    "디저트",
    "커피"
]

SHOPPING_TYPES = [
    "럭셔리 취향형",
    "감성 소비형",
    "트렌드 리더형",
    "미니멀 쇼퍼형",
    "플렉스형"
]

TIPS = [
    "오늘은 자신을 위한 작은 선물을 준비해보세요.",
    "새로운 브랜드를 둘러보면 좋은 영감을 얻을 수 있어요.",
    "밝은 컬러 아이템이 오늘의 기운을 높여줄 거예요.",
    "감각적인 액세서리가 당신의 분위기를 완성해줄 거예요."
]

# -----------------------------
# STYLE
# -----------------------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom, #fffaf7, #ffffff);
}

/* Title */
.main-title {
    text-align: center;
    font-size: 46px;
    font-weight: 800;
    color: #222;
    margin-top: 10px;
    margin-bottom: 10px;
}

.sub-title {
    text-align: center;
    color: #888;
    font-size: 18px;
    margin-bottom: 40px;
}

/* Card */
.fortune-card {
    background: white;
    padding: 40px;
    border-radius: 28px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    border: 1px solid #f5e8ea;
    margin-top: 30px;
}

/* Result Title */
.fortune-title {
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 30px;
    color: #222;
}

/* Message Box */
.message-box {
    background: linear-gradient(135deg, #fff7fa, #fff3f1);
    padding: 28px;
    border-radius: 20px;
    margin-bottom: 25px;
}

.message-title {
    font-size: 16px;
    font-weight: 700;
    color: #ff6f91;
    margin-bottom: 12px;
}

.message-content {
    font-size: 28px;
    line-height: 1.6;
    font-weight: 700;
    color: #333;
}

/* Grid */
.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    margin-top: 20px;
}

/* Item Card */
.item-card {
    background: #fffafa;
    padding: 22px;
    border-radius: 20px;
    border: 1px solid #f7eaea;
}

.item-title {
    font-size: 15px;
    color: #ff7b9c;
    font-weight: 700;
    margin-bottom: 10px;
}

.item-value {
    font-size: 24px;
    font-weight: 800;
    color: #333;
    margin-bottom: 10px;
}

.item-desc {
    color: #777;
    font-size: 15px;
    line-height: 1.6;
}

/* Button */
.stButton > button {
    width: 100%;
    height: 56px;
    border-radius: 16px;
    border: none;
    background: linear-gradient(90deg, #ff8fb1, #ffb38a);
    color: white;
    font-size: 18px;
    font-weight: 700;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    opacity: 0.95;
}

/* Footer */
.footer {
    text-align: center;
    color: #999;
    margin-top: 40px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <div class="main-title">
        ✨ 오늘의 라이프스타일 운세 ✨
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="sub-title">
        백화점 고객 체험 이벤트
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# FORM
# -----------------------------
with st.form("fortune_form"):

    name = st.text_input("이름")

    birth = st.date_input(
        "생년월일",
        min_value=datetime(1950, 1, 1),
        max_value=datetime.today()
    )

    birth_time = st.selectbox(
        "출생 시간",
        [
            "모름",
            "00:00~01:59",
            "02:00~03:59",
            "04:00~05:59",
            "06:00~07:59",
            "08:00~09:59",
            "10:00~11:59",
            "12:00~13:59",
            "14:00~15:59",
            "16:00~17:59",
            "18:00~19:59",
            "20:00~21:59",
            "22:00~23:59",
        ]
    )

    submitted = st.form_submit_button("운세 확인하기")

# -----------------------------
# RESULT
# -----------------------------
if submitted:

    seed = int(birth.strftime("%Y%m%d")) + len(name)
    random.seed(seed)

    fortune = random.choice(FORTUNE_MESSAGES)
    color = random.choice(LUCKY_COLORS)
    item = random.choice(LUCKY_ITEMS)
    shopping_type = random.choice(SHOPPING_TYPES)
    tip = random.choice(TIPS)

    # 메인 카드
    st.markdown(f"""
    <div style="
        background:white;
        padding:35px;
        border-radius:24px;
        box-shadow:0 8px 24px rgba(0,0,0,0.08);
        margin-top:30px;
    ">
        <h1 style="
            font-size:38px;
            font-weight:800;
            color:#222;
        ">
            ✨ {name}님의 오늘 운세
        </h1>

        <div style="
            background:linear-gradient(135deg,#fff5f7,#fff0ec);
            padding:24px;
            border-radius:18px;
            margin-top:20px;
        ">
            <p style="
                color:#ff6f91;
                font-size:16px;
                font-weight:700;
            ">
                💫 오늘의 메시지
            </p>

            <p style="
                font-size:30px;
                font-weight:800;
                color:#333;
                line-height:1.6;
            ">
                "{fortune}"
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 카드 4개
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"""
🎨 럭키 컬러

# {color}

오늘 당신의 분위기를 더욱 빛내줄 컬러예요.
""")

    with col2:
        st.success(f"""
🛍️ 추천 쇼핑 아이템

# {item}

오늘의 쇼핑 운을 높여줄 아이템이에요.
""")

    col3, col4 = st.columns(2)

    with col3:
        st.warning(f"""
✨ 소비 성향

# {shopping_type}

지금의 감각과 취향을 보여주는 타입이에요.
""")

    with col4:
        st.error(f"""
⭐ 오늘의 한 줄 조언

# Lucky Tip

{tip}
""")

    st.success("오늘의 운세가 생성되었어요 ✨")
    st.balloons()
