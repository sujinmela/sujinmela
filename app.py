
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import random

st.set_page_config(page_title="백화점 사주 이벤트", layout="centered")

FORTUNES = {
    "금": {
        "luck": "오늘은 럭셔리 아이템에 행운이 깃드는 날 ✨",
        "shopping": "명품 · 주얼리 · 프리미엄 뷰티",
        "color": "#D4AF37"
    },
    "목": {
        "luck": "새로운 스타일 도전이 좋은 결과로 이어져요 🌿",
        "shopping": "패션 · 라이프스타일 · 리빙",
        "color": "#3FA34D"
    },
    "수": {
        "luck": "감각적인 소비와 힐링이 필요한 하루 💧",
        "shopping": "향수 · 스파 · 디지털",
        "color": "#4C9BE8"
    },
    "화": {
        "luck": "에너지 넘치는 쇼핑이 행운을 부릅니다 🔥",
        "shopping": "스포츠 · 팝업스토어 · 트렌드패션",
        "color": "#E94F37"
    },
    "토": {
        "luck": "안정감 있는 선택이 만족도를 높여줘요 🌕",
        "shopping": "가구 · 키친 · 프리미엄 식품",
        "color": "#B08968"
    }
}

def make_result(name, birth, gender, birth_time):
    keys = list(FORTUNES.keys())
    seed = sum([ord(c) for c in name + birth + gender + birth_time])
    random.seed(seed)
    return FORTUNES[random.choice(keys)]

def draw_shopping_background(draw, width, height):
    items = ["🛍", "👠", "💄", "⌚", "🕶", "👗", "🎁"]
    for y in range(0, height, 180):
        for x in range(0, width, 180):
            item = random.choice(items)
            draw.text((x + 20, y + 20), item, fill=(255,255,255), font=None)

def generate_story_image(name, birth, gender, birth_time, result):
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), result["color"])
    draw = ImageDraw.Draw(img)

    draw_shopping_background(draw, width, height)

    try:
        title_font = ImageFont.truetype("arial.ttf", 70)
        body_font = ImageFont.truetype("arial.ttf", 42)
        small_font = ImageFont.truetype("arial.ttf", 28)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.rounded_rectangle((70, 120, 1010, 1540), radius=50, fill="white")

    draw.text((120, 180), f"{name}님의 오늘의 사주", fill="black", font=title_font)

    info = f"생년월일: {birth}\n성별: {gender}\n태어난 시간: {birth_time}"
    draw.text((120, 420), info, fill="#444444", font=body_font)

    draw.text(
        (120, 760),
        f"✨ 오늘의 운세\n\n{result['luck']}",
        fill="#111111",
        font=body_font
    )

    draw.text(
        (120, 1120),
        f"🛍 추천 쇼핑 테마\n\n{result['shopping']}",
        fill=result["color"],
        font=body_font
    )

    draw.text(
        (120, 1440),
        "#오늘의운세 #백화점이벤트 #쇼핑운세",
        fill="#777777",
        font=small_font
    )

    qr = qrcode.make("https://your-event-download-page.com")
    qr = qr.resize((220, 220))
    img.paste(qr, (760, 1630))

    draw.text(
        (110, 1710),
        "QR을 스캔하면 결과 이미지를 다운로드할 수 있어요",
        fill="white",
        font=small_font
    )

    return img

st.markdown(
    '''
    <style>
    .stApp {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
    }
    .main-title {
        text-align:center;
        color:white;
        font-size:48px;
        font-weight:bold;
        margin-bottom:10px;
    }
    .sub {
        text-align:center;
        color:white;
        margin-bottom:30px;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">🔮 백화점 사주 체험</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">오늘의 운세와 쇼핑 테마를 확인해보세요</div>', unsafe_allow_html=True)

with st.form("fortune_form"):
    name = st.text_input("이름")
    gender = st.selectbox("성별", ["여성", "남성"])
    birth = st.text_input("생년월일", placeholder="1995.05.20")
    birth_time = st.selectbox(
        "태어난 시간",
        ["모름", "00~02시", "02~04시", "04~06시", "06~08시",
         "08~10시", "10~12시", "12~14시", "14~16시",
         "16~18시", "18~20시", "20~22시", "22~24시"]
    )

    submitted = st.form_submit_button("✨ 운세 확인하기")

if submitted and name and birth:
    result = make_result(name, birth, gender, birth_time)

    st.success(result["luck"])
    st.markdown(f"## 🛍 추천 쇼핑 테마: {result['shopping']}")

    image = generate_story_image(name, birth, gender, birth_time, result)

    buf = BytesIO()
    image.save(buf, format="PNG")

    st.image(buf.getvalue(), use_container_width=True)

    st.download_button(
        label="📥 인스타 스토리 이미지 다운로드",
        data=buf.getvalue(),
        file_name=f"{name}_fortune_story.png",
        mime="image/png"
    )

    st.markdown("---")
    st.markdown("### 💡 이벤트 운영 아이디어")
    st.markdown(
        '''
        - 인스타 스토리 업로드 이벤트 연동
        - 층별 추천 브랜드 자동 연결
        - 럭키 쿠폰 랜덤 지급
        - QR 랜딩 페이지에서 회원가입 유도
        '''
    )
