import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

st.set_page_config(
    page_title="쇼핑 하이라이트 LMS 생성기",
    page_icon="🛍️",
    layout="wide"
)

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

st.title("🛍️ 쇼핑 하이라이트 LMS 생성기")
st.caption("쇼핑 하이라이트 URL만 입력하면 LMS 광고문안을 자동 생성합니다.")

url = st.text_input(
    "쇼핑 하이라이트 URL 입력",
    placeholder="https://www.lotteshopping.com/..."
)

store_name = st.text_input(
    "발송 점포명",
    value="롯데백화점 본점"
)

customer_name = st.text_input(
    "고객명",
    value="고객"
)

if st.button("LMS 생성하기"):

    with st.spinner("쇼핑 하이라이트 분석중..."):

        try:
            html = requests.get(url).text

            soup = BeautifulSoup(html, "html.parser")

            page_text = soup.get_text(
                separator="\n",
                strip=True
            )

            prompt = f"""
            아래 쇼핑 하이라이트 내용을 분석하여
            LMS 광고문안을 작성해줘.

            규칙

            1. 점포명 사용
            2. 행사 카테고리별 정리
            3. 중요 행사만 추출
            4. LMS 길이에 맞게 요약
            5. 아래 형식 유지

            형식

            (광고){store_name}

            {customer_name} 고객님 안녕하세요.
            이번주 {store_name} 소식을 안내드립니다.

            [Special Gift]
            ...

            [Brand News]
            ...

            자세한 사항은 아래 링크를 확인해주세요.
            {url}

            문의전화 1577-0001
            무료수신거부 080-880-2626

            쇼핑하이라이트 원문

            {page_text[:20000]}
            """

            response = client.chat.completions.create(
                model="gpt-5.5",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            result = response.choices[0].message.content

            st.success("생성 완료")

            st.text_area(
                "생성된 LMS",
                value=result,
                height=600
            )

            st.download_button(
                "TXT 다운로드",
                result,
                file_name="lms_message.txt"
            )

        except Exception as e:
            st.error(str(e))
