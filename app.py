import streamlit as st
import anthropic
import re
import time
from urllib.parse import urlparse, parse_qs

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
    line-height: 2.1;
    white-space: pre-wrap;
    word-break: keep-all;
    color: #1a1a1a;
    font-family: 'Noto Sans KR', sans-serif;
}
.step-badge {
    display: inline-block;
    background: #CC0000;
    color: white;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
    letter-spacing: 0.5px;
}
.char-ok   { color: #1a7a3a; font-weight: 600; }
.char-warn { color: #CC0000; font-weight: 600; }
.info-box {
    background: #f0f4ff;
    border-left: 3px solid #4466cc;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    color: #334;
    margin-bottom: 12px;
}
.error-box {
    background: #fff0f0;
    border-left: 3px solid #CC0000;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    color: #600;
}
</style>
""", unsafe_allow_html=True)

# ── 지점 목록 ────────────────────────────────────────────
STORES = {
    "서울": ["본점","잠실점","강남점","건대스타시티점","관악점","김포공항점","노원점","미아점","영등포점","청량리점"],
    "수도권": ["인천점","동탄점","구리점","수원점","안산점","일산점","중동점","평촌점"],
    "지방": ["부산본점","광복점","광주점","대구점","대전점","동래점","상인점","센텀시티점","울산점","전주점","창원점","포항점"],
}
store_flat = ["점포를 선택하세요"] + [s for g in STORES.values() for s in g]

# ── 시스템 프롬프트 ───────────────────────────────────────
SYSTEM_PROMPT = """당신은 롯데백화점 마케팅팀의 LMS 광고 문안 전문가입니다.
쇼핑 하이라이트 페이지에서 추출된 텍스트를 분석해 아래 형식으로 LMS 문안을 생성하세요.
추가 설명 없이 순수 LMS 문안 텍스트만 출력합니다.

=== 출력 형식 ===
(광고)롯데백화점 {점포명}
{고객명} 고객님 안녕하세요.
이번주 롯데백화점 {점포명} 소식을 안내드립니다.


[테마명] 테마 부제목
① [브랜드명] 행사 내용
② [브랜드명] 행사 내용
[테마명] 테마 부제목
① [브랜드명] 행사 내용
...


자세한 사항 및 더욱 다양한 소식은 하단의 링크를 통해 확인 가능합니다.
{URL}
문의전화 1577-0001
무료수신거부 080-880-2626

=== 규칙 ===
- 인사말 뒤 빈 줄 2개, 마지막 행사 뒤 빈 줄 2개
- 테마 헤더([Special Gift] 등)와 ①②③ 번호 원문 그대로
- 브랜드명·행사명 오타 없이 원문 유지
- 각 테마 사이 빈 줄 없이 연속 출력
- 순수 텍스트만 출력 (마크다운 불가)"""

# ── URL에서 파라미터 추출 ─────────────────────────────────
def extract_params(url: str):
    try:
        qs = parse_qs(urlparse(url).query)
        hhl = qs.get("shpgHhlghNo", [None])[0]
        adit = qs.get("shpgHhlghAditNo", [None])[0]
        return hhl, adit
    except:
        return None, None

# ── Playwright로 JS 렌더링 후 텍스트 추출 ────────────────
def fetch_page_text(url: str) -> tuple[str, str]:
    """
    Returns (text, error_message)
    text이 비어 있으면 error_message 참조
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "", "playwright 패키지가 설치되지 않았습니다. requirements.txt를 확인해 주세요."

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ]
            )
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="ko-KR",
            )
            page = ctx.new_page()

            page.goto(url, wait_until="networkidle", timeout=40000)
            # JS 렌더링 완료 대기
            page.wait_for_timeout(4000)

            # 본문 영역 우선 탐색
            selectors = [
                ".highlight-content",
                ".shopping-highlight",
                ".shpg-highlight",
                ".contents-wrap",
                "main",
                "#contents",
                ".container",
            ]
            text = ""
            for sel in selectors:
                try:
                    el = page.query_selector(sel)
                    if el:
                        t = el.inner_text()
                        if len(t) > 200:
                            text = t
                            break
                except:
                    pass

            # 선택자 실패 시 body 전체
            if not text:
                text = page.inner_text("body")

            browser.close()
            return text.strip(), ""

    except Exception as e:
        return "", f"페이지 로딩 실패: {e}"


# ── LMS 생성 ─────────────────────────────────────────────
def generate_lms(page_text: str, store: str, customer: str, url: str, extra: str) -> str:
    client = anthropic.Anthropic()
    user_msg = f"""아래 쇼핑 하이라이트 내용으로 LMS 문안을 생성해 주세요.

점포명: {store}
고객명: {customer}
URL: {url}
{f"추가 안내사항: {extra}" if extra else ""}

=== 쇼핑 하이라이트 추출 텍스트 ===
{page_text}
"""
    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return msg.content[0].text.strip()


# ═══════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════
st.markdown("## 🏬 롯데백화점 LMS 문안 자동생성")
st.markdown("쇼핑 하이라이트 **URL만** 입력하면 LMS 문안을 자동으로 생성합니다.")
st.divider()

# ── STEP 1: URL ───────────────────────────────────────────
st.markdown('<span class="step-badge">STEP 1</span> **쇼핑 하이라이트 URL 입력**', unsafe_allow_html=True)
url_input = st.text_input(
    "URL",
    label_visibility="collapsed",
    placeholder="https://www.lotteshopping.com/shopnow/cntsList?shpgHhlghNo=SHH...&shpgHhlghAditNo=SHA...",
)

# URL 유효성 미리 체크
if url_input:
    hhl, adit = extract_params(url_input)
    if hhl:
        st.markdown(
            f'<div class="info-box">✅ 파라미터 확인 — shpgHhlghNo: <b>{hhl}</b>'
            + (f' / shpgHhlghAditNo: <b>{adit}</b>' if adit else '')
            + '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="error-box">⚠ URL에서 shpgHhlghNo 파라미터를 찾을 수 없습니다. 주소를 다시 확인해 주세요.</div>',
            unsafe_allow_html=True,
        )

st.markdown("")

# ── STEP 2: 점포·고객 ─────────────────────────────────────
st.markdown('<span class="step-badge">STEP 2</span> **발송 정보 입력**', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])
with col1:
    store = st.selectbox("점포명", store_flat, label_visibility="collapsed")
with col2:
    customer = st.text_input("고객명", placeholder="예: 김롯데  (미입력 시 '고객')", label_visibility="collapsed")

extra = st.text_input(
    "추가 안내사항 (선택)",
    placeholder="예: 일부 행사는 조기 종료될 수 있습니다.",
)

st.divider()

# ── 생성 버튼 ─────────────────────────────────────────────
run = st.button("✨ LMS 문안 자동생성", type="primary", use_container_width=True)

if run:
    # 유효성 검사
    errors = []
    if not url_input.strip():
        errors.append("URL을 입력해 주세요.")
    else:
        hhl, _ = extract_params(url_input)
        if not hhl:
            errors.append("올바른 쇼핑 하이라이트 URL을 입력해 주세요.")
    if store == "점포를 선택하세요":
        errors.append("점포명을 선택해 주세요.")

    if errors:
        for e in errors:
            st.warning(e)
    else:
        customer_name = customer.strip() or "고객"

        # ① 페이지 크롤링
        with st.status("🌐 쇼핑 하이라이트 페이지를 불러오는 중...", expanded=True) as status:
            st.write("JavaScript 렌더링 중... (최대 40초 소요)")
            page_text, err = fetch_page_text(url_input.strip())

            if err:
                status.update(label="❌ 페이지 로딩 실패", state="error")
                st.markdown(f'<div class="error-box">{err}</div>', unsafe_allow_html=True)
                st.stop()

            if len(page_text) < 100:
                status.update(label="❌ 콘텐츠 추출 실패", state="error")
                st.markdown(
                    '<div class="error-box">페이지 텍스트를 충분히 추출하지 못했습니다. '
                    'URL을 확인하거나 잠시 후 다시 시도해 주세요.</div>',
                    unsafe_allow_html=True,
                )
                st.stop()

            status.update(label=f"✅ 페이지 로딩 완료 ({len(page_text):,}자 추출)", state="complete")

        # ② LMS 문안 생성
        with st.spinner("✍️ AI가 LMS 문안을 작성하고 있습니다..."):
            try:
                result = generate_lms(
                    page_text=page_text,
                    store=store,
                    customer=customer_name,
                    url=url_input.strip(),
                    extra=extra.strip(),
                )
                st.session_state["lms_result"] = result
            except anthropic.AuthenticationError:
                st.error("API 키 오류입니다. ANTHROPIC_API_KEY 환경변수를 확인해 주세요.")
                st.stop()
            except Exception as e:
                st.error(f"LMS 생성 오류: {e}")
                st.stop()

# ── 결과 출력 ─────────────────────────────────────────────
if st.session_state.get("lms_result"):
    result = st.session_state["lms_result"]
    result_len = len(result)
    is_over = result_len > 1000

    st.divider()
    hcol, bcol = st.columns([3, 1])
    with hcol:
        st.markdown("### 📨 생성된 LMS 문안")
    with bcol:
        cls = "char-warn" if is_over else "char-ok"
        warn = " ⚠ 권장 초과" if is_over else " ✓ 적정"
        st.markdown(
            f'<div style="padding-top:26px;text-align:right">'
            f'<span class="{cls}">{result_len:,}자{warn}</span></div>',
            unsafe_allow_html=True,
        )

    # 미리보기
    st.markdown(
        f'<div class="lms-box">{result.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )

    # 복사용
    st.text_area(
        "📋 복사용 텍스트",
        value=result,
        height=380,
        key="copy_area",
        help="전체 선택(Ctrl+A) 후 복사(Ctrl+C)",
    )

    if is_over:
        st.warning(
            f"현재 문안이 {result_len:,}자입니다. "
            "LMS 발송 시스템의 1,000자 제한을 초과할 수 있으니 항목 수를 조정해 주세요."
        )
