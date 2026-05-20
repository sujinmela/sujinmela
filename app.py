# app.py
import streamlit as st
from datetime import datetime
import random

st.set_page_config(
    page_title="오늘의 라이프스타일 운세",
    page_icon="✨",
    layout="centered"
)

# -----------------------------
# Mock fortune data
# -----------------------------
FORTUNE_MESSAGES = [
    "새로운 스타일 변화가 행운을 부르는 하루예요.",
    "오늘은 작은 소비가 큰 만족으로 이어질 수 있어요.",
    "사람들과의 대화에서 좋은 기회가 생길 가능성이 높아요.",
    "감각적인 선택이 당신의 분위기를 더욱 빛내줄 거예요.",
    "오늘은 자신을 위한 작은 선물이 필요한 날이에요.",
]

LUCKY_COLORS = [
    "Gold", "Sky Blue", "Lavender", "Emerald", "Black", "Pink"
]

LUCKY_ITEMS = [
    "향수", "가방", "스니커즈", "디저트", "커피", "액세서리"
]

SHOPPING_TYPES = [
    "감성 소비형",
    "트렌드 리더형",
    "미니멀 쇼퍼형",
    "럭셔리 취향형",
    "플렉스형",
]

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
    <style>
    .main {
        background-color: #faf8f5;
    }

    .title {
        text-align:center;
        font-size:42px;
        font-weight:700;
        margin-top:10px;
        color:#222;
    }

    .subtitle {
        text-align:center;
        color:#666;
        margin-bottom:40px;
    }

    .fortune-card {
        padding:30px;
        border-radius:20px;
        background:white;
        box-shadow:0 4px 20px rgba(0,0,0,0.08);
        margin-top:20px;
    }

    .fortune-title {
        font-size:28px;
        font-weight:700;
        margin-bottom:20px;
    }

    .fortune-item {
        font-size:18px;
        margin-bottom:12px;
    }

    .footer {
        text-align:center;
        color:#999;
        margin-top:40px;
        font-size:13px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown(
    "<div class='title'>✨ 오늘의 라이프스타일 운세 ✨</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>백화점 체험 이벤트 · 쇼핑 운세 테스트</div>",
    unsafe_allow_html=True
)

# -----------------------------
# Input form
# -----------------------------
with st.form("fortune_form"):
    name = st.text_input("이름")
    birth = st.date_input(
        "생년월일",
        min_value=datetime(1950, 1, 1),
        max_value=datetime.today()
    )

    birth_time = st.selectbox(
        "출생 시간 (선택)",
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
# Generate result
# -----------------------------
if submitted:
    seed = int(birth.strftime("%Y%m%d")) + len(name)
    random.seed(seed)

    fortune = random.choice(FORTUNE_MESSAGES)
    color = random.choice(LUCKY_COLORS)
    item = random.choice(LUCKY_ITEMS)
    shopping_type = random.choice(SHOPPING_TYPES)

    st.markdown(
        f"""
        <div class="fortune-card">
            <div class="fortune-title">
                {name}님의 오늘 운세
            </div>

            <div class="fortune-item">
                💫 <b>오늘의 메시지</b><br>
                {fortune}
            </div>

            <div class="fortune-item">
                🎨 <b>럭키 컬러</b><br>
                {color}
            </div>

            <div class="fortune-item">
                🛍️ <b>추천 쇼핑 아이템</b><br>
                {item}
            </div>

            <div class="fortune-item">
                ✨ <b>소비 성향</b><br>
                {shopping_type}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.success("오늘의 운세가 생성되었어요!")

    st.balloons()

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    """
    <div class="footer">
    ※ 본 콘텐츠는 이벤트 체험용이며 재미 요소를 포함하고 있습니다.
    </div>
    """,
    unsafe_allow_html=True
)
