
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import base64
import random
from datetime import datetime

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

def make_result(name, birth):
    keys = list(FORTUNES.keys())
    seed = sum([ord(c) for c in name + birth])
    random.seed(seed)
    return FORTUNES[random.choice(keys)]

def generate_story_image(name, birth, result):
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), result["color"])
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 72)
        body_font = ImageFont.truetype("arial.ttf", 42)
        small_font = ImageFont.truetype("arial.ttf", 32)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.rounded_rectangle((80, 120, 1000, 1500), radius=40, fill="white")

    draw.text((120, 180), f"{name}님의 오늘의 사주", fill="black", font=title_font)

    draw.text(
        (120, 420),
        f"생년월일\n{birth}",
        fill="#333333",
        font=body_font
    )

    draw.text(
        (120, 700),
        f"✨ 오늘의 운세\n\n{result['luck']}",
        fill="#111111",
        font=body_font
    )

    draw.text(
        (120, 1050),
        f"🛍 추천 쇼핑 테마\n\n{result['shopping']}",
        fill=result["color"],
        font=body_font
    )

    draw.text(
        (120, 1350),
        "#백화점이벤트 #오늘의운세 #쇼핑운세",
        fill="#666666",
        font=small_font
    )

    qr = qrcode.make("https://your-event-download-page.com")
    qr = qr.resize((220, 220))
    img.paste(qr, (760, 1580))

    draw.text(
        (120, 1660),
        "QR을 스캔하면 결과 이미지를 다운로드할 수 있어요",
        fill="white",
        font=small_font
    )

    return img

st.title("🔮 백화점 사주 체험 이벤트")
st.caption("오늘의 운세와 쇼핑 테마를 확인해보세요!")

with st.form("fortune_form"):
    name = st.text_input("이름")
    birth = st.text_input("생년월일", placeholder="1995.05.20")
    submitted = st.form_submit_button("운세 보기")

if submitted and name and birth:
    result = make_result(name, birth)

    st.success(result["luck"])
    st.markdown(f"### 🛍 추천 쇼핑 테마: {result['shopping']}")

    image = generate_story_image(name, birth, result)

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
    st.markdown("### 이벤트 운영 아이디어")
    st.markdown(
        '''
        - 고객이 직접 운세 결과를 인스타 스토리에 업로드
        - 특정 해시태그 업로드 시 경품 응모
        - 쇼핑 테마 기반 매장 쿠폰 연결
        - QR 랜딩 페이지에서 멤버십 가입 유도
        '''
    )
