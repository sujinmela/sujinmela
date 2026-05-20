
import streamlit as st
import random
import base64

st.set_page_config(
    page_title="롯데백화점 오늘의 쇼핑 운세",
    layout="wide"
)

FORTUNES = [
    {
        "title":"새로운 스타일 변화가 행운을 부르는 하루",
        "message":"지금의 작은 선택이 당신을 더 빛나게 만들어요.",
        "shopping":"럭셔리 액세서리 & 주얼리",
        "brands":"DIOR · TIFFANY · TAMBURINS",
        "item":"실버 주얼리",
        "spot":"에비뉴엘 3F",
        "color":"Pink Beige",
        "score":"92",
        "mood":"힙한 럭셔리 무드",
        "tip":"오늘은 나를 위한 소비가 가장 좋은 투자예요 ✨",
        "emoji":"💎"
    },
    {
        "title":"감각적인 소비가 좋은 흐름을 만드는 하루",
        "message":"새로운 아이템이 오늘의 분위기를 바꿔줄 거예요.",
        "shopping":"프리미엄 패션 & 뷰티",
        "brands":"CHANEL · GENTLE MONSTER · TAMBURINS",
        "item":"시그니처 향수",
        "spot":"뷰티관 1F",
        "color":"Rose Pink",
        "score":"88",
        "mood":"트렌디 감성 무드",
        "tip":"평소보다 과감한 스타일이 좋은 에너지를 가져와요 💖",
        "emoji":"🛍"
    }
]

def get_result(name):
    random.seed(sum(ord(c) for c in name))
    return random.choice(FORTUNES)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

.stApp{
    background:
    radial-gradient(circle at top left, #ffe4ef 0%, transparent 25%),
    radial-gradient(circle at bottom right, #f7d8ff 0%, transparent 25%),
    linear-gradient(180deg,#fff8fb,#fff1f6);
}

.main-title{
    text-align:center;
    font-size:58px;
    font-weight:800;
    color:#1f1f1f;
    margin-top:20px;
}

.sub-title{
    text-align:center;
    color:#ff4f87;
    font-size:20px;
    margin-bottom:40px;
}

.input-box{
    background:white;
    padding:32px;
    border-radius:28px;
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
}

.story-card{
    background:linear-gradient(180deg,#fff,#fff7fa);
    border-radius:36px;
    padding:40px;
    box-shadow:0 15px 40px rgba(0,0,0,0.08);
    border:1px solid #ffe0ea;
}

.hero{
    background:linear-gradient(135deg,#fff5f8,#fff0f3);
    border-radius:28px;
    padding:35px;
    margin-top:20px;
}

.metric-card{
    background:white;
    border-radius:24px;
    padding:24px;
    text-align:center;
    border:1px solid #ffe7ef;
    height:170px;
}

.brand-box{
    background:#fff7f0;
    border-radius:24px;
    padding:28px;
    margin-top:20px;
}

.tip-box{
    background:#fff0f6;
    border-radius:20px;
    padding:20px;
    margin-top:20px;
    font-size:18px;
}

.footer{
    text-align:center;
    color:#999;
    margin-top:30px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💖 롯데백화점 오늘의 쇼핑 운세</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">LIFESTYLE FORTUNE for LOTTE DEPARTMENT STORE</div>', unsafe_allow_html=True)

left, right = st.columns([0.9,1.3])

with left:
    st.markdown('<div class="input-box">', unsafe_allow_html=True)

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

    generate = st.button("✨ 운세 결과 확인하기", use_container_width=True)

    st.markdown(
    '''
    <div class="tip-box">
    📍 결과 이미지는 인스타 스토리 업로드용 감성 디자인으로 제작됩니다.<br><br>
    #롯데백화점 #오늘의쇼핑운세 #롯데백화점이벤트
    </div>
    ''',
    unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

with right:

    if generate and name:

        result = get_result(name)

        html = f'''
        <div class="story-card">

            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="color:#ff5d95;font-size:18px;font-weight:700;">
                    ✨ 오늘의 라이프스타일 운세
                    </div>

                    <div style="font-size:58px;font-weight:800;color:#222;margin-top:10px;">
                    {name}님의 오늘 운세
                    </div>

                    <div style="font-size:22px;color:#666;margin-top:10px;">
                    {result["mood"]}
                    </div>
                </div>

                <div style="font-size:90px;">
                    {result["emoji"]}
                </div>
            </div>

            <div class="hero">
                <div style="font-size:40px;font-weight:800;color:#222;line-height:1.4;">
                    {result["title"]}
                </div>

                <div style="margin-top:20px;font-size:22px;color:#666;">
                    {result["message"]}
                </div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:24px;">

                <div class="metric-card">
                    <div style="font-size:38px;">🎨</div>
                    <div style="margin-top:12px;color:#ff5d95;font-weight:700;">럭키 컬러</div>
                    <div style="margin-top:12px;font-size:22px;font-weight:700;">{result["color"]}</div>
                </div>

                <div class="metric-card">
                    <div style="font-size:38px;">🛍</div>
                    <div style="margin-top:12px;color:#9b59ff;font-weight:700;">추천 아이템</div>
                    <div style="margin-top:12px;font-size:22px;font-weight:700;">{result["item"]}</div>
                </div>

                <div class="metric-card">
                    <div style="font-size:38px;">⭐</div>
                    <div style="margin-top:12px;color:#ff9d00;font-weight:700;">행운 점수</div>
                    <div style="margin-top:12px;font-size:30px;font-weight:800;">{result["score"]}</div>
                </div>

                <div class="metric-card">
                    <div style="font-size:38px;">📍</div>
                    <div style="margin-top:12px;color:#16a34a;font-weight:700;">추천 스팟</div>
                    <div style="margin-top:12px;font-size:22px;font-weight:700;">{result["spot"]}</div>
                </div>

            </div>

            <div class="brand-box">
                <div style="font-size:18px;color:#ff8c00;font-weight:700;">
                ✨ 추천 쇼핑 테마
                </div>

                <div style="margin-top:14px;font-size:36px;font-weight:800;color:#222;">
                {result["shopping"]}
                </div>

                <div style="margin-top:14px;font-size:22px;color:#666;">
                추천 브랜드 : {result["brands"]}
                </div>
            </div>

            <div style="margin-top:28px;background:white;border-radius:24px;padding:24px;border:1px solid #ffe8ef;">
                <div style="font-size:18px;color:#ff5d95;font-weight:700;">
                💬 오늘의 한 줄 조언
                </div>

                <div style="margin-top:14px;font-size:28px;font-weight:700;color:#222;">
                {result["tip"]}
                </div>
            </div>

            <div style="margin-top:32px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:28px;font-weight:800;color:#ff4f87;">
                    LOTTE DEPARTMENT STORE
                    </div>

                    <div style="margin-top:8px;color:#888;">
                    QR 스캔 후 이미지 저장 & 이벤트 참여
                    </div>
                </div>

                <img src="https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=https://www.lotteshopping.com"
                width="140">
            </div>

        </div>
        '''

        st.components.v1.html(html, height=1750, scrolling=False)

        st.download_button(
            "📥 운세 결과 HTML 다운로드",
            data=html,
            file_name=f"{name}_lotte_fortune.html",
            mime="text/html",
            use_container_width=True
        )

    else:
        st.markdown(
        '''
        <div class="story-card" style="height:1000px;display:flex;align-items:center;justify-content:center;flex-direction:column;">
            <div style="font-size:120px;">🛍</div>
            <div style="font-size:42px;font-weight:800;margin-top:20px;">
            롯데백화점 쇼핑 운세
            </div>

            <div style="font-size:22px;color:#777;margin-top:12px;">
            운세를 입력하면 힙한 인스타 감성 결과가 생성돼요.
            </div>
        </div>
        ''',
        unsafe_allow_html=True
        )

st.markdown(
'''
<div class="footer">
© LOTTE DEPARTMENT STORE EVENT CONTENT
</div>
''',
unsafe_allow_html=True
)
