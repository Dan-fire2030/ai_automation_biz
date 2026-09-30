"""note記事「通信に失敗しました」用の図解3枚をPillowで描く。"""

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "note/images/2026-09-30"
FONT = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
BG = (250, 249, 246)
WHITE = (255, 255, 255)
NAVY = (31, 58, 95)
INK = (43, 58, 76)
GRAY = (138, 148, 166)
PALE = (213, 220, 229)
TINT = (238, 242, 246)
ORANGE = (232, 112, 58)
ORANGE_TINT = (253, 238, 229)
RED = (181, 69, 69)
RED_TINT = (252, 236, 234)


def canvas(height):
    image = Image.new("RGB", (1280, height), BG)
    return image, ImageDraw.Draw(image)


def text(draw, xy, value, size, color=INK, limit=None, anchor="mm"):
    face = ImageFont.truetype(FONT, size)
    box = draw.textbbox((0, 0), value, font=face, stroke_width=0)
    if limit is not None and box[2] - box[0] > limit:
        raise ValueError(f"文字幅超過: {value}: {box[2] - box[0]} > {limit}")
    draw.text(xy, value, font=face, fill=color, anchor=anchor, stroke_width=0)


def rr(draw, box, radius=30, fill=WHITE, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def heading(draw, value):
    rr(draw, (61, 58, 73, 114), 6, ORANGE)
    text(draw, (94, 52), value, 43, NAVY, 1110, "lt")


def dashed(draw, a, b, color=ORANGE, width=4, dash=11, gap=8):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    for start in range(0, int(length), dash + gap):
        end = min(start + dash, length)
        draw.line((a[0] + dx * start / length, a[1] + dy * start / length,
                   a[0] + dx * end / length, a[1] + dy * end / length),
                  fill=color, width=width)


def down_arrow(draw, x, y0, y1, color=ORANGE):
    draw.line((x, y0, x, y1 - 15), fill=color, width=5)
    draw.polygon(((x - 11, y1 - 18), (x, y1), (x + 11, y1 - 18)), fill=color)


def header():
    image, d = canvas(670)
    rr(d, (76, 129, 88, 253), 6, ORANGE)
    text(d, (111, 119), "『通信に失敗しました』", 49, NAVY, 650, "lt")
    text(d, (111, 202), "は嘘だった", 57, NAVY, 650, "lt")
    text(d, (112, 320), "エラー文より先に、", 29, INK, 580, "lt")
    text(d, (112, 369), "直前に変えたことを疑う", 29, INK, 580, "lt")

    # 画面内は設定を表す切り替えだけ。電波表示はすべて濃くする。
    rr(d, (838, 69, 1168, 607), 49, NAVY)
    rr(d, (853, 84, 1153, 592), 39, WHITE)
    rr(d, (950, 94, 1052, 105), 5, NAVY)
    for i, h in enumerate((10, 15, 21, 27)):
        rr(d, (1073 + i * 15, 143 - h, 1083 + i * 15, 143), 4, NAVY)
    text(d, (883, 131), "設定", 27, NAVY, 100, "lt")
    for y, long, active in ((210, 160, True), (277, 121, False), (344, 145, True)):
        rr(d, (878, y - 5, 878 + long, y + 5), 5, PALE)
        rr(d, (1070, y - 18, 1126, y + 18), 18, ORANGE if active else PALE)
        d.ellipse((1098 if active else 1074, y - 14, 1122 if active else 1098, y + 14), fill=WHITE)
    rr(d, (872, 416, 1134, 485), 18, RED_TINT)
    text(d, (1003, 451), "通信に失敗しました", 25, RED, 244)
    rr(d, (953, 559, 1054, 567), 4, PALE)

    # 別置きの短いリスト。抜けた位置だけを虫眼鏡が指す。
    rr(d, (624, 453, 813, 609), 28, TINT, PALE, 3)
    for y, length in ((478, 93), (507, 128), (566, 102)):
        rr(d, (647, y, 647 + length, y + 9), 4, NAVY)
    dashed(d, (647, 544), (759, 544), ORANGE, 4, 9, 7)
    d.ellipse((730, 512, 790, 572), outline=ORANGE, width=6)
    d.line((783, 564, 811, 591), fill=ORANGE, width=9)
    d.ellipse((801, 581, 817, 597), fill=ORANGE)
    return image


def cause():
    image, d = canvas(720)
    heading(d, "エラー文が指す先と、本当の原因")
    d.line((627, 171, 627, 632), fill=PALE, width=4)

    rr(d, (112, 205, 523, 304), 32, RED_TINT)
    text(d, (317, 255), "通信に失敗しました", 33, RED, 370)
    down_arrow(d, 317, 320, 364, GRAY)
    rr(d, (120, 387, 516, 553), 34, TINT, PALE, 3)
    text(d, (318, 445), "電波・回線", 38, GRAY, 300)
    text(d, (217, 506), "×", 38, GRAY, 65)
    text(d, (358, 507), "関係なかった", 27, GRAY, 260)

    cards = ((662, 906, "受け取る側の表"), (928, 1205, "取り寄せるリスト"))
    for x0, x1, label in cards:
        rr(d, (x0, 205, x1, 564), 31, WHITE, PALE, 3)
        text(d, ((x0 + x1) / 2, 249), label, 26, NAVY, x1 - x0 - 26)
        d.line((x0 + 24, 285, x1 - 24, 285), fill=PALE, width=3)
        for y, name in ((326, "名前"), (392, "日時")):
            rr(d, (x0 + 24, y - 21, x1 - 24, y + 24), 14, TINT)
            text(d, (x0 + 42, y), name, 26, INK, x1 - x0 - 75, "lm")
    rr(d, (686, 438, 882, 519), 16, TINT)
    text(d, (784, 478), "ノートの通知", 23, INK, 184)
    # 同じ位置に文字がなく、点線と説明だけが残っている。
    rr(d, (951, 438, 1182, 519), 16, ORANGE_TINT)
    dashed(d, (974, 469), (1156, 469))
    text(d, (1066, 496), "1行の書き忘れ", 20, ORANGE, 205)
    text(d, (868, 615), "○", 47, ORANGE, 55)
    text(d, (1020, 615), "本当の原因", 32, ORANGE, 270)
    return image


def order():
    image, d = canvas(720)
    heading(d, "疑う順番")
    data = (
        (72, 176, 800, 292, "①", "直前に変えたこと", 43, ORANGE, ORANGE_TINT, ORANGE),
        (101, 365, 771, 468, "②", "その前に変えたこと", 35, NAVY, WHITE, PALE),
        (134, 544, 738, 629, "③", "エラー文に書いてある原因", 28, GRAY, TINT, PALE),
    )
    for x0, y0, x1, y1, number, label, size, color, fill, outline in data:
        rr(d, (x0, y0, x1, y1), 33, fill, outline, 3)
        text(d, (x0 + 65, (y0 + y1) / 2), number, size, color, 72)
        text(d, (x0 + 120, (y0 + y1) / 2), label, size, color, x1 - x0 - 145, "lm")
    down_arrow(d, 436, 306, 351)
    down_arrow(d, 436, 482, 530, GRAY)

    rr(d, (868, 271, 1204, 444), 38, WHITE, PALE, 3)
    d.polygon(((869, 352), (830, 374), (869, 390)), fill=WHITE)
    d.line((869, 352, 830, 374, 869, 390), fill=PALE, width=3)
    text(d, (1036, 327), "エラー文＝結果", 30, NAVY, 296)
    text(d, (1036, 390), "原因とは限らない", 27, ORANGE, 296)
    return image


def main():
    if not Path(FONT).exists():
        raise FileNotFoundError(FONT)
    expected = (
        ("error_0_ヘッダー.png", header, (1280, 670)),
        ("error_1_指す先と原因.png", cause, (1280, 720)),
        ("error_2_疑う順番.png", order, (1280, 720)),
    )
    OUT.mkdir(parents=True, exist_ok=True)
    for name, render, size in expected:
        image = render()
        assert image.size == size
        image.save(OUT / name, format="PNG")
        print(f"{name}: {image.width}×{image.height}")


if __name__ == "__main__":
    main()
