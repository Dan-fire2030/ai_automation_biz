"""note記事「AIの精度を上げるのは、やめました」の画像4枚を生成する。

新シリーズ第1〜3回で確定した配色・書体・カードの型・余白を継承する。
日本語と線画をすべてPillowで決定的に描画し、微修正できるスクリプトとして残す。
ヘッダーのモチーフは、封筒・フォルダ系（1〜3本目）と重ならない「表と空欄」で組む。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "note" / "images" / "2026-08-20"

FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"

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


def draw_title(draw: ImageDraw.ImageDraw, title: str) -> None:
    draw.rounded_rectangle([60, 60, 68, 110], radius=4, fill=ORANGE)
    draw.text((88, 56), title, font=font(38, "heavy"), fill=NAVY)


def draw_check(draw, center, size=22, color=ORANGE, width=6) -> None:
    cx, cy = center
    draw.line(
        [(cx - size * 0.52, cy), (cx - size * 0.14, cy + size * 0.40), (cx + size * 0.55, cy - size * 0.44)],
        fill=color,
        width=width,
        joint="curve",
    )


def draw_arrow(draw, start, end, color=ORANGE, width=5, head=13) -> None:
    sx, sy = start
    ex, ey = end
    draw.line([(sx, sy), (ex, ey)], fill=color, width=width)
    dx, dy = ex - sx, ey - sy
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    base_x, base_y = ex - ux * head * 1.6, ey - uy * head * 1.6
    draw.polygon(
        [
            (ex, ey),
            (base_x + px * head * 0.72, base_y + py * head * 0.72),
            (base_x - px * head * 0.72, base_y - py * head * 0.72),
        ],
        fill=color,
    )


def draw_table_card(draw, box, rows=3, cols=3, blank=None, blank_mode="empty", outline=NAVY) -> None:
    """表カード。blank=(row, col) のセルだけ、空欄（empty）か推測埋め（guess）にする。"""
    x1, y1, x2, y2 = box
    header_h = 46
    draw.rounded_rectangle(box, radius=14, fill=CARD, outline=outline, width=3)
    draw.rounded_rectangle([x1 + 2, y1 + 2, x2 - 2, y1 + header_h], radius=12, fill=TINT)
    draw.rectangle([x1 + 2, y1 + header_h - 12, x2 - 2, y1 + header_h], fill=TINT)
    draw.line([(x1, y1 + header_h), (x2, y1 + header_h)], fill=outline, width=3)

    col_w = (x2 - x1) / cols
    row_h = (y2 - y1 - header_h) / rows
    for c in range(1, cols):
        cx = x1 + col_w * c
        draw.line([(cx, y1 + header_h), (cx, y2)], fill=BORDER, width=2)
    for r in range(1, rows):
        ry = y1 + header_h + row_h * r
        draw.line([(x1, ry), (x2, ry)], fill=BORDER, width=2)

    for c in range(cols):
        cx = x1 + col_w * c
        draw.rounded_rectangle([cx + 20, y1 + 17, cx + col_w - 20, y1 + 28], radius=5, fill=GRAY)

    for r in range(rows):
        for c in range(cols):
            cx = x1 + col_w * c
            ry = y1 + header_h + row_h * r
            mid = ry + row_h / 2
            if blank is not None and (r, c) == blank:
                if blank_mode == "empty":
                    draw.rounded_rectangle(
                        [cx + 13, ry + 11, cx + col_w - 13, ry + row_h - 11],
                        radius=8,
                        fill=CARD,
                        outline=ORANGE,
                        width=3,
                    )
                else:
                    draw.rounded_rectangle(
                        [cx + 13, ry + 11, cx + col_w - 13, ry + row_h - 11],
                        radius=8,
                        fill=ORANGE_TINT,
                    )
                    draw.rounded_rectangle([cx + 24, mid - 6, cx + col_w - 24, mid + 6], radius=6, fill=ORANGE)
                continue
            draw.rounded_rectangle([cx + 22, mid - 6, cx + col_w - 22, mid + 6], radius=6, fill=BORDER)


def draw_chip(draw, box, text, fill=TINT, text_color=INK, size=22) -> None:
    draw.rounded_rectangle(box, radius=12, fill=fill)
    cx = (box[0] + box[2]) / 2
    centered(draw, text, cx, box[1] + (box[3] - box[1] - size * 1.35) / 2, font(size, "bold"), text_color)


# ---------------------------------------------------------------- ヘッダー


def draw_header_motif(draw: ImageDraw.ImageDraw) -> None:
    """表の中に空欄がひとつだけ残り、そこに印が立っている線画モチーフ。"""
    table_box = (812, 152, 1152, 396)
    draw_table_card(draw, table_box, rows=3, cols=3, blank=(1, 2))

    # 空欄セルを指す旗。棒を立て、旗面をオレンジで塗る。右端に余白を残す。
    pole_x, pole_top, pole_bottom = 1188, 196, 300
    draw.line([(pole_x, pole_top), (pole_x, pole_bottom)], fill=NAVY, width=4)
    draw.polygon([(pole_x, pole_top), (pole_x + 54, pole_top + 20), (pole_x, pole_top + 40)], fill=ORANGE)
    draw_arrow(draw, (pole_x - 10, 288), (1126, 288), color=NAVY, width=4, head=11)

    # 手前：人が見る「合計1箇所」だけのカード。
    draw.rounded_rectangle([846, 428, 1116, 542], radius=16, fill=CARD, outline=NAVY, width=4)
    draw.line([(846, 470), (1116, 470)], fill=NAVY, width=3)
    draw.rounded_rectangle([872, 442, 952, 454], radius=6, fill=GRAY)
    draw.rounded_rectangle([872, 500, 996, 514], radius=7, fill=ORANGE)
    draw_check(draw, (1064, 506), size=34, color=ORANGE, width=7)


def render_header() -> Image.Image:
    image, draw = new_canvas(1280, 670)
    left = 92
    draw.rounded_rectangle([left, 186, left + 8, 254], radius=4, fill=ORANGE)
    draw.text((left + 30, 178), "AIの精度を上げるのは、", font=font(50, "heavy"), fill=NAVY)
    draw.text((left + 30, 252), "やめました", font=font(50, "heavy"), fill=NAVY)
    draw.line([(left, 372), (left + 620, 372)], fill=BORDER, width=2)
    draw.text((left, 404), "間違いに気づける形に、仕事を組み替える", font=font(31, "bold"), fill=ORANGE)
    draw.text(
        (left, 462),
        "中小企業のバックオフィスと、ひとり社長のためのAI活用",
        font=font(20),
        fill=GRAY,
    )
    draw_header_motif(draw)
    return image


# ---------------------------------------------------------------- 画像1


def render_two_shapes() -> Image.Image:
    image, draw = new_canvas(1200, 800)
    draw.line([(600, 62), (600, 726)], fill=BORDER, width=2)

    centered(draw, "気づけないままの形", 300, 54, font(27, "bold"), GRAY)
    centered(draw, "気づける形", 900, 54, font(27, "bold"), ORANGE)

    # 左：全部きれいに埋まっている表
    draw_table_card(draw, (72, 138, 528, 396), rows=3, cols=3, outline=BORDER)
    centered(draw, "ぜんぶ埋まっている", 300, 424, font(25, "bold"), INK)
    centered(draw, "どこを見ればいいか、手がかりがない", 300, 470, font(21), GRAY)
    draw_chip(draw, (118, 546, 482, 616), "確かめる場所は15箇所", fill=TINT, text_color=INK, size=25)
    centered(draw, "＝結局ぜんぶ読み直す", 300, 648, font(22), GRAY)

    # 右：空欄がひとつ残り、合計だけを照合する表
    draw_table_card(draw, (672, 138, 1128, 396), rows=3, cols=3, blank=(1, 2))
    draw_arrow(draw, (1160, 262), (1136, 262), color=ORANGE, width=5, head=12)
    centered(draw, "空欄と、合計だけが目印になる", 900, 424, font(25, "bold"), INK)
    centered(draw, "間違いが、見える場所にしか出てこない", 900, 470, font(21), GRAY)
    draw_chip(draw, (718, 546, 1082, 616), "確かめる場所は1箇所", fill=ORANGE, text_color=CARD, size=25)
    centered(draw, "＝ズレた月だけ見に行く", 900, 648, font(22), GRAY)

    return image


# ---------------------------------------------------------------- 画像2


def render_blank_signal() -> Image.Image:
    image, draw = new_canvas(1200, 800)
    draw_title(draw, "埋めさせるか、空欄で返させるか")

    # 左：頼み方と、返ってきた表
    draw.rounded_rectangle([70, 152, 530, 262], radius=16, fill=CARD, outline=BORDER, width=2)
    centered(draw, "一覧にしてください", 300, 172, font(24, "bold"), INK)
    centered(draw, "（それだけ頼む）", 300, 214, font(20), GRAY)
    draw_arrow(draw, (300, 278), (300, 322), color=GRAY, width=5, head=12)
    draw_table_card(draw, (72, 342, 528, 566), rows=3, cols=3, blank=(1, 2), blank_mode="guess", outline=BORDER)
    centered(draw, "推測で埋まる", 300, 596, font(25, "bold"), INK)
    centered(draw, "埋まった時点で、手がかりが消える", 300, 642, font(21), GRAY)

    draw.line([(600, 138), (600, 700)], fill=BORDER, width=2)

    # 右：一文を足した頼み方と、返ってきた表
    draw.rounded_rectangle([670, 152, 1130, 262], radius=16, fill=CARD, outline=ORANGE, width=3)
    centered(draw, "書いていない項目は空欄のままに。", 900, 172, font(23, "bold"), INK)
    centered(draw, "推測で埋めないでください。", 900, 212, font(23, "bold"), INK)
    draw_arrow(draw, (900, 278), (900, 322), color=ORANGE, width=5, head=12)
    draw_table_card(draw, (672, 342, 1128, 566), rows=3, cols=3, blank=(1, 2))
    centered(draw, "空欄が、そのまま合図になる", 900, 596, font(25, "bold"), INK)
    centered(draw, "AIが分からなかった場所が、目に見える", 900, 642, font(21), GRAY)

    centered(draw, "精度を上げる一文ではなく、見えるようにする一文", 600, 726, font(22), GRAY)
    return image


# ---------------------------------------------------------------- 画像3


PATTERNS = (
    ("検算できる数字が1つある", "請求書の合計。別ルートで出した数字とぶつける"),
    ("間違いが特定の言葉に集まる", "メール返信の「できます」「◯日までに」だけ読む"),
    ("分からないものが空欄で返ってくる", "①も②も無い仕事でも、頼み方ひとつで作れる"),
)


def render_three_patterns() -> Image.Image:
    image, draw = new_canvas(1200, 800)
    draw_title(draw, "気づける形の作り方は、3つありました")

    draw.line([(112, 190), (112, 660)], fill=BORDER, width=3)
    draw.text((60, 350), "上", font=font(21, "bold"), fill=GRAY)
    draw.text((60, 388), "か", font=font(21, "bold"), fill=GRAY)
    draw.text((60, 426), "ら", font=font(21, "bold"), fill=GRAY)
    draw.text((60, 464), "順", font=font(21, "bold"), fill=GRAY)
    draw.text((60, 502), "に", font=font(21, "bold"), fill=GRAY)
    draw_arrow(draw, (112, 620), (112, 676), color=GRAY, width=5, head=13)

    labels = ("①", "②", "③")
    for index, (title, note) in enumerate(PATTERNS):
        y1 = 176 + index * 162
        y2 = y1 + 126
        draw.rounded_rectangle([152, y1, 1140, y2], radius=16, fill=CARD, outline=BORDER, width=2)
        draw.rounded_rectangle([152, y1, 160, y2], radius=4, fill=ORANGE)
        draw.ellipse([190, y1 + 38, 240, y1 + 88], fill=ORANGE)
        centered(draw, labels[index], 215, y1 + 48, font(26, "heavy"), CARD)
        draw.text((272, y1 + 26), title, font=font(29, "bold"), fill=NAVY)
        draw.text((272, y1 + 76), note, font=font(21), fill=GRAY)

    centered(draw, "検算できる数字を探す → 事故が集まる言葉を探す → 無ければ空欄を作らせる", 600, 706, font(22), GRAY)
    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = (
        ("awareness_0_ヘッダー.png", render_header()),
        ("awareness_1_気づける形と気づけない形.png", render_two_shapes()),
        ("awareness_2_空欄が合図.png", render_blank_signal()),
        ("awareness_3_3つのパターン.png", render_three_patterns()),
    )
    for name, image in pages:
        path = OUTPUT_DIR / name
        image.save(path, format="PNG")
        print(f"saved: {path}  {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
