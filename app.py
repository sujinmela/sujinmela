import streamlit as st
import anthropic
import re

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="롯데백화점 LMS 문안 자동생성",
    page_icon="🏬",
    layout="centered",
)

# ── 스타일 ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.lms-box {
    background: #fff8f6;
    border: 1.5px solid #CC0000;
    border-radius: 10px;
    padding: 20px 24px;
    font-size: 14px;
    line-height: 2.0;
    white-space: pre-wrap;
    word-break: keep-all;
    color: #1a1a1a;
    font-family: 'Noto Sans KR', sans-serif;
}
.lms-header {
    background: #CC0000;
    color: white;
    padding: 10px 16px;
    border-radius: 8px 8px 0 0;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.5px;
    margin-bottom: 0;
}
.char-badge {
    display: inline-block;
    background: #f0f0f0;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 12px;
    color: #555;
    margin-left: 8px;
}
.char-badge-warn {
    background: #fff0f0;
    color: #CC0000;
}
.section-label {
    font-size: 12px;
    font-weight: 500;
    color: #888;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────
st.markdown("## 🏬 롯데백화점 LMS 문안 자동생성")
st.markdown("쇼핑 하이라이트 내용을 붙여넣으면 발송용 LMS 문안을 즉시 생성합니다.")
st.divider()

# ── 지점 목록 ────────────────────────────────────────────
STORES = {
    "서울": ["본점", "잠실점", "강남점", "건대스타시티점", "관악점", "김포공항점", "노원점", "미아점", "영등포점", "청량리점"],
    "수도권": ["인천점", "동탄점", "구리점", "수원점", "안산점", "일산점", "중동점", "평촌점"],
    "지방": ["부산본점", "광복점", "광주점", "대구점", "대전점", "동래점", "상인점", "센텀시티점", "울산점", "전주점", "창원점", "포항점"],
}
store_options = ["점포를 선택하세요"] + [s for group in STORES.values() for s in group]

# ── 시스템 프롬프트 ───────────────────────────────────────
SYSTEM_PROMPT = """당신은 롯데백화점 마케팅팀의 LMS 광고 문안 전문가입니다.
쇼핑 하이라이트 내용을 받아 아래 형식을 정확히 지켜 LMS 문안을 생성하세요.

=== LMS 출력 형식 (이 형식 그대로, 추가 설명 없이 문안만 출력) ===

(광고)롯데백화점 {점포명}
{고객명} 고객님 안녕하세요.
이번주 롯데백화점 {점포명} 소식을 안내드립니다.
[빈 줄]
[빈 줄]
{테마별 행사 목록}
[빈 줄]
[빈 줄]
자세한 사항 및 더욱 다양한 소식은 하단의 링크를 통해 확인 가능합니다.
{URL}
문의전화 1577-0001
무료수신거부 080-880-2626

=== 테마별 행사 형식 ===
[테마명] 테마 부제목
① [브랜드명] 행사 내용
② [브랜드명] 행사 내용
...
(다음 테마)
[테마명] 테마 부제목
① [브랜드명] 행사 내용
...

=== 규칙 ===
- 원문의 테마 헤더([Special Gift], [Cosmetic] 등)와 ①②③④⑤⑥⑦⑧ 번호 그대로 유지
- 브랜드명·행사명 오타 없이 원문 그대로 사용
- 테마 헤더와 다음 테마 헤더 사이에 빈 줄 없이 연속 출력
- 순수 텍스트로만 출력, 마크다운·설명 없이"""

# ── 입력 영역 ─────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    store = st.selectbox("📍 점포명", store_options)

with col2:
    customer = st.text_input("👤 고객명", placeholder="예: 김롯데  (미입력 시 '고객' 사용)")

url_input = st.text_input(
    "🔗 쇼핑 하이라이트 URL",
    placeholder="https://www.lotteshopping.com/shopnow/cntsList?shpgHhlghNo=...",
)

page_content = st.text_area(
    "📋 쇼핑 하이라이트 내용 붙여넣기",
    height=320,
    placeholder=(
        "[Special Gift] 쇼핑과 함께하는 혜택\n"
        "① [롯데카드] 뷰티 7%\n"
        "② [현대카드] 뷰티 7%\n\n"
        "[Cosmetic] 당신이 빛나는 순간\n"
        "① [에르메스뷰티] 운 자르뎅 수 라 메르 Pop-Up\n\n"
        "..."
    ),
)

char_len = len(page_content)
st.caption(f"입력 글자수: {char_len:,}자")

extra = st.text_input(
    "📌 추가 안내사항 (선택)",
    placeholder="예: 일부 행사는 조기 종료될 수 있습니다.",
)

st.divider()

# ── 생성 버튼 ─────────────────────────────────────────────
generate = st.button("✨ LMS 문안 생성", type="primary", use_container_width=True)

if generate:
    if store == "점포를 선택하세요":
        st.warning("점포명을 선택해 주세요.")
    elif not page_content.strip():
        st.warning("쇼핑 하이라이트 내용을 붙여넣어 주세요.")
    else:
        customer_name = customer.strip() if customer.strip() else "고객"
        url_line = url_input.strip() if url_input.strip() else "(URL을 입력해 주세요)"
        extra_line = f"\n{extra.strip()}" if extra.strip() else ""

        user_prompt = f"""아래 정보를 바탕으로 LMS 문안을 생성해 주세요.

점포명: {store}
고객명: {customer_name}
URL: {url_line}
{f"추가 안내사항: {extra.strip()}" if extra.strip() else ""}

=== 쇼핑 하이라이트 내용 ===
{page_content}

위 내용을 시스템 프롬프트의 형식 그대로 LMS 문안만 출력하세요."""

        with st.spinner("AI가 LMS 문안을 생성하고 있습니다..."):
            try:
                client = anthropic.Anthropic()
                message = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=1500,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                result = message.content[0].text.strip()
                st.session_state["lms_result"] = result

            except anthropic.AuthenticationError:
                st.error("API 키 오류입니다. ANTHROPIC_API_KEY 환경변수를 확인해 주세요.")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# ── 결과 출력 ─────────────────────────────────────────────
if "lms_result" in st.session_state and st.session_state["lms_result"]:
    result = st.session_state["lms_result"]
    result_len = len(result)
    is_over = result_len > 1000

    st.divider()

    header_col, badge_col = st.columns([3, 1])
    with header_col:
        st.markdown("### 📨 생성된 LMS 문안")
    with badge_col:
        badge_class = "char-badge-warn" if is_over else "char-badge"
        warn_text = " ⚠ 권장 초과" if is_over else " ✓ 적정"
        st.markdown(
            f'<div style="padding-top:28px"><span class="{badge_class}">{result_len:,}자{warn_text}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="lms-box">{result.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )

    st.text_area(
        "📋 복사용 텍스트 (전체 선택 후 복사)",
        value=result,
        height=400,
        key="copy_area",
    )

    if is_over:
        st.warning(f"현재 문안이 {result_len:,}자입니다. LMS 발송 시스템 제한(1,000자)을 초과할 수 있으니 항목을 줄여주세요.")
