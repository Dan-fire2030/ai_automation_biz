"""note記事「スキル24→7」用の図解5枚をPillowで描く。"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "note/images/2026-09-26"
FONT = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
BG = (250, 249, 246)
WHITE = (255, 255, 255)
NAVY = (31, 58, 95)
INK = (43, 58, 76)
GRAY = (138, 148, 166)
PALE = (213, 220, 229)
TINT = (238, 242, 246)
GREEN = (70, 153, 123)
GREEN_TINT = (229, 244, 238)
ORANGE = (232, 112, 58)
ORANGE_TINT = (253, 238, 229)


def font(size):
    return ImageFont.truetype(FONT, size)


def canvas(height):
    im = Image.new("RGB", (1280, height), BG)
    return im, ImageDraw.Draw(im)


def txt(d, xy, value, size, color=INK, limit=None, anchor="mm"):
    f = font(size)
    b = d.textbbox((0, 0), value, font=f, stroke_width=0)
    width = b[2] - b[0]
    if limit is not None and width > limit:
        raise ValueError(f"文字幅超過: {value}: {width} > {limit}")
    d.text(xy, value, font=f, fill=color, anchor=anchor, stroke_width=0)


def rr(d, box, radius=30, fill=WHITE, outline=None, width=2):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def heading(d, value, size=42):
    rr(d, (60, 58, 70, 112), 5, ORANGE)
    txt(d, (90, 54), value, size, NAVY, 1110, "lt")


def dashed_line(d, a, b, color=PALE, width=4, dash=13, gap=10):
    import math
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    for start in range(0, int(length), dash + gap):
        end = min(start + dash, length)
        d.line((a[0] + dx * start / length, a[1] + dy * start / length,
                a[0] + dx * end / length, a[1] + dy * end / length), fill=color, width=width)


def dashed_box(d, box, color=PALE, width=5):
    x0, y0, x1, y1 = box
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        dashed_line(d, a, b, color, width)


def arrow(d, x0, x1, y, color=PALE):
    d.line((x0, y, x1 - 17, y), fill=color, width=6)
    d.polygon(((x1 - 19, y - 12), (x1, y), (x1 - 19, y + 12)), fill=color)


def header():
    im, d = canvas(670)
    rr(d, (74, 116, 85, 234), 5, ORANGE)
    txt(d, (110, 113), "減らしたら、", 52, NAVY, 590, "lt")
    txt(d, (110, 192), "困る仕組みまで", 48, NAVY, 625, "lt")
    txt(d, (110, 270), "消えていた", 52, NAVY, 590, "lt")
    rr(d, (110, 378, 600, 450), 32, ORANGE_TINT)
    txt(d, (355, 414), "Claude Code スキル 24 → 7", 25, NAVY, 450)

    # 道具のない壁掛け棚。札だけが一本のフックに残る。
    rr(d, (739, 104, 1193, 534), 40, TINT, PALE, 3)
    rr(d, (775, 157, 1157, 177), 10, NAVY)
    for row_y in (224, 345, 466):
        for x in (810, 872, 934, 996, 1058, 1120):
            d.line((x, row_y - 24, x, row_y + 3), fill=NAVY, width=5)
            d.arc((x - 13, row_y - 9, x + 13, row_y + 20), 0, 180, fill=NAVY, width=5)
    d.line((996, 228, 996, 255), fill=GRAY, width=3)
    rr(d, (946, 255, 1046, 322), 15, WHITE, ORANGE, 3)
    txt(d, (996, 289), "見張り", 24, ORANGE, 86)
    return im


def empty_target():
    im, d = canvas(720)
    heading(d, "設定は呼び出したまま、中身だけ消えた", 40)
    rr(d, (75, 205, 505, 535), 38, WHITE, PALE, 3)
    rr(d, (112, 237, 469, 307), 28, TINT)
    txt(d, (290, 272), "settings.json", 32, NAVY, 325)
    txt(d, (290, 381), "フックの登録 24本", 34, INK, 370)
    # 複数の登録線が、存在しない呼び出し先へ向かう。
    for i in range(7):
        y = 438 + i * 12
        d.line((505, y, 766, 390 + i * 11), fill=PALE, width=3)
    rr(d, (540, 280, 736, 338), 27, ORANGE_TINT)
    txt(d, (638, 309), "エラーは出ない", 23, ORANGE, 172)
    txt(d, (959, 205), "呼び出し先（スクリプト）", 28, NAVY, 470)
    dashed_box(d, (766, 257, 1202, 532), GRAY, 5)
    txt(d, (984, 395), "空っぽ", 42, PALE, 340)
    txt(d, (640, 626), "見張りを見張る役も、この中にいた", 25, GRAY, 950)
    return im


def rules_and_gate():
    im, d = canvas(720)
    heading(d, "決まりは残る。歯止めだけが消える", 41)
    rr(d, (78, 185, 603, 548), 40, WHITE, PALE, 3)
    rr(d, (677, 185, 1202, 548), 40, WHITE, PALE, 3)
    txt(d, (340, 233), "決まり（文章）", 31, NAVY, 430)
    txt(d, (940, 233), "歯止め（仕組み）", 31, NAVY, 430)
    # 左は一枚の規約。線は文字を表さず、アイコン内だけに収める。
    rr(d, (268, 281, 412, 382), 12, TINT, NAVY, 3)
    d.line((290, 313, 389, 313), fill=PALE, width=5)
    d.line((290, 338, 367, 338), fill=PALE, width=5)
    txt(d, (340, 424), "mainでは作業しない", 29, INK, 445)
    rr(d, (224, 471, 456, 523), 25, GREEN_TINT)
    txt(d, (340, 497), "残っている", 25, GREEN, 200)
    # 右は消えかけた遮断機。実線の支柱に、途切れた棒を重ねる。
    d.line((801, 379, 801, 303), fill=GRAY, width=12)
    rr(d, (783, 379, 819, 399), 8, GRAY)
    dashed_line(d, (811, 320), (1064, 366), GRAY, 12, 21, 14)
    d.line((1075, 359, 1096, 389), fill=PALE, width=7)
    rr(d, (824, 471, 1056, 523), 25, ORANGE_TINT)
    txt(d, (940, 497), "消えていた", 25, ORANGE, 200)
    d.polygon(((343, 588), (370, 568), (386, 588)), fill=TINT)
    rr(d, (259, 588, 1021, 662), 34, TINT)
    txt(d, (640, 625), "従い続けます。でも歯止めは外れています", 28, NAVY, 700)
    return im


def missing_three():
    im, d = canvas(720)
    txt(d, (640, 86), "スキル 24 → 7", 49, NAVY, 900)
    txt(d, (640, 158), "一緒に消えた、困る仕組み3つ", 27, GRAY, 900)
    cards = [
        (65, 230, 425, 512, "①", "mainを守るフック", "見つけた：AI", NAVY, TINT),
        (460, 230, 820, 512, "②", "要件定義の検査", "見つけた：AI", NAVY, TINT),
        (855, 230, 1215, 512, "③", "サイトを作る仕組み", "見つけた：自分（20分後）", ORANGE, ORANGE_TINT),
    ]
    for x0, y0, x1, y1, n, title, found, accent, tint in cards:
        rr(d, (x0, y0, x1, y1), 36, WHITE, accent if accent == ORANGE else PALE, 3)
        d.ellipse((x0 + 31, y0 + 27, x0 + 94, y0 + 90), fill=tint)
        txt(d, (x0 + 62, y0 + 58), n, 29, accent, 48)
        txt(d, ((x0 + x1) / 2, 363), title, 27, NAVY, 330)
        rr(d, (x0 + 25, 429, x1 - 25, 485), 25, tint)
        txt(d, ((x0 + x1) / 2, 457), found, 22, accent, 305)
    rr(d, (150, 568, 1130, 642), 34, NAVY)
    txt(d, (640, 605), "3つとも、呼ばなくても裏で動いていた", 29, WHITE, 910)
    return im


def steps():
    im, d = canvas(720)
    heading(d, "片付けの点検、4ステップ", 42)
    # 括りはカードの上に置き、片付け前と後の範囲を明確にする。
    d.line((80, 214, 348, 214), fill=GREEN, width=4)
    d.line((80, 214, 80, 229), fill=GREEN, width=4)
    d.line((348, 214, 348, 229), fill=GREEN, width=4)
    txt(d, (214, 182), "片付ける前", 25, GREEN, 240)
    d.line((402, 214, 1202, 214), fill=ORANGE, width=4)
    d.line((402, 214, 402, 229), fill=ORANGE, width=4)
    d.line((1202, 214, 1202, 229), fill=ORANGE, width=4)
    txt(d, (802, 182), "片付けたあと", 25, ORANGE, 350)
    data = [
        (72, "①", "書き出す", ("裏で動いているもの",), GREEN, GREEN_TINT),
        (379, "②", "数える", ("参照24本・欠け0本",), NAVY, TINT),
        (686, "③", "動かす", ("わざとダメな操作", "→ 拒否"), NAVY, TINT),
        (993, "④", "書き残す", ("使えなくなった", "・次も消える"), NAVY, TINT),
    ]
    for x, n, title, sub, accent, tint in data:
        rr(d, (x, 262, x + 215, 589), 32, WHITE, PALE, 3)
        d.ellipse((x + 71, 295, x + 144, 368), fill=tint)
        txt(d, (x + 107, 331), n, 32, accent, 58)
        txt(d, (x + 107, 422), title, 29, NAVY, 198)
        for i, line in enumerate(sub):
            txt(d, (x + 107, 500 + i * 37), line, 20, GRAY, 195)
    for x in (301, 608, 915):
        arrow(d, x, x + 63, 421, ORANGE)
    return im


def main():
    if not Path(FONT).exists():
        raise FileNotFoundError(FONT)
    expected = [
        ("tidy_0_ヘッダー.png", header, (1280, 670)),
        ("tidy_1_呼び出し先が空.png", empty_target, (1280, 720)),
        ("tidy_2_規約と歯止め.png", rules_and_gate, (1280, 720)),
        ("tidy_3_消えた3つ.png", missing_three, (1280, 720)),
        ("tidy_4_点検の4ステップ.png", steps, (1280, 720)),
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    for name, render, size in expected:
        image = render()
        assert image.size == size
        image.save(OUT / name, format="PNG")
        print(f"{name}: {image.width}×{image.height}")


if __name__ == "__main__":
    main()
