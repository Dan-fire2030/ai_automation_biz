"""note自己紹介記事用のPNG画像を3枚生成する。"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "note" / "images" / "2026-09-26"
FONT_PATH = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"

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
BLUE_TINT = (231, 239, 247)
PURPLE_TINT = (241, 235, 246)


def font(size: int) -> ImageFont.FreeTypeFont:
    if not Path(FONT_PATH).exists():
        raise FileNotFoundError(FONT_PATH)
    return ImageFont.truetype(FONT_PATH, size)


def canvas(height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1280, height), BG)
    return image, ImageDraw.Draw(image, "RGBA")


def text_width(draw: ImageDraw.ImageDraw, value: str, size: int) -> int:
    box = draw.textbbox((0, 0), value, font=font(size), stroke_width=0)
    return box[2] - box[0]


def put_text(
    draw: ImageDraw.ImageDraw,
    xy,
    value: str,
    size: int,
    color=INK,
    max_width: int | None = None,
    anchor: str | None = None,
) -> int:
    if max_width is None:
        raise ValueError(f"max_widthが未指定です: {value!r}")
    width = text_width(draw, value, size)
    if width > max_width:
        raise ValueError(f"文字幅超過: {value!r} {width}px > {max_width}px")
    draw.text(xy, value, font=font(size), fill=color, anchor=anchor, stroke_width=0)
    return width


def section_title(draw: ImageDraw.ImageDraw, value: str, size: int = 42) -> None:
    draw.rounded_rectangle((60, 58, 70, 112), radius=5, fill=ORANGE)
    put_text(draw, (90, 53), value, size, NAVY, 1120)


def rounded_line(draw: ImageDraw.ImageDraw, xy, fill, width: int) -> None:
    x1, y1, x2, y2 = xy
    draw.line(xy, fill=fill, width=width)
    radius = width // 2
    draw.ellipse((x1 - radius, y1 - radius, x1 + radius, y1 + radius), fill=fill)
    draw.ellipse((x2 - radius, y2 - radius, x2 + radius, y2 + radius), fill=fill)


def arrow(draw: ImageDraw.ImageDraw, start, end, color=ORANGE, width: int = 8, head: int = 18) -> None:
    x1, y1 = start
    x2, y2 = end
    angle = math.atan2(y2 - y1, x2 - x1)
    bx = x2 - head * math.cos(angle)
    by = y2 - head * math.sin(angle)
    rounded_line(draw, (x1, y1, bx, by), color, width)
    spread = head * 0.7
    left = (bx + spread * math.sin(angle), by - spread * math.cos(angle))
    right = (bx - spread * math.sin(angle), by + spread * math.cos(angle))
    draw.polygon((left, (x2, y2), right), fill=color)


def check_mark(draw: ImageDraw.ImageDraw, center, color=GREEN, scale: float = 1.0) -> None:
    cx, cy = center
    points = (
        (cx - 31 * scale, cy - 1 * scale),
        (cx - 8 * scale, cy + 22 * scale),
        (cx + 37 * scale, cy - 29 * scale),
    )
    draw.line(points, fill=color, width=max(4, int(11 * scale)), joint="curve")


def document(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    line_count: int,
    highlighted_line: int | None = None,
) -> list[tuple[int, int, int, int]]:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=30, fill=WHITE, outline=PALE, width=3)
    draw.rounded_rectangle((x1 + 28, y1 + 26, x1 + 104, y1 + 38), radius=6, fill=NAVY)
    rows: list[tuple[int, int, int, int]] = []
    usable_top = y1 + 70
    usable_bottom = y2 - 32
    step = (usable_bottom - usable_top) / max(1, line_count - 1)
    for index in range(line_count):
        yy = round(usable_top + index * step)
        right = x2 - 30 - (26 if index % 3 == 2 else 0)
        row = (x1 + 30, yy, right, yy)
        rows.append((x1 + 24, yy - 11, x2 - 24, yy + 11))
        if highlighted_line == index:
            draw.rounded_rectangle(rows[-1], radius=11, fill=ORANGE_TINT)
            rounded_line(draw, row, ORANGE, 5)
        else:
            rounded_line(draw, row, PALE, 4)
    return rows


def magnifier(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int) -> None:
    cx, cy = center
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=(255, 255, 255, 174),
        outline=NAVY,
        width=12,
    )
    angle = math.radians(45)
    start = (cx + int(radius * math.cos(angle)), cy + int(radius * math.sin(angle)))
    end = (start[0] + 98, start[1] + 98)
    rounded_line(draw, (*start, *end), NAVY, 20)


def render_header() -> Image.Image:
    image, draw = canvas(670)

    draw.rounded_rectangle((72, 72, 82, 134), radius=5, fill=ORANGE)
    put_text(draw, (100, 58), "確かめるのは、1か所", 50, NAVY, 760)
    put_text(
        draw,
        (72, 132),
        "はじめまして、ハルトです｜AIに任せる事務のnote",
        24,
        NAVY,
        700,
    )
    draw.rounded_rectangle((72, 178, 772, 182), radius=2, fill=ORANGE)

    # 左：細かい行すべてを追っている状態。
    left_box = (88, 252, 398, 568)
    left_rows = document(draw, left_box, line_count=12)
    for row in left_rows:
        x1, y1, x2, y2 = row
        draw.rounded_rectangle((x1, y1, x2, y2), radius=11, fill=(*ORANGE_TINT, 56))
    # 薄い視線を、書類全体へ何度も走らせる。
    for yy in (328, 402, 476):
        draw.arc((126, yy - 22, 354, yy + 22), 195, 345, fill=(*ORANGE, 62), width=3)
        draw.ellipse((235, yy - 5, 245, yy + 5), fill=(*ORANGE, 68))
    draw.rounded_rectangle((126, 582, 360, 626), radius=22, fill=TINT)
    put_text(draw, (243, 604), "全部を見る", 20, GRAY, 190, anchor="mm")

    arrow(draw, (458, 414), (614, 414), ORANGE, width=7, head=20)
    put_text(draw, (536, 377), "見直す", 19, ORANGE, 120, anchor="mm")

    # 右：同じ書類の1行だけを大きく照らす。
    right_box = (690, 228, 1082, 588)
    rows = document(draw, right_box, line_count=9, highlighted_line=5)
    target = rows[5]
    target_center = ((target[0] + target[2]) // 2, (target[1] + target[3]) // 2)
    magnifier(draw, target_center, 104)
    draw.ellipse(
        (target_center[0] - 44, target_center[1] - 44, target_center[0] + 44, target_center[1] + 44),
        fill=GREEN_TINT,
        outline=GREEN,
        width=3,
    )
    check_mark(draw, target_center, GREEN, 0.62)
    draw.rounded_rectangle((776, 600, 1002, 644), radius=22, fill=GREEN_TINT)
    put_text(draw, (889, 622), "1か所だけ見る", 20, GREEN, 190, anchor="mm")

    return image


def render_scope() -> Image.Image:
    image, draw = canvas(720)
    section_title(draw, "AIに任せる範囲と、人が確かめる1か所", 42)

    cards = (
        ("請求書", "合計", GREEN_TINT, GREEN),
        ("問い合わせメール", "言い切り", ORANGE_TINT, ORANGE),
        ("レシート", "3か所", BLUE_TINT, NAVY),
        ("期限", "2通りで聞く", PURPLE_TINT, (106, 82, 137)),
    )
    card_width = 276
    gap = 18
    start_x = 61
    top = 158
    bottom = 564

    for index, (title, focus, face, accent) in enumerate(cards):
        x1 = start_x + index * (card_width + gap)
        x2 = x1 + card_width
        draw.rounded_rectangle((x1, top, x2, bottom), radius=38, fill=WHITE, outline=PALE, width=2)
        put_text(draw, ((x1 + x2) // 2, 205), title, 29, NAVY, card_width - 34, anchor="mm")

        # 大きな薄い面が任せる範囲、小さな濃い丸が人の確認点。
        draw.rounded_rectangle((x1 + 24, 244, x2 - 24, 530), radius=34, fill=face)
        draw.ellipse((x1 + 94, 318, x1 + 182, 406), fill=accent)
        if focus == "合計":
            put_text(draw, ((x1 + x2) // 2, 454), focus, 31, accent, card_width - 64, anchor="mm")
        else:
            draw.rounded_rectangle((x1 + 42, 426, x2 - 42, 492), radius=30, fill=WHITE)
            size = 26 if focus != "2通りで聞く" else 23
            put_text(draw, ((x1 + x2) // 2, 459), focus, size, accent, card_width - 100, anchor="mm")

    draw.rounded_rectangle((242, 620, 520, 674), radius=27, fill=TINT)
    draw.rounded_rectangle((262, 636, 298, 658), radius=11, fill=GREEN_TINT)
    put_text(draw, (316, 647), "AIに任せる", 21, GRAY, 180, anchor="lm")

    draw.rounded_rectangle((574, 620, 1018, 674), radius=27, fill=TINT)
    draw.ellipse((597, 632, 627, 662), fill=NAVY)
    put_text(draw, (647, 647), "人が確かめる", 21, NAVY, 190, anchor="lm")

    return image


def signboard(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    detail: str,
    face,
    accent,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=32, fill=WHITE, outline=accent, width=3)
    draw.rounded_rectangle((x1 + 20, y1 + 18, x2 - 20, y1 + 68), radius=24, fill=face)
    put_text(draw, ((x1 + x2) // 2, y1 + 43), title, 27, accent, x2 - x1 - 56, anchor="mm")
    put_text(draw, ((x1 + x2) // 2, y1 + 105), detail, 20, INK, x2 - x1 - 46, anchor="mm")
    # 看板の短い脚。
    rounded_line(draw, ((x1 + x2) // 2, y2, (x1 + x2) // 2, y2 + 16), accent, 7)


def render_guide() -> Image.Image:
    image, draw = canvas(720)
    section_title(draw, "このnoteの歩き方", 42)

    top_left = (72, 166, 486, 306)
    top_right = (794, 166, 1208, 306)
    bottom_left = (72, 496, 486, 636)
    bottom_right = (794, 496, 1208, 636)
    center_box = (484, 325, 796, 431)

    # 道を先に描き、看板が交点を隠すようにする。
    paths = (
        ((556, 350), (453, 290), ORANGE),
        ((724, 350), (827, 290), GREEN),
        ((556, 406), (453, 510), NAVY),
        ((724, 406), (827, 510), (106, 82, 137)),
    )
    for start, end, color in paths:
        rounded_line(draw, (*start, *end), (*color, 95), 15)
        rounded_line(draw, (*start, *end), BG, 5)

    signboard(draw, top_left, "お金の書類", "請求書・レシート・固定費", ORANGE_TINT, ORANGE)
    signboard(draw, top_right, "メールとやりとり", "問い合わせ・届かないメール", GREEN_TINT, GREEN)
    signboard(draw, bottom_left, "期限と記録", "期限・議事録・メモ", BLUE_TINT, NAVY)
    signboard(draw, bottom_right, "AIとの付き合い方", "職種を問わず読めます", PURPLE_TINT, (106, 82, 137))

    draw.rounded_rectangle(center_box, radius=34, fill=NAVY)
    put_text(draw, (640, 378), "どこで困っていますか？", 24, WHITE, 276, anchor="mm")
    rounded_line(draw, (640, 431, 640, 466), NAVY, 9)
    draw.rounded_rectangle((614, 464, 666, 480), radius=8, fill=NAVY)

    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = (
        ("intro_0_ヘッダー.png", render_header, (1280, 670)),
        ("intro_1_任せる範囲と1か所.png", render_scope, (1280, 720)),
        ("intro_2_このnoteの歩き方.png", render_guide, (1280, 720)),
    )
    expected_names = {name for name, _, _ in outputs}

    for existing in OUTPUT_DIR.iterdir():
        if existing.is_file() and existing.name not in expected_names:
            existing.unlink()

    for name, renderer, expected_size in outputs:
        image = renderer()
        if image.size != expected_size:
            raise AssertionError((name, image.size, expected_size))
        path = OUTPUT_DIR / name
        image.save(path, format="PNG")
        print(f"{path}: {image.width}×{image.height} PNG")

    actual_names = {path.name for path in OUTPUT_DIR.iterdir() if path.is_file()}
    if actual_names != expected_names:
        raise AssertionError((actual_names, expected_names))


if __name__ == "__main__":
    main()
