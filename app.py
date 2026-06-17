import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
from pathlib import Path
import base64

# =========================
# 기본 설정
# =========================

st.set_page_config(
    page_title="롯데프리미엄아울렛 파주점 동료사원 포털",
    page_icon="🏬",
    layout="wide"
)

PASSWORD = "1234"

DEPARTMENTS = {
    "영업기획팀": "#A50034",
    "지원팀": "#1E3A5F",
    "시설팀": "#2E7D32"
}

NOTICE_FILE = Path("data/notices.csv")
SHORTCUT_FILE = Path("data/shortcuts.csv")

NOTICE_FILE.parent.mkdir(exist_ok=True)

# =========================
# 파일 초기화
# =========================

if not NOTICE_FILE.exists():
    pd.DataFrame(columns=[
        "date",
        "department",
        "title",
        "detail",
        "created_at"
    ]).to_csv(NOTICE_FILE, index=False)

if not SHORTCUT_FILE.exists():
    pd.DataFrame([
        ["매장안내", "https://www.lotteshopping.com/store/main?cstrCd=0339"],
        ["주요시설", ""],
        ["파트너포털", ""],
        ["온라인 계정 생성", ""],
        ["직원식당", ""],
        ["직원주차", ""],
        ["이벤트홀", ""],
        ["사원증/유니폼", ""],
        ["점포 조직도", ""],
        ["POS/PDA", ""]
    ], columns=["name", "url"]).to_csv(SHORTCUT_FILE, index=False)

# =========================
# 데이터 로드
# =========================

notices = pd.read_csv(NOTICE_FILE)
shortcuts = pd.read_csv(SHORTCUT_FILE)

# =========================
# 배경 이미지
# =========================

bg_path = Path("assets/paju_bg.jpg")

if bg_path.exists():
    with open(bg_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                linear-gradient(
                    rgba(255,255,255,0.90),
                    rgba(255,255,255,0.92)
                ),
                url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
        }}

        .main-title {{
            background:#A50034;
            color:white;
            padding:18px 24px;
            border-radius:16px;
            font-size:28px;
            font-weight:700;
            margin-bottom:20px;
        }}

        .calendar-cell {{
            border:1px solid #E5E5E5;
            background:rgba(255,255,255,0.92);
            border-radius:12px;
            padding:10px;
            min-height:180px;
        }}

        .notice-item {{
            color:white;
            padding:4px 8px;
            margin:4px 0;
            border-radius:8px;
            font-size:12px;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
        }}

        .shortcut-btn {{
            display:block;
            text-align:center;
            padding:12px;
            margin-bottom:10px;
            background:#ffffff;
            border:1px solid #dddddd;
            border-radius:12px;
            color:#333333;
            text-decoration:none;
            font-weight:600;
        }}

        .shortcut-btn:hover {{
            border-color:#A50034;
            color:#A50034;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# 헤더
# =========================

st.markdown(
    '<div class="main-title">롯데프리미엄아울렛 파주점 동료사원 포털</div>',
    unsafe_allow_html=True
)

left, right = st.columns([4, 1])

# =========================
# 캘린더
# =========================

with left:

    today = date.today()

    c1, c2 = st.columns([1, 1])

    year = c1.selectbox(
        "연도",
        range(today.year - 1, today.year + 3),
        index=1
    )

    month = c2.selectbox(
        "월",
        range(1, 13),
        index=today.month - 1
    )

    cal = calendar.monthcalendar(year, month)

    weekdays = ["월", "화", "수", "목", "금", "토", "일"]

    cols = st.columns(7)

    for idx, day in enumerate(weekdays):
        cols[idx].markdown(f"### {day}")

    for week in cal:

        week_cols = st.columns(7)

        for i, day in enumerate(week):

            if day == 0:
                week_cols[i].empty()
                continue

            current_date = f"{year}-{month:02d}-{day:02d}"

            day_notices = notices[
                notices["date"] == current_date
            ]

            html = f'<div class="calendar-cell"><b>{day}</b><hr>'

            for dept in DEPARTMENTS.keys():

                dept_notice = day_notices[
                    day_notices["department"] == dept
                ]

                html += f"<div style='font-size:11px;color:#666'>{dept}</div>"

                for _, row in dept_notice.iterrows():

                    html += f"""
                    <div class="notice-item"
                         style="background:{DEPARTMENTS[dept]}"
                         title="{row['detail']}">
                         {row['title']}
                    </div>
                    """

            html += "</div>"

            week_cols[i].markdown(html, unsafe_allow_html=True)

# =========================
# 우측 메뉴
# =========================

with right:

    st.subheader("🔗 바로가기")

    for _, row in shortcuts.iterrows():

        url = row["url"] if pd.notna(row["url"]) else "#"

        st.markdown(
            f"""
            <a href="{url}" target="_blank" class="shortcut-btn">
                {row['name']}
            </a>
            """,
            unsafe_allow_html=True
        )

# =========================
# 관리자 입력
# =========================

st.divider()

with st.expander("🔒 관리자 등록"):

    password = st.text_input(
        "비밀번호 4자리",
        type="password"
    )

    if password == PASSWORD:

        with st.form("notice_form"):

            notice_date = st.date_input("일자")

            department = st.selectbox(
                "부서",
                list(DEPARTMENTS.keys())
            )

            title = st.text_input(
                "제목",
                max_chars=20
            )

            detail = st.text_area(
                "상세내용",
                max_chars=50
            )

            submit = st.form_submit_button("등록")

            if submit:

                new_row = pd.DataFrame([{
                    "date": notice_date.strftime("%Y-%m-%d"),
                    "department": department,
                    "title": title,
                    "detail": detail,
                    "created_at": datetime.now()
                }])

                updated = pd.concat(
                    [notices, new_row],
                    ignore_index=True
                )

                updated.to_csv(NOTICE_FILE, index=False)

                st.success("등록 완료!")
                st.rerun()

    elif password:
        st.error("비밀번호가 일치하지 않습니다.")
