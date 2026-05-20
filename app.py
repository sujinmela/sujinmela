import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime
import io
import base64
import qrcode

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="오늘의 쇼핑 운세",
    page_icon="✨",
    layout="centered"
)

# -----------------------------------
# DATA
# -----------------------------------
FORTUNES = [
    "새로운 스타일 변화가 행운을 부르는 하루예요.",
    "감각적인 소비가 당신의 분위기를 더욱 빛내줄 거예요.",
    "오늘은 자신을 위한 작은 선물이 필요한 날이에요.",
    "새로운 브랜드에서 특별한 영감을 얻게 될 수 있어요.",
]

SHOP_THEMES = [
    "럭셔리 취향형",
    "트렌드 리더형",
    "감성 소비형",
    "미니멀 쇼퍼형",
]

LUCKY_ITEMS = [
    "향수", "주얼리", "가방", "커피", "디저트", "스니커즈"
]

LUCKY_COLORS = [
    ("Pink", "#ff6fae"),
    ("Gold", "#d4a437"),
    ("Mint", "#6bd3c0"),
    ("Lavender", "#9f8cff"),
]

TIPS = [
    "오늘은 작은 소비가 큰 만족으로 이어질 수 있어요.",
    "감각적인 액세서리가 오늘의 분위기를 완성해줄 거예요.",
    "새로운 공간에서 좋은 영감을 얻을 가능성이 높아요.",
]

# -----------------------------------
# STYLE
# -----------------------------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom, #fff7f8, #ffffff);
}

.main-title {
    text-align:center;
    font-size:52px;
    font-weight:800;
    color:#222;
    margin-top:10px;
}

.sub-title {
    text-align:center;
    color:#888;
    font-size:18px;
    margin-bottom:40px;
}

.stButton > button {
    width:100%;
    height:56px;
    border:none;
    border-radius:16px;
    background:linear-gradient(90deg,#ff8fb1,#ffb08f);
    color:white;
    font-size:18px;
    font-weight:700;
}

.result-card {
    background:white;
    padding:30px;
    border-radius:28px;
    box-shadow:0 8px 24px rgba(0,0,0,0.08);
    margin-top:30px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------
st.markdown('<div class="main-title">✨ 오늘의 쇼핑 운세 ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">백화점 고객 체험 이벤트</div>', unsafe_allow_html=True)

# -----------------------------------
# FORM
# -----------------------------------
with st.form("fortune_form"):
    name = st.text_input("이름")

    birth = st.date_input(
        "생년월일",
        min_value=datetime(1950,1,1),
        max_value=datetime.today()
    )

    submitted = st.form_submit_button("운세 확인하기")

# -----------------------------------
# IMAGE GENERATOR
# -----------------------------------
def make_result_image(name, fortune, theme, item, color_name, tip):

    width = 1080
    height = 1920

    img = Image.new("RGB", (width, height), "#fff7f8")
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 72)
        big_font = ImageFont.truetype("arial.ttf", 58)
        medium_font = ImageFont.truetype("arial.ttf", 42)
        small_font = ImageFont.truetype("arial.ttf", 32)
    except:
        title_font = ImageFont.load_default()
        big_font = ImageFont.load_default()
        medium_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Background card
    draw.rounded_rectangle(
        (60, 180, 1020, 1500),
        radius=40,
        fill="white"
    )

    # Title
    draw.text(
        (120, 90),
        "✨ 오늘의 쇼핑 운세 ✨",
        fill="#ff6fae",
        font=medium_font
    )

    # Name
    draw.text(
        (120, 240),
        f"{name}님의 오늘 운세",
        fill="#222222",
        font=title_font
    )

    # Fortune
    draw.text(
        (120, 420),
        fortune,
        fill="#333333",
        font=big_font
    )

    # Info sections
    y = 760

    infos = [
        ("🎨 럭키 컬러", color_name),
        ("🛍️ 추천 아이템", item),
        ("💎 소비 성향", theme),
        ("⭐ 오늘의 팁", tip),
    ]

    for title, value in infos:

        draw.rounded_rectangle(
            (100, y, 980, y + 150),
            radius=30,
            fill="#fff5f7"
        )

        draw.text(
            (140, y + 25),
            title,
            fill="#ff6fae",
            font=medium_font
        )

        draw.text(
            (140, y + 80),
            value,
            fill="#222222",
            font=small_font
        )

        y += 190

    # QR CODE
    qr = qrcode.make("https://your-event-download-page.com")
    qr = qr.resize((220, 220))

    img.paste(qr, (430, 1600))

    draw.text(
        (290, 1840),
        "QR을 찍고 이미지를 저장해보세요",
        fill="#888888",
        font=small_font
    )

    return img

# -----------------------------------
# RESULT
# -----------------------------------
if submitted:

    seed = int(birth.strftime("%Y%m%d")) + len(name)
    random.seed(seed)

    fortune = random.choice(FORTUNES)
    theme = random.choice(SHOP_THEMES)
    item = random.choice(LUCKY_ITEMS)
    color_name, color_code = random.choice(LUCKY_COLORS)
    tip = random.choice(TIPS)

    st.markdown(f"""
    <div class="result-card">
        <h1 style="font-size:42px;color:#222;">
            {name}님의 오늘 운세
        </h1>

        <p style="font-size:28px;font-weight:700;color:#444;line-height:1.6;">
            {fortune}
        </p>

        <hr>

        <h3>🎨 럭키 컬러 : {color_name}</h3>
        <h3>🛍️ 추천 아이템 : {item}</h3>
        <h3>💎 소비 성향 : {theme}</h3>
        <h3>⭐ 오늘의 팁 : {tip}</h3>
    </div>
    """, unsafe_allow_html=True)

    # Generate Image
    result_img = make_result_image(
        name,
        fortune,
        theme,
        item,
        color_name,
        tip
    )

    st.markdown("### 📸 인스타 스토리용 결과 이미지")

    st.image(result_img, use_container_width=True)

    # Download
    buf = io.BytesIO()
    result_img.save(buf, format="PNG")

    st.download_button(
        label="이미지 다운로드",
        data=buf.getvalue(),
        file_name="shopping_fortune.png",
        mime="image/png"
    )

    st.balloons()

# Footer
st.markdown("""
<div style="
text-align:center;
margin-top:40px;
color:#999;
font-size:13px;
">
※ 본 콘텐츠는 이벤트 체험용 라이프스타일 운세입니다.
</div>
""", unsafe_allow_html=True)
