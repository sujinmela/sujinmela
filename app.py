
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import qrcode
import random
import os
import base64

st.set_page_config(page_title="백화점 오늘의 운세", layout="wide")

FORTUNES = [
    {
        "title":"새로운 스타일 변화가 행운을 부르는 하루예요.",
        "detail":"작은 소비가 당신을 더 빛나게 만들어줄 거예요.",
        "shopping":"럭셔리 액세서리 & 주얼리",
        "brands":"DIOR · TIFFANY · TAMBURINS",
        "item":"골드 목걸이",
        "lucky_color":"핑크 베이지",
        "spot":"패션관 2F",
        "score":"88",
        "tip":"오늘은 나를 위한 작은 선물이 좋은 흐름을 만들어요 ✨",
        "bg":"#FCECEF"
    },
    {
        "title":"감각적인 소비가 좋은 에너지를 만드는 날이에요.",
        "detail":"트렌디한 아이템이 오늘의 분위기를 완성해줄 거예요.",
        "shopping":"뷰티 · 향수 · 프리미엄 패션",
        "brands":"CHANEL · AESOP · GENTLE MONSTER",
        "item":"프리미엄 향수",
        "lucky_color":"로즈 핑크",
        "spot":"뷰티관 1F",
        "score":"93",
        "tip":"오늘은 새로운 스타일 도전이 행운을 불러와요 💖",
        "bg":"#FFF4F7"
    }
]

def get_font(size):
    font_path = "fonts/NanumGothic.otf"

    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)

    return ImageFont.load_default()

def create_story_image(name, gender, birth, birth_time, result):

    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), result["bg"])
    draw = ImageDraw.Draw(img)

    title_font = get_font(72)
    sub_font = get_font(42)
    small_font = get_font(28)
    medium_font = get_font(34)

    draw.rounded_rectangle((40,40,1040,1880), radius=40, fill="white")

    draw.text((120,120), "✨ 오늘의 라이프스타일 운세 ✨", fill="#E06C9F", font=small_font)
    draw.text((120,200), f"{name}님의 오늘 운세", fill="#3A2E39", font=title_font)

    draw.rounded_rectangle((90,380,990,760), radius=35, fill="#FFF3F6")

    draw.text((130,450), result["title"], fill="#222222", font=sub_font)
    draw.text((130,580), result["detail"], fill="#666666", font=small_font)

    draw.rounded_rectangle((90,820,500,1080), radius=30, fill="#FFF5FA")
    draw.text((130,870), "🎨 럭키 컬러", fill="#FF69B4", font=small_font)
    draw.text((130,960), result["lucky_color"], fill="#222222", font=medium_font)

    draw.rounded_rectangle((580,820,990,1080), radius=30, fill="#F8F1FF")
    draw.text((620,870), "🛍 추천 아이템", fill="#8A2BE2", font=small_font)
    draw.text((620,960), result["item"], fill="#222222", font=medium_font)

    draw.rounded_rectangle((90,1160,990,1420), radius=30, fill="#FFF8F0")
    draw.text((130,1220), "✨ 추천 쇼핑 테마", fill="#FF8C00", font=small_font)
    draw.text((130,1290), result["shopping"], fill="#222222", font=medium_font)
    draw.text((130,1360), result["brands"], fill="#666666", font=small_font)

    draw.rounded_rectangle((90,1480,990,1610), radius=30, fill="#F4FFF4")
    draw.text((130,1525), f"📍 추천 스팟 : {result['spot']}", fill="#228B22", font=medium_font)

    draw.text((120,1680), f"오늘의 행운 점수 : {result['score']}점", fill="#222222", font=medium_font)

    draw.text((120,1760), result["tip"], fill="#666666", font=small_font)

    qr = qrcode.make("https://event-download-page.com")
    qr = qr.resize((180,180))
    img.paste(qr, (830,1660))

    return img

st.markdown("""
<style>
.stApp{
background:linear-gradient(180deg,#FFF7F8,#FDECEF);
}

.title{
text-align:center;
font-size:56px;
font-weight:700;
color:#D85D8A;
margin-bottom:10px;
}

.subtitle{
text-align:center;
color:#777;
margin-bottom:40px;
}

.card{
background:white;
padding:30px;
border-radius:30px;
box-shadow:0 10px 30px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">💖 오늘의 쇼핑 운세</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">백화점 라이프스타일 운세 이벤트</div>', unsafe_allow_html=True)

left, right = st.columns([1,1.2])

with left:
    st.markdown("### 🔮 사주 정보 입력")

    name = st.text_input("이름")
    gender = st.radio("성별", ["여성","남성"], horizontal=True)

    birth = st.text_input("생년월일", placeholder="1995.04.25")

    birth_time = st.selectbox(
        "태어난 시간",
        ["모름","00~02시","02~04시","04~06시","06~08시",
        "08~10시","10~12시","12~14시","14~16시",
        "16~18시","18~20시","20~22시","22~24시"]
    )

    generate = st.button("✨ 운세 결과 확인하기")

    st.markdown("---")
    st.markdown("💡 결과 이미지는 인스타 스토리 업로드용으로 제작됩니다.")

with right:
    st.markdown("### 📱 결과 이미지 미리보기")
    st.info("1080 x 1920 인스타 스토리 비율")

if generate and name:

    random.seed(sum(ord(c) for c in name))
    result = random.choice(FORTUNES)

    st.success(result["title"])

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("럭키 컬러", result["lucky_color"])
    c2.metric("추천 아이템", result["item"])
    c3.metric("행운 점수", result["score"])
    c4.metric("추천 스팟", result["spot"])

    st.markdown(f"### 🛍 추천 쇼핑 테마 : {result['shopping']}")
    st.markdown(f"추천 브랜드 : **{result['brands']}**")

    image = create_story_image(name, gender, birth, birth_time, result)

    buf = BytesIO()
    image.save(buf, format="PNG")

    st.image(buf.getvalue(), use_container_width=True)

    st.download_button(
        "📥 인스타 스토리 이미지 다운로드",
        data=buf.getvalue(),
        file_name=f"{name}_fortune_story.png",
        mime="image/png"
    )
