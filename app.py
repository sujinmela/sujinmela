import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import streamlit as st

st.set_page_config(page_title="쇼핑뉴스 생성기", layout="wide")


LAYOUT_COLUMNS = [
    "order",
    "type",
    "title",
    "subtitle",
    "image_path",
    "image_url",
    "product_group",
    "note",
    "background",
    "more_label",
    "more_url",
    "link_url",
]

PRODUCT_COLUMNS = [
    "group",
    "상품ID",
    "브랜드",
    "상품명",
    "설명",
    "정가",
    "판매가",
    "할인율",
    "뱃지",
    "이미지파일",
    "이미지경로",
    "이미지URL",
    "상품링크",
    "혜택",
]

DEFAULT_LAYOUT = pd.DataFrame(
    [
        {
            "order": 1,
            "type": "hero",
            "title": "WEEKLY SHOPPING NEWS",
            "subtitle": "이번 주 꼭 봐야 할 인기 상품과 혜택",
            "image_path": "images/hero_main.jpg",
            "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1400&q=80",
            "product_group": "",
            "note": "쇼핑뉴스 메인 비주얼",
            "background": "#111111",
            "more_label": "",
            "more_url": "",
            "link_url": "",
        },
        {
            "order": 2,
            "type": "section",
            "title": "MD 추천 상품",
            "subtitle": "지금 가장 반응이 좋은 베스트 셀렉션",
            "image_path": "",
            "image_url": "",
            "product_group": "A",
            "note": "",
            "background": "",
            "more_label": "",
            "more_url": "",
            "link_url": "",
        },
        {
            "order": 3,
            "type": "banner",
            "title": "카드사 추가 할인",
            "subtitle": "행사 카드 결제 시 최대 10% 청구 할인",
            "image_path": "images/banner_card.jpg",
            "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1400&q=80",
            "product_group": "",
            "note": "배너/혜택 영역",
            "background": "#1f1f1f",
            "more_label": "",
            "more_url": "",
            "link_url": "https://www.google.com/",
        },
        {
            "order": 4,
            "type": "section",
            "title": "오늘의 특가",
            "subtitle": "한정 수량으로 준비한 추천 상품",
            "image_path": "",
            "image_url": "",
            "product_group": "B",
            "note": "",
            "background": "",
            "more_label": "",
            "more_url": "",
            "link_url": "",
        },
        {
            "order": 5,
            "type": "section",
            "title": "라스트 아이템",
            "subtitle": "마감 전에 꼭 확인해야 할 마지막 추천 아이템",
            "image_path": "",
            "image_url": "",
            "product_group": "C",
            "note": "",
            "background": "",
            "more_label": "",
            "more_url": "",
            "link_url": "",
        },
        {
            "order": 6,
            "type": "notice",
            "title": "꼭 확인하세요",
            "subtitle": "",
            "image_path": "",
            "image_url": "",
            "product_group": "",
            "note": "상품별 혜택 및 재고는 실시간으로 변동될 수 있습니다. 상세 내용은 각 상품 페이지에서 확인해주세요.",
            "background": "",
            "more_label": "",
            "more_url": "",
            "link_url": "",
        },
    ],
    columns=LAYOUT_COLUMNS,
)

DEFAULT_PRODUCTS = pd.DataFrame(
    [
        {
            "group": "A",
            "상품ID": "A001",
            "브랜드": "SPARTA SELECT",
            "상품명": "프리미엄 셔츠",
            "설명": "데일리로 입기 좋은 베이직 셔츠",
            "정가": 59000,
            "판매가": 39000,
            "할인율": "34%",
            "뱃지": "무료배송",
            "이미지파일": "shirt.jpg",
            "이미지경로": "images/products/shirt.jpg",
            "이미지URL": "https://images.unsplash.com/photo-1603252109303-2751441dd157?auto=format&fit=crop&w=900&q=80",
            "상품링크": "https://example.com/product-1",
            "혜택": "카드 5% 추가",
        },
        {
            "group": "A",
            "상품ID": "A002",
            "브랜드": "SPARTA DENIM",
            "상품명": "데님 팬츠",
            "설명": "핏과 착용감을 동시에 잡은 스테디셀러",
            "정가": 79000,
            "판매가": 49000,
            "할인율": "38%",
            "뱃지": "MD추천",
            "이미지파일": "denim.jpg",
            "이미지경로": "images/products/denim.jpg",
            "이미지URL": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=80",
            "상품링크": "https://example.com/product-2",
            "혜택": "무료배송",
        },
        {
            "group": "A",
            "상품ID": "A003",
            "브랜드": "SPARTA SHOES",
            "상품명": "클래식 스니커즈",
            "설명": "가볍고 어디에나 잘 어울리는 데일리 슈즈",
            "정가": 89000,
            "판매가": 59000,
            "할인율": "33%",
            "뱃지": "인기",
            "이미지파일": "shoes.jpg",
            "이미지경로": "images/products/shoes.jpg",
            "이미지URL": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
            "상품링크": "https://example.com/product-3",
            "혜택": "사은품 증정",
        },
        {
            "group": "B",
            "상품ID": "B001",
            "브랜드": "SPARTA BAG",
            "상품명": "미니 크로스백",
            "설명": "필수 소지품만 담아 가볍게 들기 좋은 가방",
            "정가": 69000,
            "판매가": 45000,
            "할인율": "35%",
            "뱃지": "한정수량",
            "이미지파일": "bag.jpg",
            "이미지경로": "images/products/bag.jpg",
            "이미지URL": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=80",
            "상품링크": "https://example.com/product-4",
            "혜택": "장바구니 2천원",
        },
        {
            "group": "B",
            "상품ID": "B002",
            "브랜드": "SPARTA SOUND",
            "상품명": "무선 이어폰",
            "설명": "출퇴근과 이동 시 모두 잘 어울리는 가성비 모델",
            "정가": 129000,
            "판매가": 89000,
            "할인율": "31%",
            "뱃지": "베스트",
            "이미지파일": "earbuds.jpg",
            "이미지경로": "images/products/earbuds.jpg",
            "이미지URL": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
            "상품링크": "https://example.com/product-5",
            "혜택": "무료배송",
        },
        {
            "group": "B",
            "상품ID": "B003",
            "브랜드": "SPARTA TECH",
            "상품명": "스마트 워치",
            "설명": "건강 관리와 알림 기능까지 담은 실속형 워치",
            "정가": 199000,
            "판매가": 149000,
            "할인율": "25%",
            "뱃지": "추천",
            "이미지파일": "watch.jpg",
            "이미지경로": "images/products/watch.jpg",
            "이미지URL": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
            "상품링크": "https://example.com/product-6",
            "혜택": "스트랩 증정",
        },
        {
            "group": "C",
            "상품ID": "C001",
            "브랜드": "SPARTA HOME",
            "상품명": "컴팩트 무드 램프",
            "설명": "침실과 거실 어디에나 어울리는 감성 조명",
            "정가": 54000,
            "판매가": 35000,
            "할인율": "35%",
            "뱃지": "LAST ITEM",
            "이미지파일": "lamp.jpg",
            "이미지경로": "images/products/lamp.jpg",
            "이미지URL": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80",
            "상품링크": "https://example.com/product-7",
            "혜택": "한정 수량",
        },
        {
            "group": "C",
            "상품ID": "C002",
            "브랜드": "SPARTA LIVING",
            "상품명": "소프트 블랭킷",
            "설명": "가볍고 포근하게 활용하기 좋은 데일리 담요",
            "정가": 47000,
            "판매가": 29000,
            "할인율": "38%",
            "뱃지": "마감임박",
            "이미지파일": "blanket.jpg",
            "이미지경로": "images/products/blanket.jpg",
            "이미지URL": "https://images.unsplash.com/photo-1517705008128-361805f42e86?auto=format&fit=crop&w=900&q=80",
            "상품링크": "https://example.com/product-8",
            "혜택": "즉시 할인",
        },
        {
            "group": "C",
            "상품ID": "C003",
            "브랜드": "SPARTA TABLE",
            "상품명": "세라믹 머그 세트",
            "설명": "집들이 선물로도 좋은 미니멀 머그컵 구성",
            "정가": 39000,
            "판매가": 25000,
            "할인율": "36%",
            "뱃지": "재입고",
            "이미지파일": "mug.jpg",
            "이미지경로": "images/products/mug.jpg",
            "이미지URL": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80",
            "상품링크": "https://example.com/product-9",
            "혜택": "세트 특가",
        },
    ],
    columns=PRODUCT_COLUMNS,
)

DEFAULT_SETTINGS = {
    "brand_name": "LOTTE STYLE DEMO",
    "footer_text": "본 행사는 당사 사정에 따라 조기 종료될 수 있습니다.",
    "image_base_path": ".",
    "image_mode": "local_first",
    "kakao_brand": "롯데백화점",
    "lms_sender": "롯데백화점",
}

SECTION_MORE_LINKS = {
    "MD 추천 상품": {
        "label": "더보기",
        "url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0339&cntsTpCd=C00903",
    }
}


def load_excel(uploaded_file):
    workbook = pd.ExcelFile(uploaded_file)
    layout_df = pd.read_excel(uploaded_file, sheet_name="content_layout").fillna("")
    products_df = pd.read_excel(uploaded_file, sheet_name="products").fillna("")

    def read_optional(sheet_name: str) -> pd.DataFrame:
        if sheet_name in workbook.sheet_names:
            return pd.read_excel(uploaded_file, sheet_name=sheet_name).fillna("")
        return pd.DataFrame()

    return (
        layout_df,
        products_df,
        read_optional("settings"),
        read_optional("kakao_messages"),
        read_optional("lms_messages"),
    )


def settings_to_dict(settings_df: pd.DataFrame) -> Dict[str, Any]:
    result = DEFAULT_SETTINGS.copy()
    if not settings_df.empty and {"key", "value"}.issubset(settings_df.columns):
        for _, row in settings_df.iterrows():
            key = str(row.get("key", "")).strip()
            if key:
                result[key] = row.get("value", "")
    return result


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_section_title(value: Any) -> str:
    title = normalize_text(value)
    if title == "라스트 아이템 리스트":
        return "라스트 아이템"
    return title


def format_won(value: Any) -> str:
    try:
        return f"{int(float(value)):,}원"
    except Exception:
        return str(value)


def ensure_layout_columns(layout_df: pd.DataFrame) -> pd.DataFrame:
    df = layout_df.copy()
    for column in LAYOUT_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[LAYOUT_COLUMNS].fillna("")


def ensure_product_columns(products_df: pd.DataFrame) -> pd.DataFrame:
    df = products_df.copy()
    for column in PRODUCT_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[PRODUCT_COLUMNS].fillna("")


def image_file_to_data_uri(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    mime_type, _ = mimetypes.guess_type(path.name)
    mime_type = mime_type or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def resolve_image_src(row: pd.Series, settings: Dict[str, Any], path_key: str, url_key: str) -> str:
    mode = normalize_text(settings.get("image_mode", "local_first")).lower()
    base_path = Path(normalize_text(settings.get("image_base_path", ".")) or ".")
    image_path_raw = normalize_text(row.get(path_key, ""))
    image_url = normalize_text(row.get(url_key, ""))
    local_src = None

    if image_path_raw:
        raw_path = Path(image_path_raw)
        candidates = [raw_path] if raw_path.is_absolute() else [base_path / raw_path, raw_path]
        for candidate in candidates:
            data_uri = image_file_to_data_uri(candidate)
            if data_uri:
                local_src = data_uri
                break

    if mode == "local_only":
        return local_src or ""
    if mode == "url_only":
        return image_url
    return local_src or image_url


def build_image_html(
    src: str,
    alt: str,
    image_classes: str,
    fallback_classes: str,
    fallback_style: str = "",
) -> str:
    if src:
        return f'<img class="{image_classes}" src="{src}" alt="{alt}">'
    style_attr = f' style="{fallback_style}"' if fallback_style else ""
    return f'<div class="{fallback_classes}"{style_attr}></div>'


def render_image_block(src: str, alt: str, fallback_bg: str, variant: str) -> str:
    if variant == "hero":
        return build_image_html(
            src=src,
            alt=alt,
            image_classes="product-image hero-image",
            fallback_classes="image-fallback hero-fallback",
            fallback_style=f"background:{fallback_bg};",
        )
    return build_image_html(
        src=src,
        alt=alt,
        image_classes="product-image banner-image",
        fallback_classes="image-fallback banner-fallback",
        fallback_style=f"background:{fallback_bg};",
    )


def make_auto_kakao(products_df: pd.DataFrame, settings: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    brand = normalize_text(settings.get("kakao_brand", settings.get("brand_name", "쇼핑뉴스")))
    for _, row in products_df.head(6).iterrows():
        rows.append(
            {
                "seq": len(rows) + 1,
                "구분": "친구톡",
                "메시지명": f"{normalize_text(row.get('상품명'))} 카카오 발송안",
                "타이틀": f"{brand} {normalize_text(row.get('상품명'))}",
                "본문": (
                    f"{normalize_text(row.get('상품명'))} {format_won(row.get('판매가'))} / "
                    f"{normalize_text(row.get('할인율'))}\n"
                    f"{normalize_text(row.get('혜택'))} 혜택까지 확인해보세요."
                ),
                "버튼명": "지금 확인하기",
                "버튼링크": normalize_text(row.get("상품링크")),
                "대상상품ID": normalize_text(row.get("상품ID")),
            }
        )
    return pd.DataFrame(rows)


def make_auto_lms(products_df: pd.DataFrame, settings: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    sender = normalize_text(settings.get("lms_sender", settings.get("brand_name", "쇼핑뉴스")))
    for _, row in products_df.head(6).iterrows():
        rows.append(
            {
                "seq": len(rows) + 1,
                "발송구분": "LMS",
                "메시지명": f"{normalize_text(row.get('상품명'))} LMS 발송안",
                "발신프로필": sender,
                "본문": (
                    f"[{sender}] {normalize_text(row.get('상품명'))}\n"
                    f"{normalize_text(row.get('설명'))}\n"
                    f"판매가 {format_won(row.get('판매가'))} ({normalize_text(row.get('할인율'))})\n"
                    f"혜택: {normalize_text(row.get('혜택'))}\n"
                    f"구매링크: {normalize_text(row.get('상품링크'))}"
                ),
                "대상상품ID": normalize_text(row.get("상품ID")),
            }
        )
    return pd.DataFrame(rows)


def get_section_more_config(row: pd.Series) -> Tuple[str, str]:
    more_url = normalize_text(row.get("more_url", ""))
    more_label = normalize_text(row.get("more_label", "")) or "더보기"
    if more_url:
        return more_label, more_url

    title = normalize_text(row.get("title", ""))
    config = SECTION_MORE_LINKS.get(title, {})
    if config.get("url"):
        return config.get("label", "더보기"), config["url"]
    return "", ""


def get_banner_title_link(row: pd.Series) -> str:
    title = normalize_text(row.get("title", ""))
    if title == "카드사 추가 할인":
        return "https://www.google.com/"
    return normalize_text(row.get("link_url", ""))


st.markdown(
    """
<style>
.stApp { background-color:#f5f5f7; }
.block-container { max-width:1180px; padding-top:1.2rem; padding-bottom:4rem; }
.hero-wrap,.banner-wrap{position:relative;overflow:hidden;border-radius:24px;box-shadow:0 12px 36px rgba(0,0,0,0.12);}
.hero-wrap{margin-bottom:28px;min-height:380px;}
.banner-wrap{margin:30px 0;min-height:200px;}
.product-image{width:100%;display:block;object-fit:cover;object-position:center center;background:#fafafa;}
.hero-image{height:380px;filter:brightness(0.72);}
.banner-image{height:200px;filter:brightness(0.72);}
.product-image-frame{position:relative;width:100%;overflow:hidden;background:#fafafa;line-height:0;}
.card-image-frame{position:relative;width:100%;aspect-ratio:1/1;overflow:hidden;background:#fafafa;}
.card-image-frame .card-image,.card-image-frame .card-fallback{position:absolute;inset:0;width:100%;height:100%;}
.card-image{width:100%;height:100%;}
.image-fallback{width:100%;display:block;background:#fafafa;}
.hero-fallback{height:380px;}
.banner-fallback{height:200px;}
.card-fallback{width:100%;height:100%;min-height:100%;}
.product-image-frame .card-fallback{aspect-ratio:auto;}
.hero-content,.banner-content{position:absolute;left:40px;bottom:34px;color:white;}
.hero-kicker{display:inline-block;margin-bottom:12px;padding:7px 12px;border-radius:999px;background:rgba(255,255,255,0.16);font-size:12px;font-weight:700;letter-spacing:0.08em;}
.hero-title{font-size:42px;font-weight:800;line-height:1.12;margin-bottom:8px;}
.hero-subtitle{font-size:18px;opacity:0.97;}
.banner-title{font-size:30px;font-weight:800;margin-bottom:6px;}
.banner-title-link{color:inherit !important;text-decoration:none;}
.banner-title-link:hover{text-decoration:underline;}
.banner-subtitle{font-size:16px;opacity:0.95;}
.section-wrap{margin:36px 0 16px;}
.section-head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;}
.section-meta{flex:1 1 auto;min-width:240px;}
.section-title{font-size:28px;font-weight:800;color:#111;margin-bottom:6px;}
.section-subtitle{color:#666;font-size:15px;}
.more-button{display:inline-flex;align-items:center;gap:8px;padding:11px 16px;border-radius:999px;background:#111;color:#fff !important;font-size:14px;font-weight:700;text-decoration:none;box-shadow:0 8px 18px rgba(0,0,0,0.12);transition:transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;white-space:nowrap;}
.more-button:hover{background:#2a2a2a;color:#fff !important;transform:translateY(-1px);box-shadow:0 10px 22px rgba(0,0,0,0.16);}
.more-button::after{content:"→";font-size:14px;line-height:1;}
.product-card{background:#fff;border-radius:22px;overflow:hidden;border:1px solid #ececec;box-shadow:0 10px 24px rgba(0,0,0,0.06);margin-bottom:22px;}
.product-body{padding:18px 18px 22px;}
.badge{display:inline-block;padding:5px 10px;border-radius:999px;background:#111;color:#fff;font-size:12px;font-weight:700;margin-bottom:12px;}
.brand{color:#888;font-size:12px;font-weight:700;letter-spacing:0.04em;margin-bottom:6px;text-transform:uppercase;}
.name{color:#111;font-size:18px;font-weight:800;line-height:1.35;min-height:48px;margin-bottom:8px;}
.desc{color:#666;font-size:14px;line-height:1.5;min-height:44px;margin-bottom:14px;}
.benefit{color:#444;font-size:13px;background:#f7f7f7;border-radius:12px;padding:8px 10px;margin-bottom:14px;}
.price-line{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;}
.sale-rate{color:#e60023;font-size:22px;font-weight:800;}
.sale-price{color:#111;font-size:24px;font-weight:900;}
.origin-price{color:#999;text-decoration:line-through;font-size:14px;margin-top:4px;}
.notice-box{background:#fff;border-radius:20px;border:1px solid #ececec;padding:24px 26px;margin-top:30px;box-shadow:0 8px 22px rgba(0,0,0,0.04);}
.notice-title{font-size:22px;font-weight:800;margin-bottom:10px;}
.footer-box{color:#777;font-size:13px;text-align:center;margin-top:38px;padding-top:18px;}
a.product-link{text-decoration:none;color:inherit;}
.helper-box{background:white;border:1px solid #ececec;border-radius:18px;padding:16px 18px;margin-bottom:16px;}
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
    layout_df, products_df, settings_df, kakao_df, lms_df = load_excel(uploaded_file)
    layout_df = ensure_layout_columns(layout_df)
    products_df = ensure_product_columns(products_df)
    settings = settings_to_dict(settings_df)
    data_source = "업로드한 엑셀"
elif use_demo:
    layout_df = DEFAULT_LAYOUT.copy()
    products_df = DEFAULT_PRODUCTS.copy()
    settings = DEFAULT_SETTINGS.copy()
    kakao_df = pd.DataFrame()
    lms_df = pd.DataFrame()
    data_source = "기본 샘플 데이터"
else:
    st.info("왼쪽 사이드바에서 샘플 데이터를 켜거나 엑셀 파일을 업로드해주세요.")
    st.stop()

if kakao_df.empty:
    kakao_df = make_auto_kakao(products_df, settings)
if lms_df.empty:
    lms_df = make_auto_lms(products_df, settings)

st.caption(f"현재 데이터: {data_source}")
preview_tab, kakao_tab, lms_tab, data_tab = st.tabs(
    ["쇼핑뉴스 미리보기", "카카오 메시지", "LMS 메시지", "데이터 확인"]
)

with preview_tab:
    st.markdown(
        """
    <div class="helper-box">
        <b>로컬 이미지 사용법</b><br>
        1) 앱 실행 폴더 기준으로 <code>images/</code> 폴더를 만듭니다.<br>
        2) 엑셀의 <code>image_path</code>, <code>이미지경로</code> 컬럼에 상대 경로를 적습니다.<br>
        3) <code>settings</code> 시트의 <code>image_base_path</code> 로 기준 폴더를 지정할 수 있습니다.<br>
        4) <code>image_mode</code> 는 <code>local_first</code>, <code>local_only</code>, <code>url_only</code> 중 선택합니다.<br>
        5) <code>content_layout</code> 시트에 <code>more_label</code>, <code>more_url</code> 컬럼을 넣으면 섹션별 더보기 버튼을 직접 제어할 수 있습니다.
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_hero(row: pd.Series) -> None:
    src = resolve_image_src(row, settings, "image_path", "image_url")
    bg = normalize_text(row.get("background", "#111111")) or "#111111"
    hero_title = normalize_section_title(row.get("title", ""))
    st.markdown(
        f"""
    <div class="hero-wrap">
        {render_image_block(src, hero_title, bg, "hero")}
        <div class="hero-content">
            <div class="hero-kicker">{settings.get("brand_name", "SHOPPING NEWS")}</div>
            <div class="hero-title">{hero_title}</div>
            <div class="hero-subtitle">{normalize_text(row.get("subtitle", ""))}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_banner(row: pd.Series) -> None:
    src = resolve_image_src(row, settings, "image_path", "image_url")
    bg = normalize_text(row.get("background", "#1f1f1f")) or "#1f1f1f"
    banner_title = normalize_section_title(row.get("title", ""))
    banner_link = get_banner_title_link(row)
    banner_title_html = (
        f'<a class="banner-title-link" href="{banner_link}" target="_blank" rel="noopener noreferrer">{banner_title}</a>'
        if banner_link
        else banner_title
    )
    st.markdown(
        f"""
    <div class="banner-wrap">
        {render_image_block(src, banner_title, bg, "banner")}
        <div class="banner-content">
            <div class="banner-title">{banner_title_html}</div>
            <div class="banner-subtitle">{normalize_text(row.get("subtitle", ""))}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def product_card_html(product: pd.Series) -> str:
    badge = normalize_text(product.get("뱃지", ""))
    benefit = normalize_text(product.get("혜택", ""))
    name = normalize_text(product.get("상품명", ""))
    src = resolve_image_src(product, settings, "이미지경로", "이미지URL")
    badge_html = f'<div class="badge">{badge}</div>' if badge else ""
    benefit_html = f'<div class="benefit">혜택 · {benefit}</div>' if benefit else ""
    image_html = build_image_html(
        src=src,
        alt=name,
        image_classes="product-image card-image",
        fallback_classes="image-fallback card-fallback",
    )
    image_html = f'<div class="product-image-frame card-image-frame">{image_html}</div>'
    return f"""
    <a class="product-link" href="{normalize_text(product.get('상품링크', '#'))}" target="_blank">
        <div class="product-card">
            {image_html}
            <div class="product-body">
                {badge_html}
                <div class="brand">{normalize_text(product.get("브랜드", ""))}</div>
                <div class="name">{name}</div>
                <div class="desc">{normalize_text(product.get("설명", ""))}</div>
                {benefit_html}
                <div class="price-line">
                    <span class="sale-rate">{normalize_text(product.get("할인율", ""))}</span>
                    <span class="sale-price">{format_won(product.get("판매가", ""))}</span>
                </div>
                <div class="origin-price">{format_won(product.get("정가", ""))}</div>
            </div>
        </div>
    </a>
    """


with preview_tab:
    for _, row in layout_df.sort_values("order").iterrows():
        block_type = normalize_text(row.get("type", "")).lower()
        if block_type == "hero":
            render_hero(row)
        elif block_type == "banner":
            render_banner(row)
        elif block_type == "section":
            more_label, more_url = get_section_more_config(row)
            more_button_html = (
                f'<a class="more-button" href="{more_url}" target="_blank" rel="noopener noreferrer">{more_label}</a>'
                if more_url
                else ""
            )
            st.markdown(
                f"""
            <div class="section-wrap">
                <div class="section-head">
                    <div class="section-meta">
                        <div class="section-title">{normalize_section_title(row.get("title", ""))}</div>
                        <div class="section-subtitle">{normalize_text(row.get("subtitle", ""))}</div>
                    </div>
                    {more_button_html}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            group_df = products_df[
                products_df["group"].astype(str) == str(row.get("product_group", ""))
            ].reset_index(drop=True)
            for start in range(0, len(group_df), columns_per_row):
                cols = st.columns(columns_per_row)
                chunk = group_df.iloc[start : start + columns_per_row]
                for idx, (_, product) in enumerate(chunk.iterrows()):
                    with cols[idx]:
                        st.markdown(product_card_html(product), unsafe_allow_html=True)
        elif block_type == "notice":
            st.markdown(
                f"""
            <div class="notice-box">
                <div class="notice-title">{normalize_section_title(row.get("title", "안내"))}</div>
                <div style="color:#666; line-height:1.7; font-size:14px;">{normalize_text(row.get("note", ""))}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown(f'<div class="footer-box">{settings.get("footer_text", "")}</div>', unsafe_allow_html=True)

with kakao_tab:
    st.subheader("카카오 메시지 발송안")
    st.dataframe(kakao_df, use_container_width=True)
    for _, row in kakao_df.iterrows():
        st.markdown(f"### {normalize_text(row.get('메시지명', '카카오 발송안'))}")
        st.code(
            f"[{normalize_text(settings.get('kakao_brand', '브랜드'))}] {normalize_text(row.get('타이틀', ''))}\n"
            f"{normalize_text(row.get('본문', ''))}\n"
            f"버튼: {normalize_text(row.get('버튼명', ''))} -> {normalize_text(row.get('버튼링크', ''))}",
            language="text",
        )

with lms_tab:
    st.subheader("LMS 메시지 발송안")
    st.dataframe(lms_df, use_container_width=True)
    for _, row in lms_df.iterrows():
        st.markdown(f"### {normalize_text(row.get('메시지명', 'LMS 발송안'))}")
        st.code(normalize_text(row.get("본문", "")), language="text")

with data_tab:
    if show_raw_data:
        st.subheader("content_layout")
        st.dataframe(layout_df, use_container_width=True)
        st.subheader("products")
        st.dataframe(products_df, use_container_width=True)
        st.subheader("settings")
        st.dataframe(pd.DataFrame(list(settings.items()), columns=["key", "value"]), use_container_width=True)
        st.subheader("kakao_messages")
        st.dataframe(kakao_df, use_container_width=True)
        st.subheader("lms_messages")
        st.dataframe(lms_df, use_container_width=True)
    else:
        st.info("왼쪽 사이드바에서 '원본 데이터 보기'를 켜면 시트별 데이터를 확인할 수 있습니다.")
