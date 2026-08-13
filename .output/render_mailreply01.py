"""note新シリーズ第2回「問い合わせメールの一次返信」の画像3枚を生成する。

配色・書体・カードの型は第1回（.output/render_invoice01.py）をそのまま引き継ぐ。
ヘッダー右側の線画のみCodex生成の素材を合成し、日本語はPillowで決定的に描く。

生成物：
  note/images/2026-08-13/mailreply_0_ヘッダー.png          1280x670
  note/images/2026-08-13/mailreply_1_3通の問い合わせ.png    1200x800
  note/images/2026-08-13/mailreply_3_言い切りだけ拾う.png   1200x800
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "note" / "images" / "2026-08-13"
HEADER_MOTIF_PATH = PROJECT_DIR / ".output" / "mailreply_header_motif.png"

FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"

# 新シリーズの確定パレット（第1回と同一）
BG = (251, 251, 249)
CARD = (255, 255, 255)
NAVY = (31, 51, 82)
INK = (34, 48, 63)
GRAY = (122, 135, 148)
BORDER = (216, 222, 230)
TINT = (237, 240, 244)
ORANGE = (226, 112, 58)
ORANGE_TINT = (252, 240, 232)

MOTIF_BOX = (405, 445)


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    paths = {"regular": FONT_REGULAR, "bold": FONT_BOLD, "heavy": FONT_HEAVY}
    path = paths[weight]
    if not Path(path).exists():
        path = FONT_BOLD
    return ImageFont.truetype(path, size)


def width_of(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def centered(draw, text, center_x, y, f, fill) -> None:
    draw.text((center_x - width_of(draw, text, f) / 2, y), text, font=f, fill=fill)


def new_canvas(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), BG)
    return image, ImageDraw.Draw(image)


def section_heading(draw, title: str, subtitle: str) -> None:
    """画像1・3で共通の見出し（オレンジの縦バー＋見出し＋説明）。"""
    draw.rounded_rectangle([60, 66, 68, 116], radius=4, fill=ORANGE)
    draw.text((88, 62), title, font=font(38, "heavy"), fill=NAVY)
    draw.text((88, 124), subtitle, font=font(19), fill=GRAY)


# ---------------------------------------------------------------- ヘッダー

def load_header_motif() -> Image.Image:
    """生成線画を連載の確定パレットへ正規化し、透過素材として返す。"""
    if not HEADER_MOTIF_PATH.exists():
        raise FileNotFoundError(f"ヘッダー線画が見つかりません: {HEADER_MOTIF_PATH}")

    motif = Image.open(HEADER_MOTIF_PATH).convert("RGBA")
    alpha = motif.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError(f"ヘッダー線画が空です: {HEADER_MOTIF_PATH}")
    motif = motif.crop(bbox)

    # 生成画像に含まれる微妙な色ぶれを、確定済みの色だけへ丸める。
    palette = (NAVY, ORANGE, CARD, TINT, BORDER)
    normalized = Image.new("RGBA", motif.size, (0, 0, 0, 0))
    src = motif.load()
    dst = normalized.load()
    for y in range(motif.height):
        for x in range(motif.width):
            r, g, b, a = src[x, y]
            if a == 0:
                continue
            nearest = min(
                palette,
                key=lambda color: (
                    (r - color[0]) ** 2 + (g - color[1]) ** 2 + (b - color[2]) ** 2
                ),
            )
            dst[x, y] = (*nearest, a)

    normalized.thumbnail(MOTIF_BOX, Image.Resampling.LANCZOS)
    return normalized


def render_header() -> Image.Image:
    image, draw = new_canvas(1280, 670)

    left = 92
    draw.rounded_rectangle([left, 186, left + 8, 254], radius=4, fill=ORANGE)

    draw.text((left + 30, 178), "AIに書かせた一次返信、", font=font(50, "heavy"), fill=NAVY)
    draw.text((left + 30, 252), "勝手に約束していました", font=font(50, "heavy"), fill=NAVY)

    draw.line([(left, 372), (left + 620, 372)], fill=BORDER, width=2)
    draw.text((left, 404), "見るのは「言い切り」だけ", font=font(31, "bold"), fill=ORANGE)
    draw.text((left, 462), "中小企業のバックオフィスと、ひとり社長のためのAI活用", font=font(20), fill=GRAY)

    motif = load_header_motif()
    motif_x = 1250 - motif.width
    motif_y = 126 + (MOTIF_BOX[1] - motif.height) // 2
    image.paste(motif, (motif_x, motif_y), motif)
    return image


# ---------------------------------------------------------------- 画像1

INQUIRY_CARDS = (
    {
        "sender": "製造業から｜見積依頼",
        "rows": (
            ("聞かれていること", "単価と納期"),
            ("答えるのに要るもの", "価格表・生産状況"),
        ),
        "note": "9月第1週に間に合う？",
    },
    {
        "sender": "個人のお客さん｜予約変更",
        "rows": (
            ("聞かれていること", "変更の可否とキャンセル料"),
            ("答えるのに要るもの", "空き状況・キャンセル規約"),
        ),
        "note": "変更できる？ いくら？",
    },
    {
        "sender": "取引先｜クレーム",
        "rows": (
            ("聞かれていること", "交換の可否と送料の負担"),
            ("答えるのに要るもの", "返品ポリシー・在庫"),
        ),
        "note": "交換できる？ 誰が払う？",
    },
)


def draw_inquiry_card(draw, x: int, y: int, w: int, h: int, spec: dict) -> None:
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=CARD, outline=BORDER, width=2)

    draw.rounded_rectangle([x, y, x + w, y + 62], radius=14, fill=NAVY)
    draw.rectangle([x, y + 40, x + w, y + 62], fill=NAVY)
    centered(draw, spec["sender"], x + w / 2, y + 18, font(21, "bold"), CARD)

    row_y = y + 104
    for label, value in spec["rows"]:
        draw.text((x + 26, row_y), label, font=font(17), fill=GRAY)
        draw.text((x + 26, row_y + 26), value, font=font(21, "bold"), fill=INK)
        row_y += 98

    strip_top = y + h - 104
    draw.rounded_rectangle(
        [x + 20, strip_top, x + w - 20, strip_top + 74], radius=10, fill=ORANGE_TINT
    )
    centered(draw, "渡していないので答えられない", x + w / 2, strip_top + 14, font(15, "bold"), ORANGE)
    centered(draw, spec["note"], x + w / 2, strip_top + 40, font(19, "bold"), ORANGE)


def render_inquiries() -> Image.Image:
    image, draw = new_canvas(1200, 800)

    section_heading(
        draw,
        "3通とも、まだ答えられないことを聞いてくる",
        "価格表も空き状況も規約も、AIには何ひとつ渡していない",
    )

    card_w, gap, top, card_h = 340, 30, 216, 408
    for index, spec in enumerate(INQUIRY_CARDS):
        draw_inquiry_card(draw, 60 + index * (card_w + gap), top, card_w, card_h, spec)

    centered(
        draw,
        "問い合わせは、その場で答えられることのほうが少ない",
        600,
        698,
        font(20, "bold"),
        INK,
    )
    return image


# ---------------------------------------------------------------- 画像3

VERDICT_LINES = (
    "「変更を承りました」",
    "「料金は発生いたしません」",
    "「交換にて対応させていただきます」",
    "「送料は弊社にて負担いたします」",
)


def draw_compare_card(draw, x: int, y: int, w: int, h: int, spec: dict) -> None:
    accent = spec["accent"]
    outline = ORANGE if accent else BORDER
    draw.rounded_rectangle(
        [x, y, x + w, y + h], radius=16, fill=CARD, outline=outline, width=3 if accent else 2
    )

    centered(draw, spec["heading"], x + w / 2, y + 34, font(26, "bold"), ORANGE if accent else GRAY)
    centered(draw, spec["big"], x + w / 2, y + 96, font(96, "heavy"), ORANGE if accent else NAVY)
    centered(draw, spec["small"], x + w / 2, y + 224, font(21), GRAY)
    draw.line([(x + 44, y + 282), (x + w - 44, y + 282)], fill=BORDER, width=2)


def render_verdict_comparison() -> Image.Image:
    image, draw = new_canvas(1200, 800)

    section_heading(
        draw,
        "確かめるのは、数字じゃなくて「言い切り」",
        "全文を読み直すかわりに、言い切っている文だけを拾う",
    )

    card_w, card_h, top = 470, 380, 210
    draw_compare_card(draw, 60, top, card_w, card_h, {
        "heading": "全文を読み直す",
        "big": "3,000字",
        "small": "3通ぶんの下書き",
        "accent": False,
    })
    centered(draw, "読んでも、送っていいかは分からない", 60 + card_w / 2, top + 308, font(19, "bold"), GRAY)

    draw_compare_card(draw, 670, top, card_w, card_h, {
        "heading": "言い切りだけ拾う",
        "big": "4文",
        "small": "可否・費用の負担・日程の確定",
        "accent": True,
    })
    centered(draw, "1通目 0 ／ 2通目 2 ／ 3通目 2", 670 + card_w / 2, top + 308, font(20, "bold"), INK)

    arrow_y = top + card_h / 2
    draw.line([(552, arrow_y), (628, arrow_y)], fill=NAVY, width=5)
    draw.polygon([(650, arrow_y), (626, arrow_y - 13), (626, arrow_y + 13)], fill=NAVY)

    # 引っかかった4文を下に並べる
    list_top = top + card_h + 42
    draw.rounded_rectangle([60, list_top, 1140, list_top + 108], radius=12, fill=ORANGE_TINT)
    centered(draw, "素で頼んだ版で引っかかった4文", 600, list_top + 14, font(17, "bold"), ORANGE)
    for index, line in enumerate(VERDICT_LINES):
        column_x = 300 if index % 2 == 0 else 900
        line_y = list_top + 48 + (index // 2) * 30
        centered(draw, line, column_x, line_y, font(19, "bold"), INK)

    centered(
        draw,
        "渡していない数字は0個。数字を追っても、事故は1件も捕まらない",
        600,
        list_top + 132,
        font(20, "bold"),
        INK,
    )
    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = (
        ("mailreply_0_ヘッダー.png", render_header()),
        ("mailreply_1_3通の問い合わせ.png", render_inquiries()),
        ("mailreply_3_言い切りだけ拾う.png", render_verdict_comparison()),
    )
    for name, image in pages:
        path = OUTPUT_DIR / name
        image.save(path)
        print(f"saved: {path}  {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
