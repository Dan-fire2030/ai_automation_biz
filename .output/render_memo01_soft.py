"""note記事ヘッダー「メモが161行になって、AIも自分も読まなくなった」の丸ゴ案。

実行:
    python3 .output/render_memo01_soft.py

日本語はmacOS標準のヒラギノ丸ゴシックで決定的に描画する。
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "note" / "images" / "2026-09-21"

REGULAR = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
BOLD = REGULAR
HEAVY = REGULAR

BG = (250, 249, 246)
WHITE = (255, 255, 255)
NAVY = (31, 58, 95)
INK = (43, 58, 76)
GRAY = (138, 148, 166)
PALE = (213, 220, 229)
TINT = (238, 242, 246)
BLUE_GRAY = (176, 194, 211)
ORANGE = (232, 112, 58)
ORANGE_TINT = (253, 238, 229)


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    path = {"regular": REGULAR, "bold": BOLD, "heavy": HEAVY}[weight]
    if not Path(path).exists():
        raise FileNotFoundError(f"必要な日本語フォントがありません: {path}")
    return ImageFont.truetype(path, size)


def canvas(height: int):
    image = Image.new("RGB", (1280, height), BG)
    return image, ImageDraw.Draw(image)


def text_size(
    draw: ImageDraw.ImageDraw,
    value: str,
    f: ImageFont.FreeTypeFont,
    stroke_width: int = 0,
):
    box = draw.textbbox((0, 0), value, font=f, stroke_width=stroke_width)
    return box[2] - box[0], box[3] - box[1], box


def put_text(
    draw,
    xy,
    value,
    size,
    weight="regular",
    color=INK,
    max_width=None,
    anchor=None,
    stroke_width=0,
):
    if max_width is None:
        raise ValueError(f"max_widthが未指定です: {value!r}")
    f = font(size, weight)
    width, _, _ = text_size(draw, value, f, stroke_width=stroke_width)
    if width > max_width:
        raise ValueError(f"文字幅超過: {value!r} {width}px > {max_width}px")
    draw.text(
        xy,
        value,
        font=f,
        fill=color,
        anchor=anchor,
        stroke_width=stroke_width,
        stroke_fill=color,
    )
    return width


def title(draw, value: str, size: int = 42):
    draw.rounded_rectangle((60, 60, 70, 110), radius=5, fill=ORANGE)
    put_text(draw, (88, 55), value, size, "heavy", NAVY, 1120)


def dashed_line(draw, start, end, fill, width=2, dash=9, gap=8):
    x1, y1 = start
    x2, y2 = end
    if x1 == x2:
        y = y1
        while y < y2:
            draw.line((x1, y, x2, min(y + dash, y2)), fill=fill, width=width)
            y += dash + gap
    elif y1 == y2:
        x = x1
        while x < x2:
            draw.line((x, y1, min(x + dash, x2), y2), fill=fill, width=width)
            x += dash + gap
    else:
        raise ValueError("破線は水平・垂直のみ")


def draw_paper(draw, box, line_count, folded=False, dense=False):
    """白い紙と横罫を描く。folded=Trueなら右下を折る。"""
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=12, fill=WHITE, outline=PALE, width=3)
    if line_count:
        top = y1 + 24
        bottom = y2 - 24
        step = (bottom - top) / max(line_count - 1, 1)
        line_color = INK if dense else BLUE_GRAY
        line_width = 3 if dense else 2
        for index in range(line_count):
            y = round(top + index * step)
            short = 18 if index % 4 == 3 else 0
            draw.line((x1 + 18, y, x2 - 18 - short, y), fill=line_color, width=line_width)
    if folded:
        fold = 30
        draw.polygon(((x2 - fold, y2), (x2, y2 - fold), (x2, y2)), fill=BG)
        draw.line((x2 - fold, y2, x2 - fold, y2 - fold), fill=PALE, width=2)
        draw.line((x2 - fold, y2 - fold, x2, y2 - fold), fill=PALE, width=2)
        draw.line((x2 - fold, y2 - fold, x2, y2), fill=PALE, width=2)


def render_header():
    image, draw = canvas(670)
    draw.rounded_rectangle((72, 184, 82, 250), radius=5, fill=ORANGE)
    put_text(draw, (100, 169), "メモが161行になって、", 44, "heavy", NAVY, 610, stroke_width=0)
    put_text(draw, (100, 229), "AIも自分も読まなくなった", 44, "heavy", NAVY, 610, stroke_width=0)
    put_text(draw, (72, 304), "長かったからではなく、混ざっていたからでした", 24, "bold", NAVY, 640, stroke_width=0)
    draw.rounded_rectangle((72, 348, 692, 352), radius=2, fill=ORANGE)
    put_text(draw, (72, 395), "AIと仕事をしている人のための実録", 19, "regular", GRAY, 640)

    # びっしり書かれた1枚の紙。
    draw_paper(draw, (744, 166, 874, 430), 25, dense=True)
    badge = (760, 447, 858, 483)
    draw.rounded_rectangle(badge, radius=(badge[3] - badge[1]) // 2, fill=NAVY)
    put_text(draw, (809, 465), "161行", 18, "bold", WHITE, 82, anchor="mm")

    # 右向きの矢印。
    draw.line((895, 299, 927, 299), fill=ORANGE, width=8)
    draw.ellipse((891, 295, 899, 303), fill=ORANGE)
    draw.polygon(((927, 282), (955, 299), (927, 316)), fill=ORANGE)

    # 3枚を離し、各紙の行数（4本／8本／14本）が読めるようにする。
    draw_paper(draw, (966, 216, 1038, 388), 4)
    draw_paper(draw, (1050, 188, 1128, 388), 8)
    draw_paper(draw, (1140, 158, 1228, 388), 14, folded=True)
    badge = (1042, 447, 1172, 483)
    draw.rounded_rectangle(badge, radius=(badge[3] - badge[1]) // 2, fill=NAVY)
    put_text(draw, (1107, 465), "3枚に分けた", 17, "bold", WHITE, 114, anchor="mm")
    return image


def render_line_growth():
    image, draw = canvas(720)
    title(draw, "学んだことのメモは、作り直しても増え続けた")

    chart_left, chart_right = 150, 1110
    chart_top, chart_bottom = 155, 445

    def ypos(value):
        return chart_bottom - value / 200 * (chart_bottom - chart_top)

    # 200行の上限線と縦軸。
    dashed_line(draw, (chart_left, chart_top), (chart_right, chart_top), PALE, width=3, dash=12, gap=10)
    put_text(draw, (chart_right, chart_top - 18), "自分で決めた上限 200行", 18, "bold", GRAY, 250, anchor="rs")
    draw.line((chart_left, chart_top, chart_left, chart_bottom), fill=PALE, width=2)
    draw.line((chart_left, chart_bottom, chart_right, chart_bottom), fill=PALE, width=2)
    for tick in (0, 50, 100, 150, 200):
        y = ypos(tick)
        put_text(draw, (chart_left - 18, y), str(tick), 17, "bold", GRAY, 50, anchor="rm")

    labels = ("最初", "1週間後", "2週間後", "1か月後", "2か月後", "今")
    values = (5, 21, 39, 57, 70, 81)
    xs = [chart_left + i * (chart_right - chart_left) / 5 for i in range(6)]
    points = [(x, ypos(value)) for x, value in zip(xs, values)]
    draw.line(points, fill=ORANGE, width=8, joint="curve")
    for x, y, label, value in zip(xs, [p[1] for p in points], labels, values):
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill=ORANGE)
        put_text(draw, (x, y - 24), f"{value}行", 21, "heavy", NAVY, 82, anchor="ms")
        put_text(draw, (x, chart_bottom + 28), label, 18, "bold", NAVY, 115, anchor="ma")

    # 16回の作り直しを、下向きの三角で表す。
    put_text(draw, (74, 528), "作り直した回数：16回", 20, "bold", NAVY, 230)
    tri_start, tri_end = 330, 1125
    for index in range(16):
        x = tri_start + index * (tri_end - tri_start) / 15
        draw.polygon(((x - 8, 528), (x + 8, 528), (x, 542)), fill=BLUE_GRAY)

    put_text(draw, (640, 655), "同じ紙を16回作り直しても、行数は下がらなかった", 22, "bold", GRAY, 720, anchor="mm")
    return image


def render_rewrite_speed():
    image, draw = canvas(720)
    title(draw, "同じ2か月半で、書き換わった回数")

    bar_left, bar_right = 330, 1050
    max_value = 44
    rows = (
        ("決めごと", 5, "5回", "半年後もそのまま使う", NAVY),
        ("経験", 16, "16回", "少しずつ書き足す", BLUE_GRAY),
        ("引き継ぎ", 44, "44枚", "数日で捨てる", ORANGE),
    )
    for y, (label, value, value_label, note, color) in zip((190, 340, 490), rows):
        put_text(draw, (80, y + 31), label, 26, "heavy", NAVY, 200, anchor="lm")
        draw.rounded_rectangle((bar_left, y, bar_right, y + 62), radius=31, fill=TINT)
        width = (bar_right - bar_left) * value / max_value
        draw.rounded_rectangle((bar_left, y, bar_left + width, y + 62), radius=31, fill=color)
        put_text(draw, (bar_left + width + 18, y + 31), value_label, 25, "heavy", NAVY, 90, anchor="lm")
        put_text(draw, (bar_left, y + 81), note, 19, "regular", GRAY, 340, anchor="la")

    badge = (944, 605, 1190, 652)
    draw.rounded_rectangle(badge, radius=(badge[3] - badge[1]) // 2, fill=ORANGE_TINT)
    put_text(draw, (1067, 629), "速さが10倍ちがう", 21, "bold", ORANGE, 200, anchor="mm")
    put_text(draw, (70, 668), "2026年7月3日〜9月18日の実測（77日間）", 19, "regular", GRAY, 560, anchor="lm")
    return image


def render_three_roles():
    image, draw = canvas(720)
    title(draw, "3枚に分けた、それぞれの役割")

    cards = (
        {
            "box": (55, 145, 410, 625),
            "band": NAVY,
            "heading_color": WHITE,
            "heading": "1枚目｜決めごと",
            "items": (
                ("中身", "ずっと守ってほしいこと"),
                ("書くのは", "自分"),
                ("読むのは", "AIと自分"),
                ("捨てる？", "捨てない"),
                ("実測", "65行／2か月半で5回だけ更新"),
            ),
        },
        {
            "box": (463, 145, 818, 625),
            "band": BLUE_GRAY,
            "heading_color": NAVY,
            "heading": "2枚目｜経験",
            "items": (
                ("中身", "やって分かったこと"),
                ("書くのは", "AI"),
                ("読むのは", "AI"),
                ("捨てる？", "古くなったら消す"),
                ("実測", "81行／16回作り直し"),
            ),
        },
        {
            "box": (871, 145, 1226, 625),
            "band": ORANGE,
            "heading_color": WHITE,
            "heading": "3枚目｜引き継ぎ",
            "items": (
                ("中身", "今どこまで進んだか"),
                ("書くのは", "AI"),
                ("読むのは", "次のAIと自分"),
                ("捨てる？", "毎回まるごと捨てる"),
                ("実測", "44枚／いちばん長くて161行"),
            ),
        },
    )

    for card in cards:
        x1, y1, x2, y2 = card["box"]
        draw.rounded_rectangle((x1, y1, x2, y2), radius=40, fill=WHITE, outline=PALE, width=2)
        draw.rounded_rectangle((x1, y1, x2, y1 + 68), radius=34, fill=card["band"])
        draw.rectangle((x1, y1 + 34, x2, y1 + 68), fill=card["band"])
        put_text(draw, ((x1 + x2) / 2, y1 + 35), card["heading"], 24, "heavy", card["heading_color"], x2 - x1 - 36, anchor="mm")

        for index, (label, value) in enumerate(card["items"]):
            y = y1 + 91 + index * 75
            put_text(draw, (x1 + 24, y), label, 16, "bold", GRAY, x2 - x1 - 48)
            value_size = 19 if index == 4 else 22
            put_text(draw, (x1 + 24, y + 27), value, value_size, "bold", NAVY, x2 - x1 - 48)

    put_text(draw, (640, 676), "毎回ぜんぶ読むのは、3枚目だけでよくなった", 22, "bold", GRAY, 700, anchor="mm")
    return image


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = (
        ("memo_2_書き換えの速さ.png", render_rewrite_speed, (1280, 720)),
    )
    for name, renderer, expected in outputs:
        image = renderer()
        if image.size != expected:
            raise AssertionError((name, image.size, expected))
        path = OUTPUT_DIR / name
        image.save(path, format="PNG")
        print(f"{path}: {image.width}×{image.height} PNG")


if __name__ == "__main__":
    main()
