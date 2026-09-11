"""note記事「経費精算のレシートを全部見直すのは、やめました」の画像3枚を生成する。

render_fixedcost01.py の配色・書体・カード・余白を継承する。
（画像3＝claude.aiの実画面はユーザー手動撮影のため、ここでは生成しない）
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "note" / "images" / "2026-09-11"

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


def width_of(draw, text, f):
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def assert_fits(draw, text, f, max_width):
    actual = width_of(draw, text, f)
    if actual > max_width:
        raise ValueError(f"Text exceeds width: {text!r} ({actual}px > {max_width}px)")


def new_canvas(width, height):
    image = Image.new("RGB", (width, height), BG)
    return image, ImageDraw.Draw(image)


def draw_title(draw, title):
    draw.rounded_rectangle([60, 60, 68, 110], radius=4, fill=ORANGE)
    title_font = font(38, "heavy")
    assert_fits(draw, title, title_font, 1100)
    draw.text((88, 56), title, font=title_font, fill=NAVY)


def dashed_rect(draw, box, color, width=3, dash=10, gap=8):
    x1, y1, x2, y2 = box
    for x in range(int(x1), int(x2), dash + gap):
        draw.line([(x, y1), (min(x + dash, x2), y1)], fill=color, width=width)
        draw.line([(x, y2), (min(x + dash, x2), y2)], fill=color, width=width)
    for y in range(int(y1), int(y2), dash + gap):
        draw.line([(x1, y), (x1, min(y + dash, y2))], fill=color, width=width)
        draw.line([(x2, y), (x2, min(y + dash, y2))], fill=color, width=width)


# ---------------------------------------------------------------------------
# 画像1：ヘッダー（モチーフ＝表の1列だけが点線の空欄）


def draw_table_motif(draw):
    x, y = 762, 150
    col_w = (126, 104, 104, 118)
    row_h = 62
    rows = 5
    total_w = sum(col_w)

    # 表の枠（実線の3列）
    draw.rounded_rectangle([x, y, x + total_w, y + row_h * rows], radius=14, fill=CARD, outline=BORDER, width=2)
    # 見出し行の帯
    draw.rounded_rectangle([x, y, x + total_w, y + row_h], radius=14, fill=TINT)
    draw.rectangle([x, y + row_h - 14, x + total_w, y + row_h], fill=TINT)
    draw.line([(x, y + row_h), (x + total_w, y + row_h)], fill=BORDER, width=2)

    for index in range(2, rows):
        draw.line([(x, y + row_h * index), (x + total_w, y + row_h * index)], fill=BORDER, width=1)

    col_x = [x]
    for w in col_w:
        col_x.append(col_x[-1] + w)
    for cx in col_x[1:-1]:
        draw.line([(cx, y), (cx, y + row_h * rows)], fill=BORDER, width=1)

    # 埋まっている列の中身（バーで表現する）
    for row in range(1, rows):
        for col in range(3):
            bx1 = col_x[col] + 22
            bx2 = col_x[col + 1] - 22
            by = y + row_h * row + row_h // 2 - 5
            draw.rounded_rectangle([bx1, by, bx2, by + 10], radius=5, fill=BORDER)

    # 最後の1列だけ点線の空欄
    last_x1, last_x2 = col_x[3], col_x[4]
    dashed_rect(draw, (last_x1 + 3, y + 3, last_x2 - 3, y + row_h * rows - 3), ORANGE, width=3)

    label = "紙に書いていない列"
    label_font = font(19, "bold")
    lx = last_x1 + (last_x2 - last_x1) / 2 - width_of(draw, label, label_font) / 2
    draw.text((lx - 30, y + row_h * rows + 22), label, font=label_font, fill=ORANGE)


def render_header():
    image, draw = new_canvas(1280, 670)
    left = 72
    title_font = font(38, "heavy")
    line1 = "経費精算のレシートを"
    line2 = "全部見直すのは、やめました"
    assert_fits(draw, line1, title_font, 640)
    assert_fits(draw, line2, title_font, 640)

    draw.rounded_rectangle([left, 184, left + 8, 250], radius=4, fill=ORANGE)
    draw.text((left + 28, 169), line1, font=title_font, fill=NAVY)
    draw.text((left + 28, 229), line2, font=title_font, fill=NAVY)
    draw.line([(left, 350), (left + 620, 350)], fill=ORANGE, width=3)

    sub = "AIに読ませて、人が見るのは3か所"
    sub_font = font(24, "bold")
    assert_fits(draw, sub, sub_font, 620)
    draw.text((left, 300), sub, font=sub_font, fill=INK)

    reader = "中小企業のバックオフィスと、ひとり社長のためのAI活用"
    reader_font = font(19)
    assert_fits(draw, reader, reader_font, 640)
    draw.text((left, 392), reader, font=reader_font, fill=GRAY)

    draw_table_motif(draw)
    return image


# ---------------------------------------------------------------------------
# 画像2：用意したレシート4枚と、仕込んだ3か所


def draw_receipt_card(draw, box, no, shop, note_lines, trap):
    x1, y1, x2, y2 = box
    outline = ORANGE if trap else BORDER
    draw.rounded_rectangle(box, radius=18, fill=CARD, outline=outline, width=3 if trap else 2)

    badge_font = font(20, "heavy")
    draw.rounded_rectangle([x1 + 22, y1 + 20, x1 + 62, y1 + 58], radius=10, fill=ORANGE if trap else NAVY)
    bw = width_of(draw, no, badge_font)
    draw.text((x1 + 42 - bw / 2, y1 + 27), no, font=badge_font, fill=(255, 255, 255))

    shop_font = font(24, "heavy")
    assert_fits(draw, shop, shop_font, x2 - x1 - 100)
    draw.text((x1 + 76, y1 + 25), shop, font=shop_font, fill=NAVY)
    draw.line([(x1 + 22, y1 + 78), (x2 - 22, y1 + 78)], fill=BORDER, width=2)

    body_font = font(20)
    for index, line in enumerate(note_lines):
        assert_fits(draw, line, body_font, x2 - x1 - 48)
        draw.text((x1 + 24, y1 + 104 + index * 34), line, font=body_font, fill=INK if index == 0 else GRAY)

    if trap:
        tag_font = font(18, "bold")
        tw = width_of(draw, "仕込んだところ", tag_font)
        draw.rounded_rectangle([x2 - tw - 46, y2 - 52, x2 - 22, y2 - 16], radius=10, fill=ORANGE_TINT)
        draw.text((x2 - tw - 34, y2 - 46), "仕込んだところ", font=tag_font, fill=ORANGE)


def render_traps():
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "用意したダミーのレシート4枚と、仕込んだ3か所")

    cards = (
        ((60, 150, 626, 418), "1", "フジヤマ商店", ("菓子折と事務用品が1枚に", "軽減税率の8%と10%が混在"), True),
        ((654, 150, 1220, 418), "2", "割烹 みなと", ("手書きの領収書", "但し書きが「お品代」だけ"), True),
        ((60, 446, 626, 662), "3", "カフェ・ノルド", ("小計・値引き・合計・お預かり", "どれを経費として拾うか"), True),
        ((654, 446, 1220, 662), "4", "ミドリ電機", ("難所のない1枚", "対照用に置いた"), False),
    )
    for box, no, shop, lines, trap in cards:
        draw_receipt_card(draw, box, no, shop, lines, trap)

    return image


# ---------------------------------------------------------------------------
# 画像4：人が見る3か所


def draw_check_card(draw, box, index, heading, lines, self_served):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=18, fill=CARD, outline=BORDER, width=2)

    num_font = font(28, "heavy")
    draw.ellipse([x1 + 24, y1 + 26, x1 + 68, y1 + 70], fill=ORANGE)
    nw = width_of(draw, index, num_font)
    draw.text((x1 + 46 - nw / 2, y1 + 32), index, font=num_font, fill=(255, 255, 255))

    heading_font = font(26, "heavy")
    assert_fits(draw, heading, heading_font, 560)
    draw.text((x1 + 84, y1 + 32), heading, font=heading_font, fill=NAVY)

    # 右側にタグ（本文と段を分ける）
    tag = "頼み方で自動的に空欄になる" if self_served else "ここだけ自分で見る"
    tag_font = font(18, "bold")
    color = GRAY if self_served else ORANGE
    fill = TINT if self_served else ORANGE_TINT
    tw = width_of(draw, tag, tag_font)
    draw.rounded_rectangle([x2 - tw - 52, y1 + 30, x2 - 24, y1 + 68], radius=10, fill=fill)
    draw.text((x2 - tw - 38, y1 + 38), tag, font=tag_font, fill=color)

    draw.line([(x1 + 24, y1 + 92), (x2 - 24, y1 + 92)], fill=BORDER, width=2)

    body_font = font(21)
    for i, line in enumerate(lines):
        assert_fits(draw, line, body_font, x2 - x1 - 48)
        draw.text((x1 + 24, y1 + 110 + i * 34), line, font=body_font, fill=INK if i == 0 else GRAY)


def render_three_checks():
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "AIに読ませたあと、人が見るのは3か所")

    cards = (
        ((60, 140, 1220, 316), "1", "紙に書いていない列", ("勘定科目・用途・支払方法", "紙のどこにも答えがない欄"), True),
        ((60, 338, 1220, 514), "2", "「推定」「要確認」と書かれた行", ("AIが自分から申告している場所", "今回は「お品代」の1枚だった"), True),
        ((60, 536, 1220, 712), "3", "税額の合計", ("推測が1か所混ざると動く", "今回は1,281円から554円へ"), False),
    )
    for box, index, heading, lines, served in cards:
        draw_check_card(draw, box, index, heading, lines, served)

    return image


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    render_header().save(OUTPUT_DIR / "receipt_0_ヘッダー.png")
    render_traps().save(OUTPUT_DIR / "receipt_1_仕込んだ3か所.png")
    render_three_checks().save(OUTPUT_DIR / "receipt_3_人が見る3か所.png")
    print("done")


if __name__ == "__main__":
    main()
