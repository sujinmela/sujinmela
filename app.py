
import streamlit as st
import random

st.set_page_config(
    page_title="롯데백화점 오늘의 운세",
    layout="wide"
)

FORTUNES = [
    {
        "title":"새로운 스타일 변화가 행운을 부르는 하루예요.",
        "desc":"새로운 시도와 변화가 좋은 흐름을 만들어요.",
        "wealth":"지출은 있지만 만족스러운 소비운!",
        "love":"설렘과 표현이 관계를 더 깊게 만들어요.",
        "health":"휴식과 수분 보충이 중요해요.",
        "theme":"가구 · 키친 · 프리미엄 식품",
        "brands":"BALMUDA · ZARA HOME · TEKLA",
        "items":["우드 테이블 램프","프리미엄 향수","스테인리스 키친웨어"],
        "color":"핑크 베이지",
        "number":"7 · 3 · 9",
        "spot":"에비뉴엘 3F"
    },
    {
        "title":"감각적인 소비가 당신의 분위기를 바꿔줄 거예요.",
        "desc":"오늘은 나를 위한 소비가 좋은 에너지를 만들어요.",
        "wealth":"계획한 소비가 만족으로 이어져요.",
        "love":"새로운 인연의 흐름이 들어오는 날!",
        "health":"가벼운 산책이 컨디션을 회복시켜줘요.",
        "theme":"뷰티 · 패션 · 럭셔리 액세서리",
        "brands":"DIOR · CHANEL · TIFFANY",
        "items":["골드 이어링","프리미엄 립스틱","시그니처 향수"],
        "color":"로즈 핑크",
        "number":"2 · 6 · 8",
        "spot":"뷰티관 1F"
    }
]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;800&display=swap');

html, body, [class*="css"]{
    font-family:'Noto Sans KR', sans-serif;
}

.stApp{
    background:
    radial-gradient(circle at top left,#ffe7f0 0%,transparent 25%),
    radial-gradient(circle at bottom right,#fff0f5 0%,transparent 25%),
    linear-gradient(180deg,#fff8fb,#fff3f6);
}

.main-title{
    font-size:68px;
    font-weight:800;
    color:#4b1f2f;
    line-height:1.2;
}

.side-card{
    background:rgba(255,255,255,0.75);
    backdrop-filter:blur(12px);
    padding:32px;
    border-radius:28px;
    border:1px solid #ffe3ec;
    box-shadow:0 10px 40px rgba(0,0,0,0.06);
}

.result-card{
    background:white;
    border-radius:34px;
    overflow:hidden;
    border:1px solid #ffdbe6;
    box-shadow:0 12px 40px rgba(0,0,0,0.08);
}

.hero{
    background:linear-gradient(135deg,#fff8fa,#fff0f3);
    padding:50px;
}

.section{
    background:white;
    margin:20px;
    border-radius:24px;
    border:1px solid #ffe2ea;
    padding:24px;
}

.metric-grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:14px;
}

.metric{
    background:#fff9fb;
    border:1px solid #ffe2ea;
    border-radius:20px;
    padding:20px;
    text-align:center;
}

.item-grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:16px;
}

.item-card{
    background:#fff8fa;
    border-radius:18px;
    padding:20px;
    border:1px solid #ffe2ea;
}

.download-btn{
    background:linear-gradient(90deg,#ff4f8b,#ff7aa8);
    color:white;
    padding:18px;
    border-radius:16px;
    text-align:center;
    font-weight:700;
    font-size:20px;
}
</style>
""", unsafe_allow_html=True)

left, right = st.columns([0.9,1.5])

with left:
    st.markdown('<div class="main-title">나만을 위한<br>오늘의 운세</div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-top:10px;color:#7b5a64;font-size:20px;'>롯데백화점 쇼핑 테마 운세</div>", unsafe_allow_html=True)

    st.markdown("<div class='side-card'>", unsafe_allow_html=True)
    st.markdown("### 🎀 사주 정보 입력")

    name = st.text_input("이름")
    gender = st.radio("성별", ["여성","남성"], horizontal=True)
    birth = st.date_input("생년월일")
    hour = st.selectbox("태어난 시간", ["00","02","04","06","08","10","12","14","16","18","20","22"])
    minute = st.selectbox("분", ["00","30"])

    generate = st.button("✨ 운세 결과 확인하기", use_container_width=True)

    st.markdown("---")
    st.markdown("💖 결과 이미지는 인스타 스토리(1080x1920)에 최적화되어 있습니다.")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    if generate and name:
        random.seed(sum(ord(c) for c in name))
        data = random.choice(FORTUNES)

        html = f'''
        <div class="result-card">

            <div class="hero">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="color:#ff5c94;font-weight:700;font-size:20px;">
                        ✨ 오늘의 라이프스타일 운세
                        </div>

                        <div style="font-size:72px;font-weight:800;color:#4b1f2f;line-height:1.1;margin-top:10px;">
                        오늘의 운세
                        </div>

                        <div style="margin-top:16px;font-size:28px;color:#7b5a64;">
                        {name}님, 오늘도 빛나는 하루가 될 거예요!
                        </div>
                    </div>

                    <div style="font-size:120px;">🛍️</div>
                </div>
            </div>

            <div class="section">
                <div style="font-size:42px;font-weight:800;color:#4b1f2f;">
                {data["title"]}
                </div>

                <div style="margin-top:18px;font-size:24px;color:#666;">
                {data["desc"]}
                </div>
            </div>

            <div class="section">
                <div class="metric-grid">

                    <div class="metric">
                        <div style="font-size:44px;">🍀</div>
                        <div style="margin-top:10px;font-weight:700;">전체 운세</div>
                        <div style="margin-top:10px;color:#666;">좋은 흐름의 하루</div>
                    </div>

                    <div class="metric">
                        <div style="font-size:44px;">💰</div>
                        <div style="margin-top:10px;font-weight:700;">재물운</div>
                        <div style="margin-top:10px;color:#666;">{data["wealth"]}</div>
                    </div>

                    <div class="metric">
                        <div style="font-size:44px;">❤️</div>
                        <div style="margin-top:10px;font-weight:700;">연애운</div>
                        <div style="margin-top:10px;color:#666;">{data["love"]}</div>
                    </div>

                    <div class="metric">
                        <div style="font-size:44px;">🌿</div>
                        <div style="margin-top:10px;font-weight:700;">건강운</div>
                        <div style="margin-top:10px;color:#666;">{data["health"]}</div>
                    </div>

                </div>
            </div>

            <div class="section">
                <div style="font-size:18px;color:#d9815f;font-weight:700;">
                ✨ 추천 쇼핑 테마
                </div>

                <div style="margin-top:12px;font-size:44px;font-weight:800;color:#4b1f2f;">
                {data["theme"]}
                </div>

                <div style="margin-top:12px;font-size:22px;color:#666;">
                추천 브랜드 : {data["brands"]}
                </div>
            </div>

            <div class="section">
                <div style="font-size:22px;font-weight:700;color:#ff5c94;">
                🎁 오늘의 추천 아이템
                </div>

                <div class="item-grid" style="margin-top:20px;">

                    <div class="item-card">
                        <div style="font-size:50px;">🛋️</div>
                        <div style="margin-top:10px;font-weight:700;">{data["items"][0]}</div>
                    </div>

                    <div class="item-card">
                        <div style="font-size:50px;">🍳</div>
                        <div style="margin-top:10px;font-weight:700;">{data["items"][1]}</div>
                    </div>

                    <div class="item-card">
                        <div style="font-size:50px;">💄</div>
                        <div style="margin-top:10px;font-weight:700;">{data["items"][2]}</div>
                    </div>

                </div>
            </div>

            <div class="section">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:22px;color:#ff5c94;font-weight:700;">
                        🎨 럭키 컬러
                        </div>

                        <div style="font-size:34px;font-weight:800;margin-top:10px;">
                        {data["color"]}
                        </div>
                    </div>

                    <div>
                        <div style="font-size:22px;color:#ff5c94;font-weight:700;">
                        🔢 행운 숫자
                        </div>

                        <div style="font-size:34px;font-weight:800;margin-top:10px;">
                        {data["number"]}
                        </div>
                    </div>
                </div>
            </div>

            <div class="section">
                <div style="font-size:24px;font-weight:700;color:#ff5c94;">
                💬 오늘의 한 줄 조언
                </div>

                <div style="margin-top:16px;font-size:34px;font-weight:700;color:#4b1f2f;">
                나에게 투자하는 시간이 가장 빛나는 순간을 만들어요.
                </div>
            </div>

            <div class="section">
                <div class="download-btn">
                📥 이미지 저장 & 공유하기
                </div>

                <div style="margin-top:20px;text-align:center;color:#777;">
                LOTTE DEPARTMENT STORE EVENT
                </div>
            </div>

        </div>
        '''

        st.components.v1.html(html, height=2200, scrolling=False)

    else:
        st.markdown(
        '''
        <div class="result-card" style="height:1200px;display:flex;align-items:center;justify-content:center;flex-direction:column;">
            <div style="font-size:140px;">🎀</div>
            <div style="font-size:56px;font-weight:800;color:#4b1f2f;">
            롯데백화점 오늘의 운세
            </div>

            <div style="margin-top:20px;font-size:24px;color:#777;">
            힙한 인스타 감성 쇼핑 운세를 확인해보세요.
            </div>
        </div>
        ''',
        unsafe_allow_html=True
        )
