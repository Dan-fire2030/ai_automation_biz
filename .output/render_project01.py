"""note記事「AIに毎回同じ注意を打つのは、やめました」の画像4枚を生成する。

新シリーズ第1回・第2回で確定した配色、書体、カードの型、余白を継承する。
日本語と線画をすべてPillowで決定的に描画し、微修正できるスクリプトとして残す。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "note" / "images" / "2026-08-14"

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


def draw_rule_lines(draw, box, color=GRAY, widths=(1.0, 0.82, 0.64), line_width=5) -> None:
    x1, y1, x2, y2 = box
    available = x2 - x1
    spacing = (y2 - y1) / max(len(widths) - 1, 1)
    for index, ratio in enumerate(widths):
        y = int(y1 + index * spacing)
        draw.line([(x1, y), (x1 + int(available * ratio), y)], fill=color, width=line_width)


def draw_sticky(draw, box, compact=False) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill=ORANGE_TINT, outline=ORANGE, width=2)
    fold = 18 if not compact else 13
    draw.polygon([(x2 - fold, y1), (x2, y1), (x2, y1 + fold)], fill=ORANGE)
    inset_x = 22 if not compact else 15
    inset_y = 21 if not compact else 15
    draw_rule_lines(
        draw,
        (x1 + inset_x, y1 + inset_y, x2 - inset_x, y2 - inset_y),
        color=GRAY,
        widths=(0.9, 0.72, 0.82),
        line_width=4 if not compact else 3,
    )


def draw_chat_card(draw, box, fill=CARD, outline=BORDER, tail=True, width=2) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=16, fill=fill, outline=outline, width=width)
    if tail:
        draw.polygon([(x1 + 42, y2 - 2), (x1 + 62, y2 - 2), (x1 + 48, y2 + 14)], fill=fill)
        draw.line([(x1 + 42, y2), (x1 + 48, y2 + 14), (x1 + 62, y2)], fill=outline, width=width)


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


# ---------------------------------------------------------------- ヘッダー


def draw_header_motif(draw: ImageDraw.ImageDraw) -> None:
    """フォルダ内の指示カードが、手前の会話へ効く線画モチーフ。"""
    # 背面：左上に見出しタブが付いた、明確な書類フォルダの輪郭。
    folder_back = [
        (850, 275),
        (850, 225),
        (945, 225),
        (975, 260),
        (1175, 260),
        (1175, 500),
        (850, 500),
    ]
    draw.polygon(folder_back, fill=TINT, outline=NAVY)
    draw.line(folder_back + [folder_back[0]], fill=NAVY, width=4, joint="curve")

    # フォルダから立ち上がる指示カード。
    draw.rounded_rectangle([930, 150, 1135, 410], radius=14, fill=CARD, outline=NAVY, width=4)
    draw.rounded_rectangle([957, 178, 1015, 204], radius=5, fill=ORANGE_TINT)
    draw_rule_lines(draw, (957, 244, 1103, 326), color=GRAY, widths=(1.0, 0.82, 0.64), line_width=5)

    # 手前：斜線や三角フラップを使わず、封筒に見えないフォルダ面にする。
    draw.rounded_rectangle([850, 330, 1175, 505], radius=16, fill=CARD, outline=NAVY, width=4)
    draw.line([(850, 352), (1175, 352)], fill=NAVY, width=4)
    draw.rounded_rectangle([884, 382, 958, 391], radius=4, fill=ORANGE)

    # フォルダの手前・右下に重ねる2つの小さな吹き出し。
    draw.rounded_rectangle([1038, 426, 1212, 530], radius=42, fill=CARD, outline=NAVY, width=4)
    draw.polygon([(1072, 510), (1046, 550), (1100, 526)], fill=CARD)
    draw.line([(1072, 510), (1046, 550), (1100, 526)], fill=NAVY, width=4)
    draw_rule_lines(draw, (1082, 462, 1174, 498), color=BORDER, widths=(1.0, 0.72), line_width=5)

    draw.rounded_rectangle([888, 445, 1016, 521], radius=32, fill=CARD, outline=NAVY, width=4)
    draw.polygon([(934, 505), (916, 541), (960, 516)], fill=CARD)
    draw.line([(934, 505), (916, 541), (960, 516)], fill=NAVY, width=4)
    draw.line([(920, 478), (978, 478)], fill=ORANGE, width=6)


def render_header() -> Image.Image:
    image, draw = new_canvas(1280, 670)
    left = 92
    draw.rounded_rectangle([left, 186, left + 8, 254], radius=4, fill=ORANGE)
    draw.text((left + 30, 178), "AIに毎回同じ注意を", font=font(50, "heavy"), fill=NAVY)
    draw.text((left + 30, 252), "打つのは、やめました", font=font(50, "heavy"), fill=NAVY)
    draw.line([(left, 372), (left + 620, 372)], fill=BORDER, width=2)
    draw.text((left, 404), "請求書チェックをプロジェクトに置く", font=font(31, "bold"), fill=ORANGE)
    draw.text(
        (left, 462),
        "中小企業のバックオフィスと、ひとり社長のためのAI活用",
        font=font(20),
        fill=GRAY,
    )
    draw_header_motif(draw)
    return image


# ---------------------------------------------------------------- 画像1


def render_repeat_entry() -> Image.Image:
    image, draw = new_canvas(1200, 800)
    draw_title(draw, "毎回、同じ3行を打ち直していました")

    card_x1, card_x2 = 120, 890
    card_h = 128
    for index, y in enumerate((160, 330, 500), start=1):
        draw_chat_card(draw, (card_x1, y, card_x2, y + card_h))
        draw.text((card_x1 + 28, y + 43), f"{index}回目", font=font(20, "bold"), fill=GRAY)
        draw_sticky(draw, (card_x1 + 154, y + 18, card_x2 - 28, y + 106), compact=True)

    draw.rounded_rectangle([925, 330, 1140, 400], radius=12, fill=ORANGE)
    centered(draw, "毎回これを手で打つ", 1032, 348, font(20, "bold"), CARD)
    draw_arrow(draw, (925, 365), (902, 365), color=ORANGE, width=5, head=11)

    centered(draw, "1回でも打ち忘れると、そこだけ挙動が変わる", 600, 704, font(22), GRAY)
    return image


# ---------------------------------------------------------------- 画像2


def render_write_once() -> Image.Image:
    image, draw = new_canvas(1200, 800)
    draw.line([(600, 62), (600, 730)], fill=BORDER, width=2)

    centered(draw, "毎回打つ", 300, 54, font(27, "bold"), GRAY)
    centered(draw, "一度書いておく", 900, 54, font(27, "bold"), ORANGE)

    # 左：3回それぞれに同じ付箋
    for index, y in enumerate((150, 345, 540), start=1):
        draw_chat_card(draw, (70, y, 530, y + 140))
        draw.text((94, y + 50), f"{index}回目", font=font(18, "bold"), fill=GRAY)
        draw_sticky(draw, (190, y + 22, 502, y + 116), compact=True)

    # 右：プロジェクト内に1枚だけ置き、下の3会話へ適用
    draw.rounded_rectangle([680, 124, 1120, 316], radius=18, fill=CARD, outline=NAVY, width=3)
    draw.text((708, 145), "プロジェクト", font=font(23, "bold"), fill=NAVY)
    draw_sticky(draw, (708, 190, 1092, 288), compact=True)

    card_boxes = ((725, 385, 1115, 468), (725, 510, 1115, 593), (725, 635, 1115, 718))
    for index, box in enumerate(card_boxes, start=1):
        draw_chat_card(draw, box, tail=False)
        draw.text((754, box[1] + 23), f"{index}回目", font=font(18, "bold"), fill=GRAY)
        draw_rule_lines(draw, (845, box[1] + 30, 1068, box[1] + 51), color=BORDER, widths=(1.0, 0.66), line_width=4)

    # カード描画後に、交差しない配線図型のコネクタを描く。
    # プロジェクト下辺中央から短く下ろし、カード左側の共通幹へ接続する。
    stem_x = 900
    trunk_x = 665
    stem_y = 340
    target_x = 707  # カード左辺725の18px手前。
    target_ys = [(box[1] + box[3]) // 2 for box in card_boxes]

    # 先に全ての線を描く。
    draw.line([(stem_x, 316), (stem_x, stem_y), (trunk_x, stem_y)], fill=ORANGE, width=4)
    draw.line([(trunk_x, stem_y), (trunk_x, target_ys[-1])], fill=ORANGE, width=4)
    for target_y in target_ys:
        draw.line([(trunk_x, target_y), (target_x, target_y)], fill=ORANGE, width=4)

    # 最後に矢尻だけを描く。カードには重ねず、空中にも浮かせない。
    for target_y in target_ys:
        draw.polygon(
            [(target_x, target_y), (688, target_y - 10), (688, target_y + 10)],
            fill=ORANGE,
        )

    return image


# ---------------------------------------------------------------- 画像3


ACCIDENTS = (
    ("件名を勝手に作った", "推測で埋めないでください"),
    ("和暦を勝手に西暦にした", "原本の表記のまま残してください"),
    ("頼んでない合計を出した", "合計や検算はこちらで出します"),
)


def render_accidents_and_rules() -> Image.Image:
    image, draw = new_canvas(1200, 800)
    draw_title(draw, "起きたことに、1行ずつ当てる")

    centered(draw, "打ち忘れたときに起きたこと", 280, 132, font(21, "bold"), GRAY)
    centered(draw, "手順に書いた1行", 920, 132, font(21, "bold"), ORANGE)

    left_box = (60, 0, 500, 0)
    right_box = (700, 0, 1140, 0)
    for index, (problem, rule) in enumerate(ACCIDENTS):
        y1 = 190 + index * 155
        y2 = y1 + 112
        draw.rounded_rectangle([left_box[0], y1, left_box[2], y2], radius=15, fill=TINT)
        centered(draw, problem, 280, y1 + 34, font(25, "bold"), INK)

        draw.rounded_rectangle(
            [right_box[0], y1, right_box[2], y2],
            radius=15,
            fill=CARD,
            outline=ORANGE,
            width=2,
        )
        centered(draw, rule, 920, y1 + 35, font(22, "bold"), INK)

        # 右カード外側x=700の手前、x=678で矢印を止める。
        draw_arrow(draw, (520, (y1 + y2) // 2), (678, (y1 + y2) // 2), color=ORANGE, width=5, head=12)

    centered(draw, "思いついたルールではなく、実際に起きたことを潰す", 600, 700, font(22), GRAY)
    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = (
        ("project_0_ヘッダー.png", render_header()),
        ("project_1_毎回打っている.png", render_repeat_entry()),
        ("project_2_一度書いておく.png", render_write_once()),
        ("project_3_3つの事故と3行.png", render_accidents_and_rules()),
    )
    for name, image in pages:
        path = OUTPUT_DIR / name
        image.save(path, format="PNG")
        print(f"saved: {path}  {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
