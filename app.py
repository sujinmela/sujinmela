import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import streamlit as st

# ── 상수 ─────────────────────────────────────────────────────────────
CIRCLED = ["①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩"]
NOISE   = re.compile(r"사은\s*사은\s*종료|쇼핑뉴스\s*행사\s*종료")
TRAILING = re.compile(
    r"\s+(백화점|아울렛|에비뉴엘|입점|전점|각\s*지점|일부\s*지점|모바일\s*참여"
    r"|본점|잠실점|강남점|[0-9]+F|B[0-9]+|[0-9]+\.[0-9]+\(|~).+$"
)
HISTORY_KEY = "lms_history"

# ── 파싱 ─────────────────────────────────────────────────────────────
def fetch_and_parse(url: str):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": "https://www.lotteshopping.com/",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
    except requests.exceptions.Timeout:
        return None, "페이지 응답 시간이 초과됐습니다."
    except requests.exceptions.HTTPError as e:
        return None, f"페이지를 불러오지 못했습니다. (HTTP {e.response.status_code})"
    except Exception as e:
        return None, f"네트워크 오류: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")
    sections = []
    for h3 in soup.find_all("h3"):
        title = h3.get_text(strip=True)
        if not re.search(r"\[.+?\]", title):
            continue
        # [XXX]뒤 공백 보정
        title = re.sub(r"(\])\s*([^\s])", r"\1 \2", title)

        items = []
        ul = h3.find_next_sibling("ul")
        if ul:
            for li in ul.find_all("li"):
                raw = li.get_text(separator=" ", strip=True)
                raw = NOISE.sub("", raw).strip()
                raw = re.sub(r"\s+", " ", raw)
                raw = TRAILING.sub("", raw).strip()
                if raw and "[" in raw:
                    items.append(raw)
        if items:
            sections.append((title, items))

    if not sections:
        return None, "행사 내용을 찾지 못했습니다. URL을 확인해 주세요."
    return sections, ""


# ── LMS 조립 ─────────────────────────────────────────────────────────
def build_lms_text(sections, store: str, url: str) -> str:
    lines = [
        f"(광고)롯데백화점 {store}",
        "${TMS_M_NAME} 고객님 안녕하세요.",
        f"이번주 롯데백화점 {store} 소식을 안내드립니다.",
        "",
        "",
    ]
    for title, items in sections:
        lines.append(title)
        for i, item in enumerate(items[:6]):
            num = CIRCLED[i] if i < len(CIRCLED) else f"{i+1}."
            lines.append(f"{num} {item}")
        lines.append("")   # 소그룹 사이 빈 줄

    lines += [
        "",
        "자세한 사항 및 더욱 다양한 소식은 하단의 링크를 통해 확인 가능합니다.",
        url,
        "문의전화 1577-0001",
        "무료수신거부 080-880-2626",
    ]
    return "\n".join(lines)


# ── 이력 관리 (session_state) ─────────────────────────────────────────
def load_history():
    return st.session_state.get(HISTORY_KEY, [])

def save_history(entry: dict):
    if HISTORY_KEY not in st.session_state:
        st.session_state[HISTORY_KEY] = []
    st.session_state[HISTORY_KEY].insert(0, entry)   # 최신순

def delete_history(idx: int):
    if HISTORY_KEY in st.session_state:
        st.session_state[HISTORY_KEY].pop(idx)


# ── 메인 앱 ──────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="쇼핑 하이라이트 기반 LMS 생성기", layout="wide")
    st.title("쇼핑 하이라이트 기반 LMS 생성기")

    STORES = (
        ["본점","잠실점","강남점","건대스타시티점","관악점","김포공항점","노원점","미아점","영등포점","청량리점"]
        + ["인천점","동탄점","구리점","수원점","안산점","일산점","중동점","평촌점"]
        + ["부산본점","광복점","광주점","대구점","대전점","동래점","상인점","센텀시티점","울산점","전주점","창원점","포항점"]
    )

    tab_gen, tab_history = st.tabs(["✨ LMS 자동생성 (URL)", "📋 생성 이력"])

    # ── 생성 탭 ──────────────────────────────────────────────────────
    with tab_gen:
        st.subheader("URL 입력 → LMS 문안 자동생성")
        st.caption("쇼핑 하이라이트 URL과 점포명만 입력하면 LMS 문안을 즉시 생성합니다. API 키 불필요.")

        col1, col2 = st.columns([3, 1])
        with col1:
            url_input = st.text_input(
                "쇼핑 하이라이트 URL",
                placeholder="https://www.lotteshopping.com/shopnow/cntsList?shpgHhlghNo=SHH...&shpgHhlghAditNo=SHA...",
            )
        with col2:
            store = st.selectbox("점포명", ["점포를 선택하세요"] + STORES)

        run = st.button("✨ LMS 문안 자동생성", type="primary", use_container_width=True)

        if run:
            if not url_input.strip():
                st.warning("URL을 입력해 주세요.")
            elif store == "점포를 선택하세요":
                st.warning("점포명을 선택해 주세요.")
            else:
                with st.spinner("페이지에서 행사 내용을 읽는 중..."):
                    sections, err = fetch_and_parse(url_input.strip())
                if err:
                    st.error(f"❌ {err}")
                else:
                    result = build_lms_text(sections, store, url_input.strip())
                    st.session_state["current_lms"] = result
                    st.session_state["current_meta"] = {
                        "store": store,
                        "url": url_input.strip(),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "lms": result,
                        "char_count": len(result),
                    }

        if st.session_state.get("current_lms"):
            result = st.session_state["current_lms"]
            meta   = st.session_state.get("current_meta", {})
            result_len = len(result)
            is_over = result_len > 1000

            st.divider()
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown("### 📨 생성된 LMS 문안")
            with c2:
                color = "red" if is_over else "green"
                warn  = "⚠ 권장 초과" if is_over else "✓ 적정"
                st.markdown(
                    f'<div style="padding-top:26px;text-align:right;'
                    f'color:{color};font-weight:600">{result_len:,}자 {warn}</div>',
                    unsafe_allow_html=True,
                )
            with c3:
                if st.button("📁 이력에 저장", use_container_width=True):
                    save_history(meta)
                    st.success("이력에 저장됐습니다.")

            st.text_area("복사용 LMS 문안", value=result, height=450, key="lms_copy")

            if is_over:
                st.warning(f"{result_len:,}자 — LMS 1,000자 제한을 초과할 수 있습니다.")

    # ── 이력 탭 ──────────────────────────────────────────────────────
    with tab_history:
        st.subheader("📋 LMS 생성 이력")
        history = load_history()

        if not history:
            st.info("아직 저장된 이력이 없습니다. 생성 탭에서 '이력에 저장' 버튼을 눌러주세요.")
        else:
            st.caption(f"총 {len(history)}건 저장됨 (최신순)")
            for idx, entry in enumerate(history):
                with st.expander(
                    f"[{entry['created_at']}] 롯데백화점 {entry['store']} "
                    f"— {entry['char_count']:,}자",
                    expanded=(idx == 0),
                ):
                    st.caption(f"URL: {entry['url']}")
                    st.text_area(
                        "LMS 문안",
                        value=entry["lms"],
                        height=360,
                        key=f"hist_{idx}",
                    )
                    col_dl, col_del = st.columns([1, 1])
                    with col_dl:
                        st.download_button(
                            "⬇ TXT 다운로드",
                            data=entry["lms"].encode("utf-8-sig"),
                            file_name=(
                                f"lms_{entry['store']}_"
                                f"{entry['created_at'].replace(':', '').replace(' ', '_')}.txt"
                            ),
                            mime="text/plain",
                            key=f"dl_{idx}",
                        )
                    with col_del:
                        if st.button("🗑 삭제", key=f"del_{idx}", use_container_width=True):
                            delete_history(idx)
                            st.rerun()


if __name__ == "__main__":
    main()
