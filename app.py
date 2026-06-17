import streamlit as st
import json
import base64
import calendar
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="롯데프리미엄아울렛 파주점 동료사원 소통채널",
    page_icon="🏬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 상수 ──────────────────────────────────────────────────────────────────────
ADMIN_PASSWORD = "1234"   # 운영자 비밀번호 (4자리)
DATA_FILE = Path("calendar_data.json")
SHORTCUTS_FILE = Path("shortcuts_data.json")
DEPT_COLORS = {
    "영업기획팀": "#c8ff00",   # 라임
    "지원팀":   "#60c8ff",   # 스카이블루
    "시설팀":   "#aaaaaa",   # 라이트그레이
}
DEPT_BG = {
    "영업기획팀": "rgba(200,255,0,0.12)",
    "지원팀":   "rgba(96,200,255,0.12)",
    "시설팀":   "rgba(170,170,170,0.10)",
}
DEPT_TEXT = {
    "영업기획팀": "#111111",
    "지원팀":   "#111111",
    "시설팀":   "#111111",
}
DEPTS = ["영업기획팀", "지원팀", "시설팀"]

# ── 데이터 로드 / 저장 ─────────────────────────────────────────────────────
def load_data(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_sc_order(order: list):
    with open(Path("sc_order.json"), "w", encoding="utf-8") as f:
        json.dump(order, f, ensure_ascii=False)

def get_ordered_shortcuts() -> list:
    """shortcuts를 sc_order 순서에 맞게 정렬한 [(key, sc)] 리스트 반환"""
    shortcuts = st.session_state.shortcuts
    order = st.session_state.sc_order
    # order에 없는 신규 키는 뒤에 추가
    all_keys = list(shortcuts.keys())
    ordered = [k for k in order if k in shortcuts]
    new_keys = [k for k in all_keys if k not in ordered]
    final_order = ordered + new_keys
    # sc_order 동기화
    if final_order != order:
        st.session_state.sc_order = final_order
    return [(k, shortcuts[k]) for k in final_order]

if "cal_data" not in st.session_state:
    st.session_state.cal_data = load_data(DATA_FILE)
if "shortcuts" not in st.session_state:
    st.session_state.shortcuts = load_data(SHORTCUTS_FILE)
if "updates" not in st.session_state:
    st.session_state.updates = st.session_state.cal_data.get("__updates__", [])
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "show_updates" not in st.session_state:
    st.session_state.show_updates = False
if "show_admin" not in st.session_state:
    st.session_state.show_admin = False
if "show_shortcut_admin" not in st.session_state:
    st.session_state.show_shortcut_admin = False
if "view_month" not in st.session_state:
    st.session_state.view_month = datetime.today().month
if "view_year" not in st.session_state:
    st.session_state.view_year = datetime.today().year
if "board_key" not in st.session_state:
    st.session_state.board_key = None   # 현재 열린 게시판 shortcut key
if "sc_order" not in st.session_state:
    # shortcuts의 key 순서를 저장 (없으면 현재 순서 사용)
    sc_order_file = Path("sc_order.json")
    if sc_order_file.exists():
        with open(sc_order_file, "r", encoding="utf-8") as _f:
            st.session_state.sc_order = json.load(_f)
    else:
        st.session_state.sc_order = []

# ── 배경 이미지 인코딩 ─────────────────────────────────────────────────────
def get_bg_base64() -> str:
    img_path = Path("paju_bg.png")
    if img_path.exists():
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

BG_B64 = get_bg_base64()
bg_css = (
    f"background-image: url('data:image/png;base64,{BG_B64}');"
    "background-size: cover; background-position: center top; background-attachment: fixed;"
    if BG_B64 else ""
)

# ── 글로벌 CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.0/MyLotteRegular.woff');
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700&display=swap');
@font-face {{
    font-family: 'MyLotte';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.0/MyLotteLight.woff') format('woff');
    font-weight: 300;
}}
@font-face {{
    font-family: 'MyLotte';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.0/MyLotteRegular.woff') format('woff');
    font-weight: 400;
}}
@font-face {{
    font-family: 'MyLotte';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.0/MyLotteBold.woff') format('woff');
    font-weight: 700;
}}

/* ── 키 컬러 변수 ── */
:root {{
    --black: #111111;
    --lime: #c8ff00;
    --lime-dark: #a8d900;
    --white: #ffffff;
    --gray-100: #f5f5f5;
    --gray-200: #e8e8e8;
    --gray-500: #888888;
    --gray-700: #444444;
}}

/* ── 전체 배경 ── */
.stApp {{
    {bg_css}
    background-color: #111111;
}}
.stApp::before {{
    content: '';
    position: fixed; inset: 0;
    background: linear-gradient(160deg,
        rgba(17,17,17,0.82) 0%,
        rgba(17,17,17,0.70) 50%,
        rgba(17,17,17,0.85) 100%);
    z-index: 0;
    pointer-events: none;
}}
section[data-testid="stMain"] > div {{
    position: relative; z-index: 1;
}}

/* ── 폰트 전역 ── */
html, body, [class*="css"], p, span, div, label, button, input, textarea, select {{
    font-family: 'MyLotte', 'Pretendard', -apple-system, sans-serif !important;
    color: var(--white);
}}

/* ── 헤더 ── */
.lotte-header {{
    background: rgba(17,17,17,0.96);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 2px solid var(--lime);
    padding: 14px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
    box-shadow: 0 2px 32px rgba(0,0,0,0.5);
}}
.lotte-logo {{
    font-family: 'MyLotte', sans-serif;
    font-size: 1.22rem;
    font-weight: 700;
    color: var(--white);
    letter-spacing: 0.22em;
    text-transform: uppercase;
}}
.lotte-logo .accent {{
    color: var(--lime);
    font-weight: 300;
    font-size: 1.05rem;
    letter-spacing: 0.28em;
}}
.lotte-subtitle {{
    font-size: 0.66rem;
    color: var(--gray-500);
    letter-spacing: 0.14em;
    margin-top: 5px;
    font-weight: 300;
    text-transform: uppercase;
}}

/* ── 캘린더 컨테이너 ── */
.cal-wrap {{
    background: rgba(245,245,240,0.92);
    backdrop-filter: blur(14px);
    border-radius: 10px;
    border: 1px solid rgba(200,255,0,0.3);
    box-shadow: 0 4px 40px rgba(0,0,0,0.35);
    padding: 28px 24px 24px;
    margin: 0;
}}
.cal-month-title {{
    font-family: 'MyLotte', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #111111;
    letter-spacing: 0.04em;
    margin-bottom: 18px;
    border-left: 4px solid var(--lime);
    padding-left: 14px;
}}

/* ── 캘린더 테이블 ── */
.cal-table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    overflow: visible;
}}
.cal-table th {{
    background: #111111;
    color: #cccccc;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    padding: 10px 0;
    text-align: center;
    border: 1px solid #333;
    text-transform: uppercase;
}}
.cal-table th.sun {{ color: #ff8080; }}
.cal-table th.sat {{ color: #80c8ff; }}

.cal-cell {{
    vertical-align: top;
    border: 1px solid #ddddd8;
    padding: 7px 6px 5px;
    height: 115px;
    background: rgba(255,255,255,0.82);
    transition: background 0.2s;
    overflow: visible;
    position: relative;
}}
.cal-cell:hover {{ background: rgba(255,255,255,0.98); border-color: rgba(200,255,0,0.5); }}
.cal-cell.today {{
    background: rgba(200,255,0,0.12);
    border-color: #a0cc00;
    border-width: 1.5px;
}}
.cal-cell.other-month {{ background: rgba(240,240,240,0.4); opacity: 0.5; }}

.day-num {{
    font-size: 0.8rem;
    font-weight: 700;
    color: #444444;
    margin-bottom: 4px;
    display: block;
    letter-spacing: 0.02em;
}}
.day-num.today-num {{
    background: var(--lime);
    color: var(--black);
    width: 22px; height: 22px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem;
    margin-bottom: 4px;
}}
.day-num.sun {{ color: #cc2222; }}
.day-num.sat {{ color: #2255aa; }}

/* ── 부서별 배지 ── */
.dept-row {{ margin-bottom: 2px; min-height: 20px; }}
.dept-badge {{
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 600;
    padding: 2px 5px;
    border-radius: 2px;
    max-width: 100%;
    overflow: visible;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: default;
    position: relative;
    letter-spacing: 0.01em;
    transition: opacity 0.15s;
}}
.dept-badge:hover {{ opacity: 0.8; }}

/* ── 툴팁 ── */
.has-tooltip {{ position: relative; }}
.has-tooltip .tooltip-text {{
    visibility: hidden;
    opacity: 0;
    width: 260px;
    background: var(--black);
    border: 1px solid var(--lime);
    color: var(--white);
    font-size: 0.72rem;
    line-height: 1.7;
    border-radius: 6px;
    padding: 10px 14px;
    position: fixed;
    z-index: 99999;
    box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    transition: opacity 0.12s;
    pointer-events: none;
    white-space: pre-wrap;
    word-break: keep-all;
    max-height: 220px;
    overflow-y: auto;
}}
.has-tooltip:hover .tooltip-text {{
    visibility: visible;
    opacity: 1;
}}
.tooltip-dept {{ color: var(--lime); font-weight: 700; margin-bottom: 4px; display: block; }}

/* ── 범례 ── */
.legend-wrap {{ display: flex; gap: 18px; margin-top: 16px; flex-wrap: wrap; }}
.legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #555555; }}
.legend-dot {{ width: 10px; height: 10px; border-radius: 2px; flex-shrink: 0; }}

/* ── 사이드 패널 ── */
.side-panel {{
    background: rgba(17,17,17,0.88);
    backdrop-filter: blur(12px);
    border-radius: 10px;
    border: 1px solid #2a2a2a;
    box-shadow: 0 4px 32px rgba(0,0,0,0.4);
    padding: 20px 16px;
}}
.side-title {{
    font-family: 'MyLotte', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--white);
    border-bottom: 1px solid #2a2a2a;
    padding-bottom: 10px;
    margin-bottom: 14px;
    letter-spacing: 0.04em;
}}
.side-caption {{
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    color: var(--lime);
    font-weight: 700;
    display: block;
    margin-bottom: 4px;
    text-transform: uppercase;
}}

/* ── 바로가기 버튼 ── */
.shortcut-btn {{
    display: block;
    width: 100%;
    background: #1e1e1e;
    color: var(--white) !important;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    padding: 11px 0;
    border-radius: 4px;
    text-align: center;
    margin-bottom: 7px;
    text-decoration: none;
    transition: background 0.18s, color 0.18s, transform 0.12s;
    cursor: pointer;
    border: 1px solid #333;
}}
.shortcut-btn:hover {{
    background: var(--lime);
    color: var(--black) !important;
    border-color: var(--lime);
    transform: translateY(-1px);
    text-decoration: none;
}}
.shortcut-btn.red {{
    background: #1e1e1e;
    border-color: var(--lime);
    color: var(--lime) !important;
}}
.shortcut-btn.red:hover {{
    background: var(--lime);
    color: var(--black) !important;
}}

/* ── 날씨 카드 ── */
.weather-card {{
    background: rgba(17,17,17,0.9);
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 16px;
    margin-top: 10px;
}}
.weather-title {{
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    color: var(--lime);
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: block;
}}
.weather-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}}
.weather-icon {{ font-size: 1.6rem; line-height: 1; }}
.weather-temp {{
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--white);
    letter-spacing: -0.01em;
}}
.weather-desc {{ font-size: 0.7rem; color: var(--gray-500); margin-top: 1px; }}
.weather-label {{ font-size: 0.62rem; color: var(--lime); font-weight: 600; margin-bottom: 3px; }}
.weather-divider {{
    border: none;
    border-top: 1px solid #2a2a2a;
    margin: 10px 0;
}}
.weather-last-year {{
    font-size: 0.68rem;
    color: var(--gray-500);
    line-height: 1.7;
}}
.weather-last-year b {{ color: #aaa; }}

/* ── 업데이트 패널 ── */
.update-panel {{
    background: rgba(17,17,17,0.95);
    border-radius: 8px;
    border: 1px solid #2a2a2a;
    padding: 14px 16px;
    margin-top: 10px;
    max-height: 320px;
    overflow-y: auto;
}}
.update-item {{
    border-bottom: 1px solid #1e1e1e;
    padding: 8px 0;
    font-size: 0.76rem;
    color: #ccc;
    line-height: 1.55;
}}
.update-item:last-child {{ border-bottom: none; }}
.update-date {{ font-size: 0.65rem; color: var(--gray-500); margin-top: 2px; }}

/* ── 게시판 ── */
.board-wrap {{
    background: rgba(17,17,17,0.88);
    border-radius: 10px;
    border: 1px solid #2a2a2a;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    padding: 24px 28px;
    margin-top: 16px;
}}
.board-title {{
    font-family: 'MyLotte', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--white);
    margin-bottom: 16px;
    border-left: 4px solid var(--lime);
    padding-left: 10px;
}}
.board-item {{ border-bottom: 1px solid #1e1e1e; padding: 10px 4px; }}
.board-item:last-child {{ border-bottom: none; }}
.board-item-title {{ font-size: 0.84rem; font-weight: 600; color: var(--white); }}
.board-item-body {{ font-size: 0.76rem; color: var(--gray-500); margin-top: 3px; }}
.board-item-meta {{ font-size: 0.65rem; color: #555; margin-top: 3px; }}

/* ── Streamlit 오버라이드 ── */
div[data-testid="stHorizontalBlock"] {{ gap: 12px; }}
.stApp, [data-testid="stAppViewContainer"] {{ background: transparent; }}

.stButton > button,
.stDownloadButton > button {{
    font-family: 'MyLotte', sans-serif !important;
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
    background: #111111 !important;
    color: #ffffff !important;
    border: 1px solid #333 !important;
    transition: all 0.18s !important;
    letter-spacing: 0.04em !important;
}}
.stButton > button:hover,
.stDownloadButton > button:hover {{
    background: var(--lime) !important;
    color: #111111 !important;
    border-color: var(--lime) !important;
}}
/* form submit 버튼도 동일 */
.stFormSubmitButton > button {{
    font-family: 'MyLotte', sans-serif !important;
    background: #111111 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    transition: all 0.18s !important;
}}
.stFormSubmitButton > button:hover {{
    background: var(--lime) !important;
    color: #111111 !important;
    border-color: var(--lime) !important;
}}
div[data-testid="stForm"] {{
    background: rgba(30,30,30,0.9) !important;
    border-radius: 8px !important;
    padding: 20px !important;
    border: 1px solid #2a2a2a !important;
}}
.stSelectbox label, .stTextInput label, .stTextArea label,
.stNumberInput label, .stCheckbox label {{
    font-size: 0.74rem !important;
    font-weight: 600 !important;
    color: var(--lime) !important;
    letter-spacing: 0.06em !important;
}}
.stTextInput input, .stTextArea textarea, .stSelectbox select {{
    background: #111 !important;
    color: var(--white) !important;
    border-color: #333 !important;
}}
[data-testid="stSidebar"] {{
    background: rgba(17,17,17,0.97) !important;
    border-right: 1px solid #2a2a2a !important;
}}
.stExpander {{
    background: rgba(20,20,20,0.9) !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
}}
.stInfo {{ background: rgba(200,255,0,0.08) !important; border-color: var(--lime) !important; color: var(--white) !important; }}
.stSuccess {{ background: rgba(0,200,100,0.1) !important; color: var(--white) !important; }}
.stError {{ background: rgba(255,80,80,0.1) !important; color: var(--white) !important; }}
.stWarning {{ background: rgba(255,180,0,0.1) !important; color: var(--white) !important; }}
p, span, div, label {{ color: var(--white); }}
</style>
<script>
document.addEventListener('mousemove', function(e) {{
    const tips = document.querySelectorAll('.tooltip-text');
    tips.forEach(function(tip) {{
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        let x = e.clientX + 14;
        let y = e.clientY - 10;
        if (x + 280 > vw) x = e.clientX - 280;
        if (y + 220 > vh) y = e.clientY - 230;
        tip.style.left = x + 'px';
        tip.style.top  = y + 'px';
    }});
}});
</script>
""", unsafe_allow_html=True)


# ── 유틸 ──────────────────────────────────────────────────────────────────────
def get_cal_key(year: int, month: int, day: int, dept: str) -> str:
    return f"{year}-{month:02d}-{day:02d}|{dept}"

def get_day_events(year: int, month: int, day: int) -> dict:
    """날짜의 부서별 이벤트 목록 반환"""
    result = {d: [] for d in DEPTS}
    data = st.session_state.cal_data
    for dept in DEPTS:
        key = get_cal_key(year, month, day, dept)
        if key in data:
            result[dept] = data[key]
    return result

def add_event(year: int, month: int, day: int, dept: str, title: str, detail: str):
    key = get_cal_key(year, month, day, dept)
    if key not in st.session_state.cal_data:
        st.session_state.cal_data[key] = []
    st.session_state.cal_data[key].append({"title": title, "detail": detail})
    # 업데이트 로그
    log = {
        "ts": datetime.now().strftime("%Y.%m.%d %H:%M"),
        "dept": dept,
        "title": title,
        "date": f"{year}.{month:02d}.{day:02d}",
    }
    st.session_state.updates.insert(0, log)
    st.session_state.cal_data["__updates__"] = st.session_state.updates
    save_data(DATA_FILE, st.session_state.cal_data)

def delete_event(year: int, month: int, day: int, dept: str, idx: int):
    key = get_cal_key(year, month, day, dept)
    if key in st.session_state.cal_data:
        items = st.session_state.cal_data[key]
        if 0 <= idx < len(items):
            removed = items.pop(idx)
            if not items:
                del st.session_state.cal_data[key]
            log = {
                "ts": datetime.now().strftime("%Y.%m.%d %H:%M"),
                "dept": f"[삭제] {dept}",
                "title": removed["title"],
                "date": f"{year}.{month:02d}.{day:02d}",
            }
            st.session_state.updates.insert(0, log)
            st.session_state.cal_data["__updates__"] = st.session_state.updates
            save_data(DATA_FILE, st.session_state.cal_data)


# ── 날씨 조회 (네이버 날씨 - 파주시) ────────────────────────────────────────
import re as _re

def _sky_icon(text: str) -> str:
    t = text.lower()
    if "눈" in t: return "🌨️"
    if "비" in t and "눈" in t: return "🌦️"
    if "비" in t or "소나기" in t: return "🌧️"
    if "흐림" in t or "구름많" in t: return "🌥️"
    if "구름" in t: return "⛅"
    return "☀️"

@st.cache_data(ttl=1800)
def get_naver_weather() -> dict:
    """네이버 날씨 파주시 스크래핑"""
    try:
        url = "https://search.naver.com/search.naver?query=파주시+날씨"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9",
                "Accept": "text/html,application/xhtml+xml",
            }
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            html = r.read().decode("utf-8", errors="ignore")

        # 현재 기온
        temp_m = _re.search(r'class="[^"]*current[^"]*"[^>]*>\s*([\d.\-]+)\s*</', html)
        if not temp_m:
            temp_m = _re.search(r'([\d.\-]+)</em>\s*°', html)
        temp = temp_m.group(1) if temp_m else "-"

        # 날씨 상태
        status_m = _re.search(r'class="[^"]*summary[^"]*"[^>]*>\s*([^<]{2,12})\s*</', html)
        status = status_m.group(1).strip() if status_m else ""
        if not status:
            status_m2 = _re.search(r'<p class="[^"]*cast_txt[^"]*"[^>]*>([^<]+)</p>', html)
            status = status_m2.group(1).strip() if status_m2 else "날씨 정보"

        # 최고/최저
        hi_m  = _re.search(r'최고\s*</span>[^<]*<span[^>]*>\s*([\d.\-]+)', html)
        lo_m  = _re.search(r'최저\s*</span>[^<]*<span[^>]*>\s*([\d.\-]+)', html)
        hi = hi_m.group(1) if hi_m else "-"
        lo = lo_m.group(1) if lo_m else "-"

        # 습도 / 체감
        hum_m  = _re.search(r'습도</span>[^<]*<span[^>]*>([^<]+)</span>', html)
        feel_m = _re.search(r'체감</span>[^<]*<span[^>]*>([^<]+)</span>', html)
        hum  = hum_m.group(1).strip()  if hum_m  else "-"
        feel = feel_m.group(1).strip() if feel_m else "-"

        icon = _sky_icon(status)
        return {"ok": True, "temp": temp, "status": status, "icon": icon,
                "hi": hi, "lo": lo, "hum": hum, "feel": feel}
    except Exception as e:
        return {"ok": False, "err": str(e)}

@st.cache_data(ttl=7200)
def get_naver_weather_lastyear() -> dict:
    """네이버 날씨 작년 동일 날짜 (과거날씨)"""
    try:
        now = datetime.now()
        ly  = now.replace(year=now.year - 1)
        url = (f"https://search.naver.com/search.naver?query=파주시+날씨"
               f"&date={ly.strftime('%Y%m%d')}")
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9",
            }
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            html = r.read().decode("utf-8", errors="ignore")

        hi_m  = _re.search(r'최고\s*</span>[^<]*<span[^>]*>\s*([\d.\-]+)', html)
        lo_m  = _re.search(r'최저\s*</span>[^<]*<span[^>]*>\s*([\d.\-]+)', html)
        hi = hi_m.group(1) if hi_m else "-"
        lo = lo_m.group(1) if lo_m else "-"
        return {"ok": True, "hi": hi, "lo": lo, "date": ly.strftime("%Y.%m.%d")}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def render_weather_card() -> str:
    now   = datetime.now()
    today = get_naver_weather()
    ly    = get_naver_weather_lastyear()

    if today.get("ok") and today["temp"] != "-":
        today_html = f"""
        <div class='weather-row'>
            <span class='weather-icon'>{today["icon"]}</span>
            <div>
                <div class='weather-temp'>{today["temp"]}°C</div>
                <div class='weather-desc'>{today["status"]} · 파주시</div>
            </div>
        </div>
        <div style='display:flex;gap:10px;margin-top:6px;flex-wrap:wrap;'>
            <span style='font-size:0.65rem;color:#888;'>최고 <b style='color:#ff6b6b;'>{today["hi"]}°</b></span>
            <span style='font-size:0.65rem;color:#888;'>최저 <b style='color:#6bb5ff;'>{today["lo"]}°</b></span>
            <span style='font-size:0.65rem;color:#888;'>습도 <b style='color:#ccc;'>{today["hum"]}</b></span>
            <span style='font-size:0.65rem;color:#888;'>체감 <b style='color:#ccc;'>{today["feel"]}°</b></span>
        </div>"""
    else:
        err = today.get("err","")
        today_html = f"<div style='font-size:0.68rem;color:#555;padding:6px 0;'>날씨 조회 실패<br><span style='font-size:0.6rem;'>{err[:60]}</span></div>"

    if ly.get("ok") and ly["hi"] != "-":
        ly_html = f"""
        <div class='weather-last-year'>
            <b>작년 오늘 ({ly["date"]})</b><br>
            최고 {ly["hi"]}°C &nbsp;/&nbsp; 최저 {ly["lo"]}°C
        </div>"""
    else:
        ly_html = "<div class='weather-last-year' style='color:#444;'>작년 데이터 조회 불가</div>"

    return f"""
    <div class='weather-card'>
        <span class='weather-title'>🌤 TODAY'S WEATHER · PAJU</span>
        <div class='weather-label'>현재 날씨 <span style='color:#555;font-weight:400;font-size:0.58rem;'>(네이버 날씨)</span></div>
        {today_html}
        <hr class='weather-divider'>
        <div class='weather-label'>작년 오늘</div>
        {ly_html}
    </div>"""

def edit_event(year: int, month: int, day: int, dept: str, idx: int, new_title: str, new_detail: str):
    key = get_cal_key(year, month, day, dept)
    if key in st.session_state.cal_data:
        items = st.session_state.cal_data[key]
        if 0 <= idx < len(items):
            items[idx]["title"] = new_title
            items[idx]["detail"] = new_detail
            log = {
                "ts": datetime.now().strftime("%Y.%m.%d %H:%M"),
                "dept": f"[수정] {dept}",
                "title": new_title,
                "date": f"{year}.{month:02d}.{day:02d}",
            }
            st.session_state.updates.insert(0, log)
            st.session_state.cal_data["__updates__"] = st.session_state.updates
            save_data(DATA_FILE, st.session_state.cal_data)

# ── 캘린더 HTML 생성 ──────────────────────────────────────────────────────────
def render_calendar_html(year: int, month: int) -> str:
    today = datetime.today()
    cal = calendar.monthcalendar(year, month)
    day_headers = ["월", "화", "수", "목", "금", "토", "일"]
    cls_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    rows_html = ""
    for week in cal:
        row = ""
        for wi, day in enumerate(week):
            if day == 0:
                row += "<td class='cal-cell other-month'></td>"
                continue
            is_today = (year == today.year and month == today.month and day == today.day)
            cell_cls = "cal-cell" + (" today" if is_today else "")
            day_cls = "day-num " + cls_map[wi]

            day_html = f"<span class='{day_cls}'>{day}</span>"

            events = get_day_events(year, month, day)
            dept_rows = ""
            for dept in DEPTS:
                color = DEPT_COLORS[dept]
                bg = DEPT_BG[dept]
                evs = events[dept]
                if evs:
                    badges = ""
                    for ev in evs:
                        detail_safe = ev['detail'].replace('"', '&quot;').replace("'", "&#39;")
                        title_safe = ev['title'].replace('"', '&quot;').replace("'", "&#39;")
                        badges += f"""
                        <span class='dept-badge has-tooltip'
                            style='background:{bg}; color:{color}; border-left:2px solid {color};'>
                            {title_safe}
                            <span class='tooltip-text'><span class='tooltip-dept'>[{dept}]</span>{detail_safe if detail_safe else title_safe}</span>
                        </span> """
                    dept_rows += f"<div class='dept-row'>{badges}</div>"
                else:
                    dept_rows += "<div class='dept-row'></div>"

            row += f"<td class='{cell_cls}'>{day_html}{dept_rows}</td>"
        rows_html += f"<tr>{row}</tr>"

    header_html = "".join(
        f"<th class='{cls_map[i]}'>{h}</th>" for i, h in enumerate(day_headers)
    )

    return f"""
    <div class='cal-wrap'>
        <div class='cal-month-title'>{year}년 {month}월</div>
        <table class='cal-table'>
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        <div class='legend-wrap'>
            {''.join(f"<div class='legend-item'><div class='legend-dot' style='background:{DEPT_COLORS[d]}'></div>{d}</div>" for d in DEPTS)}
        </div>
    </div>
    """


# ── 사이드바 (관리자 로그인) ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔐 관리자")
    if not st.session_state.authenticated:
        pw = st.text_input("비밀번호 (4자리)", type="password", max_chars=4)
        if st.button("로그인"):
            if pw == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    else:
        st.success("관리자 인증됨 ✔")
        if st.button("로그아웃"):
            st.session_state.authenticated = False
            st.rerun()


# ── 헤더 ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='lotte-header'>
    <div style='display:flex;align-items:center;gap:20px;'>
        <div style='width:3px;height:38px;background:#c8ff00;border-radius:2px;flex-shrink:0;'></div>
        <div>
            <div class='lotte-logo'>LOTTE PREMIUM OUTLETS &nbsp;<span class='accent'>PAJU</span></div>
            <div class='lotte-subtitle'>파트너 소통채널 &nbsp;·&nbsp; Partner Communication Hub</div>
        </div>
    </div>
    <div style='display:flex;align-items:center;gap:16px;'>
        <div style='text-align:right;'>
            <div style='font-size:0.58rem;letter-spacing:0.16em;color:#555;text-transform:uppercase;'>Internal Only</div>
            <div style='font-size:0.7rem;color:#c8ff00;font-weight:600;letter-spacing:0.08em;margin-top:2px;'>영업기획팀</div>
        </div>
        <div style='width:36px;height:36px;background:#c8ff00;border-radius:50%;display:flex;align-items:center;justify-content:center;'>
            <span style='font-size:1.1rem;font-weight:900;color:#111;line-height:1;'>ℓ</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ── 메인 레이아웃 ─────────────────────────────────────────────────────────────
main_col, side_col = st.columns([7.5, 2.5], gap="medium")

# ────────────────── 캘린더 영역 ───────────────────────────────────────────────
with main_col:
    # 월 이동
    nav_l, nav_mid, nav_r = st.columns([1, 3, 1])
    with nav_l:
        if st.button("◀ 이전달"):
            m, y = st.session_state.view_month, st.session_state.view_year
            m -= 1
            if m < 1:
                m, y = 12, y - 1
            st.session_state.view_month, st.session_state.view_year = m, y
            st.rerun()
    with nav_mid:
        st.markdown(
            f"<p style='text-align:center;font-size:0.85rem;color:#888;margin:8px 0'>"
            f"{st.session_state.view_year}년 {st.session_state.view_month}월</p>",
            unsafe_allow_html=True,
        )
    with nav_r:
        if st.button("다음달 ▶"):
            m, y = st.session_state.view_month, st.session_state.view_year
            m += 1
            if m > 12:
                m, y = 1, y + 1
            st.session_state.view_month, st.session_state.view_year = m, y
            st.rerun()

    # 캘린더 렌더링
    cal_html = render_calendar_html(
        st.session_state.view_year, st.session_state.view_month
    )
    st.markdown(cal_html, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── 공지 등록 (인증된 경우만) ─────────────────────────────────────────────
    if st.session_state.authenticated:
        with st.expander("➕ 공지 등록", expanded=st.session_state.show_admin):
            with st.form("add_event_form", clear_on_submit=True):
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    dept_sel = st.selectbox("부서 선택", DEPTS)
                    year_sel = st.number_input(
                        "년도", min_value=2020, max_value=2035,
                        value=st.session_state.view_year
                    )
                    month_sel = st.number_input(
                        "월", min_value=1, max_value=12,
                        value=st.session_state.view_month
                    )
                    day_sel = st.number_input("일", min_value=1, max_value=31, value=1)
                with f_col2:
                    title_in = st.text_input("제목 (캘린더 표시)", max_chars=20)
                    detail_in = st.text_area(
                        "상세 내용 (툴팁, 200자 이내)", max_chars=200, height=120
                    )
                submitted = st.form_submit_button("등록", use_container_width=True)
                if submitted:
                    if not title_in.strip():
                        st.error("제목을 입력해주세요.")
                    else:
                        add_event(
                            int(year_sel), int(month_sel), int(day_sel),
                            dept_sel, title_in.strip(), detail_in.strip()
                        )
                        st.success("등록되었습니다.")
                        st.rerun()

        # ── 공지 수정 / 삭제 ────────────────────────────────────────────────
        with st.expander("✏️ 공지 수정 / 삭제"):
            md_col1, md_col2, md_col3, md_col4 = st.columns(4)
            with md_col1:
                md_year = st.number_input("년도 ", min_value=2020, max_value=2035,
                                          value=st.session_state.view_year, key="mdy")
            with md_col2:
                md_month = st.number_input("월 ", min_value=1, max_value=12,
                                           value=st.session_state.view_month, key="mdm")
            with md_col3:
                md_day = st.number_input("일 ", min_value=1, max_value=31,
                                         value=1, key="mdd")
            with md_col4:
                md_dept = st.selectbox("부서 ", DEPTS, key="mddept")

            md_key = get_cal_key(int(md_year), int(md_month), int(md_day), md_dept)
            items = st.session_state.cal_data.get(md_key, [])
            if items:
                for i, it in enumerate(items):
                    st.markdown(f"---")
                    st.markdown(f"**#{i+1}** · {it['title']}")
                    edit_mode_key = f"edit_mode_{md_key}_{i}"
                    if edit_mode_key not in st.session_state:
                        st.session_state[edit_mode_key] = False

                    btn_c1, btn_c2 = st.columns([1, 1])
                    with btn_c1:
                        if st.button("✏️ 수정", key=f"editbtn_{md_key}_{i}"):
                            st.session_state[edit_mode_key] = not st.session_state[edit_mode_key]
                            st.rerun()
                    with btn_c2:
                        if st.button("🗑️ 삭제", key=f"delbtn_{md_key}_{i}"):
                            delete_event(int(md_year), int(md_month), int(md_day), md_dept, i)
                            st.rerun()

                    if st.session_state.get(edit_mode_key, False):
                        with st.form(key=f"edit_form_{md_key}_{i}"):
                            new_title = st.text_input("제목 수정", value=it["title"], max_chars=20)
                            new_detail = st.text_area("상세내용 수정", value=it["detail"],
                                                       max_chars=200, height=100)
                            if st.form_submit_button("저장"):
                                if new_title.strip():
                                    edit_event(int(md_year), int(md_month), int(md_day),
                                               md_dept, i, new_title.strip(), new_detail.strip())
                                    st.session_state[edit_mode_key] = False
                                    st.success("수정되었습니다.")
                                    st.rerun()
            else:
                st.info("해당 날짜/부서에 등록된 공지가 없습니다.")

    # ── 게시판 영역 ───────────────────────────────────────────────────────────
    if st.session_state.board_key:
        sc = st.session_state.shortcuts.get(st.session_state.board_key, {})
        stype = sc.get("type", "board")
        if stype == "board":
            st.markdown(f"<div class='board-wrap'>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='board-title'>📋 {sc.get('label', '')} 게시판</div>",
                unsafe_allow_html=True,
            )
            board_posts = sc.get("posts", [])
            if board_posts:
                for post in board_posts:
                    st.markdown(f"""
                    <div class='board-item'>
                        <div class='board-item-title'>{post['title']}</div>
                        <div class='board-item-body'>{post.get('body','')}</div>
                        <div class='board-item-meta'>{post.get('date','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("게시물이 없습니다.")

            if st.session_state.authenticated:
                with st.form(f"board_post_{st.session_state.board_key}"):
                    bp_title = st.text_input("게시물 제목", max_chars=50)
                    bp_body = st.text_area("내용", max_chars=500, height=100)
                    if st.form_submit_button("게시"):
                        if bp_title:
                            sc.setdefault("posts", []).insert(0, {
                                "title": bp_title,
                                "body": bp_body,
                                "date": datetime.now().strftime("%Y.%m.%d"),
                            })
                            save_data(SHORTCUTS_FILE, st.session_state.shortcuts)
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("게시판 닫기"):
                st.session_state.board_key = None
                st.rerun()


# ────────────────── 사이드 패널 ───────────────────────────────────────────────
with side_col:
    # 三 업데이트 버튼
    upd_btn_label = "≡   업데이트 내역"
    if st.button(upd_btn_label, use_container_width=True):
        st.session_state.show_updates = not st.session_state.show_updates

    if st.session_state.show_updates:
        st.markdown("<div class='update-panel'>", unsafe_allow_html=True)
        updates = st.session_state.updates
        if updates:
            for u in updates[:30]:
                dept_name = u['dept'].replace('[삭제] ', '')
                dept_color = DEPT_COLORS.get(dept_name, "#888")
                dept_badge = f"<span style='color:{dept_color};font-weight:700'>{u['dept']}</span>"
                st.markdown(f"""
                <div class='update-item'>
                    {dept_badge} · {u['date']}<br>
                    <b>{u['title']}</b>
                    <div class='update-date'>{u['ts']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:0.78rem;color:#aaa'>업데이트 내역이 없습니다.</p>",
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='side-panel'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='side-title'>
        <span class='side-caption'>QUICK ACCESS</span>
        바로가기
    </div>""", unsafe_allow_html=True)

    # 바로가기 버튼 렌더링 (순서 적용)
    ordered_sc = get_ordered_shortcuts()
    for key, sc in ordered_sc:
        label = sc.get("label", key)
        stype = sc.get("type", "board")
        url = sc.get("url", "")
        is_red = sc.get("red", False)
        btn_cls = "shortcut-btn red" if is_red else "shortcut-btn"

        if stype == "url" and url:
            st.markdown(
                f"<a href='{url}' target='_blank' class='{btn_cls}'>{label}</a>",
                unsafe_allow_html=True,
            )
        elif stype == "file":
            file_b64 = sc.get("file_b64", "")
            file_name = sc.get("file_name", "download")
            if file_b64:
                file_bytes = base64.b64decode(file_b64)
                st.download_button(
                    label=label,
                    data=file_bytes,
                    file_name=file_name,
                    use_container_width=True,
                    key=f"dl_{key}",
                )
            else:
                st.markdown(f"<span class='{btn_cls}' style='opacity:.5'>{label} (파일없음)</span>",
                            unsafe_allow_html=True)
        else:  # board
            if st.button(label, key=f"sc_{key}", use_container_width=True):
                st.session_state.board_key = (
                    None if st.session_state.board_key == key else key
                )
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 날씨 카드 ─────────────────────────────────────────────────────────────
    st.markdown(render_weather_card(), unsafe_allow_html=True)

    # ── 바로가기 관리 (인증된 경우만) ────────────────────────────────────────
    if st.session_state.authenticated:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        with st.expander("⚙️ 바로가기 관리"):
            # ── 순서 조정 ─────────────────────────────────────────────────
            ordered_keys = [k for k, _ in get_ordered_shortcuts()]
            if len(ordered_keys) > 1:
                st.markdown("**🔀 버튼 순서 조정**")
                move_key = st.selectbox("이동할 버튼", ordered_keys, key="move_sc_sel")
                mv_c1, mv_c2 = st.columns(2)
                with mv_c1:
                    if st.button("▲ 위로", key="sc_mv_up"):
                        idx = ordered_keys.index(move_key)
                        if idx > 0:
                            ordered_keys[idx-1], ordered_keys[idx] = ordered_keys[idx], ordered_keys[idx-1]
                            st.session_state.sc_order = ordered_keys
                            save_sc_order(ordered_keys)
                            st.rerun()
                with mv_c2:
                    if st.button("▼ 아래로", key="sc_mv_dn"):
                        idx = ordered_keys.index(move_key)
                        if idx < len(ordered_keys)-1:
                            ordered_keys[idx], ordered_keys[idx+1] = ordered_keys[idx+1], ordered_keys[idx]
                            st.session_state.sc_order = ordered_keys
                            save_sc_order(ordered_keys)
                            st.rerun()
                # 현재 순서 미리보기
                st.markdown(
                    "<div style='font-size:0.68rem;color:#888;margin-bottom:8px;'>"
                    + " → ".join([st.session_state.shortcuts.get(k,{}).get("label",k) for k in ordered_keys])
                    + "</div>",
                    unsafe_allow_html=True
                )
                st.markdown("---")
            # ── 버튼 추가 ─────────────────────────────────────────────────
            sc_label = st.text_input("버튼 이름", max_chars=15, key="sc_label")
            sc_key_in = st.text_input("키 (영문/숫자, 중복불가)", max_chars=20, key="sc_key")
            sc_type = st.selectbox("타입", ["board", "url", "file"], key="sc_type")
            sc_url = st.text_input("URL (타입=url일 때)", placeholder="https://...", key="sc_url")
            sc_file = None
            if sc_type == "file":
                sc_file = st.file_uploader("파일 업로드 (타입=file일 때)", key="sc_file")
            sc_red = st.checkbox("빨간 버튼", key="sc_red")
            if st.button("추가", key="sc_add_btn"):
                if sc_label and sc_key_in:
                    sc_key_clean = sc_key_in.strip().replace(" ", "_")
                    entry = {
                        "label": sc_label,
                        "type": sc_type,
                        "url": sc_url,
                        "red": sc_red,
                        "posts": [],
                        "file_b64": "",
                        "file_name": "",
                    }
                    if sc_type == "file" and sc_file is not None:
                        entry["file_b64"] = base64.b64encode(sc_file.read()).decode()
                        entry["file_name"] = sc_file.name
                    st.session_state.shortcuts[sc_key_clean] = entry
                    save_data(SHORTCUTS_FILE, st.session_state.shortcuts)
                    # 순서 목록에 추가
                    if sc_key_clean not in st.session_state.sc_order:
                        st.session_state.sc_order.append(sc_key_clean)
                        save_sc_order(st.session_state.sc_order)
                    st.success(f"'{sc_label}' 버튼이 추가됐습니다.")
                    st.rerun()
                else:
                    st.warning("버튼 이름과 키를 입력해주세요.")
            # 수정
            if shortcuts:
                st.markdown("---")
                st.markdown("**버튼 수정**")
                edit_sc_key = st.selectbox("수정할 버튼 선택", list(shortcuts.keys()), key="edit_sc_sel")
                if edit_sc_key and edit_sc_key in shortcuts:
                    esc = shortcuts[edit_sc_key]
                    with st.form("edit_shortcut_form"):
                        new_sc_label = st.text_input("버튼 이름", value=esc.get("label",""), max_chars=15)
                        new_sc_type  = st.selectbox("타입", ["board","url","file"],
                                                    index=["board","url","file"].index(esc.get("type","board")))
                        new_sc_url   = st.text_input("URL", value=esc.get("url",""), placeholder="https://...")
                        new_sc_file  = None
                        if new_sc_type == "file":
                            new_sc_file = st.file_uploader("새 파일 업로드 (변경 시에만)", key="edit_sc_file")
                        new_sc_red   = st.checkbox("빨간 버튼", value=esc.get("red", False))
                        if st.form_submit_button("수정 저장"):
                            esc["label"] = new_sc_label
                            esc["type"]  = new_sc_type
                            esc["url"]   = new_sc_url
                            esc["red"]   = new_sc_red
                            if new_sc_type == "file" and new_sc_file is not None:
                                esc["file_b64"]  = base64.b64encode(new_sc_file.read()).decode()
                                esc["file_name"] = new_sc_file.name
                            save_data(SHORTCUTS_FILE, st.session_state.shortcuts)
                            st.success("수정되었습니다.")
                            st.rerun()

            # 삭제
            if shortcuts:
                st.markdown("---")
                st.markdown("**버튼 삭제**")
                del_sc_key = st.selectbox("삭제할 버튼", list(shortcuts.keys()), key="del_sc_sel")
                if st.button("삭제 확인"):
                    del st.session_state.shortcuts[del_sc_key]
                    save_data(SHORTCUTS_FILE, st.session_state.shortcuts)
                    if del_sc_key in st.session_state.sc_order:
                        st.session_state.sc_order.remove(del_sc_key)
                        save_sc_order(st.session_state.sc_order)
                    st.rerun()


# ── 푸터 ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:28px 0 16px; font-size:0.64rem;
     color:#444; letter-spacing:0.12em; margin-top:20px; border-top:1px solid #1e1e1e;'>
    LOTTE PREMIUM OUTLETS PAJU &nbsp;·&nbsp; 영업기획팀 내부 시스템
    &nbsp;<span style='color:#c8ff00;'>·</span>&nbsp;
    무단 배포 및 외부 공유 금지
</div>
""", unsafe_allow_html=True)
