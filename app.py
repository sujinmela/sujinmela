import streamlit as st
import pandas as pd
from typing import List, Dict, Any

st.set_page_config(page_title="쇼핑뉴스 생성기", layout="wide")


def load_excel(uploaded_file):
    layout_df = pd.read_excel(uploaded_file, sheet_name="content_layout")
    products_df = pd.read_excel(uploaded_file, sheet_name="products")

    settings_df = None
    try:
        settings_df = pd.read_excel(uploaded_file, sheet_name="settings")
    except Exception:
        settings_df = pd.DataFrame(columns=["key", "value"])

    return layout_df, products_df, settings_df


DEFAULT_LAYOUT = pd.DataFrame([
    {
        "order": 1,
        "type": "hero",
        "title": "4월 쇼핑뉴스",
        "subtitle": "오늘만 만나는 인기 상품 특가",
        "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1400&q=80",
        "product_group": "",
        "note": "지금 바로 혜택을 확인해보세요",
    },
    {
        "order": 2,
        "type": "section",
        "title": "MD 추천 상품",
        "subtitle": "지금 가장 많이 보는 상품",
        "image_url": "",
        "product_group": "A",
        "note": "",
    },
    {
        "order": 3,
        "type": "banner",
        "title": "카드사 청구 할인",
        "subtitle": "일부 상품 최대 10% 추가 할인",
        "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1400&q=80",
        "product_group": "",
        "note": "행사카드 결제 시 자동 적용",
    },
    {
        "order": 4,
        "type": "section",
        "title": "오늘의 특가",
        "subtitle": "한정 수량 특가 상품",
        "image_url": "",
        "product_group": "B",
        "note": "",
    },
    {
        "order": 5,
        "type": "notice",
        "title": "꼭 확인하세요",
        "subtitle": "행사 유의사항",
        "image_url": "",
        "product_group": "",
        "note": "상품별 혜택 및 재고는 실시간으로 변동될 수 있습니다. 상세 내용은 각 상품 페이지에서 확인해주세요.",
    },
])

DEFAULT_PRODUCTS = pd.DataFrame([
    {
        "group": "A",
        "상품명": "프리미엄 셔츠",
        "브랜드": "SPARTA SELECT",
        "정가": 59000,
        "판매가": 39000,
        "할인율": "34%",
        "이미지URL": "https://images.unsplash.com/photo-1603252109303-2751441dd157?auto=format&fit=crop&w=900&q=80",
        "상품링크": "https://example.com/product-1",
        "뱃지": "무료배송",
        "설명": "데일리로 입기 좋은 베이직 핏 셔츠",
    },
    {
        "group": "A",
        "상품명": "데님 팬츠",
        "브랜드": "SPARTA DENIM",
        "정가": 79000,
        "판매가": 49000,
        "할인율": "38%",
        "이미지URL": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=80",
        "상품링크": "https://example.com/product-2",
        "뱃지": "MD추천",
        "설명": "핏과 착용감을 동시에 잡은 스테디셀러",
    },
    {
        "group": "A",
        "상품명": "클래식 스니커즈",
        "브랜드": "SPARTA SHOES",
        "정가": 89000,
        "판매가": 59000,
        "할인율": "33%",
        "이미지URL": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
        "상품링크": "https://example.com/product-3",
        "뱃지": "인기",
        "설명": "가볍고 어디에나 잘 어울리는 데일리 슈즈",
    },
    {
        "group": "B",
        "상품명": "미니 크로스백",
        "브랜드": "SPARTA BAG",
        "정가": 69000,
        "판매가": 45000,
        "할인율": "35%",
        "이미지URL": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=80",
        "상품링크": "https://example.com/product-4",
        "뱃지": "한정수량",
        "설명": "필수 소지품만 담아 가볍게 들기 좋은 백",
    },
    {
        "group": "B",
        "상품명": "무선 이어폰",
        "브랜드": "SPARTA SOUND",
        "정가": 129000,
        "판매가": 89000,
        "할인율": "31%",
        "이미지URL": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
        "상품링크": "https://example.com/product-5",
        "뱃지": "베스트",
        "설명": "출퇴근과 운동에 모두 잘 어울리는 가성비 모델",
    },
    {
        "group": "B",
        "상품명": "스마트 워치",
        "브랜드": "SPARTA TECH",
        "정가": 199000,
        "판매가": 149000,
        "할인율": "25%",
        "이미지URL": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
        "상품링크": "https://example.com/product-6",
        "뱃지": "사은품",
        "설명": "건강 관리와 알림 기능을 한 번에",
    },
])

DEFAULT_SETTINGS = {
    "brand_name": "LOTTE STYLE DEMO",
    "footer_text": "본 행사는 당사 사정에 따라 조기 종료될 수 있습니다.",
}


def settings_to_dict(settings_df: pd.DataFrame) -> Dict[str, Any]:
    if settings_df is None or settings_df.empty:
        return DEFAULT_SETTINGS.copy()
    if not {"key", "value"}.issubset(settings_df.columns):
        return DEFAULT_SETTINGS.copy()
    result = DEFAULT_SETTINGS.copy()
    for _, row in settings_df.iterrows():
        key = str(row.get("key", "")).strip()
        if key:
            result[key] = row.get("value", "")
    return result


st.markdown(
    """
    <style>
    .stApp {
        background-color: #f6f6f6;
    }
    .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 4rem;
    }
    .hero-wrap {
        position: relative;
        border-radius: 24px;
        overflow: hidden;
        margin-bottom: 28px;
        background: #111;
        min-height: 360px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    .hero-wrap img {
        width: 100%;
        height: 360px;
        object-fit: cover;
        display: block;
        filter: brightness(0.78);
    }
    .hero-content {
        position: absolute;
        left: 40px;
        bottom: 36px;
        color: white;
    }
    .hero-kicker {
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.08em;
        opacity: 0.9;
        margin-bottom: 10px;
    }
    .hero-title {
        font-size: 40px;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 18px;
        opacity: 0.95;
    }
    .section-wrap {
        margin: 34px 0 16px;
    }
    .section-title {
        font-size: 28px;
        font-weight: 800;
        color: #111;
        margin-bottom: 6px;
    }
    .section-subtitle {
        color: #666;
        font-size: 15px;
        margin-bottom: 12px;
    }
    .product-card {
        background: #fff;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 8px 22px rgba(0,0,0,0.06);
        margin-bottom: 22px;
        border: 1px solid #ececec;
    }
    .product-image {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        background: #fafafa;
        display: block;
    }
    .product-body {
        padding: 18px 18px 20px;
    }
    .badge {
        display: inline-block;
        background: #111;
        color: #fff;
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .brand {
        color: #888;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
        text-transform: uppercase;
    }
    .name {
        color: #111;
        font-size: 18px;
        font-weight: 800;
        line-height: 1.35;
        min-height: 48px;
        margin-bottom: 8px;
    }
    .desc {
        color: #666;
        font-size: 14px;
        line-height: 1.45;
        min-height: 42px;
        margin-bottom: 14px;
    }
    .price-line {
        display: flex;
        gap: 10px;
        align-items: baseline;
        flex-wrap: wrap;
    }
    .sale-rate {
        color: #e60023;
        font-size: 22px;
        font-weight: 800;
    }
    .sale-price {
        color: #111;
        font-size: 24px;
        font-weight: 900;
    }
    .origin-price {
        color: #999;
        text-decoration: line-through;
        font-size: 14px;
        margin-top: 4px;
    }
    .banner-wrap {
        position: relative;
        border-radius: 22px;
        overflow: hidden;
        margin: 28px 0;
        background: #1f1f1f;
        min-height: 180px;
    }
    .banner-wrap img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        display: block;
        filter: brightness(0.72);
    }
    .banner-content {
        position: absolute;
        left: 28px;
        bottom: 24px;
        color: white;
    }
    .banner-title {
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 6px;
    }
    .banner-subtitle {
        font-size: 16px;
        opacity: 0.95;
    }
    .notice-box {
        background: #fff;
        border-radius: 20px;
        border: 1px solid #ececec;
        padding: 24px 26px;
        margin-top: 30px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.04);
    }
    .notice-title {
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .footer-box {
        color: #777;
        font-size: 13px;
        text-align: center;
        margin-top: 36px;
        padding-top: 18px;
    }
    a.product-link {
        text-decoration: none;
        color: inherit;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.sidebar.title("설정")
use_demo = st.sidebar.toggle("샘플 데이터로 보기", value=True)
uploaded_file = st.sidebar.file_uploader("엑셀 업로드", type=["xlsx"])
show_raw_data = st.sidebar.checkbox("원본 데이터 보기", value=False)
columns_per_row = st.sidebar.selectbox("카드 개수", [2, 3, 4], index=1)

if uploaded_file is not None:
    try:
        layout_df, products_df, settings_df = load_excel(uploaded_file)
        settings = settings_to_dict(settings_df)
        data_source = "업로드한 엑셀"
    except Exception as e:
        st.sidebar.error(f"엑셀을 읽는 중 오류가 발생했습니다: {e}")
        layout_df, products_df = DEFAULT_LAYOUT.copy(), DEFAULT_PRODUCTS.copy()
        settings = DEFAULT_SETTINGS.copy()
        data_source = "기본 샘플 데이터"
elif use_demo:
    layout_df, products_df = DEFAULT_LAYOUT.copy(), DEFAULT_PRODUCTS.copy()
    settings = DEFAULT_SETTINGS.copy()
    data_source = "기본 샘플 데이터"
else:
    st.info("왼쪽에서 샘플 데이터를 켜거나 엑셀 파일을 업로드해주세요.")
    st.stop()

st.caption(f"현재 데이터: {data_source}")


def format_won(value: Any) -> str:
    try:
        return f"{int(value):,}원"
    except Exception:
        return str(value)


def render_hero(row: pd.Series):
    brand = settings.get("brand_name", "SHOPPING NEWS")
    st.markdown(
        f"""
        <div class="hero-wrap">
            <img src="{row.get('image_url', '')}" alt="hero">
            <div class="hero-content">
                <div class="hero-kicker">{brand}</div>
                <div class="hero-title">{row.get('title', '')}</div>
                <div class="hero-subtitle">{row.get('subtitle', '')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_banner(row: pd.Series):
    st.markdown(
        f"""
        <div class="banner-wrap">
            <img src="{row.get('image_url', '')}" alt="banner">
            <div class="banner-content">
                <div class="banner-title">{row.get('title', '')}</div>
                <div class="banner-subtitle">{row.get('subtitle', '')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_section_title(row: pd.Series):
    st.markdown(
        f"""
        <div class="section-wrap">
            <div class="section-title">{row.get('title', '')}</div>
            <div class="section-subtitle">{row.get('subtitle', '')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def product_card_html(product: pd.Series) -> str:
    badge = product.get("뱃지", "")
    brand = product.get("브랜드", "")
    name = product.get("상품명", "")
    desc = product.get("설명", "")
    sale_rate = product.get("할인율", "")
    sale_price = format_won(product.get("판매가", ""))
    origin_price = format_won(product.get("정가", ""))
    image_url = product.get("이미지URL", "")
    link = product.get("상품링크", "#")
    badge_html = f'<div class="badge">{badge}</div>' if str(badge).strip() else ''

    return f"""
    <a class="product-link" href="{link}" target="_blank">
        <div class="product-card">
            <img class="product-image" src="{image_url}" alt="{name}">
            <div class="product-body">
                {badge_html}
                <div class="brand">{brand}</div>
                <div class="name">{name}</div>
                <div class="desc">{desc}</div>
                <div class="price-line">
                    <span class="sale-rate">{sale_rate}</span>
                    <span class="sale-price">{sale_price}</span>
                </div>
                <div class="origin-price">{origin_price}</div>
            </div>
        </div>
    </a>
    """



def render_products(group_name: str):
    group_df = products_df[products_df["group"].astype(str) == str(group_name)].reset_index(drop=True)
    if group_df.empty:
        st.warning(f"group '{group_name}' 에 해당하는 상품이 없습니다.")
        return

    for start in range(0, len(group_df), columns_per_row):
        cols = st.columns(columns_per_row)
        chunk = group_df.iloc[start:start + columns_per_row]
        for idx, (_, product) in enumerate(chunk.iterrows()):
            with cols[idx]:
                st.markdown(product_card_html(product), unsafe_allow_html=True)



def render_notice(row: pd.Series):
    note = row.get("note", "")
    st.markdown(
        f"""
        <div class="notice-box">
            <div class="notice-title">{row.get('title', '안내')}</div>
            <div style="color:#666; line-height:1.7; font-size:14px;">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


for _, row in layout_df.sort_values("order").iterrows():
    block_type = str(row.get("type", "")).strip().lower()

    if block_type == "hero":
        render_hero(row)
    elif block_type == "banner":
        render_banner(row)
    elif block_type == "section":
        render_section_title(row)
        render_products(row.get("product_group", ""))
    elif block_type == "notice":
        render_notice(row)

st.markdown(
    f"""
    <div class="footer-box">{settings.get('footer_text', '')}</div>
    """,
    unsafe_allow_html=True,
)

with st.expander("엑셀 템플릿 컬럼 가이드"):
    st.markdown(
        """
        **content_layout 시트**
        - `order`: 노출 순서
        - `type`: `hero`, `section`, `banner`, `notice`
        - `title`: 블록 제목
        - `subtitle`: 보조 문구
        - `image_url`: hero/banner 이미지 URL
        - `product_group`: section에 연결할 상품 그룹 코드
        - `note`: notice 문구

        **products 시트**
        - `group`: 섹션 연결 그룹 코드
        - `상품명`, `브랜드`, `정가`, `판매가`, `할인율`, `이미지URL`, `상품링크`, `뱃지`, `설명`

        **settings 시트**
        - `key`, `value`
        - 예: `brand_name`, `footer_text`
        """
    )

if show_raw_data:
    st.subheader("content_layout")
    st.dataframe(layout_df, use_container_width=True)
    st.subheader("products")
    st.dataframe(products_df, use_container_width=True)
