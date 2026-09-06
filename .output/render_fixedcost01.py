"""note記事「毎月の引き落とし、名前を見ても何か分からない」の図解3枚を生成する。

render_deadline01.py / render_minutes01.py の配色・書体・カード・余白を継承し、
日本語と図形をすべてPillowで決定的に描画する。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "note" / "images" / "2026-09-06"

REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"

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
    path = {"regular": REGULAR, "bold": BOLD, "heavy": HEAVY}[weight]
    if not Path(path).exists():
        raise FileNotFoundError(f"Required font is missing: {path}")
    return ImageFont.truetype(path, size)


def width_of(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def assert_fits(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, max_width: int) -> None:
    actual = width_of(draw, text, f)
    if actual > max_width:
        raise ValueError(f"Text exceeds width: {text!r} ({actual}px > {max_width}px)")


def centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    center_x: float,
    y: float,
    f: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    max_width: int,
) -> None:
    assert_fits(draw, text, f, max_width)
    draw.text((center_x - width_of(draw, text, f) / 2, y), text, font=f, fill=fill)


def new_canvas(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), BG)
    return image, ImageDraw.Draw(image)


def draw_title(draw: ImageDraw.ImageDraw, title: str) -> None:
    draw.rounded_rectangle([60, 60, 68, 110], radius=4, fill=ORANGE)
    title_font = font(38, "heavy")
    assert_fits(draw, title, title_font, 1100)
    draw.text((88, 56), title, font=title_font, fill=NAVY)


def draw_arrow_head(
    draw: ImageDraw.ImageDraw,
    end: tuple[float, float],
    direction: tuple[float, float],
    color: tuple[int, int, int],
    size: int = 10,
) -> None:
    ex, ey = end
    dx, dy = direction
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    bx, by = ex - ux * size * 1.6, ey - uy * size * 1.6
    draw.polygon(
        [(ex, ey), (bx + px * size * 0.65, by + py * size * 0.65), (bx - px * size * 0.65, by - py * size * 0.65)],
        fill=color,
    )


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    color: tuple[int, int, int],
    width: int = 4,
    head: int = 10,
) -> None:
    draw.line(points, fill=color, width=width, joint="curve")
    draw_arrow_head(
        draw,
        points[-1],
        (points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]),
        color,
        head,
    )


def draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    width: int = 3,
    dash: int = 9,
    gap: int = 8,
) -> None:
    x1, y1 = start
    x2, y2 = end
    if x1 != x2:
        raise ValueError("This helper intentionally supports vertical lines only")
    y = y1
    while y < y2:
        draw.line([(x1, y), (x1, min(y + dash, y2))], fill=color, width=width)
        y += dash + gap


# ---------------------------------------------------------------------------
# 画像0：ヘッダー


def draw_statement_motif(draw: ImageDraw.ImageDraw) -> None:
    """カード明細の名前欄だけが読めない様子を描く。"""
    x1, y1, x2, y2 = 770, 128, 1218, 500
    draw.rounded_rectangle([x1, y1, x2, y2], radius=18, fill=CARD, outline=NAVY, width=4)

    draw.rounded_rectangle([x1 + 28, y1 + 26, x1 + 128, y1 + 39], radius=6, fill=NAVY)
    draw.rounded_rectangle([x2 - 132, y1 + 26, x2 - 28, y1 + 39], radius=6, fill=TINT)
    draw.line([(x1 + 24, y1 + 62), (x2 - 24, y1 + 62)], fill=BORDER, width=2)

    column_header_y = y1 + 76
    centered(draw, "名前", x1 + 108, column_header_y, font(15, "bold"), GRAY, 100)
    centered(draw, "金額", x2 - 92, column_header_y, font(15, "bold"), GRAY, 100)
    draw.line([(x1 + 24, y1 + 101), (x2 - 24, y1 + 101)], fill=BORDER, width=1)

    rows = (
        ("エー＊＊", "12,800円", False),
        ("？", "4,980円", True),
        ("エル＊＊", "18,600円", False),
        ("？", "2,400円", True),
        ("？", "9,900円", True),
    )
    name_font = font(22, "bold")
    amount_font = font(19, "bold")
    for index, (name, amount, unknown) in enumerate(rows):
        top = y1 + 119 + index * 48
        if unknown:
            draw.rounded_rectangle([x1 + 22, top - 4, x2 - 22, top + 42], radius=9, fill=ORANGE_TINT)
        if index:
            draw.line([(x1 + 30, top - 10), (x2 - 30, top - 10)], fill=BORDER, width=1)
        draw.rounded_rectangle([x1 + 34, top + 8, x1 + 43, top + 17], radius=4, fill=ORANGE if unknown else GRAY)
        name_color = ORANGE if unknown else INK
        draw.text((x1 + 62, top), name, font=name_font, fill=name_color)
        amount_x = x2 - 36 - width_of(draw, amount, amount_font)
        draw.text((amount_x, top + 2), amount, font=amount_font, fill=NAVY)

def render_header() -> Image.Image:
    image, draw = new_canvas(1280, 670)
    left = 72
    title_font = font(38, "heavy")
    line1 = "毎月の引き落とし、"
    line2 = "名前を見ても何か分からない"
    assert_fits(draw, line1, title_font, 660)
    assert_fits(draw, line2, title_font, 660)

    draw.rounded_rectangle([left, 184, left + 8, 250], radius=4, fill=ORANGE)
    draw.text((left + 28, 169), line1, font=title_font, fill=NAVY)
    draw.text((left + 28, 229), line2, font=title_font, fill=NAVY)
    draw.line([(left, 350), (left + 650, 350)], fill=ORANGE, width=3)

    reader = "中小企業のバックオフィスと、ひとり社長のためのAI活用"
    reader_font = font(19)
    assert_fits(draw, reader, reader_font, 666)
    draw.text((left, 392), reader, font=reader_font, fill=GRAY)
    draw_statement_motif(draw)
    return image


# ---------------------------------------------------------------------------
# 画像1：情報の散らばり


def draw_info_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    heading: str,
    lines: tuple[str, ...],
    active: bool,
) -> None:
    x1, y1, x2, y2 = box
    outline = ORANGE if active else BORDER
    width = 3 if active else 2
    draw.rounded_rectangle(box, radius=18, fill=CARD, outline=outline, width=width)
    draw.rounded_rectangle([x1 + 24, y1 + 24, x1 + 32, y1 + 64], radius=4, fill=ORANGE if active else NAVY)
    heading_font = font(25 if len(heading) > 8 else 28, "heavy")
    assert_fits(draw, heading, heading_font, x2 - x1 - 82)
    draw.text((x1 + 48, y1 + 19), heading, font=heading_font, fill=NAVY)
    draw.line([(x1 + 24, y1 + 85), (x2 - 24, y1 + 85)], fill=BORDER, width=2)

    body_font = font(21)
    for index, line in enumerate(lines):
        assert_fits(draw, line, body_font, x2 - x1 - 48)
        draw.text((x1 + 24, y1 + 116 + index * 43), line, font=body_font, fill=INK if index == 0 else GRAY)


def draw_break_mark(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.line([(x - 12, y + 7), (x - 2, y - 7)], fill=GRAY, width=3)
    draw.line([(x + 2, y + 7), (x + 12, y - 7)], fill=GRAY, width=3)


def render_information_scattered() -> Image.Image:
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "固定費の情報は、3か所に分かれている")

    cards = (
        ((60, 146, 386, 458), "明細", ("金額と日付はある", "名前が読めない"), True),
        ((419, 146, 829, 458), "契約したときのメール", ("プラン名と条件はある", "今いくら引かれているかは", "出てこない"), False),
        ((862, 146, 1220, 458), "自分の頭の中", ("誰が何のために申し込んだか", "しかも忘れている"), False),
    )
    for box, heading, lines, active in cards:
        draw_info_card(draw, box, heading, lines, active)

    # 実線は明細だけからAIへ。残り2つは途中で切れている。
    draw_arrow(draw, [(223, 458), (223, 562)], ORANGE, width=4, head=11)
    note_box = (82, 486, 364, 530)
    draw.rounded_rectangle(note_box, radius=12, fill=ORANGE_TINT)
    centered(draw, "AIに渡せるのはここだけ", 223, 496, font(18, "bold"), ORANGE, 256)

    for x in (624, 1041):
        draw_dashed_line(draw, (x, 458), (x, 523), GRAY, width=3)
        draw_break_mark(draw, x, 536)

    ai_box = (126, 568, 320, 648)
    draw.rounded_rectangle(ai_box, radius=18, fill=CARD, outline=ORANGE, width=3)
    centered(draw, "AI", 223, 585, font(30, "heavy"), NAVY, 150)
    centered(draw, "明細だけを見る", 223, 621, font(15, "bold"), GRAY, 160)

    centered(draw, "材料がつながっていない", 624, 577, font(17, "bold"), GRAY, 330)
    centered(draw, "材料がつながっていない", 1041, 577, font(17, "bold"), GRAY, 320)
    return image


# ---------------------------------------------------------------------------
# 画像2：揃っている仕事


def draw_small_work_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    heading: str,
    material: str,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=14, fill=CARD, outline=BORDER, width=2)
    draw.rounded_rectangle([x1 + 18, y1 + 18, x1 + 26, y2 - 18], radius=4, fill=NAVY)
    heading_font = font(22, "bold")
    material_font = font(17)
    assert_fits(draw, heading, heading_font, x2 - x1 - 72)
    assert_fits(draw, material, material_font, x2 - x1 - 72)
    draw.text((x1 + 44, y1 + 15), heading, font=heading_font, fill=INK)
    draw.text((x1 + 44, y1 + 50), material, font=material_font, fill=GRAY)


def draw_source_chip(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=12, fill=TINT)
    centered(draw, label, (x1 + x2) / 2, y1 + 14, font(17, "bold"), NAVY, x2 - x1 - 20)


def render_ready_work() -> Image.Image:
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "AIが始められる形になっているか")

    left_panel = (60, 136, 620, 636)
    right_panel = (660, 136, 1220, 636)
    for panel in (left_panel, right_panel):
        draw.rounded_rectangle(panel, radius=18, fill=CARD, outline=BORDER, width=2)

    centered(draw, "モノが揃っている仕事", 340, 166, font(28, "heavy"), NAVY, 500)
    centered(draw, "揃っていない仕事", 940, 166, font(28, "heavy"), NAVY, 500)
    centered(draw, "AIはすぐ作業に入れる", 340, 208, font(17, "bold"), GRAY, 500)
    centered(draw, "先に材料を集める工程がある", 940, 208, font(17, "bold"), GRAY, 500)

    left_cards = (
        ((92, 252, 588, 332), "請求書の転記", "請求書のPDFがある"),
        ((92, 348, 588, 428), "問い合わせの返信", "メール本文が届いている"),
        ((92, 444, 588, 524), "議事録の抜き書き", "文字起こしがある"),
        ((92, 540, 588, 620), "期限の見張り", "一覧がある"),
    )
    for box, heading, material in left_cards:
        draw_small_work_card(draw, box, heading, material)

    source_boxes = (
        ((692, 258, 830, 312), "明細"),
        ((871, 258, 1009, 312), "契約メール"),
        ((1050, 258, 1188, 312), "記憶"),
    )
    for box, label in source_boxes:
        draw_source_chip(draw, box, label)

    # 3つの材料から、固定費カード上端の空いた位置へ矢印を集める。
    targets = ((810, 374), (940, 374), (1070, 374))
    for (box, _), target in zip(source_boxes, targets):
        sx = (box[0] + box[2]) // 2
        sy = box[3]
        draw_arrow(draw, [(sx, sy + 8), (sx, 340), target], ORANGE, width=3, head=8)

    fixed_box = (722, 376, 1158, 546)
    draw.rounded_rectangle(fixed_box, radius=18, fill=CARD, outline=ORANGE, width=3)
    centered(draw, "固定費の棚卸し", 940, 411, font(30, "heavy"), NAVY, 390)
    draw.line([(762, 461), (1118, 461)], fill=BORDER, width=2)
    centered(draw, "材料が3か所に散っている", 940, 481, font(20, "bold"), INK, 390)
    centered(draw, "集めてから、やっと始められる", 940, 515, font(18), GRAY, 390)

    note_box = (755, 568, 1125, 616)
    draw.rounded_rectangle(note_box, radius=12, fill=ORANGE_TINT)
    centered(draw, "集めてくる工程", 940, 580, font(20, "bold"), ORANGE, 340)

    centered(
        draw,
        "違いは善悪ではなく、AIが得意な形になっているかどうか",
        640,
        660,
        font(18, "bold"),
        GRAY,
        1120,
    )
    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = (
        ("fixedcost_0_ヘッダー.png", render_header()),
        ("fixedcost_1_情報の散らばり.png", render_information_scattered()),
        ("fixedcost_2_揃っている仕事.png", render_ready_work()),
    )
    for name, image in pages:
        path = OUTPUT_DIR / name
        image.save(path, format="PNG")
        print(f"saved: {path}  {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
