"""note記事「同じ期限をAIに2通りの頼み方で聞いたら」の画像4枚を生成する。

render_minutes01.py / render_awareness01.py の配色・書体・カード・余白を継承し、
日本語・表・分岐図をすべてPillowで決定的に描画する。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "note" / "images" / "2026-08-29"

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


def text_size(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0], box[3] - box[1]


def width_of(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont) -> int:
    return text_size(draw, text, f)[0]


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
    size: int = 12,
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


def draw_poly_arrow(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    color: tuple[int, int, int],
    width: int = 4,
    head: int = 11,
) -> None:
    draw.line(points, fill=color, width=width, joint="curve")
    draw_arrow_head(draw, points[-1], (points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]), color, head)


def draw_chip(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fill: tuple[int, int, int],
    text_color: tuple[int, int, int],
    size: int,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=12, fill=fill)
    f = font(size, "bold")
    centered(draw, text, (x1 + x2) / 2, y1 + (y2 - y1 - size * 1.25) / 2, f, text_color, x2 - x1 - 24)


# ---------------------------------------------------------------------------
# 画像0：ヘッダー


def draw_header_motif(draw: ImageDraw.ImageDraw) -> None:
    source = (754, 276, 916, 354)
    draw.rounded_rectangle(source, radius=14, fill=CARD, outline=NAVY, width=3)
    draw.rectangle([755, 277, 795, 353], fill=TINT)
    draw.line([(795, 277), (795, 353)], fill=BORDER, width=2)
    centered(draw, "1行", 775, 296, font(18, "bold"), NAVY, 38)
    draw.rounded_rectangle([814, 298, 890, 309], radius=5, fill=GRAY)
    draw.rounded_rectangle([814, 322, 872, 333], radius=5, fill=BORDER)

    upper = (996, 154, 1230, 274)
    lower = (996, 378, 1230, 498)
    for box, outline in ((upper, NAVY), (lower, ORANGE)):
        draw.rounded_rectangle(box, radius=16, fill=CARD, outline=outline, width=4)
        draw.line([(box[0] + 18, box[1] + 43), (box[2] - 18, box[1] + 43)], fill=BORDER, width=2)
    centered(draw, "8月30日", 1113, 200, font(34, "heavy"), NAVY, 205)
    centered(draw, "8月31日", 1113, 424, font(34, "heavy"), ORANGE, 205)

    branch_x, source_y = 956, 315
    draw.line([(916, source_y), (branch_x, source_y)], fill=NAVY, width=4)
    draw.ellipse([branch_x - 6, source_y - 6, branch_x + 6, source_y + 6], fill=ORANGE)
    draw_poly_arrow(draw, [(branch_x, source_y), (branch_x, 214), (988, 214)], NAVY, width=4)
    draw_poly_arrow(draw, [(branch_x, source_y), (branch_x, 438), (988, 438)], ORANGE, width=4)


def render_header() -> Image.Image:
    image, draw = new_canvas(1280, 670)
    left = 72
    title_font = font(30, "heavy")
    line1 = "同じ期限をAIに2通りの頼み方で聞いたら、"
    line2 = "締切が1日ずれました"
    assert_fits(draw, line1, title_font, 666)
    assert_fits(draw, line2, title_font, 666)
    draw.rounded_rectangle([left, 184, left + 8, 250], radius=4, fill=ORANGE)
    draw.text((left + 28, 176), line1, font=title_font, fill=NAVY)
    draw.text((left + 28, 232), line2, font=title_font, fill=NAVY)
    draw.line([(left, 350), (left + 650, 350)], fill=ORANGE, width=3)

    sub1 = "要約ではなく全件を出させる｜更新期限の見張らせ方"
    sub2 = "中小企業のバックオフィスと、ひとり社長のためのAI活用"
    sub1_font = font(23, "bold")
    sub2_font = font(19)
    assert_fits(draw, sub1, sub1_font, 666)
    assert_fits(draw, sub2, sub2_font, 666)
    draw.text((left, 382), sub1, font=sub1_font, fill=INK)
    draw.text((left, 430), sub2, font=sub2_font, fill=GRAY)
    draw_header_motif(draw)
    return image


# ---------------------------------------------------------------------------
# 画像1：期限一覧


DEADLINE_ROWS = (
    ("1", "クラウドストレージ", "2026-09-05", "月額・自動更新"),
    ("2", "工場の火災保険", "2026-09-15", "満期。自動継続の契約ではない"),
    ("3", "会計ソフト 年間ライセンス", "2026-09-30", "自動更新（停止する場合は当月中に連絡）"),
    ("4", "計量器の定期検査", "2026-10-20", "2年ごと"),
    ("5", "社用車の車検", "2026-11-05", ""),
    ("6", "複合機のリース契約", "2026-11-30", "更新しない場合は3か月前までに書面で通知"),
    ("7", "消防設備点検の報告", "2026-12-10", "年1回"),
    ("8", "事務所の賃貸借契約", "2027-02-28", "自動更新（申し出がなければ継続）"),
    ("9", "産業廃棄物収集運搬業の許可", "2027-06-30", "5年ごと。更新申請は2〜3か月前から"),
    ("10", "健康診断の実施", "", "去年は11月に実施した"),
)


def render_deadline_table() -> Image.Image:
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "期限一覧（全部ダミーです）")
    draw.rounded_rectangle([60, 132, 1220, 672], radius=18, fill=CARD, outline=BORDER, width=2)

    x_positions = (88, 152, 444, 626, 1144)
    table_top, header_h, row_h = 158, 36, 36
    table_bottom = table_top + header_h + row_h * len(DEADLINE_ROWS)
    draw.rectangle([x_positions[0], table_top, x_positions[-1], table_top + header_h], fill=TINT)
    headers = ("No", "項目", "期限日", "備考")
    header_font = font(16, "bold")
    body_font = font(15)
    body_bold = font(15, "bold")

    for index, label in enumerate(headers):
        cell_left, cell_right = x_positions[index], x_positions[index + 1]
        centered(draw, label, (cell_left + cell_right) / 2, table_top + 7, header_font, NAVY, cell_right - cell_left - 12)

    for row_index, row in enumerate(DEADLINE_ROWS):
        y1 = table_top + header_h + row_index * row_h
        y2 = y1 + row_h
        if row_index == 5:
            draw.rectangle([x_positions[0], y1, x_positions[-1], y2], fill=ORANGE_TINT)
        draw.line([(x_positions[0], y2), (x_positions[-1], y2)], fill=BORDER, width=1)

        no, item, deadline, note = row
        values = (no, item, deadline)
        for col_index, value in enumerate(values):
            left, right = x_positions[col_index], x_positions[col_index + 1]
            f = body_bold if row_index == 5 else body_font
            assert_fits(draw, value, f, right - left - 16)
            if col_index == 0:
                centered(draw, value, (left + right) / 2, y1 + 8, f, INK, right - left - 12)
            else:
                draw.text((left + 8, y1 + 8), value, font=f, fill=INK)

        note_left, note_right = x_positions[3], x_positions[4]
        if row_index == 5:
            prefix = "更新しない場合は"
            highlight = "3か月前までに書面で通知"
            assert_fits(draw, prefix + highlight, body_font, note_right - note_left - 16)
            draw.text((note_left + 8, y1 + 8), prefix, font=body_font, fill=INK)
            hx = note_left + 8 + width_of(draw, prefix, body_font)
            draw.text((hx, y1 + 8), highlight, font=body_bold, fill=ORANGE)
        else:
            assert_fits(draw, note, body_font, note_right - note_left - 16)
            draw.text((note_left + 8, y1 + 8), note, font=body_font, fill=INK)

    for x in x_positions:
        draw.line([(x, table_top), (x, table_bottom)], fill=BORDER, width=1)
    draw.rectangle([x_positions[0], table_top, x_positions[-1], table_bottom], outline=BORDER, width=2)

    # No.6から表の右外側へ出し、表の下を通して注記へつなぐ。
    row6_center_y = table_top + header_h + 5 * row_h + row_h / 2
    note_box = (718, 584, 1144, 630)
    draw.line(
        [(1144, row6_center_y), (1176, row6_center_y), (1176, 568), (931, 568), (931, 580)],
        fill=ORANGE,
        width=3,
        joint="curve",
    )
    draw.ellipse([1139, row6_center_y - 5, 1149, row6_center_y + 5], fill=ORANGE)
    draw.rounded_rectangle(note_box, radius=12, fill=CARD, outline=ORANGE, width=3)
    centered(draw, "期限は11月なのに、動く締切は8月末", 931, 594, font(20, "bold"), ORANGE, 398)

    foot = "※ 架空の会社・架空の契約です"
    foot_font = font(16)
    assert_fits(draw, foot, foot_font, 320)
    draw.text((1174 - width_of(draw, foot, foot_font), 642), foot, font=foot_font, fill=GRAY)
    return image


# ---------------------------------------------------------------------------
# 画像2：頼み方の違い


def draw_bubble(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    color: tuple[int, int, int],
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=16, fill=color)
    draw.polygon([(x1 + 46, y1), (x1 + 65, y1 - 17), (x1 + 84, y1)], fill=color)
    centered(draw, text, (x1 + x2) / 2, y1 + 15, font(22, "bold"), CARD, x2 - x1 - 28)


def render_request_difference() -> Image.Image:
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "同じファイル、頼み方だけ変えた")
    draw.rounded_rectangle([60, 136, 1220, 664], radius=18, fill=CARD, outline=BORDER, width=2)
    draw.line([(640, 166), (640, 630)], fill=BORDER, width=2)

    centered(draw, "「危ないものを教えて」", 350, 174, font(27, "heavy"), NAVY, 500)
    centered(draw, "「選ばないでください」", 930, 174, font(27, "heavy"), ORANGE, 500)

    left_rows = (
        (ORANGE, "複合機のリース"),
        (NAVY, "工場の火災保険"),
        (GRAY, "会計ソフト"),
    )
    for index, (color, label) in enumerate(left_rows):
        y = 254 + index * 70
        draw.rounded_rectangle([112, y - 10, 588, y + 44], radius=11, fill=BG, outline=BORDER, width=1)
        draw.ellipse([139, y + 6, 157, y + 24], fill=color)
        assert_fits(draw, label, font(23, "bold"), 380)
        draw.text((178, y), label, font=font(23, "bold"), fill=INK)
    centered(draw, "＋ 残り7件にも短いコメント", 350, 466, font(19), GRAY, 470)
    draw_bubble(draw, (154, 548, 546, 604), "優先順位はAIが決めた", NAVY)

    # 右側は順序を保った10行。日付が返った3・6行目以外に「記載なし」を付ける。
    missing_rows = {1, 2, 4, 5, 7, 8, 9, 10}
    number_font = font(16, "bold")
    label_font = font(13, "bold")
    for index in range(1, 11):
        y = 242 + (index - 1) * 27
        centered(draw, str(index), 701, y - 3, number_font, GRAY, 32)
        draw.rounded_rectangle([730, y + 3, 1000, y + 11], radius=4, fill=TINT)
        if index in missing_rows:
            box = (1024, y - 5, 1136, y + 19)
            draw.rounded_rectangle(box, radius=8, fill=ORANGE_TINT)
            centered(draw, "記載なし", 1080, y - 3, label_font, ORANGE, 96)
    centered(draw, "日付が入ったのは10行のうち2行だけ", 930, 508, font(14), GRAY, 400)
    draw_bubble(draw, (730, 548, 1130, 604), "判断はこちらに返ってきた", ORANGE)
    return image


# ---------------------------------------------------------------------------
# 画像3：締切が1日ずれた


def render_one_day_difference() -> Image.Image:
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "同じ行の「実際に動く締切」")

    source = (310, 134, 970, 212)
    draw.rounded_rectangle(source, radius=15, fill=CARD, outline=BORDER, width=2)
    source_text = "複合機のリース契約　期限日 2026-11-30"
    centered(draw, source_text, 640, 153, font(26, "bold"), INK, 620)

    left_card = (70, 276, 610, 628)
    right_card = (670, 276, 1210, 628)
    # 線はカード外の空白だけを通し、カードの背面で止める。
    draw.line([(640, 212), (640, 244)], fill=BORDER, width=4)
    draw.ellipse([634, 238, 646, 250], fill=ORANGE)
    draw_poly_arrow(draw, [(640, 244), (340, 244), (340, 268)], NAVY, width=4)
    draw_poly_arrow(draw, [(640, 244), (940, 244), (940, 268)], ORANGE, width=4)

    draw.rounded_rectangle(left_card, radius=18, fill=CARD, outline=BORDER, width=2)
    draw.rounded_rectangle(right_card, radius=18, fill=CARD, outline=BORDER, width=2)

    centered(draw, "1回目：危ないものを教えて", 340, 306, font(20, "bold"), GRAY, 480)
    centered(draw, "2回目：全件を出して", 940, 306, font(20, "bold"), GRAY, 480)
    centered(draw, "8月30日", 340, 366, font(58, "heavy"), NAVY, 450)
    centered(draw, "8月31日", 940, 366, font(58, "heavy"), ORANGE, 450)

    centered(draw, "「11/30の3か月前は8/30（日曜）」", 340, 474, font(20), INK, 480)
    right_line1 = "「逆算した日付なので、起算方法までは"
    right_line2 = "備考に記載がありません」"
    centered(draw, right_line1, 940, 462, font(19), INK, 480)
    centered(draw, right_line2, 940, 494, font(19), INK, 480)

    draw_chip(draw, (226, 552, 454, 596), "言い切り", NAVY, CARD, 20)
    draw_chip(draw, (826, 552, 1054, 596), "留保つき", ORANGE, CARD, 20)

    footer = "同じCSV・同じモデル。違うのは頼み方だけ"
    centered(draw, footer, 640, 666, font(19), GRAY, 1120)
    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "deadline_2_頼み方の違い.png"
    image = render_request_difference()
    image.save(path, format="PNG")
    print(f"saved: {path}  {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
