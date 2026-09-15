"""note要件定義記事のPNG4枚。実行: python3 .output/render_req01.py

render_receipt01.py の書体・配色・draw_title・assert_fitsを直接継承。
日本語は指定のヒラギノで描き、全文字の境界と相互の重なりを検査する。
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw
from render_receipt01 import (
    BG, CARD, NAVY, INK, GRAY, BORDER, TINT, ORANGE, ORANGE_TINT,
    font, width_of, assert_fits, draw_title,
)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "note/images/2026-09-15"


class CheckedDraw:
    """参照draw_titleも含め、実際のtextbboxを描画前に検査する。"""
    def __init__(self, image):
        self.raw = ImageDraw.Draw(image)
        self.size = image.size
        self.boxes = []

    def __getattr__(self, name):
        return getattr(self.raw, name)

    def text(self, xy, text, font, fill, **kwargs):
        box = self.raw.textbbox(xy, text, font=font, **kwargs)
        x1, y1, x2, y2 = box
        assert 0 <= x1 <= x2 <= self.size[0], (text, box)
        assert 0 <= y1 <= y2 <= self.size[1], (text, box)
        for old, label in self.boxes:
            assert not (x1 < old[2] and x2 > old[0] and y1 < old[3] and y2 > old[1]), (text, label)
        self.boxes.append((box, text))
        self.raw.text(xy, text, font=font, fill=fill, **kwargs)


def canvas(height):
    image = Image.new("RGB", (1280, height), BG)
    return image, CheckedDraw(image)


def text(draw, box, value, size=24, weight="regular", color=INK, align="left"):
    """文字を指定枠の上端に配置。収まる最大サイズに縮小してから検査。"""
    x1, y1, x2, y2 = box
    for candidate in range(size, 13, -1):
        f = font(candidate, weight)
        bb = draw.textbbox((0, 0), value, font=f)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        if w <= x2 - x1 and h <= y2 - y1:
            break
    else:
        raise ValueError(f"Text does not fit: {value}")
    assert_fits(draw, value, f, x2 - x1)
    x = x1 if align == "left" else (x2 - w if align == "right" else (x1 + x2 - w) / 2)
    draw.text((x - bb[0], y1 - bb[1]), value, font=f, fill=color)


def card(draw, box, fill=CARD):
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=BORDER, width=2)


def sticky(image, xy, angle, label=None):
    layer = Image.new("RGBA", (94, 80), (0, 0, 0, 0))
    draw = CheckedDraw(layer)
    draw.rounded_rectangle((4, 4, 88, 73), radius=5, fill=ORANGE)
    draw.line((13, 16, 79, 16), fill=ORANGE_TINT, width=2)
    if label:
        text(draw, (10, 31, 83, 61), label, 20, "bold", CARD, "center")
    else:
        draw.line((20, 36, 67, 36), fill=ORANGE_TINT, width=3)
        draw.line((20, 49, 56, 49), fill=ORANGE_TINT, width=3)
    rotated = layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    assert xy[0] >= 0 and xy[1] >= 0
    assert xy[0] + rotated.width <= image.width and xy[1] + rotated.height <= image.height
    image.paste(rotated, xy, rotated)


def render_header():
    image, draw = canvas(670)
    draw.rounded_rectangle((72, 184, 80, 250), radius=4, fill=ORANGE)
    # 参照ヘッダーと同じ座標・フォント。
    for y, value in ((169, "要件定義をAIに任せたら、"), (229, "決めることが71個に増えた")):
        f = font(38, "heavy")
        assert_fits(draw, value, f, 620)
        draw.text((100, y), value, font=f, fill=NAVY)
    text(draw, (72, 303, 710, 335), "書く手間は消えた。決める手間は消えなかった", 24, "bold")
    draw.line((72, 350, 692, 350), fill=ORANGE, width=3)
    text(draw, (72, 395, 714, 427), "AIでiOSアプリを作っている、個人開発者のための実録", 19, color=GRAY)

    # 厚みのある束。背面から1枚ずつずらして描く。
    for i in range(5, -1, -1):
        offset = i * 8
        draw.rounded_rectangle((944 + offset, 190 + offset, 1166 + offset, 416 + offset),
                               radius=12, fill=CARD, outline=BORDER, width=2)
    text(draw, (968, 244, 1148, 282), "8,584行", 32, "heavy", NAVY)
    for y, length in ((307, 166), (330, 166), (353, 134), (376, 150)):
        draw.rounded_rectangle((968, y, 968 + length, y + 7), radius=3, fill=BORDER)

    # 薄いメモ1枚と、右上の束へ向かう矢印。
    draw.rounded_rectangle((772, 338, 880, 458), radius=9, fill=CARD, outline=BORDER, width=2)
    for y, length in ((362, 66), (380, 66), (398, 44)):
        draw.rounded_rectangle((792, y, 792 + length, y + 5), radius=2, fill=BORDER)
    text(draw, (780, 474, 880, 505), "103行", 22, "bold", GRAY, "center")
    draw.line((891, 355, 920, 315), fill=ORANGE, width=5)
    draw.polygon(((914, 310), (934, 298), (930, 323)), fill=ORANGE)

    sticky(image, (956, 148), 11)
    sticky(image, (1029, 136), -9)
    sticky(image, (1100, 160), 7, "決めて")
    text(draw, (922, 502, 1212, 535), "決めてください ×71", 22, "bold", ORANGE, "center")
    return image


def render_comparison():
    image, draw = canvas(720)
    draw_title(draw, "渡したのは103行。返ってきたのは78ファイル")
    card(draw, (60, 190, 414, 626))
    text(draw, (88, 224, 386, 261), "渡したもの", 25, "bold", NAVY)
    text(draw, (88, 302, 386, 388), "103行", 72, "heavy", NAVY)
    draw.line((88, 426, 386, 426), fill=BORDER, width=2)
    text(draw, (88, 458, 386, 495), "メモ1枚だけ", 24, "bold")
    text(draw, (88, 514, 392, 552), "最後に『まだ決まっていないこと』が8つ", 18, color=GRAY)

    text(draw, (428, 319, 674, 353), "AIに要件定義を書かせた", 19, "bold", GRAY, "center")
    draw.line((446, 398, 628, 398), fill=ORANGE, width=12)
    draw.polygon(((628, 376), (659, 398), (628, 420)), fill=ORANGE)

    draw.rounded_rectangle((690, 166, 1220, 642), radius=22, fill=TINT)
    text(draw, (716, 191, 1194, 228), "返ってきたもの", 25, "bold", NAVY)
    for box, number, unit in (
        ((710, 254, 946, 430), "78", "ファイル"),
        ((964, 254, 1200, 430), "8,584", "行"),
        ((710, 448, 946, 622), "11", "枚（図）"),
        ((964, 448, 1200, 622), "66", "ページ"),
    ):
        card(draw, box)
        x1, y1, x2, y2 = box
        text(draw, (x1 + 18, y1 + 28, x2 - 18, y1 + 99), number, 60, "heavy", NAVY, "center")
        text(draw, (x1 + 18, y1 + 122, x2 - 18, y2 - 20), unit, 23, color=GRAY, align="center")
    return image


def render_review():
    image, draw = canvas(720)
    draw_title(draw, "レビュー107件のうち、直させたのは7件だけ")
    values = (91, 7, 6, 3)
    colors = (NAVY, ORANGE, GRAY, BORDER)
    names = ("そのままでいい", "直させた", "今回は作らない", "保留")
    assert sum(values) == 107

    # 区画の幅を件数に比例させ、棒全体だけを角丸に切り抜く。
    bar = Image.new("RGB", (1160, 90), BG)
    bd = ImageDraw.Draw(bar)
    centers = []
    cumulative = 0
    for value, color in zip(values, colors):
        start = round(1160 * cumulative / 107)
        cumulative += value
        end = round(1160 * cumulative / 107)
        bd.rectangle((start, 0, end - 1, 89), fill=color)
        centers.append(60 + (start + end) / 2)
    mask = Image.new("L", bar.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 1159, 89), radius=18, fill=255)
    image.paste(bar, (60, 210), mask)
    text(draw, (88, 238, 1014, 282), "そのままでいい  91", 32, "bold", CARD, "center")

    # 狭い区画の文字は棒の外へ。線と文字が交差しない専用の段を使う。
    cx = centers[1]
    draw.line(((cx, 302), (cx, 326), (888, 326), (888, 340)), fill=ORANGE, width=2)
    text(draw, (784, 350, 1000, 381), "直させた 7", 23, "bold", ORANGE, "center")
    cx = centers[2]
    draw.line(((cx, 302), (cx, 312), (1112, 312), (1112, 397), (1042, 397), (1042, 409)), fill=GRAY, width=2)
    text(draw, (927, 418, 1165, 449), "今回は作らない 6", 23, "bold", GRAY, "center")
    cx = centers[3]
    draw.line(((cx, 302), (cx, 337)), fill=GRAY, width=2)
    text(draw, (1129, 350, 1220, 382), "保留 3", 23, "bold", INK, "center")

    for i, (name, value, color) in enumerate(zip(names, values, colors)):
        x = 60 + i * 296
        card(draw, (x, 480, x + 272, 568))
        draw.rounded_rectangle((x + 18, 502, x + 32, 516), radius=3, fill=color)
        text(draw, (x + 44, 500, x + 256, 528), name, 21, "bold")
        text(draw, (x + 44, 534, x + 256, 559), f"{value}件", 21, "bold", color=NAVY)

    draw.rounded_rectangle((60, 608, 1220, 677), radius=18, fill=ORANGE_TINT)
    text(draw, (84, 633, 1196, 663),
         "AIの出力は9割そのまま正しい。でも『これでいい』と言えるのは人間だけ",
         25, "bold", INK, "center")
    return image


def render_breakdown():
    """実フォルダ名を表示せず、役割と実測件数だけを比較する。"""
    image, draw = canvas(720)
    draw_title(draw, "返ってきた78ファイルの内訳")
    rows = (
        ("概要", 6),
        ("業務ルール・シナリオ", 6),
        ("機能ごとの仕様", 37),
        ("外部連携", 5),
        ("データ", 6),
        ("移行", 1),
        ("テスト", 2),
        ("非機能", 3),
        ("管理台帳（決定・未確定・traceability）", 6),
        ("自動生成の索引", 5),
        ("入口のREADME", 1),
    )
    assert len(rows) == 11 and sum(value for _, value in rows) == 78
    card(draw, (60, 148, 1220, 630))
    bar_x, unit_width = 590, 14
    for index, (label, value) in enumerate(rows):
        cy = 188 + index * 40
        highlighted = label == "機能ごとの仕様"
        color = ORANGE if highlighted else NAVY
        if highlighted:
            draw.rounded_rectangle((76, cy - 18, 1204, cy + 18), radius=9, fill=ORANGE_TINT)
        text(draw, (88, cy - 11, 558, cy + 17), label, 21,
             "bold" if highlighted else "regular", color if highlighted else INK)
        # 四角い端で描き、1件も37件も横幅を厳密に14px/件とする。
        end_x = bar_x + value * unit_width
        draw.rectangle((bar_x, cy - 9, end_x - 1, cy + 8), fill=color)
        text(draw, (end_x + 14, cy - 12, end_x + 78, cy + 17),
             str(value), 24, "heavy" if highlighted else "bold", color)
    text(draw, (60, 654, 1220, 687), "合計78ファイル・8,584行・図11枚",
         21, color=GRAY, align="right")
    return image


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, render, expected in (
        ("req_0_ヘッダー.png", render_header, (1280, 670)),
        ("req_1_103行と8584行.png", render_comparison, (1280, 720)),
        ("req_2_設計書の内訳.png", render_breakdown, (1280, 720)),
        ("req_5_レビュー107件の内訳.png", render_review, (1280, 720)),
    ):
        image = render()
        assert image.size == expected
        path = OUTPUT_DIR / name
        image.save(path, format="PNG")
        print(f"{path}: {image.width}×{image.height}; text checks passed")


if __name__ == "__main__":
    main()
