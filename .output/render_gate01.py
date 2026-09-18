"""note記事「一番危なかったのは、心配していない方だった」の図解4枚。

実行:
    python3 .output/render_gate01.py

日本語はmacOS標準のヒラギノ角ゴシックで決定的に描画する。
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "note" / "images" / "2026-09-17"

REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"

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


def text_size(draw: ImageDraw.ImageDraw, value: str, f: ImageFont.FreeTypeFont):
    box = draw.textbbox((0, 0), value, font=f)
    return box[2] - box[0], box[3] - box[1], box


def put_text(draw, xy, value, size, weight="regular", color=INK, max_width=None, anchor=None):
    f = font(size, weight)
    width, _, _ = text_size(draw, value, f)
    if max_width is not None and width > max_width:
        raise ValueError(f"文字幅超過: {value!r} {width}px > {max_width}px")
    draw.text(xy, value, font=f, fill=color, anchor=anchor)
    return width


def title(draw, value: str, size: int = 38):
    draw.rounded_rectangle((60, 60, 68, 110), radius=4, fill=ORANGE)
    put_text(draw, (88, 55), value, size, "heavy", NAVY, 1120)


def centered_segments(draw, center_x, y, segments, size, weight="bold"):
    """segments: [(text, color, optional-size, optional-weight), ...]"""
    measured = []
    total = 0
    for segment in segments:
        value, color = segment[0], segment[1]
        seg_size = segment[2] if len(segment) > 2 else size
        seg_weight = segment[3] if len(segment) > 3 else weight
        f = font(seg_size, seg_weight)
        w, _, _ = text_size(draw, value, f)
        measured.append((value, color, f, w))
        total += w
    x = center_x - total / 2
    for value, color, f, w in measured:
        draw.text((x, y), value, font=f, fill=color)
        x += w


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


def draw_lock(draw, cx, top, color=NAVY, open_shackle=False):
    if open_shackle:
        draw.arc((cx - 31, top, cx + 19, top + 58), 155, 350, fill=color, width=7)
    else:
        draw.arc((cx - 28, top, cx + 28, top + 58), 180, 360, fill=color, width=7)
        draw.line((cx - 28, top + 29, cx - 28, top + 52), fill=color, width=7)
        draw.line((cx + 28, top + 29, cx + 28, top + 52), fill=color, width=7)
    draw.rounded_rectangle((cx - 43, top + 48, cx + 43, top + 116), radius=10, fill=color)
    draw.ellipse((cx - 6, top + 70, cx + 6, top + 82), fill=WHITE)
    draw.rounded_rectangle((cx - 4, top + 78, cx + 4, top + 97), radius=3, fill=WHITE)


def render_header():
    image, draw = canvas(670)
    draw.rounded_rectangle((72, 184, 80, 250), radius=4, fill=ORANGE)
    put_text(draw, (100, 169), "一番危なかったのは、", 38, "heavy", NAVY, 620)
    put_text(draw, (100, 229), "心配していない方だった", 38, "heavy", NAVY, 620)
    put_text(draw, (72, 304), "心配していた方は通った。疑っていない方で転んだ", 23, "bold", INK, 640)
    draw.line((72, 350, 692, 350), fill=ORANGE, width=3)
    put_text(draw, (72, 395), "AIでiOSアプリを作っている、個人開発者のための実録", 19, "regular", GRAY, 640)

    # 左の扉：閉じており、大きな南京錠が掛かっている。
    draw.rounded_rectangle((760, 165, 946, 430), radius=9, fill=WHITE, outline=PALE, width=3)
    draw.rectangle((783, 189, 923, 429), fill=TINT, outline=NAVY, width=4)
    draw.ellipse((894, 302, 907, 315), fill=NAVY)
    draw_lock(draw, 853, 230, NAVY, False)
    put_text(draw, (853, 459), "心配していた方", 20, "bold", NAVY, anchor="mm")

    # 右の扉：枠の内側からオレンジの警告が漏れ、扉が少し手前へ開く。
    draw.rounded_rectangle((1010, 165, 1205, 430), radius=9, fill=WHITE, outline=PALE, width=3)
    draw.polygon(((1030, 189), (1182, 189), (1182, 430), (1030, 430)), fill=ORANGE_TINT)
    draw.polygon(((1030, 189), (1150, 212), (1150, 410), (1030, 430)), fill=TINT, outline=NAVY)
    draw.line((1030, 189, 1150, 212, 1150, 410, 1030, 430, 1030, 189), fill=NAVY, width=4)
    draw.ellipse((1124, 307, 1137, 320), fill=NAVY)
    draw_lock(draw, 1102, 220, ORANGE, True)
    put_text(draw, (1181, 284), "!", 52, "heavy", ORANGE, anchor="mm")
    put_text(draw, (1107, 459), "危なかった方", 20, "bold", ORANGE, anchor="mm")
    return image


def render_expiry():
    image, draw = canvas(720)
    title(draw, "時間が来た部屋は、確実に消えたか")

    # 左側の運転ラベルと帯が接触しないよう、数直線の始点を十分右に置く。
    axis_x1, axis_x2 = 250, 1120
    scale = (axis_x2 - axis_x1) / 300

    def xpos(seconds):
        return axis_x1 + seconds * scale

    dashed_line(draw, (axis_x2, 150), (axis_x2, 526), NAVY, width=2, dash=10, gap=8)
    put_text(draw, (axis_x2 - 14, 145), "目標：5分以内", 22, "bold", NAVY, anchor="rs")

    put_text(draw, (70, 215), "通常の運転", 23, "bold", NAVY, 180)
    draw.rounded_rectangle((axis_x1, 205, xpos(58.5), 275), radius=14, fill=ORANGE)
    put_text(draw, ((axis_x1 + xpos(58.5)) / 2, 240), "中央 27.5秒", 18, "bold", WHITE, anchor="mm")
    put_text(draw, (xpos(58.5) + 18, 240), "最大 58.5秒", 20, "bold", ORANGE, anchor="lm")

    put_text(draw, (70, 337), "掃除を止めて30件溜めてから再開", 21, "bold", NAVY, 430)
    draw.rounded_rectangle((xpos(86), 360, xpos(146.2), 430), radius=14, fill=BLUE_GRAY)
    put_text(draw, ((xpos(86) + xpos(146.2)) / 2, 395), "中央 115.1秒", 18, "bold", NAVY, anchor="mm")
    put_text(draw, (xpos(146.2) + 18, 395), "最大 146.2秒", 20, "bold", NAVY, anchor="lm")

    draw.line((axis_x1, 526, axis_x2, 526), fill=NAVY, width=3)
    for tick in range(0, 301, 60):
        x = xpos(tick)
        draw.line((x, 516, x, 539), fill=NAVY, width=3)
        put_text(draw, (x, 555), str(tick), 18, "bold", GRAY, anchor="mm")
    put_text(draw, (1182, 555), "秒", 18, "bold", GRAY, anchor="mm")

    centered_segments(draw, 640, 620, [
        ("30部屋・消え残り ", NAVY, 31, "heavy"),
        ("0件", ORANGE, 42, "heavy"),
    ], 31, "heavy")
    put_text(draw, (640, 682), "どちらも目標の5分より内側に収まった", 20, "bold", GRAY, anchor="mm")
    return image


def person(draw, x, y, filled=True):
    color = NAVY if filled else PALE
    if filled:
        draw.ellipse((x + 6, y, x + 16, y + 10), fill=color)
        draw.rounded_rectangle((x + 4, y + 12, x + 18, y + 27), radius=5, fill=color)
        draw.polygon(((x + 4, y + 25), (x + 9, y + 25), (x + 6, y + 34), (x + 2, y + 34)), fill=color)
        draw.polygon(((x + 13, y + 25), (x + 18, y + 25), (x + 20, y + 34), (x + 16, y + 34)), fill=color)
    else:
        draw.ellipse((x + 6, y, x + 16, y + 10), outline=color, width=2)
        draw.rounded_rectangle((x + 4, y + 12, x + 18, y + 27), radius=5, outline=color, width=2)
        draw.line((x + 7, y + 27, x + 3, y + 34), fill=color, width=2)
        draw.line((x + 15, y + 27, x + 19, y + 34), fill=color, width=2)


def draw_people_grid(draw, start_x, start_y, filled_count):
    index = 0
    for row in range(10):
        for col in range(15):
            person(draw, start_x + col * 29, start_y + row * 31, index < filled_count)
            index += 1


def render_concurrency():
    image, draw = canvas(720)
    title(draw, "150人が一斉に入ったとき")
    put_text(draw, (310, 142), "最初の配り方", 27, "heavy", NAVY, anchor="mm")
    put_text(draw, (970, 142), "配り方を変えたあと", 27, "heavy", NAVY, anchor="mm")

    draw_people_grid(draw, 88, 178, 130)
    draw_people_grid(draw, 748, 178, 150)

    # 2カラム間の矢印はこの1本だけ。
    draw.line((595, 332, 681, 332), fill=ORANGE, width=7)
    draw.polygon(((681, 317), (706, 332), (681, 347)), fill=ORANGE)

    centered_segments(draw, 310, 514, [
        ("入れた人 ", NAVY), ("130", NAVY, 35, "heavy"), (" / 150", GRAY),
    ], 27, "bold")
    put_text(draw, (310, 580), "届くまで 0.5秒", 27, "bold", NAVY, anchor="mm")
    put_text(draw, (310, 646), "入れなかった20人は、記録に残らない", 18, "regular", GRAY, anchor="mm")

    centered_segments(draw, 970, 514, [
        ("入れた人 ", NAVY), ("150", NAVY, 35, "heavy"), (" / 150", GRAY),
    ], 27, "bold")
    centered_segments(draw, 970, 572, [
        ("届くまで ", NAVY, 27, "bold"), ("0.13秒", ORANGE, 42, "heavy"),
    ], 27, "bold")
    return image


def render_connection_gap():
    image, draw = canvas(720)
    title(draw, "「繋がりました」の合図は、まだ届く合図ではなかった", 34)

    x_start, x_end = 215, 1000
    y_axis = 335
    # ハッチング区間。軸とは別の矢印を作らず、矩形内の斜線だけで表現する。
    hatch_box = (285, 220, 900, 305)
    draw.rounded_rectangle(hatch_box, radius=14, fill=TINT, outline=PALE, width=2)
    x1, y1, x2, y2 = hatch_box
    for x in range(x1 - 60, x2 + 60, 24):
        sx = max(x, x1)
        sy = y1 + max(0, x1 - x)
        ex = min(x + (y2 - y1), x2)
        ey = y1 + (ex - x)
        if sx <= ex and sy <= y2 and ey >= y1:
            draw.line((sx, sy, ex, min(ey, y2)), fill=PALE, width=3)
    put_text(draw, ((x1 + x2) / 2, (y1 + y2) / 2), "この間に送った発言は、誰にも届かない", 23, "bold", GRAY, anchor="mm")

    # 時間軸の矢印は1本だけ。
    draw.line((120, y_axis, 1115, y_axis), fill=NAVY, width=5)
    draw.polygon(((1115, 321), (1142, y_axis), (1115, 349)), fill=NAVY)
    draw.ellipse((x_start - 12, y_axis - 12, x_start + 12, y_axis + 12), fill=BG, outline=NAVY, width=4)
    draw.ellipse((x_end - 12, y_axis - 12, x_end + 12, y_axis + 12), fill=BG, outline=NAVY, width=4)
    put_text(draw, (x_start, 383), "「繋がりました」の合図", 22, "bold", NAVY, anchor="mm")
    put_text(draw, (x_end, 383), "配信が始まる", 22, "bold", NAVY, anchor="mm")

    draw.rounded_rectangle((115, 463, 1165, 548), radius=16, fill=ORANGE_TINT)
    centered_segments(draw, 640, 485, [
        ("すぐ送った → 25件中 ", NAVY, 27, "bold"),
        ("2件", ORANGE, 38, "heavy"),
        (" しか届かない", NAVY, 27, "bold"),
    ], 27, "bold")

    draw.rounded_rectangle((115, 577, 1165, 662), radius=16, fill=TINT)
    centered_segments(draw, 640, 599, [
        ("2秒待ってから送った → 25件中 ", NAVY, 27, "bold"),
        ("25件", NAVY, 38, "heavy"),
        (" 届いた", NAVY, 27, "bold"),
    ], 27, "bold")
    return image


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = (
        ("gate_0_ヘッダー.png", render_header, (1280, 670)),
        ("gate_1_消える方の実測.png", render_expiry, (1280, 720)),
        ("gate_2_150人の比較.png", render_concurrency, (1280, 720)),
        ("gate_3_繋がった直後の空白.png", render_connection_gap, (1280, 720)),
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
