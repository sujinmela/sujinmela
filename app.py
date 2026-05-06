import io
import html
import base64
import mimetypes
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


TEMPLATE_FILENAME = "lotte_highlight_lms_template.xlsx"

REQUIRED_EVENT_COLUMNS = [
    "Include",
    "Week_Label",
    "Branch",
    "Section_Order",
    "Section_Code",
    "Section_Title",
    "Item_Order",
    "Brand_Label",
    "Event_Title",
    "Benefit_Copy",
    "Start_Date",
    "End_Date",
    "Location",
    "Detail_URL",
    "Image_URL",
    "Highlight_Copy",
]

DEFAULT_SETTINGS = {
    "Store_Name": "롯데백화점 본점",
    "Customer_Name": "김롯데",
    "Week_Label": "2026-W19",
    "Ad_Prefix": "(광고)",
    "Highlight_URL": "https://www.lotteshopping.com/shopnow/cntsList?shpgHhlghNo=SHH00000000000038699",
    "Inquiry_Phone": "1577-0001",
    "Optout_Phone": "080-880-2626",
    "Max_LMS_Length": 2000,
    "Message_Intro": "이번주 {STORE} 소식을 안내드립니다.",
    "Footer_Lead": "자세한 사항 및 더욱 다양한 소식은 하단의 링크를 통해 확인 가능합니다.",
}

DEFAULT_SECTIONS = pd.DataFrame(
    [
        [1, "SUPER HAPPY", "일상 속 커다란 행복", "시즌 대표 테마와 아트 콘텐츠", "Y"],
        [2, "Special Gift", "사은행사 안내", "카드/상품군별 사은 행사", "Y"],
        [3, "Cosmetic", "뷰티 아이템 추천", "뷰티 브랜드 신제품 및 프로모션", "Y"],
        [4, "Spring News", "봄을 여는 스타일 제안", "패션/잡화/스포츠 팝업 및 신상품", "Y"],
        [5, "For Kids", "아이와 함께할 쇼핑", "아동·유아 브랜드 행사", "Y"],
        [6, "Life Style", "안락한 생활 디자인", "가전/가구/리빙 프로모션", "Y"],
        [7, "F&B", "신선함 가득 식품", "디저트/커피/청과 행사", "Y"],
    ],
    columns=["Section_Order", "Section_Code", "Section_Title", "Page_Description", "Include"],
)


CIRCLED = [
    "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩",
    "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳",
    "㉑", "㉒", "㉓", "㉔", "㉕", "㉖", "㉗", "㉘", "㉙", "㉚",
    "㉛", "㉜", "㉝", "㉞", "㉟", "㊱", "㊲", "㊳", "㊴", "㊵",
    "㊶", "㊷", "㊸", "㊹", "㊺", "㊻", "㊼", "㊽", "㊾", "㊿",
]


def circled_number(value) -> str:
    try:
        idx = int(float(value)) - 1
    except (TypeError, ValueError):
        return ""
    if 0 <= idx < len(CIRCLED):
        return CIRCLED[idx]
    return f"{idx + 1}."


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "nat"}:
        return ""
    return text


def normalize_yes(value) -> bool:
    return clean_text(value).upper() in {"Y", "YES", "TRUE", "1", "노출"}


def settings_df_to_dict(settings_df: pd.DataFrame) -> dict:
    settings = DEFAULT_SETTINGS.copy()
    if settings_df is None or settings_df.empty:
        return settings

    if {"Field", "Value"}.issubset(settings_df.columns):
        for _, row in settings_df.iterrows():
            key = clean_text(row.get("Field"))
            if key:
                settings[key] = row.get("Value")
    else:
        for _, row in settings_df.iterrows():
            if len(row) >= 2:
                key = clean_text(row.iloc[0])
                if key:
                    settings[key] = row.iloc[1]

    settings["Store_Name"] = clean_text(settings.get("Store_Name")) or DEFAULT_SETTINGS["Store_Name"]
    settings["Customer_Name"] = clean_text(settings.get("Customer_Name")) or DEFAULT_SETTINGS["Customer_Name"]
    settings["Ad_Prefix"] = clean_text(settings.get("Ad_Prefix")) or DEFAULT_SETTINGS["Ad_Prefix"]
    settings["Highlight_URL"] = clean_text(settings.get("Highlight_URL")) or DEFAULT_SETTINGS["Highlight_URL"]
    settings["Inquiry_Phone"] = clean_text(settings.get("Inquiry_Phone")) or DEFAULT_SETTINGS["Inquiry_Phone"]
    settings["Optout_Phone"] = clean_text(settings.get("Optout_Phone")) or DEFAULT_SETTINGS["Optout_Phone"]
    settings["Message_Intro"] = clean_text(settings.get("Message_Intro")) or DEFAULT_SETTINGS["Message_Intro"]
    settings["Footer_Lead"] = clean_text(settings.get("Footer_Lead")) or DEFAULT_SETTINGS["Footer_Lead"]

    try:
        settings["Max_LMS_Length"] = int(float(settings.get("Max_LMS_Length", 2000)))
    except (TypeError, ValueError):
        settings["Max_LMS_Length"] = 2000

    return settings


def dict_to_settings_df(settings: dict) -> pd.DataFrame:
    descriptions = {
        "Store_Name": "LMS 첫 줄 및 인사말에 표시할 점포명",
        "Customer_Name": "고객명 샘플. 실제 발송 시 개인화 변수로 치환 가능",
        "Week_Label": "운영 주차",
        "Ad_Prefix": "광고성 메시지 표기",
        "Highlight_URL": "하이라이트 페이지 URL 또는 생성된 HTML 링크",
        "Inquiry_Phone": "문의전화",
        "Optout_Phone": "무료수신거부 번호",
        "Max_LMS_Length": "내부 가이드용 문자수 기준",
        "Message_Intro": "{STORE}는 Store_Name으로 치환",
        "Footer_Lead": "링크 안내 문구",
    }
    rows = []
    for key in DEFAULT_SETTINGS.keys():
        rows.append([key, settings.get(key, DEFAULT_SETTINGS[key]), descriptions.get(key, "")])
    return pd.DataFrame(rows, columns=["Field", "Value", "Description"])


def ensure_event_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in REQUIRED_EVENT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[REQUIRED_EVENT_COLUMNS].copy()

    text_cols = [
        "Include", "Week_Label", "Branch", "Section_Code", "Section_Title",
        "Brand_Label", "Event_Title", "Benefit_Copy", "Location",
        "Detail_URL", "Image_URL", "Highlight_Copy",
    ]
    for col in text_cols:
        df[col] = df[col].where(pd.notna(df[col]), "")
        df[col] = df[col].astype(str).replace({"nan": "", "NaN": "", "NaT": "", "<NA>": ""})

    for col in ["Section_Order", "Item_Order"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    def normalize_date_series(series: pd.Series) -> pd.Series:
        numeric = pd.to_numeric(series, errors="coerce")
        converted = pd.to_datetime(series, errors="coerce")
        excel_date_mask = numeric.between(20000, 60000)
        if excel_date_mask.any():
            converted.loc[excel_date_mask] = pd.to_datetime(
                numeric.loc[excel_date_mask], unit="D", origin="1899-12-30", errors="coerce"
            )
        return converted

    for col in ["Start_Date", "End_Date"]:
        df[col] = normalize_date_series(df[col])

    return df


def load_excel(uploaded_file):
    if uploaded_file is not None:
        excel_source = uploaded_file
    elif Path(TEMPLATE_FILENAME).exists():
        excel_source = TEMPLATE_FILENAME
    else:
        return dict_to_settings_df(DEFAULT_SETTINGS), DEFAULT_SECTIONS.copy(), pd.DataFrame(columns=REQUIRED_EVENT_COLUMNS)

    xl = pd.ExcelFile(excel_source)
    settings_df = pd.read_excel(xl, "Settings") if "Settings" in xl.sheet_names else dict_to_settings_df(DEFAULT_SETTINGS)
    sections_df = pd.read_excel(xl, "Sections") if "Sections" in xl.sheet_names else DEFAULT_SECTIONS.copy()
    events_df = pd.read_excel(xl, "Highlight_Input") if "Highlight_Input" in xl.sheet_names else pd.DataFrame(columns=REQUIRED_EVENT_COLUMNS)

    events_df = ensure_event_columns(events_df)
    sections_df = sections_df[["Section_Order", "Section_Code", "Section_Title", "Page_Description", "Include"]].copy()
    return settings_df, sections_df, events_df


def active_events(events_df: pd.DataFrame, week_label: str | None = None) -> pd.DataFrame:
    df = ensure_event_columns(events_df)
    df = df[df["Include"].apply(normalize_yes)].copy()

    if week_label:
        week_label = clean_text(week_label)
        if week_label:
            has_week = df["Week_Label"].apply(clean_text) == week_label
            if has_week.any():
                df = df[has_week].copy()

    df["Section_Order_Num"] = pd.to_numeric(df["Section_Order"], errors="coerce").fillna(9999)
    df["Item_Order_Num"] = pd.to_numeric(df["Item_Order"], errors="coerce").fillna(9999)
    return df.sort_values(["Section_Order_Num", "Item_Order_Num", "Brand_Label", "Event_Title"])


def active_sections(sections_df: pd.DataFrame) -> pd.DataFrame:
    df = sections_df.copy()
    df = df[df["Include"].apply(normalize_yes)].copy()
    df["Section_Order_Num"] = pd.to_numeric(df["Section_Order"], errors="coerce").fillna(9999)
    return df.sort_values(["Section_Order_Num", "Section_Code"])


def build_lms_message(settings: dict, sections_df: pd.DataFrame, events_df: pd.DataFrame) -> str:
    store_name = clean_text(settings.get("Store_Name"))
    customer_name = clean_text(settings.get("Customer_Name"))
    ad_prefix = clean_text(settings.get("Ad_Prefix"))
    intro = clean_text(settings.get("Message_Intro")).replace("{STORE}", store_name)

    lines = [
        f"{ad_prefix}{store_name}",
        "",
        f"{customer_name} 고객님 안녕하세요.",
        intro,
        "",
    ]

    event_data = active_events(events_df, clean_text(settings.get("Week_Label")))
    section_data = active_sections(sections_df)

    for _, section in section_data.iterrows():
        section_order = pd.to_numeric(pd.Series([section.get("Section_Order")]), errors="coerce").iloc[0]
        section_code = clean_text(section.get("Section_Code"))
        section_title = clean_text(section.get("Section_Title"))
        section_events = event_data[event_data["Section_Order_Num"] == section_order]

        if section_events.empty:
            continue

        lines.append(f"[{section_code}] {section_title}")
        for _, item in section_events.iterrows():
            brand = clean_text(item.get("Brand_Label"))
            title = clean_text(item.get("Event_Title"))
            prefix = circled_number(item.get("Item_Order"))
            if brand and title:
                lines.append(f"{prefix} [{brand}] {title}".strip())
            elif title:
                lines.append(f"{prefix} {title}".strip())
        lines.append("")

    footer_lead = clean_text(settings.get("Footer_Lead"))
    highlight_url = clean_text(settings.get("Highlight_URL"))
    inquiry = clean_text(settings.get("Inquiry_Phone"))
    optout = clean_text(settings.get("Optout_Phone"))

    lines.extend(
        [
            footer_lead,
            highlight_url,
            "",
            f"문의전화 {inquiry}",
            f"무료수신거부 {optout}",
        ]
    )
    return "\n".join(lines).strip() + "\n"



def build_image_lookup(uploaded_image_files) -> dict[str, str]:
    """Convert uploaded image files into data URIs that can be used inside HTML cards."""
    image_lookup: dict[str, str] = {}
    if not uploaded_image_files:
        return image_lookup

    for uploaded in uploaded_image_files:
        try:
            raw = uploaded.getvalue()
        except Exception:
            continue

        filename = clean_text(getattr(uploaded, "name", ""))
        if not filename or not raw:
            continue

        mime = getattr(uploaded, "type", None) or mimetypes.guess_type(filename)[0] or "image/png"
        encoded = base64.b64encode(raw).decode("ascii")
        data_uri = f"data:{mime};base64,{encoded}"

        path_name = Path(filename).name
        stem = Path(filename).stem
        for key in {filename, path_name, stem, filename.lower(), path_name.lower(), stem.lower()}:
            if key:
                image_lookup[key] = data_uri

    return image_lookup


def resolve_image_src(value, image_lookup: dict[str, str] | None = None) -> str:
    """Resolve Image_URL field as an external URL, data URI, or uploaded image filename."""
    text = clean_text(value)
    if not text:
        return ""

    lowered = text.lower()
    if lowered.startswith(("http://", "https://", "data:image/")):
        return text

    image_lookup = image_lookup or {}
    candidate_keys = [
        text,
        Path(text).name,
        Path(text).stem,
        text.lower(),
        Path(text).name.lower(),
        Path(text).stem.lower(),
    ]

    # Some users paste local paths such as C:\\Users\\...\\image.jpg or file:///.../image.jpg.
    # Browser-side apps cannot read those paths, but the filename can still be matched to an uploaded file.
    normalized = text.replace("file://", "").replace("\\\\", "/").replace("\\", "/")
    candidate_keys.extend([
        normalized,
        Path(normalized).name,
        Path(normalized).stem,
        normalized.lower(),
        Path(normalized).name.lower(),
        Path(normalized).stem.lower(),
    ])

    for key in candidate_keys:
        if key in image_lookup:
            return image_lookup[key]

    # Return blank rather than a local path, because Streamlit Cloud/browser cannot access local files.
    if lowered.startswith(("file:", "/", "c:", "d:")) or ":\\" in lowered:
        return ""

    # Allow relative/static paths for advanced deployments.
    return text


def build_highlight_html(settings: dict, sections_df: pd.DataFrame, events_df: pd.DataFrame, image_lookup: dict[str, str] | None = None) -> str:
    store = html.escape(clean_text(settings.get("Store_Name")))
    week = html.escape(clean_text(settings.get("Week_Label")))
    url = html.escape(clean_text(settings.get("Highlight_URL")))
    event_data = active_events(events_df, clean_text(settings.get("Week_Label")))
    section_data = active_sections(sections_df)

    css = """
    <style>
      :root {
        --lotte-red: #e60012;
        --ink: #111827;
        --muted: #6b7280;
        --line: #e5e7eb;
        --soft: #f9fafb;
      }
      .lotte-wrap {font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: var(--ink);}
      .hero {padding: 32px 28px; border-radius: 28px; background: linear-gradient(135deg, #fff1f2 0%, #fff7ed 48%, #eef2ff 100%); border: 1px solid var(--line); margin-bottom: 24px;}
      .eyebrow {font-size: 13px; letter-spacing: .16em; font-weight: 800; color: var(--lotte-red); text-transform: uppercase;}
      .hero h1 {font-size: 34px; margin: 8px 0 8px; line-height: 1.15;}
      .hero p {font-size: 16px; color: var(--muted); margin: 0;}
      .chips {display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0 0;}
      .chip {padding: 7px 12px; border-radius: 999px; background: #fff; border: 1px solid var(--line); font-size: 13px; font-weight: 700;}
      .section {margin: 28px 0;}
      .section-title {display: flex; justify-content: space-between; gap: 12px; align-items: end; border-bottom: 2px solid var(--ink); padding-bottom: 10px; margin-bottom: 14px;}
      .section-title h2 {font-size: 23px; margin: 0;}
      .section-title p {font-size: 13px; color: var(--muted); margin: 4px 0 0;}
      .grid {display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px;}
      @media (max-width: 980px) {.grid {grid-template-columns: repeat(2, minmax(0, 1fr));}}
      @media (max-width: 640px) {.grid {grid-template-columns: 1fr;}}
      .card {border: 1px solid var(--line); border-radius: 22px; overflow: hidden; background: #fff; box-shadow: 0 8px 20px rgba(15,23,42,.06);}
      .thumb {width: 100%; aspect-ratio: 1 / 1; background: var(--soft); border-bottom: 1px solid var(--line); overflow: hidden;}
      .thumb img {width: 100%; height: 100%; object-fit: cover; object-position: center; display: block;}
      .card-body {padding: 16px;}
      .card .brand {font-size: 13px; color: var(--lotte-red); font-weight: 800; margin-bottom: 8px;}
      .card h3 {font-size: 17px; margin: 0 0 10px; line-height: 1.35;}
      .meta {font-size: 12px; color: var(--muted); line-height: 1.6;}
      .badge {display: inline-block; padding: 4px 8px; background: var(--soft); border-radius: 999px; margin-top: 8px; font-size: 12px;}
      .footer-link {margin-top: 28px; padding: 18px; background: var(--soft); border-radius: 18px; border: 1px solid var(--line); word-break: break-all;}
    </style>
    """

    chips = "".join(
        f"<span class='chip'>{html.escape(clean_text(row['Section_Code']))}</span>"
        for _, row in section_data.iterrows()
    )

    body = [
        css,
        "<div class='lotte-wrap'>",
        "<div class='hero'>",
        "<div class='eyebrow'>Enjoy * Your Time at LOTTE</div>",
        f"<h1>{store} 주차별 쇼핑 하이라이트</h1>",
        f"<p>{week} 주요 브랜드 행사와 사은 혜택을 한눈에 확인하세요.</p>",
        f"<div class='chips'>{chips}</div>",
        "</div>",
    ]

    for _, section in section_data.iterrows():
        section_order = pd.to_numeric(section.get("Section_Order"), errors="coerce")
        section_events = event_data[event_data["Section_Order_Num"] == section_order]
        if section_events.empty:
            continue

        code = html.escape(clean_text(section.get("Section_Code")))
        title = html.escape(clean_text(section.get("Section_Title")))
        desc = html.escape(clean_text(section.get("Page_Description")))

        body.extend(
            [
                "<section class='section'>",
                "<div class='section-title'>",
                f"<div><h2>[{code}] {title}</h2><p>{desc}</p></div>",
                f"<span class='badge'>{len(section_events)} items</span>",
                "</div>",
                "<div class='grid'>",
            ]
        )

        for _, item in section_events.iterrows():
            brand = html.escape(clean_text(item.get("Brand_Label")))
            title = html.escape(clean_text(item.get("Event_Title")))
            benefit = html.escape(clean_text(item.get("Benefit_Copy")))
            location = html.escape(clean_text(item.get("Location")))
            date_text = format_date_range(item.get("Start_Date"), item.get("End_Date"))
            detail_url = html.escape(clean_text(item.get("Detail_URL")) or url)
            image_src = resolve_image_src(item.get("Image_URL"), image_lookup)
            image_url = html.escape(image_src, quote=True)
            alt_text = html.escape(f"{brand} {title}".strip(), quote=True)
            image_html = (
                f"<div class='thumb'><img src='{image_url}' alt='{alt_text}' loading='lazy' referrerpolicy='no-referrer'></div>"
                if image_url
                else ""
            )

            body.extend(
                [
                    "<article class='card'>",
                    image_html,
                    "<div class='card-body'>",
                    f"<div class='brand'>{brand}</div>",
                    f"<h3>{title}</h3>",
                    "<div class='meta'>",
                    f"{'기간: ' + html.escape(date_text) + '<br>' if date_text else ''}",
                    f"{'위치: ' + location + '<br>' if location else ''}",
                    f"{'혜택: ' + benefit if benefit else ''}",
                    "</div>",
                    f"<div class='badge'><a href='{detail_url}' target='_blank'>Read more</a></div>",
                    "</div>",
                    "</article>",
                ]
            )

        body.extend(["</div>", "</section>"])

    body.extend(
        [
            f"<div class='footer-link'>자세히 보기: <a href='{url}' target='_blank'>{url}</a></div>",
            "</div>",
        ]
    )

    return "\n".join(body)


def format_date_range(start, end) -> str:
    def fmt(value):
        if pd.isna(value) or clean_text(value) == "":
            return ""
        try:
            return pd.to_datetime(value).strftime("%m/%d")
        except Exception:
            return clean_text(value)

    s = fmt(start)
    e = fmt(end)
    if s and e:
        return f"{s} ~ {e}"
    return s or e


def build_export_excel(settings_df: pd.DataFrame, sections_df: pd.DataFrame, events_df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        settings_df.to_excel(writer, index=False, sheet_name="Settings")
        sections_df.to_excel(writer, index=False, sheet_name="Sections")
        ensure_event_columns(events_df).to_excel(writer, index=False, sheet_name="Highlight_Input")
    return output.getvalue()


def main():
    st.set_page_config(page_title="하이라이트 & LMS 생성기", layout="wide")
    st.title("롯데백화점 하이라이트 페이지 & LMS 생성기")
    st.caption("엑셀 템플릿의 행사 데이터를 수정하면 카드형 하이라이트 페이지와 LMS 홍보 문안이 자동 생성됩니다.")

    uploaded_file = st.sidebar.file_uploader("엑셀 템플릿 업로드", type=["xlsx"])
    uploaded_image_files = st.sidebar.file_uploader(
        "이미지 파일 업로드",
        type=["png", "jpg", "jpeg", "webp", "gif"],
        accept_multiple_files=True,
        help="이미지 URL이 없으면 여기에 이미지 파일을 올리고, 엑셀 Image_URL 칸에는 파일명만 입력하세요. 예: main_event.jpg",
    )
    image_lookup = build_image_lookup(uploaded_image_files)

    settings_df, sections_df, events_df = load_excel(uploaded_file)
    settings = settings_df_to_dict(settings_df)

    st.sidebar.subheader("빠른 설정")
    settings["Store_Name"] = st.sidebar.text_input("점포명", clean_text(settings.get("Store_Name")))
    settings["Customer_Name"] = st.sidebar.text_input("고객명 샘플", clean_text(settings.get("Customer_Name")))
    settings["Week_Label"] = st.sidebar.text_input("주차", clean_text(settings.get("Week_Label")))
    settings["Highlight_URL"] = st.sidebar.text_input("하이라이트 URL", clean_text(settings.get("Highlight_URL")))
    settings_df = dict_to_settings_df(settings)

    tab_edit, tab_preview, tab_lms, tab_export = st.tabs(["데이터 편집", "하이라이트 페이지", "LMS 문안", "다운로드"])

    with tab_edit:
        st.subheader("섹션 설정")
        sections_df = st.data_editor(
            sections_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Include": st.column_config.SelectboxColumn("Include", options=["Y", "N"], default="Y"),
                "Section_Order": st.column_config.NumberColumn("Section_Order", min_value=1, step=1),
            },
            key="sections_editor",
        )

        st.subheader("행사 데이터")
        st.info("Include=Y인 행만 하이라이트 페이지와 LMS에 반영됩니다. Item_Order는 LMS 번호 순서입니다. Image_URL에는 이미지 URL 또는 업로드한 이미지 파일명을 입력할 수 있습니다.")
        events_df = st.data_editor(
            ensure_event_columns(events_df),
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Include": st.column_config.SelectboxColumn("Include", options=["Y", "N"], default="Y"),
                "Section_Order": st.column_config.NumberColumn("Section_Order", min_value=1, step=1),
                "Item_Order": st.column_config.NumberColumn("Item_Order", min_value=1, step=1),
                "Start_Date": st.column_config.DateColumn("Start_Date", format="YYYY-MM-DD"),
                "End_Date": st.column_config.DateColumn("End_Date", format="YYYY-MM-DD"),
                "Detail_URL": st.column_config.LinkColumn("Detail_URL"),
                "Image_URL": st.column_config.TextColumn("Image_URL / Image_File", help="URL 또는 사이드바에 업로드한 이미지 파일명"),
            },
            key="events_editor",
        )

    lms_message = build_lms_message(settings, sections_df, events_df)
    highlight_html = build_highlight_html(settings, sections_df, events_df, image_lookup)

    with tab_preview:
        st.subheader("하이라이트 페이지 미리보기")
        st.markdown(highlight_html, unsafe_allow_html=True)

    with tab_lms:
        max_len = settings.get("Max_LMS_Length", 2000)
        status = "OK" if len(lms_message) <= max_len else "검토 필요"
        st.metric("문자수", len(lms_message), f"기준 {max_len} / {status}")
        st.text_area("생성된 LMS 홍보 문안", lms_message, height=620)

    with tab_export:
        st.subheader("다운로드")
        st.download_button(
            "LMS 문안 TXT 다운로드",
            data=lms_message.encode("utf-8-sig"),
            file_name=f"lms_message_{clean_text(settings.get('Week_Label')) or 'week'}.txt",
            mime="text/plain",
        )
        st.download_button(
            "하이라이트 HTML 다운로드",
            data=highlight_html.encode("utf-8"),
            file_name=f"highlight_page_{clean_text(settings.get('Week_Label')) or 'week'}.html",
            mime="text/html",
        )
        st.download_button(
            "수정 데이터 엑셀 다운로드",
            data=build_export_excel(settings_df, sections_df, events_df),
            file_name=f"highlight_lms_data_{clean_text(settings.get('Week_Label')) or 'week'}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.code(
            "streamlit run app.py",
            language="bash",
        )


if __name__ == "__main__":
    main()
