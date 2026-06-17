import streamlit as st
import json
import base64
import calendar
from datetime import datetime
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
    "영업기획팀": "#c8102e",   # 롯데 레드
    "지원팀":   "#1a3a5c",   # 딥 네이비
    "시설팀":   "#5a5a5a",   # 차콜
}
DEPT_BG = {
    "영업기획팀": "rgba(200,16,46,0.10)",
    "지원팀":   "rgba(26,58,92,0.10)",
    "시설팀":   "rgba(90,90,90,0.10)",
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
    "background-size: cover; background-position: center; background-attachment: fixed;"
    if BG_B64 else ""
)

# ── 글로벌 CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

/* 전체 배경 */
.stApp {{
    {bg_css}
    background-color: #f2f0ec;
}}
.stApp::before {{
    content: '';
    position: fixed; inset: 0;
    background: rgba(242,240,236,0.82);
    z-index: 0;
    pointer-events: none;
}}
section[data-testid="stMain"] > div {{
    position: relative; z-index: 1;
}}

/* 폰트 전역 */
html, body, [class*="css"] {{
    font-family: 'Noto Sans KR', sans-serif;
    color: #1a1a1a;
}}

/* 헤더 */
.lotte-header {{
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(12px);
    border-bottom: 2px solid #c8102e;
    padding: 18px 36px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
    box-shadow: 0 2px 16px rgba(0,0,0,0.08);
}}
.lotte-logo {{
    font-family: 'Noto Serif KR', serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: #c8102e;
    letter-spacing: 0.04em;
}}
.lotte-subtitle {{
    font-size: 0.78rem;
    color: #888;
    letter-spacing: 0.08em;
    margin-top: 2px;
    text-transform: uppercase;
}}

/* 캘린더 컨테이너 */
.cal-wrap {{
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    box-shadow: 0 4px 32px rgba(0,0,0,0.09);
    padding: 28px 24px 24px;
    margin: 0;
}}
.cal-month-title {{
    font-family: 'Noto Serif KR', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: 0.02em;
    margin-bottom: 18px;
    border-left: 4px solid #c8102e;
    padding-left: 12px;
}}

/* 캘린더 테이블 */
.cal-table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    overflow: visible;
}}
.cal-table th {{
    background: #1a3a5c;
    color: #fff;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    padding: 8px 0;
    text-align: center;
    border: 1px solid #1a3a5c;
}}
.cal-table th.sun {{ background: #c8102e; }}
.cal-table th.sat {{ background: #3a6491; }}

.cal-cell {{
    vertical-align: top;
    border: 1px solid #e0ddd8;
    padding: 6px 5px 4px;
    height: 110px;
    background: rgba(255,255,255,0.7);
    transition: background 0.2s;
    overflow: visible;
    position: relative;
}}
.cal-cell:hover {{ background: rgba(255,255,255,0.96); }}
.cal-cell.today {{ background: rgba(200,16,46,0.04); border-color: #c8102e; }}
.cal-cell.other-month {{ background: rgba(240,240,240,0.3); }}

.day-num {{
    font-size: 0.82rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
    display: block;
}}
.day-num.sun {{ color: #c8102e; }}
.day-num.sat {{ color: #2a5fa5; }}

/* 부서별 공지 배지 */
.dept-row {{
    margin-bottom: 2px;
    min-height: 20px;
}}
.dept-badge {{
    display: inline-block;
    font-size: 0.64rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 3px;
    max-width: 100%;
    overflow: visible;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: default;
    position: relative;
    letter-spacing: 0.01em;
    transition: opacity 0.15s;
}}
.dept-badge:hover {{ opacity: 0.85; }}

/* 툴팁 */
.has-tooltip {{ position: relative; }}
.has-tooltip .tooltip-text {{
    visibility: hidden;
    opacity: 0;
    width: 240px;
    background: #1a1a1a;
    color: #fff;
    font-size: 0.72rem;
    line-height: 1.6;
    border-radius: 6px;
    padding: 10px 12px;
    position: fixed;
    z-index: 99999;
    box-shadow: 0 6px 24px rgba(0,0,0,0.30);
    transition: opacity 0.15s;
    pointer-events: none;
    white-space: pre-wrap;
    word-break: keep-all;
    max-height: 200px;
    overflow-y: auto;
}}
.has-tooltip:hover .tooltip-text {{
    visibility: visible;
    opacity: 1;
}}

/* 범례 */
.legend-wrap {{
    display: flex; gap: 16px; margin-top: 14px; flex-wrap: wrap;
}}
.legend-item {{
    display: flex; align-items: center; gap: 5px;
    font-size: 0.72rem; color: #555;
}}
.legend-dot {{
    width: 10px; height: 10px; border-radius: 2px; flex-shrink: 0;
}}

/* 사이드 패널 */
.side-panel {{
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    box-shadow: 0 4px 32px rgba(0,0,0,0.09);
    padding: 22px 18px;
}}
.side-title {{
    font-family: 'Noto Serif KR', serif;
    font-size: 1.0rem;
    font-weight: 700;
    color: #1a3a5c;
    border-bottom: 1px solid #e0ddd8;
    padding-bottom: 10px;
    margin-bottom: 14px;
    letter-spacing: 0.02em;
}}

/* 바로가기 버튼 */
.shortcut-btn {{
    display: block;
    width: 100%;
    background: #1a3a5c;
    color: #fff !important;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 10px 0;
    border-radius: 5px;
    text-align: center;
    margin-bottom: 8px;
    text-decoration: none;
    transition: background 0.2s, transform 0.15s;
    cursor: pointer;
    border: none;
}}
.shortcut-btn:hover {{
    background: #c8102e;
    transform: translateY(-1px);
    text-decoration: none;
}}
.shortcut-btn.red {{
    background: #c8102e;
}}
.shortcut-btn.red:hover {{
    background: #a00d25;
}}

/* 업데이트 패널 */
.update-panel {{
    background: #fff;
    border-radius: 10px;
    border: 1px solid #e0ddd8;
    padding: 16px 18px;
    margin-top: 12px;
    max-height: 340px;
    overflow-y: auto;
}}
.update-item {{
    border-bottom: 1px solid #f0ede8;
    padding: 8px 0;
    font-size: 0.78rem;
    color: #333;
    line-height: 1.55;
}}
.update-item:last-child {{ border-bottom: none; }}
.update-date {{
    font-size: 0.68rem;
    color: #aaa;
    margin-top: 2px;
}}

/* 게시판 */
.board-wrap {{
    background: rgba(255,255,255,0.9);
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    padding: 24px 28px;
    margin-top: 16px;
}}
.board-title {{
    font-family: 'Noto Serif KR', serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #1a3a5c;
    margin-bottom: 16px;
    border-left: 4px solid #c8102e;
    padding-left: 10px;
}}
.board-item {{
    border-bottom: 1px solid #f0ede8;
    padding: 10px 4px;
}}
.board-item:last-child {{ border-bottom: none; }}
.board-item-title {{
    font-size: 0.85rem;
    font-weight: 600;
    color: #1a1a1a;
}}
.board-item-body {{
    font-size: 0.78rem;
    color: #666;
    margin-top: 3px;
}}
.board-item-meta {{
    font-size: 0.68rem;
    color: #bbb;
    margin-top: 3px;
}}

/* Streamlit 기본 스타일 오버라이드 */
div[data-testid="stHorizontalBlock"] {{ gap: 12px; }}
.stButton > button {{
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    border-radius: 5px;
    transition: all 0.2s;
}}
div[data-testid="stForm"] {{
    background: rgba(255,255,255,0.9);
    border-radius: 10px;
    padding: 20px;
    border: 1px solid #e0ddd8;
}}
.stSelectbox label, .stTextInput label, .stTextArea label {{
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #1a3a5c !important;
}}
</style>
<script>
document.addEventListener('mousemove', function(e) {{
    const tips = document.querySelectorAll('.tooltip-text');
    tips.forEach(function(tip) {{
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        let x = e.clientX + 14;
        let y = e.clientY - 10;
        if (x + 260 > vw) x = e.clientX - 260;
        if (y + 200 > vh) y = e.clientY - 210;
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
                            <span class='tooltip-text'><b>[{dept}]</b><br>{detail_safe if detail_safe else title_safe}</span>
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
    <div>
        <div class='lotte-logo'>🏬 롯데프리미엄아울렛 파주점</div>
        <div class='lotte-subtitle'>동료사원 소통채널 · Partner Communication Hub</div>
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
    upd_btn_label = "≡  업데이트 내역"
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
    st.markdown("<div class='side-title'>바로가기</div>", unsafe_allow_html=True)

    # 바로가기 버튼 렌더링
    shortcuts = st.session_state.shortcuts
    for key, sc in shortcuts.items():
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

    # ── 바로가기 관리 (인증된 경우만) ────────────────────────────────────────
    if st.session_state.authenticated:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        with st.expander("⚙️ 바로가기 관리"):
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
                    st.rerun()


# ── 푸터 ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:28px 0 16px; font-size:0.68rem;
     color:#bbb; letter-spacing:0.05em; margin-top:20px'>
    LOTTE PREMIUM OUTLETS PAJU &nbsp;·&nbsp; 영업기획팀 내부 시스템 &nbsp;·&nbsp;
    무단 배포 및 외부 공유 금지
</div>
""", unsafe_allow_html=True)
