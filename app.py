import streamlit as st
import datetime
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import base64

# --- 페이지 설정 ---
st.set_page_config(page_title="백화점 오늘의 쇼핑 운세", layout="centered")

# --- 데이터 영역 (사주 일간별 쇼핑 테마) ---
FORTUNE_DATA = {
    "목(木) - 숲의 기운": {"theme": "플랜테리어 & 그린 라이프", "item": "리빙 소품, 화분", "color": "초록색"},
    "화(火) - 불의 기운": {"theme": "트렌디 패션 & 팝업스토어", "item": "화려한 액세서리", "color": "빨간색"},
    "토(土) - 대지의 기운": {"theme": "스테디셀러 & 명품 잡화", "item": "가죽 가방, 슈즈", "color": "베이지/브라운"},
    "금(金) - 바위의 기운": {"theme": "테크 & 프리미엄 가전", "item": "워치, 최신 가젯", "color": "실버/화이트"},
    "수(水) - 물의 기운": {"theme": "뷰티 & 스파 힐링", "item": "향수, 스킨케어", "color": "블랙/네이비"}
}

def get_saju_type(birthday):
    # 간단한 로직: 생일의 일자를 5가지 기운으로 나눔 (실제 사주는 만세력 필요)
    day = birthday.day
    types = list(FORTUNE_DATA.keys())
    return types[day % 5]

def create_insta_image(name, saju_type, data):
    # 인스타 스토리 규격 (1080x1920)
    img = Image.new('RGB', (1080, 1920), color='#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # 배경 디자인 (간단한 색상 블록)
    draw.rectangle([0, 0, 1080, 400], fill='#F0F2F6')
    
    # 텍스트 삽입 (시스템 폰트 활용, 실제 서비스 시 예쁜 폰트 파일 경로 지정 필요)
    try:
        title_font = ImageFont.truetype("AppleGothic.ttf", 80)
        content_font = ImageFont.truetype("AppleGothic.ttf", 50)
    except:
        title_font = ImageFont.load_default()
        content_font = ImageFont.load_default()

    draw.text((540, 250), f"{name}님의 쇼핑 운세", fill="#333333", font=title_font, anchor="mm")
    draw.text((540, 500), f"기운: {saju_type}", fill="#FF4B4B", font=content_font, anchor="mm")
    
    draw.text((100, 700), f"오늘의 테마: {data['theme']}", fill="#000000", font=content_font)
    draw.text((100, 800), f"럭키 아이템: {data['item']}", fill="#000000", font=content_font)
    draw.text((100, 900), f"행운의 컬러: {data['color']}", fill="#000000", font=content_font)
    
    draw.text((540, 1200), "이 화면을 캡처해 매장에 방문해보세요!", fill="#888888", font=content_font, anchor="mm")

    # QR 코드 생성 (현재 URL 혹은 이벤트 페이지 연동)
    qr = qrcode.QRCode(box_size=10)
    qr.add_data("https://your-department-store.com/event") # 실제 URL로 변경
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((300, 300))
    img.paste(qr_img, (390, 1400))
    
    return img

# --- UI 구현 ---
st.title("✨ OO백화점 오늘의 쇼핑 운세")
st.subheader("사주로 보는 나만의 쇼핑 테마 찾기")

with st.form("saju_form"):
    name = st.text_input("이름을 입력해주세요", placeholder="홍길동")
    birthday = st.date_input("생년월일", min_value=datetime.date(1950, 1, 1))
    submitted = st.form_submit_button("운세 확인하기")

if submitted and name:
    saju_type = get_saju_type(birthday)
    res_data = FORTUNE_DATA[saju_type]
    
    # 이미지 생성
    result_img = create_insta_image(name, saju_type, res_data)
    
    # 화면 표시
    st.image(result_img, caption="인스타그램 스토리에 공유해보세요!", use_column_width=True)
    
    # 다운로드 버튼
    buf = BytesIO()
    result_img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="이미지 다운로드 받기",
        data=byte_im,
        file_name=f"{name}_shopping_fortune.png",
        mime="image/png"
    )
