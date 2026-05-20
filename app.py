from __future__ import annotations

import base64
import hashlib
import io
import math
import os
import random
import subprocess
import textwrap
import time
import uuid
from dataclasses import dataclass
from datetime import date
from importlib import resources as importlib_resources
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import qrcode
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFilter, ImageFont


# -----------------------------------------------------------------------------
# Lotte Department Store styled fortune event app
# -----------------------------------------------------------------------------
# Deploy note:
#   QR download links need a public URL that phones can open.
#   Set PUBLIC_BASE_URL to your deployed Streamlit URL, e.g.
#   PUBLIC_BASE_URL="https://your-fortune-event.streamlit.app"
# -----------------------------------------------------------------------------

APP_TITLE = "오늘의 운세 | LOTTE Department Store"
STORY_SIZE = (1080, 1920)
GENERATED_DIR = Path(__file__).resolve().parent / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
FONT_DIR = Path(__file__).resolve().parent / ".fortune_fonts"
FONT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Profile:
    name: str
    gender: str
    birth_date: date
    hour: int
    minute: int


@dataclass(frozen=True)
class FortuneTheme:
    headline: str
    headline_sub: str
    theme: str
    theme_desc: str
    brands: tuple[str, ...]
    items: tuple[tuple[str, str, str], ...]
    color_name: str
    color_hex: str
    lucky_item: str
    advice: str
    spots: tuple[tuple[str, str], ...]


FORTUNE_THEMES: tuple[FortuneTheme, ...] = (
    FortuneTheme(
        headline="새로운 스타일 변화가 행운을 부르는 하루예요.",
        headline_sub="지금의 작은 선택이 당신을 더욱 빛나게 해줄 거예요. 새로운 시도와 변화가 좋은 흐름을 만들어줍니다.",
        theme="가구 · 키친 · 프리미엄 식품",
        theme_desc="집을 더 특별하게 만들어 줄 아이템에서 좋은 에너지가 가득해요!",
        brands=("DIOR", "TAMBURINS", "TIFFANY & CO.", "maje", "LE CREUSET"),
        items=(
            ("우드 테이블 램프", "따뜻한 무드로 공간을 기분 좋게!", "lamp"),
            ("스테인리스 키친웨어", "실용적인 소비가 행운을 가져다줘요!", "cookware"),
            ("프리미엄 향수", "나를 표현하는 향이 자신감을 높여줘요!", "perfume"),
        ),
        color_name="핑크 베이지",
        color_hex="#FFC1CC",
        lucky_item="에코백",
        advice="나에게 투자하는 시간이 가장 빛나는 순간을 만듭니다.",
        spots=(
            ("패션관 2F", "트렌디 브랜드가 가득! 오늘의 스타일을 완성해보세요."),
            ("리빙관 6F", "감각적인 집꾸미기 아이템으로 일상에 행복을 더해보세요."),
            ("푸드에비뉴 B1", "맛있는 음식이 주는 행복! 오늘의 기운을 채워보세요."),
        ),
    ),
    FortuneTheme(
        headline="감각적인 선택이 쇼핑운을 끌어올리는 날이에요.",
        headline_sub="평소보다 취향이 또렷해지는 하루예요. 오래 두고 쓸 물건을 고르면 만족감이 커집니다.",
        theme="패션 · 주얼리 · 뷰티",
        theme_desc="스타일링 포인트가 되는 작은 아이템이 오늘의 분위기를 바꿔줘요.",
        brands=("CHANEL", "GUCCI", "Aesop", "SANDRO", "LONGCHAMP"),
        items=(
            ("실크 스카프", "가벼운 포인트로 분위기를 세련되게!", "scarf"),
            ("미니 주얼리", "작은 반짝임이 좋은 인연을 부릅니다.", "jewelry"),
            ("핸드크림 세트", "부드러운 향이 하루를 산뜻하게 해줘요.", "cream"),
        ),
        color_name="로즈 골드",
        color_hex="#E9A6A1",
        lucky_item="스카프",
        advice="사소한 디테일 하나가 오늘의 이미지를 완성합니다.",
        spots=(
            ("해외패션 3F", "취향을 선명하게 보여줄 포인트 아이템을 찾아보세요."),
            ("주얼리존 1F", "은은한 반짝임이 좋은 만남을 돕습니다."),
            ("뷰티관 1F", "향과 컬러로 오늘의 무드를 바꿔보세요."),
        ),
    ),
    FortuneTheme(
        headline="맛있는 기분 전환이 금전운을 편안하게 열어줘요.",
        headline_sub="무리한 소비보다 나를 기분 좋게 하는 합리적인 선택이 어울리는 하루입니다.",
        theme="델리 · 카페 · 라이프스타일",
        theme_desc="달콤한 휴식과 산뜻한 라이프스타일 아이템에서 활력이 살아나요.",
        brands=("GODIVA", "TWG TEA", "NESPRESSO", "MUJI", "KINFOLK"),
        items=(
            ("티 세트", "향긋한 차 한 잔이 머리를 맑게 해줘요.", "tea"),
            ("디저트 박스", "기분 좋은 달콤함이 웃음을 부릅니다.", "dessert"),
            ("데일리 노트", "정리된 생각이 좋은 결정을 도와줘요.", "note"),
        ),
        color_name="크림 옐로",
        color_hex="#FFE7A8",
        lucky_item="텀블러",
        advice="잠깐의 쉼이 다음 선택을 더 현명하게 만들어줍니다.",
        spots=(
            ("푸드홀 B1", "달콤한 메뉴로 기분 전환을 해보세요."),
            ("카페 라운지 4F", "잠깐 쉬어가면 좋은 아이디어가 떠오릅니다."),
            ("라이프스타일 5F", "매일 쓰는 물건에서 작은 행복을 발견해보세요."),
        ),
    ),
    FortuneTheme(
        headline="활동적인 움직임이 건강운과 인연운을 함께 올려줘요.",
        headline_sub="몸을 가볍게 움직이면 마음도 산뜻해지는 날입니다. 편안함을 주는 선택이 행운입니다.",
        theme="스포츠 · 아웃도어 · 웰니스",
        theme_desc="가볍게 움직일 수 있는 아이템이 컨디션과 자신감을 높여줘요.",
        brands=("lululemon", "NIKE", "adidas", "ARC'TERYX", "VITALBEAUTIE"),
        items=(
            ("데일리 스니커즈", "편안한 발걸음이 좋은 기회를 불러요.", "sneakers"),
            ("요가 매트", "균형 잡힌 루틴이 마음을 안정시켜줘요.", "yoga"),
            ("보틀", "수분 충전이 오늘의 컨디션 포인트!", "bottle"),
        ),
        color_name="세이지 그린",
        color_hex="#A9C7A2",
        lucky_item="스니커즈",
        advice="가볍게 움직이는 순간, 막혀 있던 흐름이 풀립니다.",
        spots=(
            ("스포츠관 5F", "편안하고 활동적인 아이템을 만나보세요."),
            ("아웃도어 6F", "새로운 산책 코스를 떠올리게 하는 공간이에요."),
            ("웰니스존 4F", "컨디션을 챙기는 선택이 좋은 하루를 만듭니다."),
        ),
    ),
    FortuneTheme(
        headline="차분한 고급스러움이 당신의 매력을 살려주는 날이에요.",
        headline_sub="과한 선택보다 정돈된 취향이 빛납니다. 클래식한 아이템이 오래가는 만족을 줍니다.",
        theme="클래식 패션 · 홈데코 · 기프트",
        theme_desc="오래 간직하고 싶은 선물 같은 아이템이 오늘의 행운을 완성해요.",
        brands=("BURBERRY", "HERMES", "JO MALONE", "VILLEROY & BOCH", "BOSS"),
        items=(
            ("레더 카드지갑", "정돈된 소지품이 금전 흐름을 가볍게 해요.", "wallet"),
            ("홈 프래그런스", "공간의 향이 마음을 차분하게 해줘요.", "diffuser"),
            ("기프트 박스", "고마운 사람에게 마음을 전하면 운이 돌아와요.", "gift"),
        ),
        color_name="아이보리 브라운",
        color_hex="#D7B899",
        lucky_item="카드지갑",
        advice="품격 있는 선택은 오래 남는 좋은 기운이 됩니다.",
        spots=(
            ("남성패션 4F", "정돈된 클래식 룩을 완성해보세요."),
            ("홈데코 6F", "공간의 분위기를 바꾸는 작은 디테일을 찾아보세요."),
            ("기프트샵 1F", "마음을 전하는 소비가 좋은 관계를 만듭니다."),
        ),
    ),
)


ZODIAC_ANIMALS = ("쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지")
TIME_BRANCHES = ("자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해")

PALETTE = {
    "bg_top": "#FFF7F8",
    "bg_bottom": "#FDE4E8",
    "card": "#FFFDFC",
    "card_2": "#FFF6F4",
    "line": "#F5D4CF",
    "pink": "#EF4D7C",
    "pink_2": "#FF82A4",
    "rose": "#BD3E62",
    "deep": "#3E2022",
    "brown": "#6D3B2E",
    "muted": "#8F6562",
    "gold": "#E8A666",
    "green": "#7E9E34",
    "soft": "#FFF2F3",
}


# -----------------------------------------------------------------------------
# Query params and public URL helpers
# -----------------------------------------------------------------------------

def first_query_value(value, default: str | None = None) -> str | None:
    if isinstance(value, list):
        return value[0] if value else default
    if value is None:
        return default
    return str(value)


def get_query_params() -> dict:
    try:
        return dict(st.query_params)
    except Exception:
        return st.experimental_get_query_params()


def normalize_base_url(raw_url: str) -> str:
    raw_url = (raw_url or "").strip()
    if not raw_url:
        return "http://localhost:8501"
    if "://" not in raw_url:
        raw_url = "https://" + raw_url
    parsed = urlparse(raw_url)
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
    return base or "http://localhost:8501"


def get_default_base_url() -> str:
    return normalize_base_url(
        os.environ.get("PUBLIC_BASE_URL")
        or os.environ.get("STREAMLIT_PUBLIC_URL")
        or "http://localhost:8501"
    )


def make_download_url(base_url: str, result_id: str) -> str:
    return f"{normalize_base_url(base_url)}?rid={result_id}"


# -----------------------------------------------------------------------------
# Font helpers
# -----------------------------------------------------------------------------
# Korean text in the generated PNG is drawn with Pillow, not with browser CSS.
# Therefore the server that runs Streamlit must have a Korean-capable TrueType/
# OpenType font. The app checks, in order:
#   1) explicit env vars FORTUNE_FONT / FORTUNE_BOLD_FONT
#   2) local project folders such as ./assets/fonts
#   3) fonts bundled by koreanize-matplotlib, if installed
#   4) common Linux/macOS/Windows Korean fonts
# Streamlit Cloud: add packages.txt with fonts-nanum or fonts-noto-cjk.

_FONT_CACHE: dict[tuple[int, bool, str], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}
_FONT_DEBUG_CACHE: dict[str, str] = {}
_FONT_DOWNLOAD_FAILED: set[str] = set()

# Runtime fallback for hosted environments without Korean system fonts.
# The URLs point to open-source Nanum Gothic TTF files from the Google Fonts
# repository/CDN. No font file is bundled in this project.
NANUM_FONT_URLS = {
    "regular": (
        "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/nanumgothic/NanumGothic-Regular.ttf",
        "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
        "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
    ),
    "bold": (
        "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/nanumgothic/NanumGothic-Bold.ttf",
        "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf",
        "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf",
    ),
}


def _valid_font_file(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 100_000


def _download_font(kind: str) -> str | None:
    """Download a Korean TTF font when the deployment image has no CJK font."""
    target = FONT_DIR / ("NanumGothicBold.ttf" if kind == "bold" else "NanumGothic.ttf")
    if _valid_font_file(target):
        return str(target)
    if kind in _FONT_DOWNLOAD_FAILED:
        return None

    for url in NANUM_FONT_URLS[kind]:
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=12) as response:
                data = response.read()
            if len(data) < 100_000:
                continue
            tmp = target.with_suffix(".tmp")
            tmp.write_bytes(data)
            ImageFont.truetype(str(tmp), size=24)  # validation
            tmp.replace(target)
            return str(target)
        except Exception:
            continue

    _FONT_DOWNLOAD_FAILED.add(kind)
    return None



def _existing(paths: Iterable[str]) -> list[str]:
    found: list[str] = []
    for raw in paths:
        if not raw:
            continue
        try:
            path = str(raw)
            if Path(path).exists():
                found.append(path)
        except Exception:
            continue
    return found


def _project_font_candidates(bold: bool = False, family: str = "sans") -> list[str]:
    base = Path(__file__).resolve().parent
    names_regular = (
        "NanumGothic.ttf",
        "NanumSquareR.ttf",
        "NanumBarunGothic.ttf",
        "NotoSansKR-Regular.otf",
        "NotoSansCJK-Regular.ttc",
        "Pretendard-Regular.ttf",
    )
    names_bold = (
        "NanumGothicBold.ttf",
        "NanumSquareB.ttf",
        "NanumBarunGothicBold.ttf",
        "NotoSansKR-Bold.otf",
        "NotoSansCJK-Bold.ttc",
        "Pretendard-Bold.ttf",
    )
    names_serif = (
        "NanumMyeongjo.ttf",
        "NanumMyeongjoBold.ttf",
        "NotoSerifCJK-Regular.ttc",
        "NotoSerifKR-Regular.otf",
    )
    selected = names_serif if family == "serif" else (names_bold if bold else names_regular)
    roots = (
        FONT_DIR,
        base,
        base / "assets",
        base / "asset",
        base / "fonts",
        base / "assets" / "fonts",
    )
    return [str(root / name) for root in roots for name in selected]


def _koreanize_matplotlib_candidates(bold: bool = False) -> list[str]:
    names = ("NanumGothicBold.ttf", "NanumSquareB.ttf") if bold else ("NanumGothic.ttf", "NanumSquareR.ttf")
    candidates: list[str] = []
    try:
        font_dir = importlib_resources.files("koreanize_matplotlib") / "fonts"
        for name in names:
            candidates.append(str(font_dir / name))
    except Exception:
        pass
    return candidates


def _fontconfig_match(query: str) -> str | None:
    """Return a font path from fontconfig when available.

    Streamlit Cloud/Linux images do not always have Korean fonts installed by
    default. When fonts-nanum or fonts-noto-cjk is installed through packages.txt,
    fc-match gives us the exact path, even if the distro stores it differently.
    """
    try:
        completed = subprocess.run(
            ["fc-match", "-f", "%{file}", query],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=1.5,
        )
        candidate = completed.stdout.strip()
        if candidate and Path(candidate).exists():
            return candidate
    except Exception:
        return None
    return None


def _font_candidates(bold: bool = False, family: str = "sans") -> list[str]:
    env_key = "FORTUNE_BOLD_FONT" if bold else "FORTUNE_FONT"
    env_path = os.environ.get(env_key)
    candidates: list[str] = []
    if env_path:
        candidates.append(env_path)

    candidates.extend(_project_font_candidates(bold=bold, family=family))
    if family != "serif":
        candidates.extend(_koreanize_matplotlib_candidates(bold=bold))

    # English script title only. This font is intentionally not used as the
    # Korean fallback, because DejaVu renders Hangul as square tofu boxes.
    if family == "serif":
        candidates.extend(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
                "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
                "C:/Windows/Fonts/georgiai.ttf",
            ]
        )
        return candidates

    # Ask fontconfig first. This makes the app resilient across Ubuntu,
    # Streamlit Cloud, Docker images, and managed Linux servers.
    fc_queries = (
        [
            "NanumGothic:style=Bold",
            "NanumBarunGothic:style=Bold",
            "NanumSquareRound:style=Bold",
            "Noto Sans CJK KR:style=Bold",
            "Noto Sans KR:style=Bold",
            "Apple SD Gothic Neo:style=Bold",
            "Malgun Gothic:style=Bold",
        ]
        if bold
        else [
            "NanumGothic:style=Regular",
            "NanumBarunGothic:style=Regular",
            "NanumSquareRound:style=Regular",
            "Noto Sans CJK KR:style=Regular",
            "Noto Sans KR:style=Regular",
            "Apple SD Gothic Neo:style=Regular",
            "Malgun Gothic:style=Regular",
        ]
    )
    for query in fc_queries:
        found = _fontconfig_match(query)
        if found:
            candidates.append(found)

    if bold:
        candidates.extend(
            [
                "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
                "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf",
                "/usr/share/fonts/truetype/nanum/NanumSquareB.ttf",
                "/usr/share/fonts/truetype/nanum/NanumSquareRoundB.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJKkr-Bold.otf",
                "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
                "/Library/Fonts/NanumGothicBold.ttf",
                "C:/Windows/Fonts/malgunbd.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
                "/usr/share/fonts/truetype/nanum/NanumSquareR.ttf",
                "/usr/share/fonts/truetype/nanum/NanumSquareRoundR.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJKkr-Regular.otf",
                "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
                "/Library/Fonts/NanumGothic.ttf",
                "C:/Windows/Fonts/malgun.ttf",
            ]
        )

    # Remove duplicates while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for item in candidates:
        if item not in seen:
            unique.append(item)
            seen.add(item)
    return unique

def font(size: int, bold: bool = False, family: str = "sans") -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    key = (size, bold, family)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    for path in _font_candidates(bold=bold, family=family):
        try:
            if Path(path).exists():
                loaded = ImageFont.truetype(path, size=size)
                _FONT_CACHE[key] = loaded
                _FONT_DEBUG_CACHE[f"{family}:{'bold' if bold else 'regular'}"] = path
                return loaded
        except Exception:
            continue
    if family != "serif":
        downloaded = _download_font("bold" if bold else "regular")
        if downloaded:
            loaded = ImageFont.truetype(downloaded, size=size)
            _FONT_CACHE[key] = loaded
            _FONT_DEBUG_CACHE[f"{family}:{'bold' if bold else 'regular'}"] = downloaded
            return loaded
        if bold:
            downloaded_regular = _download_font("regular")
            if downloaded_regular:
                loaded = ImageFont.truetype(downloaded_regular, size=size)
                _FONT_CACHE[key] = loaded
                _FONT_DEBUG_CACHE[f"{family}:{'bold' if bold else 'regular'}"] = downloaded_regular
                return loaded

    loaded = ImageFont.load_default()
    _FONT_CACHE[key] = loaded
    _FONT_DEBUG_CACHE[f"{family}:{'bold' if bold else 'regular'}"] = "Pillow default font - Korean unsupported"
    return loaded


def get_active_font_paths() -> dict[str, str]:
    # Prime the cache so the UI can show a useful diagnostic message.
    font(20, False)
    font(20, True)
    return dict(_FONT_DEBUG_CACHE)


def has_server_korean_font() -> bool:
    paths = []
    paths.extend(_font_candidates(False, "sans"))
    paths.extend(_font_candidates(True, "sans"))
    return bool(_existing(paths))


def text_bbox(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), text, font=fnt)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> int:
    left, top, right, bottom = text_bbox(draw, text, fnt)
    return right - left


def text_height(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> int:
    left, top, right, bottom = text_bbox(draw, text, fnt)
    return bottom - top


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            candidate = word if not line else f"{line} {word}"
            if text_width(draw, candidate, fnt) <= max_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                if text_width(draw, word, fnt) <= max_width:
                    line = word
                else:
                    current = ""
                    for ch in word:
                        candidate_ch = current + ch
                        if text_width(draw, candidate_ch, fnt) <= max_width:
                            current = candidate_ch
                        else:
                            if current:
                                lines.append(current)
                            current = ch
                    line = current
        if line:
            lines.append(line)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_gap: int = 8,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += text_height(draw, line, fnt) + line_gap
    return y


# -----------------------------------------------------------------------------
# Drawing helpers
# -----------------------------------------------------------------------------

def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def vertical_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    w, h = size
    top_rgb = hex_to_rgb(top)
    bottom_rgb = hex_to_rgb(bottom)
    img = Image.new("RGB", size, top_rgb)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        ratio = y / max(h - 1, 1)
        color = tuple(int(top_rgb[i] * (1 - ratio) + bottom_rgb[i] * ratio) for i in range(3))
        draw.line((0, y, w, y), fill=color)
    return img.convert("RGBA")


def add_shadowed_round_rect(
    img: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 2,
    shadow: bool = True,
    shadow_offset: tuple[int, int] = (0, 9),
    shadow_radius: int = 20,
    shadow_alpha: int = 30,
) -> None:
    if shadow:
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(layer)
        sx1, sy1, sx2, sy2 = box
        ox, oy = shadow_offset
        sdraw.rounded_rectangle(
            (sx1 + ox, sy1 + oy, sx2 + ox, sy2 + oy),
            radius=radius,
            fill=(144, 70, 90, shadow_alpha),
        )
        layer = layer.filter(ImageFilter.GaussianBlur(shadow_radius))
        img.alpha_composite(layer)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def sparkle_points(cx: float, cy: float, r1: float, r2: float) -> list[tuple[float, float]]:
    return [(cx, cy - r1), (cx + r2, cy), (cx, cy + r1), (cx - r2, cy)]


def draw_sparkle(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: str, outline: str | None = None) -> None:
    pts = sparkle_points(cx, cy, r, max(2, r // 3))
    draw.polygon(pts, fill=fill, outline=outline)
    small = max(2, r // 5)
    draw.ellipse((cx - small, cy - small, cx + small, cy + small), fill="#FFFFFF")


def star_polygon(cx: int, cy: int, outer: int, inner: int, points: int = 5) -> list[tuple[float, float]]:
    coords: list[tuple[float, float]] = []
    angle = -math.pi / 2
    step = math.pi / points
    for i in range(points * 2):
        radius = outer if i % 2 == 0 else inner
        coords.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        angle += step
    return coords


def draw_star_rating(draw: ImageDraw.ImageDraw, x: int, y: int, score: int, size: int = 14) -> None:
    for i in range(5):
        cx = x + i * (size * 2 + 4)
        fill = PALETTE["pink"] if i < score else "#E7D6D8"
        draw.polygon(star_polygon(cx, y, size, max(3, size // 2)), fill=fill)


def draw_clover(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    s = int(18 * scale)
    fill = "#86A52A"
    dark = "#64831E"
    draw.ellipse((cx - s * 2, cy - s * 2, cx, cy), fill=fill, outline=dark, width=2)
    draw.ellipse((cx, cy - s * 2, cx + s * 2, cy), fill=fill, outline=dark, width=2)
    draw.ellipse((cx - s * 2, cy, cx, cy + s * 2), fill=fill, outline=dark, width=2)
    draw.ellipse((cx, cy, cx + s * 2, cy + s * 2), fill=fill, outline=dark, width=2)
    draw.line((cx, cy + s * 2, cx + s, cy + s * 4), fill=dark, width=max(3, int(4 * scale)))


def draw_money_bag(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    s = int(30 * scale)
    draw.polygon([(cx - s // 2, cy - s), (cx + s // 2, cy - s), (cx + s // 3, cy - s // 2), (cx - s // 3, cy - s // 2)], fill="#D99A48")
    draw.rounded_rectangle((cx - s, cy - s // 2, cx + s, cy + int(s * 1.2)), radius=int(s * 0.55), fill="#F3C176", outline="#C9822F", width=2)
    draw.line((cx - s // 2, cy - s // 2, cx + s // 2, cy - s // 2), fill="#8C5A18", width=3)
    draw.text((cx, cy + 5), "$", font=font(int(30 * scale), True), fill="#61380F", anchor="mm")


def draw_heart(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    s = int(26 * scale)
    draw.ellipse((cx - s, cy - s, cx, cy), fill="#FF6D8C")
    draw.ellipse((cx, cy - s, cx + s, cy), fill="#FF6D8C")
    draw.polygon([(cx - s, cy - s // 4), (cx + s, cy - s // 4), (cx, cy + int(s * 1.4))], fill="#FF6D8C")
    draw.ellipse((cx - s + 8, cy - s + 7, cx - s + 18, cy - s + 16), fill="#FFD5DF")


def draw_sprout(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    s = int(32 * scale)
    draw.line((cx, cy + s, cx, cy - s // 2), fill="#4E8D33", width=max(4, int(5 * scale)))
    draw.ellipse((cx - s, cy - s // 2, cx + 2, cy + 8), fill="#8FBE55", outline="#5A9138", width=2)
    draw.ellipse((cx - 2, cy - s // 2, cx + s, cy + 8), fill="#9BC85F", outline="#5A9138", width=2)


def draw_lamp(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 8, y1 + 52, cx + 8, y2 - 42), radius=5, fill="#B68058")
    draw.ellipse((cx - 44, y2 - 50, cx + 44, y2 - 22), fill="#D6B18E")
    draw.rounded_rectangle((cx - 58, y2 - 30, cx + 58, y2 - 18), radius=8, fill="#A86E48")
    shade = [(cx - 55, y1 + 38), (cx + 55, y1 + 38), (cx + 72, y1 + 100), (cx - 72, y1 + 100)]
    draw.polygon(shade, fill="#FFE0B5", outline="#E5AC79")
    draw.ellipse((cx - 52, y1 + 45, cx - 36, y1 + 61), fill="#FFF3D7")


def draw_cookware(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    steel = "#D9D6CF"
    edge = "#8F8C85"
    draw.ellipse((cx - 70, y1 + 74, cx + 70, y1 + 124), fill=steel, outline=edge, width=3)
    draw.arc((cx - 50, y1 + 40, cx + 50, y1 + 110), 180, 360, fill=edge, width=4)
    draw.line((cx - 105, y1 + 94, cx - 72, y1 + 99), fill=edge, width=6)
    draw.line((cx + 72, y1 + 99, cx + 105, y1 + 94), fill=edge, width=6)
    draw.rounded_rectangle((cx - 34, y1 + 20, cx + 34, y1 + 94), radius=12, fill="#EEEAE2", outline=edge, width=3)
    draw.ellipse((cx - 34, y1 + 13, cx + 34, y1 + 29), fill="#F8F5EE", outline=edge, width=2)
    draw.line((cx - 20, y1 + 55, cx + 20, y1 + 55), fill="#B4B1AA", width=2)


def draw_perfume(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 52, y1 + 52, cx + 10, y1 + 132), radius=16, fill="#F5C1B7", outline="#C98275", width=3)
    draw.rectangle((cx - 32, y1 + 35, cx - 10, y1 + 54), fill="#C98678")
    draw.rounded_rectangle((cx - 25, y1 + 25, cx - 2, y1 + 42), radius=5, fill="#E7A195")
    draw.rounded_rectangle((cx + 5, y1 + 33, cx + 62, y1 + 132), radius=22, fill="#FDB7AE", outline="#C98275", width=3)
    draw.rectangle((cx + 25, y1 + 16, cx + 42, y1 + 36), fill="#C98678")
    draw.rounded_rectangle((cx + 18, y1 + 7, cx + 49, y1 + 23), radius=6, fill="#E7A195")
    draw.text((cx - 21, y1 + 95), "soft", font=font(16, True), fill="#8A514A", anchor="mm")
    draw.text((cx + 34, y1 + 92), "mood", font=font(15, True), fill="#8A514A", anchor="mm")


def draw_scarf(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.pieslice((cx - 70, y1 + 35, cx + 30, y1 + 135), start=20, end=340, fill="#F5A0B4", outline="#D56C8A", width=3)
    draw.polygon([(cx + 8, y1 + 90), (cx + 72, y1 + 120), (cx + 28, y1 + 138)], fill="#FAD2DA", outline="#D56C8A")
    draw.line((cx - 42, y1 + 75, cx + 20, y1 + 108), fill="#FFFFFF", width=4)


def draw_jewelry(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.arc((cx - 65, y1 + 42, cx + 65, y1 + 150), 20, 160, fill="#D6A34B", width=6)
    for dx in (-42, -20, 0, 22, 43):
        draw.ellipse((cx + dx - 7, y1 + 86, cx + dx + 7, y1 + 100), fill="#FFF6D7", outline="#D6A34B", width=2)
    draw.polygon(star_polygon(cx, y1 + 72, 22, 9), fill="#FFF0A0", outline="#D6A34B")


def draw_cream(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 45, y1 + 45, cx + 45, y1 + 132), radius=20, fill="#F8E9DE", outline="#BD987F", width=3)
    draw.rectangle((cx - 30, y1 + 25, cx + 30, y1 + 50), fill="#D3AA8F")
    draw.rounded_rectangle((cx - 34, y1 + 17, cx + 34, y1 + 32), radius=6, fill="#B98B70")
    draw.text((cx, y1 + 88), "HAND", font=font(16, True), fill="#7B5D4C", anchor="mm")


def draw_tea(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.ellipse((cx - 58, y1 + 104, cx + 58, y1 + 134), fill="#E4D0B4", outline="#A87555", width=2)
    draw.rounded_rectangle((cx - 52, y1 + 58, cx + 38, y1 + 122), radius=18, fill="#FFF4DF", outline="#A87555", width=3)
    draw.arc((cx + 25, y1 + 72, cx + 75, y1 + 112), 260, 100, fill="#A87555", width=5)
    for dx in (-18, 0, 20):
        draw.arc((cx + dx, y1 + 28, cx + dx + 15, y1 + 58), 100, 240, fill="#D2A779", width=2)


def draw_dessert(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 68, y1 + 72, cx + 68, y1 + 128), radius=16, fill="#F6B7C8", outline="#C4768D", width=3)
    draw.rectangle((cx - 62, y1 + 88, cx + 62, y1 + 108), fill="#FFF0C8")
    draw.ellipse((cx - 50, y1 + 48, cx - 18, y1 + 80), fill="#E75C7E")
    draw.ellipse((cx + 18, y1 + 48, cx + 50, y1 + 80), fill="#E75C7E")
    draw.line((cx - 74, y1 + 132, cx + 74, y1 + 132), fill="#9E6656", width=4)


def draw_note(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 55, y1 + 34, cx + 55, y1 + 136), radius=10, fill="#F8EFE1", outline="#B6906C", width=3)
    for i in range(5):
        y = y1 + 58 + i * 15
        draw.line((cx - 35, y, cx + 35, y), fill="#D6BEA6", width=2)
    draw.rectangle((cx - 56, y1 + 34, cx - 36, y1 + 136), fill="#E7A9A0")


def draw_sneakers(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 80, y1 + 82, cx + 8, y1 + 126), radius=18, fill="#FFFFFF", outline="#8F8F8F", width=3)
    draw.polygon([(cx - 65, y1 + 82), (cx - 20, y1 + 45), (cx + 2, y1 + 82)], fill="#E8F1DA", outline="#8F8F8F")
    draw.line((cx - 48, y1 + 81, cx - 10, y1 + 95), fill="#9FB56B", width=4)
    draw.rounded_rectangle((cx - 4, y1 + 94, cx + 85, y1 + 132), radius=18, fill="#FFFFFF", outline="#8F8F8F", width=3)
    draw.polygon([(cx + 5, y1 + 94), (cx + 45, y1 + 58), (cx + 70, y1 + 94)], fill="#E8F1DA", outline="#8F8F8F")


def draw_yoga(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 78, y1 + 93, cx + 78, y1 + 132), radius=18, fill="#D2A3C8", outline="#9C6E93", width=3)
    draw.ellipse((cx - 62, y1 + 82, cx - 25, y1 + 118), fill="#E3B9DA", outline="#9C6E93", width=3)
    draw.line((cx - 40, y1 + 100, cx + 56, y1 + 100), fill="#FFFFFF", width=3)


def draw_bottle(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 35, y1 + 42, cx + 35, y1 + 136), radius=22, fill="#B8D8E3", outline="#6094A5", width=3)
    draw.rectangle((cx - 20, y1 + 24, cx + 20, y1 + 46), fill="#6EA6B6")
    draw.rounded_rectangle((cx - 25, y1 + 13, cx + 25, y1 + 30), radius=7, fill="#4A8190")
    draw.line((cx - 22, y1 + 73, cx + 22, y1 + 73), fill="#FFFFFF", width=3)


def draw_wallet(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 76, y1 + 58, cx + 76, y1 + 126), radius=14, fill="#B77B5F", outline="#7B4D3D", width=3)
    draw.line((cx - 65, y1 + 82, cx + 65, y1 + 82), fill="#D5A284", width=3)
    draw.ellipse((cx + 34, y1 + 88, cx + 50, y1 + 104), fill="#F3CF95")


def draw_diffuser(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 38, y1 + 72, cx + 38, y1 + 134), radius=14, fill="#E5C5B9", outline="#9A6B5B", width=3)
    for dx in (-30, -14, 0, 15, 31):
        draw.line((cx, y1 + 74, cx + dx, y1 + 20), fill="#B0836B", width=3)


def draw_gift_icon(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.rounded_rectangle((cx - 62, y1 + 66, cx + 62, y1 + 134), radius=10, fill="#F7B4C2", outline="#D57A8E", width=3)
    draw.rectangle((cx - 8, y1 + 66, cx + 8, y1 + 134), fill="#FFF1F2")
    draw.rectangle((cx - 62, y1 + 88, cx + 62, y1 + 104), fill="#FFF1F2")
    draw.ellipse((cx - 44, y1 + 38, cx - 4, y1 + 78), outline="#D57A8E", width=5)
    draw.ellipse((cx + 4, y1 + 38, cx + 44, y1 + 78), outline="#D57A8E", width=5)


ITEM_DRAWERS = {
    "lamp": draw_lamp,
    "cookware": draw_cookware,
    "perfume": draw_perfume,
    "scarf": draw_scarf,
    "jewelry": draw_jewelry,
    "cream": draw_cream,
    "tea": draw_tea,
    "dessert": draw_dessert,
    "note": draw_note,
    "sneakers": draw_sneakers,
    "yoga": draw_yoga,
    "bottle": draw_bottle,
    "wallet": draw_wallet,
    "diffuser": draw_diffuser,
    "gift": draw_gift_icon,
}


def draw_top_shopping_illustration(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)
    # shopping bag
    x, y = 790, 98
    draw.rounded_rectangle((x, y + 70, x + 170, y + 255), radius=8, fill="#F8CFCB", outline="#C88176", width=3)
    draw.arc((x + 28, y + 38, x + 78, y + 108), 180, 360, fill="#B2684C", width=5)
    draw.arc((x + 92, y + 38, x + 142, y + 108), 180, 360, fill="#B2684C", width=5)
    draw.text((x + 85, y + 162), "LOTTE", font=font(24, True), fill="#B95048", anchor="mm")
    draw.text((x + 85, y + 188), "DEPARTMENT STORE", font=font(10, False), fill="#B95048", anchor="mm")
    # coffee cup
    draw.rounded_rectangle((700, 210, 766, 310), radius=18, fill="#F4D8C9", outline="#D19C85", width=3)
    draw.rounded_rectangle((688, 198, 778, 224), radius=12, fill="#FFF7F0", outline="#D19C85", width=2)
    draw.rectangle((704, 186, 762, 202), fill="#FFF7F0", outline="#D19C85")
    draw.ellipse((719, 244, 748, 273), outline="#E1A19D", width=3)
    draw.text((733, 259), "L", font=font(20, True), fill="#E1A19D", anchor="mm")
    # gift box
    draw.rounded_rectangle((742, 315, 858, 420), radius=8, fill="#F6AAB8", outline="#C97586", width=3)
    draw.rectangle((792, 315, 810, 420), fill="#FFF0F2")
    draw.rectangle((742, 360, 858, 378), fill="#FFF0F2")
    draw.ellipse((760, 282, 800, 326), outline="#C97586", width=6)
    draw.ellipse((802, 282, 842, 326), outline="#C97586", width=6)
    # lipstick
    draw.rectangle((900, 280, 933, 398), fill="#D9B981", outline="#A87343")
    draw.rectangle((895, 350, 938, 406), fill="#F4C99D", outline="#A87343")
    draw.pieslice((898, 236, 934, 306), start=200, end=520, fill="#E93C6A", outline="#9F2647", width=2)
    draw.rectangle((894, 308, 938, 351), fill="#C58B5E", outline="#9A6743")
    # ribbon sweep
    ribbon = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ribbon)
    for i, alpha in enumerate((95, 55)):
        offset = i * 22
        pts = []
        for t in range(0, 280, 10):
            px = 36 + t * 3.5
            py = 330 + 28 * math.sin(t / 28) + offset
            pts.append((px, py))
        rdraw.line(pts, fill=(239, 88, 120, alpha), width=26)
    img.alpha_composite(ribbon)


def make_qr_image(url: str, size: int = 128) -> Image.Image:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#111111", back_color="#FFFFFF").convert("RGBA")
    qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
    return qr_img


# -----------------------------------------------------------------------------
# Fortune data
# -----------------------------------------------------------------------------

def seed_for_profile(profile: Profile) -> int:
    raw = f"{profile.name}|{profile.gender}|{profile.birth_date.isoformat()}|{profile.hour:02d}:{profile.minute:02d}"
    return int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16], 16)


def zodiac_for_year(year: int) -> str:
    return ZODIAC_ANIMALS[(year - 4) % 12]


def time_branch_for_hour(hour: int) -> str:
    return TIME_BRANCHES[((hour + 1) // 2) % 12]


def korean_time(hour: int, minute: int) -> str:
    period = "오전" if hour < 12 else "오후"
    h12 = hour % 12
    if h12 == 0:
        h12 = 12
    return f"{period} {h12:02d}:{minute:02d}"


def build_fortune(profile: Profile) -> dict:
    seed = seed_for_profile(profile)
    rng = random.Random(seed)
    theme = FORTUNE_THEMES[(seed + 4) % len(FORTUNE_THEMES)]

    labels = ("전체 운세", "재물 운", "연애 운", "건강 운")
    subtitles = (
        "새로운 기회와 만남이 있는 날!",
        "지출은 있지만 만족스러운 하루!",
        "설렘과 표현이 관계를 더 깊게!",
        "휴식과 수분이 컨디션을 좌우해요.",
    )
    icon_types = ("clover", "money", "heart", "sprout")
    scores = [rng.choice((4, 4, 4, 5)) for _ in labels]
    if max(scores) < 5:
        scores[rng.randrange(4)] = 5

    luck_numbers = rng.sample(range(1, 10), 3)
    return {
        "theme": theme,
        "scores": tuple(zip(labels, subtitles, icon_types, scores)),
        "numbers": luck_numbers,
        "zodiac": zodiac_for_year(profile.birth_date.year),
        "time_branch": time_branch_for_hour(profile.hour),
        "seed": seed,
    }


# -----------------------------------------------------------------------------
# Main result image renderer
# -----------------------------------------------------------------------------

def render_result_image(profile: Profile, download_url: str) -> bytes:
    fortune = build_fortune(profile)
    theme: FortuneTheme = fortune["theme"]
    w, h = STORY_SIZE

    img = vertical_gradient((w, h), PALETTE["bg_top"], PALETTE["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # Background sparkles
    rng = random.Random(fortune["seed"])
    for _ in range(70):
        cx = rng.randint(20, w - 20)
        cy = rng.randint(15, h - 15)
        r = rng.choice((5, 7, 9, 12))
        color = rng.choice(("#F2B27B", "#F28FA8", "#FFFFFF", "#E6A0AA"))
        draw_sparkle(draw, cx, cy, r, color)

    # Main card
    add_shadowed_round_rect(img, (38, 34, 1042, 1886), 44, (255, 253, 252, 238), outline="#FFFFFF", width=4, shadow=True, shadow_alpha=18)
    draw.rounded_rectangle((54, 50, 1026, 1870), radius=38, outline="#F7DAD8", width=2)

    # Header
    draw.text((90, 72), "LOTTE", font=font(34, True), fill="#D71920")
    draw.text((92, 110), "DEPARTMENT STORE", font=font(10, True), fill="#D71920")
    draw_top_shopping_illustration(img)
    draw_sparkle(draw, 385, 113, 12, PALETTE["gold"])
    draw_sparkle(draw, 695, 113, 12, PALETTE["gold"])
    draw.text((540, 113), "오늘의 라이프스타일 운세", font=font(24, True), fill=PALETTE["pink"], anchor="mm")
    draw.text((540, 193), "오늘의 운세", font=font(80, True), fill="#7C2C50", anchor="mm")
    draw.text((540, 263), "Today's Fortune", font=font(44, False, "serif"), fill="#DD6D8B", anchor="mm")

    # Greeting
    greeting = f"{profile.name}님, 오늘도 빛나는 하루가 될 거예요!"
    draw.text((540, 356), greeting, font=font(25, True), fill=PALETTE["deep"], anchor="mm")

    # Main message card
    add_shadowed_round_rect(img, (86, 404, 994, 610), 18, "#FFFDFC", outline=PALETTE["line"], width=2, shadow=False)
    draw.ellipse((118, 450, 198, 530), fill=PALETTE["pink_2"])
    draw_sparkle(draw, 158, 490, 28, "#FFFFFF")
    draw.text((238, 444), theme.headline, font=font(34, True), fill=PALETTE["deep"])
    draw_wrapped(draw, (238, 507), theme.headline_sub, font(22), PALETTE["deep"], 685, line_gap=9, max_lines=3)

    # Profile row
    add_shadowed_round_rect(img, (86, 636, 994, 742), 18, "#FFFDFC", outline=PALETTE["line"], width=2, shadow=False)
    profile_items = (
        ("성별", profile.gender),
        ("생년월일", profile.birth_date.strftime("%Y.%m.%d")),
        ("태어난 시간", korean_time(profile.hour, profile.minute)),
        ("띠", f"{fortune['zodiac']}띠"),
    )
    col_w = (994 - 86) // 4
    for i, (label, value) in enumerate(profile_items):
        x0 = 86 + i * col_w
        if i:
            draw.line((x0, 658, x0, 720), fill=PALETTE["line"], width=2)
        draw.text((x0 + col_w // 2, 665), label, font=font(20, True), fill=PALETTE["pink"], anchor="mm")
        draw.text((x0 + col_w // 2, 711), value, font=font(25, True), fill=PALETTE["deep"], anchor="mm")

    # Fortune cards
    card_y = 766
    card_h = 222
    gap = 16
    card_w = (908 - gap * 3) // 4
    for i, (label, subtitle, icon_type, score) in enumerate(fortune["scores"]):
        x1 = 86 + i * (card_w + gap)
        x2 = x1 + card_w
        add_shadowed_round_rect(img, (x1, card_y, x2, card_y + card_h), 18, "#FFFDFC", outline=PALETTE["line"], width=2, shadow=True, shadow_alpha=12, shadow_radius=10)
        cx = (x1 + x2) // 2
        if icon_type == "clover":
            draw_clover(draw, cx, card_y + 56, 0.85)
        elif icon_type == "money":
            draw_money_bag(draw, cx, card_y + 55, 0.8)
        elif icon_type == "heart":
            draw_heart(draw, cx, card_y + 55, 0.9)
        elif icon_type == "sprout":
            draw_sprout(draw, cx, card_y + 55, 0.85)
        draw.text((cx, card_y + 115), label, font=font(24, True), fill=PALETTE["deep"], anchor="mm")
        draw.text((cx, card_y + 151), subtitle, font=font(17), fill=PALETTE["deep"], anchor="mm")
        draw_star_rating(draw, x1 + 34, card_y + 194, score, size=12)

    # Shopping theme
    y = 1012
    add_shadowed_round_rect(img, (86, y, 994, y + 174), 18, "#FFFDFC", outline=PALETTE["line"], width=2, shadow=False)
    draw_sparkle(draw, 102, y + 32, 10, PALETTE["gold"])
    draw.text((122, y + 32), "추천 쇼핑 테마", font=font(20, True), fill=PALETTE["pink"])
    draw.text((114, y + 84), theme.theme, font=font(34, True), fill=PALETTE["deep"])
    draw_wrapped(draw, (114, y + 127), theme.theme_desc, font(20), PALETTE["deep"], 520, line_gap=6, max_lines=2)
    # mini living illustration
    draw.rounded_rectangle((740, y + 88, 835, y + 148), radius=28, fill="#F6B9B5", outline="#CF8F8A", width=2)
    draw.rounded_rectangle((716, y + 116, 858, y + 157), radius=20, fill="#F8C5C2", outline="#CF8F8A", width=2)
    draw.line((742, y + 157, 728, y + 170), fill="#A96C57", width=4)
    draw.line((836, y + 157, 852, y + 170), fill="#A96C57", width=4)
    draw.rectangle((896, y + 82, 904, y + 155), fill="#C89270")
    draw.polygon([(872, y + 82), (928, y + 82), (912, y + 42), (888, y + 42)], fill="#FFF0E2", outline="#D5A387")
    draw.rectangle((894, y + 153, 906, y + 165), fill="#A76E52")
    draw.ellipse((930, y + 126, 980, y + 172), fill="#AEC586", outline="#7E9F5E", width=2)
    draw.line((956, y + 116, 956, y + 172), fill="#58773D", width=4)
    draw.ellipse((940, y + 100, 958, y + 124), fill="#7DA35F")
    draw.ellipse((956, y + 96, 978, y + 124), fill="#8EB66D")

    # Brands
    y = 1210
    add_shadowed_round_rect(img, (86, y, 994, y + 112), 18, "#FFFDFC", outline=PALETTE["line"], width=2, shadow=False)
    draw.text((112, y + 34), "오늘의 추천 브랜드", font=font(21, True), fill=PALETTE["pink"])
    bx = 112
    by = y + 54
    b_gap = 12
    b_w = (860 - b_gap * (len(theme.brands) - 1)) // len(theme.brands)
    for brand in theme.brands:
        draw.rounded_rectangle((bx, by, bx + b_w, by + 46), radius=12, fill="#FFFFFF", outline="#F0D6D3", width=2)
        draw.text((bx + b_w // 2, by + 23), brand, font=font(18, True if len(brand) < 11 else False), fill=PALETTE["deep"], anchor="mm")
        bx += b_w + b_gap

    # Recommended items
    y = 1344
    add_shadowed_round_rect(img, (86, y, 994, y + 228), 18, "#FFFDFC", outline=PALETTE["line"], width=2, shadow=False)
    draw.text((112, y + 36), "♡ 오늘의 추천 아이템", font=font(22, True), fill=PALETTE["pink"])
    item_gap = 20
    item_w = (854 - item_gap * 2) // 3
    ix = 112
    for title, desc, icon_key in theme.items:
        draw.rounded_rectangle((ix, y + 64, ix + item_w, y + 204), radius=16, fill="#FFF7F5", outline="#F0D6D3", width=2)
        # image band
        draw.rounded_rectangle((ix + 10, y + 74, ix + item_w - 10, y + 145), radius=12, fill="#F7DDD5")
        drawer = ITEM_DRAWERS.get(icon_key, draw_gift_icon)
        drawer(draw, (ix + 10, y + 42, ix + item_w - 10, y + 148))
        draw.text((ix + item_w // 2, y + 163), title, font=font(19, True), fill=PALETTE["deep"], anchor="mm")
        draw.text((ix + item_w // 2, y + 191), desc, font=font(15), fill=PALETTE["deep"], anchor="mm")
        ix += item_w + item_gap

    # Lucky row
    y = 1592
    add_shadowed_round_rect(img, (86, y, 994, y + 104), 18, "#FFFDFC", outline=PALETTE["line"], width=2, shadow=False)
    third = (994 - 86) // 3
    draw.ellipse((120, y + 25, 184, y + 89), fill=theme.color_hex)
    draw.text((206, y + 38), "럭키 컬러", font=font(20, True), fill=PALETTE["pink"])
    draw.text((206, y + 74), theme.color_name, font=font(20, True), fill=PALETTE["deep"])
    draw.line((86 + third, y + 18, 86 + third, y + 88), fill=PALETTE["line"], width=2)
    draw_gift_icon(draw, (86 + third + 24, y - 6, 86 + third + 134, y + 86))
    draw.text((86 + third + 156, y + 38), "럭키 아이템", font=font(20, True), fill=PALETTE["pink"])
    draw.text((86 + third + 156, y + 74), theme.lucky_item, font=font(20, True), fill=PALETTE["deep"])
    draw.line((86 + third * 2, y + 18, 86 + third * 2, y + 88), fill=PALETTE["line"], width=2)
    draw.text((86 + third * 2 + 72, y + 38), "행운 숫자", font=font(20, True), fill=PALETTE["pink"])
    num_x = 86 + third * 2 + 66
    for n in fortune["numbers"]:
        draw.ellipse((num_x, y + 54, num_x + 44, y + 98), fill=PALETTE["pink"])
        draw.text((num_x + 22, y + 76), str(n), font=font(23, True), fill="#FFFFFF", anchor="mm")
        num_x += 62

    # Spots and QR
    y = 1718
    add_shadowed_round_rect(img, (86, y, 994, y + 122), 18, "#FFFDFC", outline=PALETTE["line"], width=2, shadow=False)
    draw.text((112, y + 29), "롯데백화점 추천 스팟", font=font(20, True), fill=PALETTE["pink"])
    sx = 112
    for title, desc in theme.spots:
        draw.text((sx, y + 64), title, font=font(17, True), fill=PALETTE["deep"])
        draw_wrapped(draw, (sx, y + 88), desc, font(12), PALETTE["deep"], 200, line_gap=3, max_lines=2)
        sx += 245
    # QR code
    qr = make_qr_image(download_url, size=112)
    qr_box = (864, y + 8, 976, y + 120)
    draw.rounded_rectangle((856, y + 1, 984, y + 129), radius=14, fill="#FFFFFF", outline=PALETTE["line"], width=2)
    img.alpha_composite(qr, (864, y + 8))

    # Quote and footer
    draw.text((540, 1862), f"“ {theme.advice} ”", font=font(24, True), fill="#94414E", anchor="mm")
    draw.text((540, 1897), "QR코드를 스캔하면 이 이미지를 다운로드할 수 있어요.", font=font(16), fill=PALETTE["muted"], anchor="mm")

    # crop back to exact size in case any decoration ran over
    img = img.crop((0, 0, w, h))

    out = io.BytesIO()
    img.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

def cleanup_old_results(max_age_hours: int = 10) -> None:
    cutoff = time.time() - max_age_hours * 3600
    try:
        for path in GENERATED_DIR.glob("*.png"):
            if path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
    except Exception:
        pass


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --pink: #ef4d7c;
            --pink2: #ff82a4;
            --deep: #3e2022;
            --line: #f5d4cf;
            --soft: #fff2f3;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 12% 4%, rgba(255,255,255,.95) 0 0.7rem, transparent 0.75rem),
                radial-gradient(circle at 88% 8%, rgba(255,255,255,.9) 0 0.55rem, transparent 0.6rem),
                linear-gradient(135deg, #fff7f8 0%, #fde7eb 48%, #fffafb 100%);
            color: var(--deep);
            font-family: Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif;
        }

        .block-container {
            max-width: 1480px;
            padding-top: 1.2rem;
            padding-bottom: 1.5rem;
        }

        #MainMenu, footer, header { visibility: hidden; }

        .lotte-logo {
            color: #d71920;
            font-size: 34px;
            line-height: 1;
            font-weight: 900;
            letter-spacing: .03em;
            margin-bottom: 0;
        }
        .lotte-sub {
            color: #d71920;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: .08em;
            margin-top: -4px;
            margin-bottom: 22px;
        }
        .side-title-small {
            text-align: center;
            font-size: 25px;
            margin: .25rem 0 0;
            color: #3e2022;
        }
        .side-title {
            text-align: center;
            font-size: 56px;
            line-height: 1.04;
            margin: .1rem 0 .3rem;
            color: #3e2022;
            font-weight: 900;
            letter-spacing: -.05em;
        }
        .side-caption {
            text-align: center;
            font-size: 17px;
            margin-bottom: 1.4rem;
            color: #6d3b2e;
            font-weight: 700;
        }
        .panel {
            background: rgba(255,255,255,.82);
            border: 1px solid #f6d8d6;
            border-radius: 24px;
            box-shadow: 0 14px 40px rgba(188, 67, 102, .10);
            padding: 1.15rem 1.25rem;
            margin-bottom: 1.05rem;
        }
        .panel-title {
            color: var(--pink);
            font-weight: 900;
            font-size: 21px;
            margin: 0 0 .8rem 0;
        }
        .notice {
            background: linear-gradient(135deg, #fff1f4, #fff7f7);
            border-radius: 16px;
            padding: 1rem 1rem .8rem;
            color: #704748;
            font-size: 14px;
            line-height: 1.65;
            margin-top: .8rem;
        }
        .hero-card {
            background: rgba(255,255,255,.72);
            border: 4px solid rgba(255,255,255,.9);
            border-radius: 34px;
            box-shadow: 0 20px 70px rgba(188, 67, 102, .18);
            padding: 1.25rem;
        }
        .download-card {
            background: rgba(255,255,255,.88);
            border: 1px solid #f5d4cf;
            border-radius: 24px;
            box-shadow: 0 14px 40px rgba(188, 67, 102, .10);
            padding: 1.2rem;
            margin-bottom: 1rem;
            text-align: center;
        }
        .download-title {
            color: #ef4d7c;
            font-size: 32px;
            font-weight: 900;
            margin-bottom: .4rem;
        }
        div[data-testid="stForm"] {
            border: none;
            padding: 0;
        }
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            border-color: #ead3d1;
            border-radius: 10px;
            background: rgba(255,255,255,.95);
        }
        .stRadio label {
            color: #3e2022 !important;
        }
        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"] {
            background: linear-gradient(90deg, #ef4d7c, #f36f9a) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            height: 3.2rem;
            font-weight: 900 !important;
            box-shadow: 0 10px 24px rgba(239,77,124,.25);
        }
        .stDownloadButton > button {
            width: 100%;
        }
        .qr-note {
            font-size: 13px;
            color: #7f5c5a;
            line-height: 1.55;
            background: #fff6f5;
            border: 1px solid #f5d4cf;
            border-radius: 14px;
            padding: .7rem .8rem;
            margin-top: .5rem;
        }
        img {
            border-radius: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def save_result_image(png_bytes: bytes, result_id: str) -> Path:
    path = GENERATED_DIR / f"{result_id}.png"
    path.write_bytes(png_bytes)
    return path


def generate_and_store(profile: Profile, base_url: str, result_id: str | None = None) -> tuple[str, bytes, str]:
    result_id = result_id or uuid.uuid4().hex[:14]
    download_url = make_download_url(base_url, result_id)
    png = render_result_image(profile, download_url)
    save_result_image(png, result_id)
    return result_id, png, download_url


def show_download_page(result_id: str) -> None:
    path = GENERATED_DIR / f"{result_id}.png"

    st.markdown(
        """
        <div class="download-card">
          <div class="download-title">오늘의 운세 이미지 다운로드</div>
          <div>QR코드로 접속한 결과 이미지예요. 아래 버튼으로 저장해 주세요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not path.exists():
        st.error("결과 이미지가 만료되었거나 서버에서 찾을 수 없습니다. 현장 키오스크에서 다시 생성해 주세요.")
        st.stop()

    png = path.read_bytes()
    file_name = f"lotte_today_fortune_{result_id}.png"
    st.image(png, use_container_width=True)
    st.download_button(
        "이미지 저장하기",
        data=png,
        file_name=file_name,
        mime="image/png",
        use_container_width=True,
    )

    # Best-effort auto download. Some mobile browsers block this, so the button above remains visible.
    b64 = base64.b64encode(png).decode("utf-8")
    components.html(
        f"""
        <html>
          <body style="margin:0; font-family:sans-serif; color:#7f5c5a;">
            <a id="download-link"
               download="{file_name}"
               href="data:image/png;base64,{b64}"
               style="display:inline-block; padding:10px 14px; border-radius:12px; background:#fff2f3; color:#ef4d7c; text-decoration:none; font-weight:700;">
               자동 다운로드가 시작되지 않으면 여기를 눌러 저장하세요
            </a>
            <script>
              setTimeout(function() {{
                document.getElementById("download-link").click();
              }}, 500);
            </script>
          </body>
        </html>
        """,
        height=58,
    )


def main_app() -> None:
    cleanup_old_results()
    inject_css()

    if not has_server_korean_font():
        st.warning(
            "서버에 한글 폰트가 없어 결과 이미지의 한글이 깨질 수 있습니다. "
            "Streamlit Cloud라면 저장소에 packages.txt를 추가하고 fonts-nanum 또는 fonts-noto-cjk를 설치해 주세요."
        )
    else:
        with st.sidebar.expander("폰트 진단", expanded=False):
            st.caption("결과 이미지 생성에 사용 중인 서버 폰트")
            st.code("\n".join(f"{k}: {v}" for k, v in get_active_font_paths().items()))

    query = get_query_params()
    result_id = first_query_value(query.get("rid"))
    if result_id:
        show_download_page(result_id)
        st.stop()

    base_url_default = get_default_base_url()
    with st.sidebar:
        st.markdown("### 운영 설정")
        base_url = st.text_input(
            "QR 다운로드용 앱 주소",
            value=base_url_default,
            help="휴대폰 카메라가 열 수 있는 공개 URL을 입력하세요. Streamlit Cloud, 사내망 URL, ngrok 주소 등을 사용할 수 있습니다.",
        )
        st.markdown(
            """
            <div class="qr-note">
            배포 후에는 환경변수 <b>PUBLIC_BASE_URL</b>에 앱 주소를 넣어두면 운영자가 매번 입력하지 않아도 됩니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    default_profile = Profile(
        name="이수진",
        gender="여성",
        birth_date=date(1990, 4, 25),
        hour=14,
        minute=30,
    )

    if "fortune_profile" not in st.session_state:
        st.session_state.fortune_profile = default_profile
    if "fortune_result_id" not in st.session_state:
        rid, png, url = generate_and_store(default_profile, base_url)
        st.session_state.fortune_result_id = rid
        st.session_state.fortune_png = png
        st.session_state.fortune_url = url

    left, right = st.columns([0.31, 0.69], gap="large")

    with left:
        st.markdown(
            """
            <div class="lotte-logo">LOTTE</div>
            <div class="lotte-sub">DEPARTMENT STORE</div>
            <div class="side-title-small">나만을 위한</div>
            <div class="side-title">오늘의 운세</div>
            <div class="side-caption">쇼핑 테마로 확인하는 운세</div>
            """,
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">🎁 사주 정보 입력</div>', unsafe_allow_html=True)
            st.caption("정확한 운세를 위해 정보를 입력해주세요.")

            with st.form("fortune_form", clear_on_submit=False):
                name = st.text_input("이름", value="", placeholder="이름을 입력해주세요")
                gender = st.radio("성별", options=["여성", "남성"], horizontal=True, index=0)
                birth_date = st.date_input(
                    "생년월일",
                    value=default_profile.birth_date,
                    min_value=date(1920, 1, 1),
                    max_value=date(2035, 12, 31),
                    format="YYYY-MM-DD",
                )
                col_h, col_m = st.columns(2)
                with col_h:
                    hour = st.selectbox("태어난 시간 - 시", list(range(24)), index=14, format_func=lambda v: f"{v:02d}")
                with col_m:
                    minute = st.selectbox("태어난 시간 - 분", list(range(0, 60, 5)), index=6, format_func=lambda v: f"{v:02d}")
                st.caption("※ 시간을 모를 경우 12:00(정오)로 입력하세요.")
                submitted = st.form_submit_button("운세 결과 확인하기 ✨", use_container_width=True)

            st.markdown(
                """
                <div class="notice">
                <b>안내사항</b><br>
                • 입력하신 정보는 서버에 별도로 저장하지 않고 결과 이미지 생성에만 사용됩니다.<br>
                • 오늘의 운세는 재미로 참고해주세요.<br>
                • QR 다운로드는 공개 앱 주소가 설정되어야 휴대폰에서 열립니다.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            clean_name = (name or "고객").strip()[:12]
            profile = Profile(
                name=clean_name,
                gender=gender,
                birth_date=birth_date,
                hour=int(hour),
                minute=int(minute),
            )
            rid, png, url = generate_and_store(profile, base_url)
            st.session_state.fortune_profile = profile
            st.session_state.fortune_result_id = rid
            st.session_state.fortune_png = png
            st.session_state.fortune_url = url
            st.success("운세 이미지가 생성되었어요!")

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">♡ 인스타 스토리 미리보기</div>', unsafe_allow_html=True)
        st.image(st.session_state.fortune_png, use_container_width=True)
        st.caption("결과 이미지는 인스타 스토리 1080×1920에 최적화되어 제공됩니다.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="panel" style="display:flex; align-items:center; gap:14px;">
              <div style="font-size:42px;">🛍️</div>
              <div>
                <b>오늘도 행복한 쇼핑 되세요!</b><br>
                롯데백화점이 당신의 하루를 응원합니다 💖
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="hero-card">', unsafe_allow_html=True)
        st.image(st.session_state.fortune_png, use_container_width=True)
        st.download_button(
            "이미지 다운로드",
            data=st.session_state.fortune_png,
            file_name=f"lotte_today_fortune_{st.session_state.fortune_result_id}.png",
            mime="image/png",
            use_container_width=True,
        )
        st.markdown(
            f"""
            <div class="qr-note">
            QR 연결 주소: <code>{st.session_state.fortune_url}</code><br>
            현장에서는 고객이 결과 이미지 하단 QR을 카메라로 스캔하면 다운로드 페이지로 이동합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

main_app()
