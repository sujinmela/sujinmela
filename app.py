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
    "영업기획팀": "#c8102e",   # 빨강
    "지원팀":   "#1a3a7c",   # 남색
    "시설팀":   "#1a7a3c",   # 초록
}
DEPT_BG = {
    "영업기획팀": "rgba(200,16,46,0.10)",
    "지원팀":   "rgba(26,58,124,0.10)",
    "시설팀":   "rgba(26,122,60,0.10)",
}
DEPT_TEXT = {
    "영업기획팀": "#c8102e",
    "지원팀":   "#1a3a7c",
    "시설팀":   "#1a7a3c",
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

# ── 로고 이미지 (base64 내장) ──────────────────────────────────────────────
LOTTE_LOGO_B64 = "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"

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
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');

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
    font-family: 'Pretendard Variable', Pretendard, -apple-system, sans-serif !important;
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
    font-family: 'Pretendard Variable', Pretendard, sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--white);
    letter-spacing: 0.16em;
    text-transform: uppercase;
}}
.lotte-logo .accent {{
    color: var(--lime);
    font-weight: 300;
    font-size: 1.0rem;
    letter-spacing: 0.22em;
}}
.lotte-subtitle {{
    font-size: 0.64rem;
    color: var(--gray-500);
    letter-spacing: 0.1em;
    margin-top: 5px;
    font-weight: 400;
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
    font-family: 'Pretendard Variable', Pretendard, sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #111111;
    letter-spacing: -0.02em;
    margin-bottom: 20px;
    border-left: 5px solid var(--lime);
    padding-left: 16px;
    line-height: 1.15;
}}
.cal-month-title .year-part {{
    font-size: 1.0rem;
    font-weight: 500;
    color: #666;
    letter-spacing: 0.02em;
    display: block;
    margin-bottom: 2px;
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
    height: 120px;
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
.dept-row {{ margin-bottom: 3px; min-height: 22px; }}
.dept-badge {{
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 2px 6px 2px 4px;
    border-radius: 3px;
    max-width: 100%;
    overflow: visible;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: default;
    position: relative;
    letter-spacing: -0.01em;
    transition: opacity 0.15s;
    line-height: 1.4;
}}
.dept-badge:hover {{ opacity: 0.75; }}

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
    font-family: 'Pretendard Variable', Pretendard, sans-serif;
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
    background: rgba(17,17,17,0.92);
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 16px 16px 14px;
    margin-top: 10px;
}}
.weather-title {{
    font-size: 0.56rem;
    letter-spacing: 0.18em;
    color: var(--lime);
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: block;
}}
.weather-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 2px;
}}
.weather-icon {{
    font-size: 2.6rem;
    line-height: 1;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.3));
}}
.weather-temp {{
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--white);
    letter-spacing: -0.03em;
    line-height: 1;
}}
.weather-desc {{
    font-size: 0.72rem;
    color: #999;
    margin-top: 3px;
    font-weight: 400;
}}
.weather-label {{
    font-size: 0.58rem;
    color: var(--lime);
    font-weight: 700;
    margin-bottom: 4px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}
.weather-divider {{
    border: none;
    border-top: 1px solid #222;
    margin: 12px 0 10px;
}}
.weather-last-year {{
    font-size: 0.68rem;
    color: #666;
    line-height: 1.8;
}}
.weather-last-year b {{ color: #999; }}

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
    font-family: 'Pretendard Variable', Pretendard, sans-serif;
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
    font-family: 'Pretendard Variable', Pretendard, sans-serif !important;
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
    font-family: 'Pretendard Variable', Pretendard, sans-serif !important;
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


# ── 날씨 조회 (Open-Meteo API - 파주시, 키 없이 무료) ───────────────────────
# 파주시 문발동 좌표: 37.7377, 126.7798
_PAJU_LAT, _PAJU_LON = 37.7377, 126.7798

# WMO weather code → (한글설명, 이모지)
_WMO_CODE = {
    0:  ("맑음",       "☀️"),
    1:  ("대체로 맑음", "🌤️"),
    2:  ("구름많음",   "⛅"),
    3:  ("흐림",       "🌥️"),
    45: ("안개",       "🌫️"), 48: ("안개",  "🌫️"),
    51: ("이슬비",     "🌦️"), 53: ("이슬비","🌦️"), 55: ("이슬비","🌦️"),
    61: ("비",         "🌧️"), 63: ("비",    "🌧️"), 65: ("강한비","🌧️"),
    71: ("눈",         "🌨️"), 73: ("눈",    "🌨️"), 75: ("강한눈","❄️"),
    80: ("소나기",     "🌦️"), 81: ("소나기","🌦️"), 82: ("강한소나기","⛈️"),
    85: ("눈소나기",   "🌨️"), 86: ("눈소나기","🌨️"),
    95: ("뇌우",       "⛈️"), 96: ("뇌우",  "⛈️"), 99: ("뇌우",  "⛈️"),
}

def _wind_dir(deg: float) -> str:
    dirs = ["북","북동","동","남동","남","남서","서","북서"]
    return dirs[round(deg / 45) % 8]

@st.cache_data(ttl=1800)
def get_openmeteo_weather() -> dict:
    """Open-Meteo 현재 날씨 + 오늘 최고/최저"""
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={_PAJU_LAT}&longitude={_PAJU_LON}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            "weather_code,wind_speed_10m,wind_direction_10m"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            "&timezone=Asia%2FSeoul&forecast_days=1"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
        c = data["current"]
        d = data["daily"]
        code = int(c.get("weather_code", 0))
        desc, icon = _WMO_CODE.get(code, ("날씨정보", "🌤️"))
        return {
            "ok":    True,
            "temp":  round(c["temperature_2m"], 1),
            "feel":  round(c["apparent_temperature"], 1),
            "hum":   int(c["relative_humidity_2m"]),
            "wind":  round(c["wind_speed_10m"], 1),
            "wdir":  _wind_dir(c.get("wind_direction_10m", 0)),
            "hi":    round(d["temperature_2m_max"][0], 1),
            "lo":    round(d["temperature_2m_min"][0], 1),
            "rain":  round(d["precipitation_sum"][0], 1),
            "desc":  desc,
            "icon":  icon,
        }
    except Exception as e:
        return {"ok": False, "err": str(e)[:100]}

@st.cache_data(ttl=7200)
def get_openmeteo_lastyear() -> dict:
    """작년 동일 날짜 최고/최저 (Open-Meteo Historical API)"""
    try:
        from datetime import date as _date
        now = datetime.now()
        ly  = now.replace(year=now.year - 1)
        ds  = ly.strftime("%Y-%m-%d")
        url = (
            "https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={_PAJU_LAT}&longitude={_PAJU_LON}"
            f"&start_date={ds}&end_date={ds}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            "&timezone=Asia%2FSeoul"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
        d = data["daily"]
        return {
            "ok":   True,
            "hi":   round(d["temperature_2m_max"][0], 1),
            "lo":   round(d["temperature_2m_min"][0], 1),
            "rain": round(d["precipitation_sum"][0] or 0, 1),
            "date": ly.strftime("%Y.%m.%d"),
        }
    except Exception as e:
        return {"ok": False, "err": str(e)[:80]}

def render_weather_card() -> str:
    now   = datetime.now()
    today = get_openmeteo_weather()
    ly    = get_openmeteo_lastyear()

    if today.get("ok"):
        today_html = f"""
        <div class='weather-row'>
            <span class='weather-icon'>{today["icon"]}</span>
            <div>
                <div class='weather-temp'>{today["temp"]}°</div>
                <div class='weather-desc'>{today["desc"]}</div>
            </div>
        </div>
        <div style='font-size:0.66rem;color:#777;margin:5px 0 4px;'>
            체감 {today["feel"]}° &nbsp;·&nbsp; 습도 {today["hum"]}%
            &nbsp;·&nbsp; {today["wdir"]}풍 {today["wind"]}m/s
        </div>
        <div style='display:flex;gap:8px;margin-top:4px;'>
            <span style='font-size:0.65rem;background:rgba(255,80,80,0.12);
                color:#ff6060;padding:2px 7px;border-radius:3px;font-weight:700;'>
                최고 {today["hi"]}°
            </span>
            <span style='font-size:0.65rem;background:rgba(80,160,255,0.12);
                color:#60b0ff;padding:2px 7px;border-radius:3px;font-weight:700;'>
                최저 {today["lo"]}°
            </span>
            <span style='font-size:0.65rem;background:rgba(100,200,255,0.08);
                color:#888;padding:2px 7px;border-radius:3px;'>
                강수 {today["rain"]}mm
            </span>
        </div>"""
    else:
        err = today.get("err", "")
        today_html = f"<div style='font-size:0.66rem;color:#555;padding:4px 0;'>날씨 조회 실패<br><small>{err}</small></div>"

    if ly.get("ok"):
        diff = round(today["temp"] - ly["hi"], 1) if today.get("ok") else None
        diff_str = ""
        if diff is not None:
            arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
            color = "#ff6060" if diff > 0 else "#60b0ff" if diff < 0 else "#888"
            diff_str = f" <span style='color:{color};font-weight:700;'>{abs(diff)}° {arrow}</span>"
        ly_html = f"""
        <div class='weather-last-year'>
            <b>작년 오늘 ({ly["date"]})</b>{diff_str}<br>
            최고 <b style='color:#ff6060;'>{ly["hi"]}°</b>
            &nbsp;/&nbsp; 최저 <b style='color:#60b0ff;'>{ly["lo"]}°</b>
            &nbsp;/&nbsp; 강수 {ly["rain"]}mm
        </div>"""
    else:
        ly_html = "<div class='weather-last-year' style='color:#555;'>작년 데이터 조회 불가</div>"

    return f"""
    <div class='weather-card'>
        <span class='weather-title'>🌤 TODAY'S WEATHER · PAJU</span>
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
                            style='background:{bg}; color:{color}; border-left:3px solid {color}; font-weight:700;'>
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
        <div class='cal-month-title'>
            <span class='year-part'>{year}</span>{month}월
        </div>
        <table class='cal-table'>
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        <div class='legend-wrap'>
            {''.join(f"<div class='legend-item'><div class='legend-dot' style='background:{DEPT_COLORS[d]}'></div><span style='color:{DEPT_COLORS[d]};font-weight:700;'>{d}</span></div>" for d in DEPTS)}
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
st.markdown(f"""
<div class='lotte-header'>
    <div style='display:flex;align-items:center;gap:20px;'>
        <div style='width:3px;height:38px;background:#c8ff00;border-radius:2px;flex-shrink:0;'></div>
        <div>
            <div class='lotte-logo'>LOTTE PREMIUM OUTLETS &nbsp;<span class='accent'>PAJU</span></div>
            <div class='lotte-subtitle'>파트너 소통채널 &nbsp;·&nbsp; Partner Communication Hub</div>
        </div>
    </div>
    <div style='display:flex;align-items:center;'>
        <img src='data:image/png;base64,{LOTTE_LOGO_B64}'
             style='height:42px;object-fit:contain;background:white;border-radius:6px;padding:4px 10px;box-shadow:0 1px 8px rgba(0,0,0,0.2);'
             alt='Lotte Premium Outlets Paju'>
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
