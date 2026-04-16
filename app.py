import streamlit as st
import pandas as pd

st.set_page_config(page_title="쇼핑뉴스 생성기", layout="wide")

st.title("🛍️ 쇼핑뉴스 자동 생성기")

st.write("엑셀 파일을 업로드하면 쇼핑뉴스 콘텐츠를 자동 생성합니다.")

# 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx", "csv"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
    except:
        df = pd.read_csv(uploaded_file)

    st.subheader("📊 업로드된 데이터")
    st.dataframe(df)

    st.subheader("📰 생성된 쇼핑뉴스")

    # 간단한 뉴스 생성 로직
    for idx, row in df.iterrows():
        st.markdown(f"""
        ### {row.get('상품명', '상품명 없음')}
        - 💰 가격: {row.get('가격', '정보 없음')}
        - 🏷️ 할인: {row.get('할인율', '정보 없음')}
        - 📦 설명: {row.get('설명', '설명 없음')}
        ---
        """)

    # 카카오/LMS 메시지 예시
    st.subheader("📩 마케팅 메시지")

    for idx, row in df.iterrows():
        message = f"[특가] {row.get('상품명')} {row.get('가격')}원! 지금 확인하세요 👉"
        st.code(message)

else:
    st.info("엑셀 파일을 업로드해주세요.")
