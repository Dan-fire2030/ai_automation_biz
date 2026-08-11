from pathlib import Path
import math

from PIL import Image, ImageCms, ImageDraw, ImageFont


ROOT = Path("/Users/haruto/Documents/起業/ai-automation-biz")
OUT_DIR = ROOT / "note/images/2026-08-11"

NAVY = "#12305C"
GROUND = "#F4F8FC"
WHITE = "#FFFFFF"
GRAY = "#5A6675"
ORANGE = "#D9772F"

FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"
FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

if not Path(FONT_HEAVY).exists():
    FONT_HEAVY = FONT_BOLD


def font(size: int, weight: str = "bold") -> ImageFont.FreeTypeFont:
    path = {
        "heavy": FONT_HEAVY,
        "bold": FONT_BOLD,
        "regular": FONT_REGULAR,
    }[weight]
    return ImageFont.truetype(path, size)


def text_size(draw, text, text_font):
    box = draw.textbbox((0, 0), text, font=text_font)
    return box[2] - box[0], box[3] - box[1]


def centered(draw, text, center_x, y, text_font, fill):
    width, _ = text_size(draw, text, text_font)
    draw.text((center_x - width / 2, y), text, font=text_font, fill=fill)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(
        box, radius=radius, fill=fill, outline=outline, width=width
    )


def mix(color_a, color_b, amount):
    a = tuple(int(color_a[i : i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(color_b[i : i + 2], 16) for i in (1, 3, 5))
    rgb = tuple(round(x * (1 - amount) + y * amount) for x, y in zip(a, b))
    return "#" + "".join(f"{v:02X}" for v in rgb)


PALE_NAVY = mix(NAVY, WHITE, 0.83)
PALE_ORANGE = mix(ORANGE, WHITE, 0.78)
SOFT_ORANGE = mix(ORANGE, WHITE, 0.9)


def checkmark(draw, center, color=NAVY, width=9, scale=1.0):
    x, y = center
    points = [
        (x - 20 * scale, y),
        (x - 6 * scale, y + 15 * scale),
        (x + 25 * scale, y - 22 * scale),
    ]
    draw.line(points, fill=color, width=max(1, int(width * scale)), joint="curve")


def arrow_line(draw, start, end, color=NAVY, width=8):
    draw.line([start, end], fill=color, width=width)


def arrowhead(draw, end, angle, color=NAVY, width=8, head=22):
    for delta in (2.55, -2.55):
        point = (
            end[0] + head * math.cos(angle + delta),
            end[1] + head * math.sin(angle + delta),
        )
        draw.line([end, point], fill=color, width=width)


def dotted_line(draw, start, end, color, width=7, dash=17, gap=13):
    x1, y1 = start
    x2, y2 = end
    distance = math.hypot(x2 - x1, y2 - y1)
    if distance == 0:
        return
    dx = (x2 - x1) / distance
    dy = (y2 - y1) / distance
    cursor = 0
    while cursor < distance:
        stop = min(cursor + dash, distance)
        draw.line(
            [
                (x1 + dx * cursor, y1 + dy * cursor),
                (x1 + dx * stop, y1 + dy * stop),
            ],
            fill=color,
            width=width,
        )
        cursor += dash + gap


def save_png(image, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    image.save(path, "PNG", icc_profile=srgb, dpi=(144, 144), optimize=True)


def header_corners(draw):
    # 前号ヘッダーの四隅にある、柔らかい雲形の装飾を踏襲。
    for x, y, radius, color in [
        (-14, -10, 52, PALE_NAVY),
        (40, -8, 48, PALE_NAVY),
        (1242, -10, 53, PALE_ORANGE),
        (1280, 20, 47, PALE_ORANGE),
        (-4, 676, 58, PALE_ORANGE),
        (52, 660, 48, PALE_ORANGE),
        (1235, 680, 54, PALE_NAVY),
        (1280, 635, 53, PALE_NAVY),
    ]:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_note_paper(draw, box, outline=NAVY):
    x1, y1, x2, y2 = box
    rounded(draw, box, 24, WHITE, outline, 4)
    # 左上の小さなテープ
    rounded(draw, (x1 + 115, y1 - 12, x1 + 245, y1 + 14), 9, PALE_ORANGE)
    row1_y = y1 + 92
    row2_y = y1 + 190
    draw.line((x1 + 48, row1_y + 35, x2 - 48, row1_y + 35), fill=PALE_NAVY, width=3)
    draw.line((x1 + 48, row2_y + 35, x2 - 48, row2_y + 35), fill=PALE_NAVY, width=3)
    draw.ellipse((x1 + 38, row1_y - 10, x1 + 86, row1_y + 38), fill=PALE_NAVY)
    checkmark(draw, (x1 + 62, row1_y + 13), NAVY, width=7, scale=0.7)
    # 1行目だけ記入済みを示す短い筆記線。
    draw.line((x1 + 110, row1_y + 2, x2 - 58, row1_y + 2), fill=NAVY, width=7)
    draw.line((x1 + 110, row1_y + 22, x2 - 125, row1_y + 22), fill=NAVY, width=5)
    draw.ellipse((x1 + 45, row2_y + 1, x1 + 64, row2_y + 20), outline=GRAY, width=3)


def make_header():
    image = Image.new("RGB", (1280, 670), GROUND)
    draw = ImageDraw.Draw(image)
    header_corners(draw)

    # 左の文字領域は x=80〜735、右のイラスト領域は x=815〜1215。
    draw.text((80, 178), "士業のAI実録 vol.21", font=font(34, "bold"), fill=NAVY)
    draw.text((80, 258), "あの2行メモ、", font=font(62, "heavy"), fill=NAVY)
    draw.text((80, 350), "全部の用事には", font=font(62, "heavy"), fill=NAVY)
    draw.text((80, 442), "要りませんでした", font=font(62, "heavy"), fill=NAVY)

    draw_note_paper(draw, (830, 172, 1160, 470))
    centered(draw, "?", 1193, 346, font(64, "heavy"), ORANGE)

    save_png(image, OUT_DIR / "knowhow14_0_ヘッダー.png")


def draw_pen(draw, tip, color=NAVY):
    tx, ty = tip
    # ペン先が空欄の直前で止まっているように、右上から斜めに置く。
    body = [(tx + 18, ty - 17), (tx + 120, ty - 119), (tx + 143, ty - 96), (tx + 41, ty + 6)]
    draw.polygon(body, fill=PALE_NAVY, outline=color)
    draw.line((tx + 36, ty - 1, tx + 137, ty - 102), fill=color, width=4)
    draw.polygon([(tx, ty), (tx + 18, ty - 17), (tx + 41, ty + 6)], fill=WHITE, outline=color)
    draw.ellipse((tx + 117, ty - 119, tx + 145, ty - 91), fill=ORANGE, outline=color, width=2)


def make_two_line_memo():
    image = Image.new("RGB", (1200, 800), GROUND)
    draw = ImageDraw.Draw(image)

    rounded(draw, (70, 55, 1130, 735), 30, WHITE, PALE_NAVY, 3)
    centered(draw, "2行メモを書いてみました", 600, 78, font(46, "heavy"), NAVY)

    # 上段：書けた行。
    rounded(draw, (120, 170, 1080, 350), 22, mix(NAVY, WHITE, 0.95), PALE_NAVY, 3)
    draw.text((160, 195), "【今日AIに頼むこと】", font=font(31, "bold"), fill=NAVY)
    draw.text((168, 269), "更新手続きの必要書類を調べて", font=font(38, "heavy"), fill=NAVY)
    draw.ellipse((990, 244, 1045, 299), fill=PALE_NAVY)
    checkmark(draw, (1017, 272), NAVY, width=8, scale=0.8)

    # 下段：書けなかった行だけ淡いオレンジで強調。
    rounded(draw, (120, 375, 1080, 590), 22, SOFT_ORANGE, ORANGE, 4)
    draw.text((160, 400), "【浮いた時間でやること】", font=font(31, "bold"), fill=ORANGE)
    draw.line((165, 522, 810, 522), fill=PALE_ORANGE, width=4)
    draw_pen(draw, (815, 521), NAVY)
    centered(draw, "?", 1010, 454, font(78, "heavy"), ORANGE)

    centered(
        draw,
        "上の行は数秒。下の行で止まりました。",
        600,
        650,
        font(34, "bold"),
        GRAY,
    )

    save_png(image, OUT_DIR / "knowhow14_1_2行メモ.png")


def column_card(draw, box, color, heading, examples, conclusion, goal):
    x1, y1, x2, y2 = box
    rounded(draw, box, 26, WHITE, color, 4)
    rounded(draw, (x1, y1, x2, y1 + 92), 24, color)
    centered(draw, heading, (x1 + x2) / 2, y1 + 23, font(33, "heavy"), WHITE)

    for index, example in enumerate(examples):
        cy = y1 + 142 + index * 80
        draw.ellipse((x1 + 50, cy + 5, x1 + 70, cy + 25), fill=color)
        draw.text((x1 + 92, cy - 4), example, font=font(31, "bold"), fill=NAVY)

    line_y = y1 + 353
    start_x = x1 + 65
    if goal:
        end_x = x2 - 105
        draw.line((start_x, line_y, end_x, line_y), fill=color, width=8)
        draw.ellipse((end_x - 23, line_y - 23, end_x + 23, line_y + 23), fill=mix(color, WHITE, 0.82))
        checkmark(draw, (end_x, line_y), color, width=8, scale=0.78)
        centered(draw, "終わり", end_x, line_y + 38, font(24, "bold"), color)
    else:
        # 終点を置かず、カード外から画面端へ抜ける点線にする。
        dotted_line(draw, (start_x, line_y), (1198, line_y), color, width=8, dash=20, gap=15)
        draw.text((start_x, line_y + 38), "どこまで？", font=font(24, "bold"), fill=color)

    rounded(draw, (x1 + 48, y2 - 112, x2 - 48, y2 - 35), 19, color)
    centered(draw, conclusion, (x1 + x2) / 2, y2 - 94, font(37, "heavy"), WHITE)


def make_sorting():
    image = Image.new("RGB", (1200, 800), GROUND)
    draw = ImageDraw.Draw(image)

    centered(draw, "用事を、終わりの合図で仕分ける", 600, 34, font(48, "heavy"), NAVY)
    column_card(
        draw,
        (55, 120, 580, 745),
        NAVY,
        "終わりの合図がある用事",
        ["下書きを作ってもらう", "メモを整理してもらう"],
        "メモは要らない",
        True,
    )
    column_card(
        draw,
        (620, 120, 1145, 745),
        ORANGE,
        "終わりの合図がない用事",
        ["調べもの", "比べもの"],
        "2行メモを書く",
        False,
    )

    save_png(image, OUT_DIR / "knowhow14_2_仕分け.png")


def make_branch():
    image = Image.new("RGB", (1200, 800), GROUND)
    draw = ImageDraw.Draw(image)

    rounded(draw, (190, 45, 1010, 155), 28, NAVY)
    centered(draw, "これ、終わったって分かる？", 600, 71, font(50, "heavy"), WHITE)

    left_box = (70, 405, 545, 735)
    right_box = (655, 405, 1130, 735)

    # 先にカードを描き、コネクターはカードの手前 y=373 で止める。
    rounded(draw, left_box, 28, WHITE, NAVY, 4)
    rounded(draw, right_box, 28, WHITE, ORANGE, 4)

    # 分岐線。矢尻はすべてのカード・ラベルの後に最後に描画する。
    arrow_line(draw, (600, 155), (600, 245), NAVY, 8)
    arrow_line(draw, (305, 245), (895, 245), NAVY, 8)
    arrow_line(draw, (305, 245), (305, 373), NAVY, 8)
    arrow_line(draw, (895, 245), (895, 373), ORANGE, 8)

    rounded(draw, (245, 205, 365, 273), 24, NAVY)
    centered(draw, "YES", 305, 218, font(31, "heavy"), WHITE)
    rounded(draw, (835, 205, 955, 273), 24, ORANGE)
    centered(draw, "NO", 895, 218, font(31, "heavy"), WHITE)

    centered(draw, "そのまま頼む", 307, 457, font(46, "heavy"), NAVY)
    centered(draw, "メモは要りません", 307, 535, font(29, "regular"), GRAY)
    draw.ellipse((265, 610, 349, 694), fill=PALE_NAVY)
    checkmark(draw, (307, 652), NAVY, width=11, scale=1.2)

    centered(draw, "2行書いてから頼む", 892, 443, font(39, "heavy"), ORANGE)
    rounded(draw, (715, 520, 1070, 690), 18, SOFT_ORANGE, ORANGE, 3)
    draw.text((744, 542), "【頼むこと】", font=font(25, "bold"), fill=NAVY)
    draw.line((750, 587, 1034, 587), fill=PALE_ORANGE, width=3)
    draw.text((744, 607), "【浮いた時間でやること】", font=font(23, "bold"), fill=ORANGE)
    draw.line((750, 657, 1034, 657), fill=PALE_ORANGE, width=3)

    # カード上端（y=405）より32px手前で、矢尻を最後に描く。
    arrowhead(draw, (305, 373), math.pi / 2, NAVY, width=8, head=22)
    arrowhead(draw, (895, 373), math.pi / 2, ORANGE, width=8, head=22)

    save_png(image, OUT_DIR / "knowhow14_3_分かれ道.png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_header()
    make_two_line_memo()
    make_sorting()
    make_branch()


if __name__ == "__main__":
    main()
