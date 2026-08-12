"""note新シリーズ第1回「請求書の転記」の画像3枚を生成する。

新連載の1本目なので、ここで作った配色・書体・カードの型を次回以降そのまま引き継ぐ。
旧シリーズ（士業のAI実録）のテイストは意図的に参照していない。

生成物：
  note/images/2026-08-11/invoice_0_ヘッダー.png        1280x670
  note/images/2026-08-11/invoice_1_3枚バラバラ.png      1200x800
  note/images/2026-08-11/invoice_3_15箇所が1回に.png    1200x800
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "note" / "images" / "2026-08-11"
HEADER_MOTIF_PATH = PROJECT_DIR / ".output" / "invoice_header_motif.png"

FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"

# 新シリーズの配色：淡い地／ネイビー主色／アクセントはオレンジ1色だけ
BG = (251, 251, 249)
CARD = (255, 255, 255)
NAVY = (31, 51, 82)
INK = (34, 48, 63)
GRAY = (122, 135, 148)
BORDER = (216, 222, 230)
TINT = (237, 240, 244)
ORANGE = (226, 112, 58)
ORANGE_TINT = (252, 240, 232)


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

    normalized.thumbnail((405, 445), Image.Resampling.LANCZOS)
    return normalized


def render_header() -> Image.Image:
    image, draw = new_canvas(1280, 670)

    left = 92
    draw.rounded_rectangle([left, 186, left + 8, 254], radius=4, fill=ORANGE)

    draw.text((left + 30, 178), "AIが読んだ請求書を", font=font(50, "heavy"), fill=NAVY)
    draw.text((left + 30, 252), "全部見直すのは、やめました", font=font(50, "heavy"), fill=NAVY)

    draw.line([(left, 372), (left + 620, 372)], fill=BORDER, width=2)
    draw.text((left, 404), "確かめるのは合計1個だけ", font=font(31, "bold"), fill=ORANGE)
    draw.text((left, 462), "中小企業のバックオフィスと、ひとり社長のためのAI活用", font=font(20), fill=GRAY)

    motif = load_header_motif()
    motif_x = 1250 - motif.width
    motif_y = 126 + (445 - motif.height) // 2
    image.paste(motif, (motif_x, motif_y), motif)
    return image


# ---------------------------------------------------------------- 画像1

INVOICE_CARDS = (
    {
        "company": "株式会社ミナトデザイン",
        "rows": (("日付", "西暦"), ("金額", "税込を表示"), ("期限の呼び方", "支払期限")),
        "note": "件名の欄がない",
    },
    {
        "company": "有限会社カワセ工材",
        "rows": (("日付", "西暦・スラッシュ区切り"), ("金額", "税込を表示"), ("期限の呼び方", "支払期日")),
        "note": "明細に値引きの行がある",
    },
    {
        "company": "サクラ配送サービス",
        "rows": (("日付", "和暦"), ("金額", "税抜を表示"), ("期限の呼び方", "お支払期日")),
        "note": "税込は下のほうに小さく",
    },
)


def draw_invoice_card(draw, x: int, y: int, w: int, h: int, spec: dict) -> None:
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=CARD, outline=BORDER, width=2)

    draw.rounded_rectangle([x, y, x + w, y + 62], radius=14, fill=NAVY)
    draw.rectangle([x, y + 40, x + w, y + 62], fill=NAVY)
    centered(draw, spec["company"], x + w / 2, y + 18, font(22, "bold"), CARD)

    row_y = y + 96
    for label, value in spec["rows"]:
        draw.text((x + 26, row_y), label, font=font(17), fill=GRAY)
        draw.text((x + 26, row_y + 26), value, font=font(21, "bold"), fill=INK)
        row_y += 82

    strip_top = y + h - 96
    draw.rounded_rectangle(
        [x + 20, strip_top, x + w - 20, strip_top + 68], radius=10, fill=ORANGE_TINT
    )
    centered(draw, "ここが引っかけ", x + w / 2, strip_top + 12, font(15, "bold"), ORANGE)
    centered(draw, spec["note"], x + w / 2, strip_top + 36, font(18, "bold"), ORANGE)


def render_invoice_differences() -> Image.Image:
    image, draw = new_canvas(1200, 800)

    draw.rounded_rectangle([60, 66, 68, 116], radius=4, fill=ORANGE)
    draw.text((88, 62), "同じ請求書でも、3枚とも書き方が違う", font=font(38, "heavy"), fill=NAVY)
    draw.text((88, 124), "取引先ごとにテンプレートが違うので、そろっている前提は置けない", font=font(19), fill=GRAY)

    card_w, gap, top, card_h = 340, 30, 210, 470
    for index, spec in enumerate(INVOICE_CARDS):
        draw_invoice_card(draw, 60 + index * (card_w + gap), top, card_w, card_h, spec)

    centered(draw, "西暦と和暦、税込と税抜、期限の呼び方。3枚とも違う", 600, 726, font(20, "bold"), INK)
    return image


# ---------------------------------------------------------------- 画像3

def draw_compare_card(draw, x: int, y: int, w: int, h: int, spec: dict) -> None:
    accent = spec["accent"]
    outline = ORANGE if accent else BORDER
    draw.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=CARD, outline=outline, width=3 if accent else 2)

    centered(draw, spec["heading"], x + w / 2, y + 34, font(26, "bold"), ORANGE if accent else GRAY)

    centered(draw, spec["big"], x + w / 2, y + 96, font(96, "heavy"), ORANGE if accent else NAVY)
    centered(draw, spec["small"], x + w / 2, y + 224, font(21), GRAY)

    draw.line([(x + 44, y + 282), (x + w - 44, y + 282)], fill=BORDER, width=2)
    centered(draw, spec["foot"], x + w / 2, y + 308, font(spec["foot_size"], "bold"), spec["foot_color"])


def render_check_comparison() -> Image.Image:
    image, draw = new_canvas(1200, 800)

    draw.rounded_rectangle([60, 66, 68, 116], radius=4, fill=ORANGE)
    draw.text((88, 62), "確かめるのは、合計1個だけでいい", font=font(38, "heavy"), fill=NAVY)
    draw.text((88, 124), "全部見比べるかわりに、合計を1回だけ突き合わせる", font=font(19), fill=GRAY)

    card_w, card_h, top = 470, 380, 226
    draw_compare_card(draw, 60, top, card_w, card_h, {
        "heading": "全部見比べる",
        "big": "15箇所",
        "small": "5項目 × 3枚",
        "foot": "転記を2回やっているのと同じ",
        "foot_size": 20,
        "foot_color": GRAY,
        "accent": False,
    })
    draw_compare_card(draw, 670, top, card_w, card_h, {
        "heading": "合計だけ照らす",
        "big": "1回",
        "small": "3枚の合計欄を足すだけ",
        "foot": "264,000 + 354,420 + 1,188,000",
        "foot_size": 20,
        "foot_color": INK,
        "accent": True,
    })
    centered(draw, "= 1,806,420", 670 + card_w / 2, top + 340, font(24, "heavy"), ORANGE)

    arrow_y = top + card_h / 2
    draw.line([(552, arrow_y), (628, arrow_y)], fill=NAVY, width=5)
    draw.polygon([(650, arrow_y), (626, arrow_y - 13), (626, arrow_y + 13)], fill=NAVY)

    centered(draw, "合計が合わなかった月だけ、1枚ずつ見に行けばいい", 600, 686, font(20, "bold"), INK)
    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = (
        ("invoice_0_ヘッダー.png", render_header()),
        ("invoice_1_3枚バラバラ.png", render_invoice_differences()),
        ("invoice_3_15箇所が1回に.png", render_check_comparison()),
    )
    for name, image in pages:
        path = OUTPUT_DIR / name
        image.save(path)
        print(f"saved: {path}  {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
