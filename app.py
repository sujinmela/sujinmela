
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Lotte Highlight CMS",
    layout="wide"
)

st.title("🛍️ Lotte Highlight CMS")

uploaded = st.file_uploader(
    "업그레이드된 엑셀 템플릿 업로드",
    type=["xlsx"]
)

if not uploaded:
    st.info("업그레이드된 엑셀 템플릿을 업로드 해주세요.")
    st.stop()

xls = pd.ExcelFile(uploaded)

settings_df = pd.read_excel(xls, sheet_name="Settings")
sections_df = pd.read_excel(xls, sheet_name="Sections")
highlight_df = pd.read_excel(xls, sheet_name="Highlight_Input")

highlight_df = highlight_df.fillna("")

highlight_df = highlight_df[
    highlight_df["Include"].astype(str).str.upper() == "Y"
]

# Sidebar filters
st.sidebar.header("필터")

branches = ["전체"] + sorted(
    [x for x in highlight_df["Branch"].unique() if x]
)

selected_branch = st.sidebar.selectbox(
    "지점 선택",
    branches
)

if selected_branch != "전체":
    highlight_df = highlight_df[
        highlight_df["Branch"] == selected_branch
    ]

sections = sorted(
    highlight_df["Section_Title"].unique()
)

tab_list = st.tabs(sections)

for idx, section_name in enumerate(sections):

    with tab_list[idx]:

        section_df = highlight_df[
            highlight_df["Section_Title"] == section_name
        ].sort_values("Item_Order")

        cols = st.columns(3)

        for i, (_, row) in enumerate(section_df.iterrows()):

            with cols[i % 3]:

                image_url = (
                    row["Thumbnail_Image_URL"]
                    if row["Thumbnail_Image_URL"]
                    else row["Image_URL"]
                )

                if image_url:
                    st.image(image_url, use_container_width=True)

                st.markdown(
                    f"### {row['Event_Title']}"
                )

                st.caption(
                    f"{row['Branch']} · {row['Brand_Label']}"
                )

                if row["Tag_List"]:
                    tags = row["Tag_List"].split(",")
                    tag_html = " ".join(
                        [
                            f"<span style='background:#f2f2f2;padding:4px 8px;border-radius:999px;margin-right:6px;font-size:12px'>{tag.strip()}</span>"
                            for tag in tags
                        ]
                    )
                    st.markdown(tag_html, unsafe_allow_html=True)

                st.write(row["Highlight_Copy"])

                with st.expander("상세 보기"):

                    st.markdown(
                        f"""
                        #### {row['Event_Title']}

                        **운영기간**  
                        {row['Start_Date']} ~ {row['End_Date']}

                        **위치**  
                        {row['Location']}
                        """,
                        unsafe_allow_html=True
                    )

                    if row["Detail_HTML"]:
                        st.markdown(
                            row["Detail_HTML"],
                            unsafe_allow_html=True
                        )

                    if row["Detail_URL"]:
                        button_label = (
                            row["Button_Label"]
                            if row["Button_Label"]
                            else "상세 쇼핑뉴스 이동"
                        )

                        target = (
                            row["External_Link_Target"]
                            if row["External_Link_Target"]
                            else "_blank"
                        )

                        st.markdown(
                            f"""
                            <a href="{row['Detail_URL']}" target="{target}">
                                <button style="
                                    background:#e60012;
                                    color:white;
                                    border:none;
                                    padding:10px 18px;
                                    border-radius:10px;
                                    cursor:pointer;
                                    width:100%;
                                    font-size:15px;
                                    font-weight:600;
                                ">
                                    {button_label}
                                </button>
                            </a>
                            """,
                            unsafe_allow_html=True
                        )

st.success("쇼핑뉴스 상세 연결 및 하이라이트 렌더링 완료")
