# app.py

import streamlit as st
from datetime import datetime
import random

st.set_page_config(
    page_title="오늘의 라이프스타일 운세",
    page_icon="✨",
    layout="wide"
)

FORTUNE_MESSAGES = [
    "새로운 스타일 변화가 행운을 부르는 하루예요.",
    "감각적인 선택이 당신을 더욱 빛나게 만들어줄 거예요.",
    "오늘은 새로운 공간에서 좋은 영감을 얻을 가능성이 높아요.",
    "당신의 취향이 특별한 매력을 만들어주는 날이에요.",
]

LUCKY_COLORS = [
    ("Pink", "#ff77b7"),
    ("Gold", "#e3b341"),
    ("Lavender", "#b48cff"),
    ("Mint", "#63d1b2"),
]

LUCKY_ITEMS = [
    "액세서리",
    "향수",
    "가방",
    "커피",
    "디저트",
]

SHOPPING_TYPES = [
    "럭셔리 취향형",
    "트렌드 리더형",
    "감성 소비형",
    "미니멀 쇼퍼형",
]

TIPS = [
    "오늘은 나 자신을 위한 작은 선물을 준비해보세요.",
    "새로운 브랜드를 둘러보면 좋은 영감을 얻을 수 있어요.",
    "감각적인 액세서리가 오늘의 분위기를 완성해줄 거예요.",
]

st.markdown("<h1 style='text-align:center;'>✨ 오늘의 쇼핑 운세 ✨</h1>", unsafe_allow_html=True)

with st.form("fortune_form"):
    name = st.text_input("이름")
    birth = st.date_input("생년월일")
    submitted = st.form_submit_button("운세 확인하기")

if submitted:

    seed = int(birth.strftime("%Y%m%d")) + len(name)
    random.seed(seed)

    fortune = random.choice(FORTUNE_MESSAGES)
    color_name, color_code = random.choice(LUCKY_COLORS)
    item = random.choice(LUCKY_ITEMS)
    shopping_type = random.choice(SHOPPING_TYPES)
    tip = random.choice(TIPS)

    st.markdown(f'''
    <div style="background:white;padding:40px;border-radius:30px;">
        <h1>{name}님의 오늘 운세</h1>
        <h2>{fortune}</h2>
    </div>
    ''', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("럭키 컬러", color_name)

    with c2:
        st.metric("추천 아이템", item)

    with c3:
        st.metric("소비 성향", shopping_type)

    with c4:
        st.metric("오늘의 팁", "Lucky")

    st.info(tip)
