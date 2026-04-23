
import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

st.set_page_config(page_title="롯데형 콘텐츠 생성기", layout="wide")


def read_optional(xls: pd.ExcelFile, uploaded_file, sheet_name: str) -> pd.DataFrame:
    if sheet_name in xls.sheet_names:
        return pd.read_excel(uploaded_file, sheet_name=sheet_name).fillna("")
    return pd.DataFrame()


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def to_bool(value: Any, default: bool = True) -> bool:
    text = normalize_text(value).lower()
    if text in ["n", "no", "false", "0"]:
        return False
    if text in ["y", "yes", "true", "1"]:
        return True
    return default


def format_won(value: Any) -> str:
    try:
        return f"{int(float(value)):,}원"
    except Exception:
        return str(value)


def file_to_data_uri(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    mime, _ = mimetypes.guess_type(path.name)
    mime = mime or "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def settings_to_dict(df: pd.DataFrame, defaults: Dict[str, Any]) -> Dict[str, Any]:
    result = defaults.copy()
    if not df.empty and {"key", "value"}.issubset(df.columns):
        for _, row in df.iterrows():
            key = normalize_text(row.get("key", ""))
            if key:
                result[key] = row.get("value", "")
    return result


def resolve_image_src(row: pd.Series, settings: Dict[str, Any], path_key: str, url_key: str) -> str:
    mode = normalize_text(settings.get("image_mode", "local_first")).lower()
    base_path = Path(normalize_text(settings.get("image_base_path", ".")) or ".")
    image_path_raw = normalize_text(row.get(path_key, ""))
    image_url = normalize_text(row.get(url_key, ""))
    local_src = None

    if image_path_raw:
        p = Path(image_path_raw)
        candidates = [p] if p.is_absolute() else [base_path / p, p]
        for candidate in candidates:
            uri = file_to_data_uri(candidate)
            if uri:
                local_src = uri
                break

    if mode == "local_only":
        return local_src or ""
    if mode == "url_only":
        return image_url
    return local_src or image_url


DEFAULT_COMMON_SETTINGS = {
    "image_base_path": ".",
    "image_mode": "local_first",
}

DEFAULT_NEWS_SETTINGS = {
    **DEFAULT_COMMON_SETTINGS,
    "brand_name": "LOTTE STYLE DEMO",
    "footer_text": "본 행사는 당사 사정에 따라 조기 종료될 수 있습니다.",
    "kakao_brand": "롯데백화점",
    "lms_sender": "롯데백화점",
}

DEFAULT_INFO_SETTINGS = {
    **DEFAULT_COMMON_SETTINGS,
    "store_label": "백화점 본점",
    "page_title": "Shopping info",
    "page_eyebrow": "shopping",
    "page_description": "주요 행사와 혜택을 한눈에 확인하세요.",
    "default_more_label": "Read more",
    "cards_per_row": 3,
    "footer_text": "행사 내용은 당사 사정에 따라 변경될 수 있습니다.",
}

DEFAULT_LAYOUT = pd.DataFrame([
    {"order": 1, "type": "hero", "title": "WEEKLY SHOPPING NEWS", "subtitle": "이번 주 꼭 봐야 할 인기 상품과 혜택", "image_path": "images/hero_main.jpg", "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1400&q=80", "product_group": "", "note": "쇼핑뉴스 메인 비주얼", "background": "#111111", "more_label": "", "more_url": ""},
    {"order": 2, "type": "section", "title": "MD 추천 상품", "subtitle": "지금 가장 반응이 좋은 베스트 셀렉션", "image_path": "", "image_url": "", "product_group": "A", "note": "", "background": "", "more_label": "더보기", "more_url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0339&cntsTpCd=C00903"},
    {"order": 3, "type": "banner", "title": "카드사 추가 할인", "subtitle": "행사 카드 결제 시 최대 10% 청구 할인", "image_path": "images/banner_card.jpg", "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1400&q=80", "product_group": "", "note": "배너/혜택 영역", "background": "#1f1f1f", "more_label": "", "more_url": ""},
    {"order": 4, "type": "section", "title": "오늘의 특가", "subtitle": "한정 수량으로 준비한 추천 상품", "image_path": "", "image_url": "", "product_group": "B", "note": "", "background": "", "more_label": "", "more_url": ""},
    {"order": 5, "type": "notice", "title": "꼭 확인하세요", "subtitle": "", "image_path": "", "image_url": "", "product_group": "", "note": "상품별 혜택 및 재고는 실시간으로 변동될 수 있습니다. 상세 내용은 각 상품 페이지에서 확인해주세요.", "background": "", "more_label": "", "more_url": ""},
])

DEFAULT_PRODUCTS = pd.DataFrame([
    {"group": "A", "상품ID": "A001", "브랜드": "SPARTA SELECT", "상품명": "프리미엄 셔츠", "설명": "데일리로 입기 좋은 베이직 핏 셔츠", "정가": 59000, "판매가": 39000, "할인율": "34%", "뱃지": "무료배송", "이미지파일": "shirt.jpg", "이미지경로": "images/products/shirt.jpg", "이미지URL": "https://images.unsplash.com/photo-1603252109303-2751441dd157?auto=format&fit=crop&w=900&q=80", "상품링크": "https://example.com/product-1", "혜택": "카드 5% 추가"},
    {"group": "A", "상품ID": "A002", "브랜드": "SPARTA DENIM", "상품명": "데님 팬츠", "설명": "핏과 착용감을 동시에 잡은 스테디셀러", "정가": 79000, "판매가": 49000, "할인율": "38%", "뱃지": "MD추천", "이미지파일": "denim.jpg", "이미지경로": "images/products/denim.jpg", "이미지URL": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=80", "상품링크": "https://example.com/product-2", "혜택": "무료배송"},
    {"group": "A", "상품ID": "A003", "브랜드": "SPARTA SHOES", "상품명": "클래식 스니커즈", "설명": "가볍고 어디에나 잘 어울리는 데일리 슈즈", "정가": 89000, "판매가": 59000, "할인율": "33%", "뱃지": "인기", "이미지파일": "shoes.jpg", "이미지경로": "images/products/shoes.jpg", "이미지URL": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80", "상품링크": "https://example.com/product-3", "혜택": "사은품 증정"},
    {"group": "B", "상품ID": "B001", "브랜드": "SPARTA BAG", "상품명": "미니 크로스백", "설명": "필수 소지품만 담아 가볍게 들기 좋은 백", "정가": 69000, "판매가": 45000, "할인율": "35%", "뱃지": "한정수량", "이미지파일": "bag.jpg", "이미지경로": "images/products/bag.jpg", "이미지URL": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=80", "상품링크": "https://example.com/product-4", "혜택": "적립금 2천원"},
    {"group": "B", "상품ID": "B002", "브랜드": "SPARTA SOUND", "상품명": "무선 이어폰", "설명": "출퇴근과 운동에 모두 잘 어울리는 가성비 모델", "정가": 129000, "판매가": 89000, "할인율": "31%", "뱃지": "베스트", "이미지파일": "earbuds.jpg", "이미지경로": "images/products/earbuds.jpg", "이미지URL": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80", "상품링크": "https://example.com/product-5", "혜택": "무료배송"},
    {"group": "B", "상품ID": "B003", "브랜드": "SPARTA TECH", "상품명": "스마트 워치", "설명": "건강 관리와 알림 기능을 한 번에", "정가": 199000, "판매가": 149000, "할인율": "25%", "뱃지": "사은품", "이미지파일": "watch.jpg", "이미지경로": "images/products/watch.jpg", "이미지URL": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80", "상품링크": "https://example.com/product-6", "혜택": "스트랩 증정"},
])

DEFAULT_PAGE_META = pd.DataFrame([
    {"key": "page_eyebrow", "value": "shopping"},
    {"key": "page_title", "value": "Shopping info"},
    {"key": "store_label", "value": "백화점 본점"},
    {"key": "page_description", "value": "주요 행사와 혜택을 한눈에 확인하세요."},
])

DEFAULT_INFO_LAYOUT = pd.DataFrame([
    {"order": 1, "section_key": "benefit", "section_title": "Special Benefit", "section_subtitle": "사은행사와 특별 혜택", "more_label": "Read more", "more_url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0001&cntsTpCd=C00903"},
    {"order": 2, "section_key": "event", "section_title": "Season Event", "section_subtitle": "시즌 프로모션과 추천 행사", "more_label": "Read more", "more_url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0001&cntsTpCd=C00903"},
])

DEFAULT_PROMO_CARDS = pd.DataFrame([
    {"section_key": "benefit", "card_order": 1, "display_yn": "Y", "card_label": "Special Gift", "card_title": "사은행사 안내", "card_subtitle": "구매 금액대별 특별 사은 혜택", "card_description": "기간 한정 사은품 및 멤버십 추가 혜택을 확인하세요.", "image_path": "", "image_url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=80", "card_url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0001&cntsTpCd=C00903"},
    {"section_key": "benefit", "card_order": 2, "display_yn": "Y", "card_label": "Wedding Fair", "card_title": "웨딩의 모든 것", "card_subtitle": "롯데웨딩페어", "card_description": "가전, 가구, 예물까지 한 번에 비교할 수 있는 웨딩 행사.", "image_path": "", "image_url": "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=900&q=80", "card_url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0001&cntsTpCd=C00903"},
    {"section_key": "benefit", "card_order": 3, "display_yn": "Y", "card_label": "Spring Sale", "card_title": "기분 좋은 봄 소식", "card_subtitle": "시즌 특가", "card_description": "패션·리빙 카테고리 인기 브랜드 시즌 할인전.", "image_path": "", "image_url": "https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&w=900&q=80", "card_url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0001&cntsTpCd=C00903"},
    {"section_key": "event", "card_order": 1, "display_yn": "Y", "card_label": "Luxury Brand", "card_title": "하이 주얼리 페어", "card_subtitle": "브랜드 큐레이션", "card_description": "럭셔리 브랜드의 시즌 하이라이트를 모아보세요.", "image_path": "", "image_url": "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?auto=format&fit=crop&w=900&q=80", "card_url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0001&cntsTpCd=C00903"},
    {"section_key": "event", "card_order": 2, "display_yn": "Y", "card_label": "Cosmetic", "card_title": "블루밍 뷰티 페스타", "card_subtitle": "뷰티 특집", "card_description": "향수, 스킨케어, 메이크업 인기 브랜드 기획전.", "image_path": "", "image_url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=900&q=80", "card_url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0001&cntsTpCd=C00903"},
    {"section_key": "event", "card_order": 3, "display_yn": "Y", "card_label": "Issue Brand", "card_title": "브랜드 쇼핑 리스트", "card_subtitle": "지금 주목할 브랜드", "card_description": "이번 주 반응 좋은 브랜드 모음과 프로모션 큐레이션.", "image_path": "", "image_url": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=900&q=80", "card_url": "https://www.lotteshopping.com/contents/shpgInfo?cstrCd=0001&cntsTpCd=C00903"},
])

st.markdown("""
<style>
.stApp { background:#f5f5f7; }
.block-container { max-width:1180px; padding-top:1.2rem; padding-bottom:4rem; }
.hero-wrap,.banner-wrap{position:relative;overflow:hidden;border-radius:24px;box-shadow:0 12px 36px rgba(0,0,0,0.12);}
.hero-wrap{margin-bottom:28px;min-height:380px;}
.banner-wrap{margin:30px 0;min-height:200px;}
.hero-wrap img,.banner-wrap img{width:100%;display:block;object-fit:cover;filter:brightness(0.72);}
.hero-wrap img{height:380px;}
.banner-wrap img{height:200px;}
.hero-content,.banner-content{position:absolute;left:40px;bottom:34px;color:white;}
.hero-kicker{display:inline-block;margin-bottom:12px;padding:7px 12px;border-radius:999px;background:rgba(255,255,255,0.16);font-size:12px;font-weight:700;letter-spacing:0.08em;}
.hero-title{font-size:42px;font-weight:800;line-height:1.12;margin-bottom:8px;}
.hero-subtitle{font-size:18px;opacity:0.97;}
.banner-title{font-size:30px;font-weight:800;margin-bottom:6px;}
.banner-subtitle{font-size:16px;opacity:0.95;}
.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin:36px 0 16px;}
.section-head-left{flex:1;}
.section-title{font-size:28px;font-weight:800;color:#111;margin-bottom:6px;}
.section-subtitle{color:#666;font-size:15px;}
.more-btn{display:inline-flex;align-items:center;gap:6px;padding:12px 16px;border-radius:12px;background:#111;color:#fff !important;text-decoration:none;font-weight:800;font-size:15px;white-space:nowrap;}
.product-card,.info-card{background:#fff;border-radius:22px;overflow:hidden;border:1px solid #ececec;box-shadow:0 10px 24px rgba(0,0,0,0.06);margin-bottom:22px;}
.product-frame{position:relative;width:100%;aspect-ratio:1 / 1;background:#f4f4f4;overflow:hidden;}
.product-image{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;background:#fafafa;}
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
.footer-box{color:#777;font-size:13px;text-align:center;margin-top:38px;padding-top:18px;}
.helper-box{background:white;border:1px solid #ececec;border-radius:18px;padding:16px 18px;margin-bottom:16px;}
.info-page-head{margin-bottom:30px;}
.info-eyebrow{text-transform:lowercase;font-size:15px;color:#777;margin-bottom:10px;}
.info-title{font-size:42px;font-weight:800;color:#111;line-height:1.1;margin-bottom:10px;}
.info-store{font-size:18px;font-weight:700;color:#444;margin-bottom:8px;}
.info-desc{font-size:16px;color:#666;}
.info-card .info-frame{position:relative;width:100%;aspect-ratio:1.18 / 1;background:#f4f4f4;overflow:hidden;}
.info-card .product-image{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
.info-card-body{padding:18px 18px 22px;}
.info-label{font-size:12px;font-weight:800;color:#777;letter-spacing:0.04em;text-transform:uppercase;margin-bottom:8px;}
.info-card-title{font-size:24px;font-weight:800;color:#111;line-height:1.3;margin-bottom:8px;}
.info-card-subtitle{font-size:15px;color:#444;font-weight:700;margin-bottom:10px;}
.info-card-desc{font-size:14px;color:#666;line-height:1.6;min-height:64px;margin-bottom:18px;}
.info-link{display:inline-flex;align-items:center;gap:6px;font-size:15px;font-weight:800;color:#111;text-decoration:none;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("설정")
use_demo = st.sidebar.toggle("샘플 데이터로 보기", value=True)
uploaded_file = st.sidebar.file_uploader("엑셀 업로드", type=["xlsx"])
show_raw_data = st.sidebar.checkbox("원본 데이터 보기", value=False)
preview_mode = st.sidebar.radio("미리보기 모드", ["자동 감지", "쇼핑뉴스", "쇼핑정보"], index=0)

if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)
    layout_df = read_optional(xls, uploaded_file, "content_layout")
    products_df = read_optional(xls, uploaded_file, "products")
    settings_df = read_optional(xls, uploaded_file, "settings")
    kakao_df = read_optional(xls, uploaded_file, "kakao_messages")
    lms_df = read_optional(xls, uploaded_file, "lms_messages")
    page_meta_df = read_optional(xls, uploaded_file, "page_meta")
    promo_cards_df = read_optional(xls, uploaded_file, "promo_cards")
    data_source = "업로드한 엑셀"
else:
    layout_df = DEFAULT_LAYOUT.copy()
    products_df = DEFAULT_PRODUCTS.copy()
    settings_df = pd.DataFrame()
    kakao_df = pd.DataFrame()
    lms_df = pd.DataFrame()
    page_meta_df = DEFAULT_PAGE_META.copy()
    promo_cards_df = DEFAULT_PROMO_CARDS.copy()
    data_source = "기본 샘플 데이터"

has_info_template = (not page_meta_df.empty) or (not promo_cards_df.empty)
if preview_mode == "쇼핑뉴스":
    is_info_mode = False
elif preview_mode == "쇼핑정보":
    is_info_mode = True
else:
    is_info_mode = has_info_template

if uploaded_file is None and not use_demo:
    st.info("왼쪽에서 샘플 데이터를 켜거나 엑셀 파일을 업로드해주세요.")
    st.stop()

if is_info_mode:
    settings = settings_to_dict(settings_df, DEFAULT_INFO_SETTINGS)
    page_meta = settings_to_dict(page_meta_df, settings)
else:
    settings = settings_to_dict(settings_df, DEFAULT_NEWS_SETTINGS)
    page_meta = {}

st.caption(f"현재 데이터: {data_source}")

tab_names = ["미리보기", "데이터 확인"] if is_info_mode else ["쇼핑뉴스 미리보기", "카카오 메시지", "LMS 메시지", "데이터 확인"]
tabs = st.tabs(tab_names)
preview_tab = tabs[0]
data_tab = tabs[-1]


def make_auto_kakao(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    brand = normalize_text(settings.get("kakao_brand", settings.get("brand_name", "쇼핑뉴스")))
    for _, row in df.head(6).iterrows():
        rows.append({
            "seq": len(rows)+1,
            "구분": "친구톡",
            "메시지명": f"{normalize_text(row.get('상품명'))} 카카오 발송안",
            "타이틀": f"{brand} {normalize_text(row.get('상품명'))}",
            "본문": f"{normalize_text(row.get('상품명'))} {format_won(row.get('판매가'))} / {normalize_text(row.get('할인율'))}\n{normalize_text(row.get('혜택'))} 혜택까지 확인해보세요.",
            "버튼명": "지금 확인하기",
            "버튼링크": normalize_text(row.get("상품링크")),
            "대상상품ID": normalize_text(row.get("상품ID")),
        })
    return pd.DataFrame(rows)


def make_auto_lms(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    sender = normalize_text(settings.get("lms_sender", settings.get("brand_name", "쇼핑뉴스")))
    for _, row in df.head(6).iterrows():
        rows.append({
            "seq": len(rows)+1,
            "발송구분": "LMS",
            "메시지명": f"{normalize_text(row.get('상품명'))} LMS 발송안",
            "발신프로필": sender,
            "본문": f"[{sender}] {normalize_text(row.get('상품명'))}\n{normalize_text(row.get('설명'))}\n판매가 {format_won(row.get('판매가'))} ({normalize_text(row.get('할인율'))})\n혜택: {normalize_text(row.get('혜택'))}\n구매링크: {normalize_text(row.get('상품링크'))}",
            "대상상품ID": normalize_text(row.get("상품ID")),
        })
    return pd.DataFrame(rows)


def render_image_block(src: str, fallback_bg: str, hero: bool) -> str:
    if src:
        return f'<img src="{src}" alt="visual">'
    return f'<div style="height:{380 if hero else 200}px;background:{fallback_bg};"></div>'


def render_more_button(label: str, url: str) -> str:
    label = normalize_text(label)
    url = normalize_text(url)
    if not label or not url:
        return ""
    return f'<a class="more-btn" href="{url}" target="_blank">{label} ↗</a>'


if not is_info_mode:
    if kakao_df.empty:
        kakao_df = make_auto_kakao(products_df)
    if lms_df.empty:
        lms_df = make_auto_lms(products_df)

    with preview_tab:
        st.markdown("""
        <div class="helper-box">
            <b>로컬 이미지 사용법</b><br>
            1) 앱 실행 폴더 기준으로 <code>images/</code> 폴더를 만듭니다.<br>
            2) 엑셀의 <code>image_path</code>, <code>이미지경로</code> 에 상대경로를 적습니다.<br>
            3) <code>settings</code> 시트의 <code>image_base_path</code> 로 기준 폴더를 지정할 수 있습니다.<br>
            4) <code>image_mode</code> 는 <code>local_first</code>, <code>local_only</code>, <code>url_only</code> 중 선택합니다.
        </div>
        """, unsafe_allow_html=True)

        for _, row in layout_df.sort_values("order").iterrows():
            block_type = normalize_text(row.get("type", "")).lower()
            if block_type == "hero":
                src = resolve_image_src(row, settings, "image_path", "image_url")
                bg = normalize_text(row.get("background", "#111111")) or "#111111"
                st.markdown(f"""
                <div class="hero-wrap">
                    {render_image_block(src, bg, True)}
                    <div class="hero-content">
                        <div class="hero-kicker">{settings.get("brand_name", "SHOPPING NEWS")}</div>
                        <div class="hero-title">{row.get("title","")}</div>
                        <div class="hero-subtitle">{row.get("subtitle","")}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif block_type == "banner":
                src = resolve_image_src(row, settings, "image_path", "image_url")
                bg = normalize_text(row.get("background", "#1f1f1f")) or "#1f1f1f"
                st.markdown(f"""
                <div class="banner-wrap">
                    {render_image_block(src, bg, False)}
                    <div class="banner-content">
                        <div class="banner-title">{row.get("title","")}</div>
                        <div class="banner-subtitle">{row.get("subtitle","")}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif block_type == "section":
                st.markdown(f"""
                <div class="section-head">
                    <div class="section-head-left">
                        <div class="section-title">{row.get("title","")}</div>
                        <div class="section-subtitle">{row.get("subtitle","")}</div>
                    </div>
                    {render_more_button(row.get("more_label",""), row.get("more_url",""))}
                </div>
                """, unsafe_allow_html=True)
                group_df = products_df[products_df["group"].astype(str) == str(row.get("product_group",""))].reset_index(drop=True)
                for start in range(0, len(group_df), 3):
                    cols = st.columns(3)
                    chunk = group_df.iloc[start:start+3]
                    for idx, (_, product) in enumerate(chunk.iterrows()):
                        src = resolve_image_src(product, settings, "이미지경로", "이미지URL")
                        image_html = f'<img class="product-image" src="{src}" alt="{normalize_text(product.get("상품명",""))}">' if src else '<div class="product-image"></div>'
                        badge_html = f"<div class='badge'>{normalize_text(product.get('뱃지',''))}</div>" if normalize_text(product.get("뱃지","")) else ""
                        benefit_html = f"<div class='benefit'>혜택 · {normalize_text(product.get('혜택',''))}</div>" if normalize_text(product.get("혜택","")) else ""
                        with cols[idx]:
                            st.markdown(f"""
                            <div class="product-card">
                                <div class="product-frame">{image_html}</div>
                                <div class="product-body">
                                    {badge_html}
                                    <div class="brand">{normalize_text(product.get("브랜드",""))}</div>
                                    <div class="name">{normalize_text(product.get("상품명",""))}</div>
                                    <div class="desc">{normalize_text(product.get("설명",""))}</div>
                                    {benefit_html}
                                    <div class="price-line">
                                        <span class="sale-rate">{normalize_text(product.get("할인율",""))}</span>
                                        <span class="sale-price">{format_won(product.get("판매가",""))}</span>
                                    </div>
                                    <div class="origin-price">{format_won(product.get("정가",""))}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            elif block_type == "notice":
                st.markdown(f"""
                <div class="notice-box">
                    <div class="section-title" style="font-size:22px;margin-bottom:10px;">{row.get("title","안내")}</div>
                    <div style="color:#666;line-height:1.7;font-size:14px;">{row.get("note","")}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f'<div class="footer-box">{settings.get("footer_text","")}</div>', unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("카카오 메시지 발송안")
        st.dataframe(kakao_df, use_container_width=True)
    with tabs[2]:
        st.subheader("LMS 메시지 발송안")
        st.dataframe(lms_df, use_container_width=True)

else:
    info_layout_df = layout_df if (not layout_df.empty and "section_key" in layout_df.columns) else DEFAULT_INFO_LAYOUT.copy()
    if promo_cards_df.empty:
        promo_cards_df = DEFAULT_PROMO_CARDS.copy()

    with preview_tab:
        st.markdown("""
        <div class="helper-box">
            <b>쇼핑정보형 템플릿</b><br>
            <code>page_meta</code> 시트로 상단 제목/설명을 제어하고,
            <code>content_layout</code> 의 <code>section_key</code> 와
            <code>promo_cards</code> 의 <code>section_key</code> 를 연결하면 섹션별 카드 리스트가 만들어집니다.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-page-head">
            <div class="info-eyebrow">{page_meta.get("page_eyebrow","shopping")}</div>
            <div class="info-title">{page_meta.get("page_title","Shopping info")}</div>
            <div class="info-store">{page_meta.get("store_label","백화점 본점")}</div>
            <div class="info-desc">{page_meta.get("page_description","주요 행사와 혜택을 한눈에 확인하세요.")}</div>
        </div>
        """, unsafe_allow_html=True)

        cards_per_row = int(float(page_meta.get("cards_per_row", settings.get("cards_per_row", 3))))
        cards_per_row = max(1, min(cards_per_row, 4))

        for _, section in info_layout_df.sort_values("order").iterrows():
            section_key = normalize_text(section.get("section_key", ""))
            section_cards = promo_cards_df[promo_cards_df["section_key"].astype(str) == section_key].copy()
            if "display_yn" in section_cards.columns:
                section_cards = section_cards[section_cards["display_yn"].apply(lambda x: to_bool(x, True))]
            if "card_order" in section_cards.columns:
                section_cards = section_cards.sort_values("card_order")
            if section_cards.empty:
                continue

            more_label = normalize_text(section.get("more_label", "")) or normalize_text(page_meta.get("default_more_label", settings.get("default_more_label", "Read more")))
            more_url = normalize_text(section.get("more_url", ""))

            st.markdown(f"""
            <div class="section-head">
                <div class="section-head-left">
                    <div class="section-title">{section.get("section_title","")}</div>
                    <div class="section-subtitle">{section.get("section_subtitle","")}</div>
                </div>
                {render_more_button(more_label, more_url)}
            </div>
            """, unsafe_allow_html=True)

            for start in range(0, len(section_cards), cards_per_row):
                cols = st.columns(cards_per_row)
                chunk = section_cards.iloc[start:start+cards_per_row]
                for idx, (_, card) in enumerate(chunk.iterrows()):
                    src = resolve_image_src(card, page_meta, "image_path", "image_url")
                    image_html = f'<img class="product-image" src="{src}" alt="{normalize_text(card.get("card_title",""))}">' if src else '<div class="product-image"></div>'
                    link = normalize_text(card.get("card_url", "#"))
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="info-card">
                            <div class="info-frame">{image_html}</div>
                            <div class="info-card-body">
                                <div class="info-label">{normalize_text(card.get("card_label",""))}</div>
                                <div class="info-card-title">{normalize_text(card.get("card_title",""))}</div>
                                <div class="info-card-subtitle">{normalize_text(card.get("card_subtitle",""))}</div>
                                <div class="info-card-desc">{normalize_text(card.get("card_description",""))}</div>
                                <a class="info-link" href="{link}" target="_blank">{normalize_text(page_meta.get("default_more_label", settings.get("default_more_label", "Read more")))} ↗</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown(f'<div class="footer-box">{page_meta.get("footer_text", settings.get("footer_text",""))}</div>', unsafe_allow_html=True)

with data_tab:
    if show_raw_data:
        if is_info_mode:
            st.subheader("page_meta")
            st.dataframe(pd.DataFrame(list(page_meta.items()), columns=["key", "value"]), use_container_width=True)
            st.subheader("content_layout")
            st.dataframe(info_layout_df, use_container_width=True)
            st.subheader("promo_cards")
            st.dataframe(promo_cards_df, use_container_width=True)
            st.subheader("settings")
            st.dataframe(pd.DataFrame(list(settings.items()), columns=["key", "value"]), use_container_width=True)
        else:
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
