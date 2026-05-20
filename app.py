
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import random

st.set_page_config(page_title="오늘의 쇼핑 운세", layout="wide")

FORTUNE_DATA = [
    {
        "message": "새로운 스타일 변화가 행운을 부르는 하루예요.",
        "detail": "작은 소비가 큰 만족으로 이어질 수 있어요.",
        "shopping": "럭셔리 액세서리 & 주얼리",
        "brand": "DIOR · TAMBURINS · TORY BURCH",
        "lucky_color": "Pink Beige",
        "score": 87,
        "item": "골드 목걸이",
        "spot": "패션관 2F",
        "tip": "오늘은 나를 위한 작은 선물이 행운을 불러와요 ✨",
        "bg": "#F8D7DA"
    },
    {
        "message": "안정적인 선택이 만족도를 높여주는 날이에요.",
        "detail": "집 안 분위기를 바꾸는 소비가 좋은 흐름을 만들어요.",
        "shopping": "리빙 · 프리미엄 식품",
        "brand": "ZARA HOME · BALMUDA · TEKLA",
        "lucky_color": "Cream",
        "score": 78,
        "item": "무드 조명",
        "spot": "리빙관 5F",
        "tip": "편안함을 위한 소비가 오늘의 포인트예요 🌿",
        "bg": "#EFE2D0"
    }
]

def get_fortune(name):
    random.seed(sum(ord(c) for c in name))
    return random.choice(FORTUNE_DATA)

def make_story_image(name, gender, birth, birth_time, result):
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), result["bg"])
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 68)
        text_font = ImageFont.truetype("arial.ttf", 38)
        small_font = ImageFont.truetype("arial.ttf", 28)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.rounded_rectangle((50, 80, 1030, 1840), radius=45, fill="white")

    draw.text((120, 140), "✨ 오늘의 라이프스타일 운세 ✨", fill="#D87093", font=small_font)
    draw.text((120, 220), f"{name}님의 오늘 운세", fill="#222222", font=title_font)

    draw.rounded_rectangle((100, 380, 980, 760), radius=35, fill=result["bg"])

    draw.text((140, 450), result["message"], fill="#222222", font=text_font)
    draw.text((140, 580), result["detail"], fill="#666666", font=small_font)

    draw.rounded_rectangle((120, 850, 450, 1120), radius=30, fill="#FFF4F6")
    draw.text((170, 900), "🎨 럭키 컬러", fill="#FF69B4", font=small_font)
    draw.text((170, 980), result["lucky_color"], fill="#222222", font=text_font)

    draw.rounded_rectangle((620, 850, 950, 1120), radius=30, fill="#F7F0FF")
    draw.text((670, 900), "🛍 추천 아이템", fill="#8A2BE2", font=small_font)
    draw.text((670, 980), result["item"], fill="#222222", font=text_font)

    draw.rounded_rectangle((100, 1200, 980, 1450), radius=30, fill="#FFF8EE")
    draw.text((140, 1260), "✨ 추천 쇼핑 테마", fill="#FF8C00", font=small_font)
    draw.text((140, 1320), result["shopping"], fill="#222222", font=text_font)
    draw.text((140, 1390), result["brand"], fill="#666666", font=small_font)

    draw.rounded_rectangle((100, 1510, 980, 1660), radius=30, fill="#F6FFF5")
    draw.text((140, 1560), f"📍 추천 스팟 : {result['spot']}", fill="#228B22", font=text_font)

    draw.text((120, 1730), f"오늘의 운세 점수 : {result['score']}점", fill="#222222", font=text_font)

    qr = qrcode.make("https://event-download-page.com")
    qr = qr.resize((180, 180))
    img.paste(qr, (820, 1660))

    draw.text((120, 1790), result["tip"], fill="#555555", font=small_font)

    return img

st.markdown(
    '''
    <style>
    .stApp {
        background: linear-gradient(180deg,#FFF7F8,#FDF0F2);
    }

    .main-box {
        background:white;
        padding:40px;
        border-radius:30px;
        box-shadow:0 10px 30px rgba(0,0,0,0.08);
    }

    h1 {
        text-align:center;
        color:#D87093;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

st.markdown("<h1>💖 오늘의 쇼핑 운세</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("### 🔮 사주 정보 입력")

    name = st.text_input("이름")
    gender = st.radio("성별", ["여성", "남성"], horizontal=True)
    birth = st.text_input("생년월일", placeholder="1995.04.25")
    birth_time = st.selectbox(
        "태어난 시간",
        ["모름", "00~02시", "02~04시", "04~06시", "06~08시",
         "08~10시", "10~12시", "12~14시", "14~16시",
         "16~18시", "18~20시", "20~22시", "22~24시"]
    )

    generate = st.button("✨ 운세 결과 확인하기")

with col2:
    st.markdown("### 📱 인스타 스토리 결과 예시")
    st.image("https://images.unsplash.com/photo-1523381210434-271e8be1f52b?q=80&w=1200&auto=format&fit=crop")

if generate and name:
    result = get_fortune(name)

    st.markdown("---")
    st.markdown(f"## 💖 {name}님의 오늘 운세")
    st.success(result["message"])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("럭키 컬러", result["lucky_color"])
    c2.metric("추천 아이템", result["item"])
    c3.metric("행운 점수", f"{result['score']}점")
    c4.metric("추천 스팟", result["spot"])

    st.markdown(f"### 🛍 추천 쇼핑 테마 : {result['shopping']}")
    st.markdown(f"추천 브랜드 : **{result['brand']}**")

    story = make_story_image(name, gender, birth, birth_time, result)

    buf = BytesIO()
    story.save(buf, format="PNG")

    st.image(buf.getvalue(), use_container_width=True)

    st.download_button(
        "📥 인스타 스토리 이미지 다운로드",
        data=buf.getvalue(),
        file_name=f"{name}_fortune_story.png",
        mime="image/png"
    )
