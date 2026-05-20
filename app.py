
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import qrcode
import random
import os

st.set_page_config(page_title="럭셔리 쇼핑 운세", layout="wide")

FORTUNES = [
    {
        "message": "새로운 스타일 변화가 행운을 부르는 하루예요.",
        "detail": "작은 소비가 당신을 더 빛나게 만들어줄 거예요.",
        "shopping": "럭셔리 액세서리 & 주얼리",
        "brand": "DIOR · TAMBURINS · TIFFANY",
        "item": "골드 목걸이",
        "color": "핑크 베이지",
        "score": 88,
        "spot": "패션관 2F",
        "tip": "오늘은 나를 위한 작은 선물이 좋은 흐름을 만들어요 ✨",
        "bg": "#F9E7EA"
    },
    {
        "message": "안정적인 소비가 만족도를 높여주는 날이에요.",
        "detail": "집 안 분위기를 바꾸는 쇼핑이 좋은 에너지를 가져와요.",
        "shopping": "리빙 · 프리미엄 홈데코",
        "brand": "ZARA HOME · BALMUDA · TEKLA",
        "item": "무드 조명",
        "color": "크림 화이트",
        "score": 79,
        "spot": "리빙관 5F",
        "tip": "편안함을 위한 소비가 오늘의 포인트예요 🌿",
        "bg": "#EFE5D8"
    }
]

def get_font(size):
    font_candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "C:/Windows/Fonts/malgun.ttf"
    ]

    for path in font_candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()

def create_story(name, gender, birth, birth_time, result):
    width, height = 1080, 1920

    img = Image.new("RGB", (width, height), result["bg"])
    draw = ImageDraw.Draw(img)

    title_font = get_font(70)
    sub_font = get_font(38)
    small_font = get_font(28)

    draw.rounded_rectangle((50, 70, 1030, 1840), radius=40, fill="white")

    draw.text((120, 120), "✨ 오늘의 라이프스타일 운세 ✨", fill="#D87093", font=small_font)
    draw.text((120, 200), f"{name}님의 오늘 운세", fill="#222222", font=title_font)

    draw.rounded_rectangle((100, 360, 980, 720), radius=35, fill=result["bg"])

    draw.text((140, 430), result["message"], fill="#222222", font=sub_font)
    draw.text((140, 560), result["detail"], fill="#666666", font=small_font)

    draw.rounded_rectangle((100, 800, 460, 1080), radius=30, fill="#FFF4F7")
    draw.text((150, 860), "🎨 럭키 컬러", fill="#FF69B4", font=small_font)
    draw.text((150, 950), result["color"], fill="#222222", font=sub_font)

    draw.rounded_rectangle((620, 800, 980, 1080), radius=30, fill="#F7F1FF")
    draw.text((670, 860), "🛍 추천 아이템", fill="#8A2BE2", font=small_font)
    draw.text((670, 950), result["item"], fill="#222222", font=sub_font)

    draw.rounded_rectangle((100, 1160, 980, 1410), radius=30, fill="#FFF8F0")
    draw.text((140, 1220), "✨ 추천 쇼핑 테마", fill="#FF8C00", font=small_font)
    draw.text((140, 1290), result["shopping"], fill="#222222", font=sub_font)
    draw.text((140, 1360), result["brand"], fill="#666666", font=small_font)

    draw.rounded_rectangle((100, 1470, 980, 1600), radius=30, fill="#F5FFF5")
    draw.text((140, 1515), f"📍 추천 스팟 : {result['spot']}", fill="#228B22", font=sub_font)

    draw.text((120, 1670), f"오늘의 행운 점수 : {result['score']}점", fill="#222222", font=sub_font)

    draw.text((120, 1740), result["tip"], fill="#666666", font=small_font)

    qr = qrcode.make("https://event-download-page.com")
    qr = qr.resize((180, 180))
    img.paste(qr, (830, 1660))

    return img

st.markdown("""
<style>
.stApp{
background:linear-gradient(180deg,#FFF7F8,#FCECEF);
}
h1{
text-align:center;
color:#D87093;
}
.block-container{
padding-top:2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>💖 오늘의 쇼핑 운세</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1,1.2])

with col1:
    st.markdown("### 🔮 사주 정보 입력")

    name = st.text_input("이름")
    gender = st.radio("성별", ["여성", "남성"], horizontal=True)
    birth = st.text_input("생년월일", placeholder="1995.04.25")

    birth_time = st.selectbox(
        "태어난 시간",
        ["모름","00~02시","02~04시","04~06시","06~08시",
         "08~10시","10~12시","12~14시","14~16시",
         "16~18시","18~20시","20~22시","22~24시"]
    )

    btn = st.button("✨ 운세 결과 확인하기")

with col2:
    st.markdown("### 📱 결과 이미지 미리보기")
    st.info("인스타 스토리 업로드용 1080x1920 이미지로 생성됩니다.")

if btn and name:
    random.seed(sum(ord(c) for c in name))
    result = random.choice(FORTUNES)

    st.success(result["message"])

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("럭키 컬러", result["color"])
    c2.metric("추천 아이템", result["item"])
    c3.metric("행운 점수", f"{result['score']}점")
    c4.metric("추천 스팟", result["spot"])

    st.markdown(f"### 🛍 추천 쇼핑 테마 : {result['shopping']}")
    st.markdown(f"추천 브랜드 : **{result['brand']}**")

    img = create_story(name, gender, birth, birth_time, result)

    buf = BytesIO()
    img.save(buf, format="PNG")

    st.image(buf.getvalue(), use_container_width=True)

    st.download_button(
        "📥 인스타 스토리 이미지 다운로드",
        data=buf.getvalue(),
        file_name=f"{name}_fortune_story.png",
        mime="image/png"
    )
