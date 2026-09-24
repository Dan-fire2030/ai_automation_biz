"""note記事「メールが届かない原因」用のPNG画像を3枚生成する。

実行:
    python3 .output/render_mail01.py

日本語とメールアドレスはmacOS標準のヒラギノ丸ゴ ProN W4で決定的に描画する。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "note" / "images" / "2026-09-24"
FONT_PATH = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"

# render_memo01_soft.py から流用した配色。
BG = (250, 249, 246)
WHITE = (255, 255, 255)
NAVY = (31, 58, 95)
INK = (43, 58, 76)
GRAY = (138, 148, 166)
PALE = (213, 220, 229)
TINT = (238, 242, 246)
ORANGE = (232, 112, 58)
ORANGE_TINT = (253, 238, 229)


def font(size: int) -> ImageFont.FreeTypeFont:
    if not Path(FONT_PATH).exists():
        raise FileNotFoundError(f"必要なフォントがありません: {FONT_PATH}")
    return ImageFont.truetype(FONT_PATH, size)


def canvas(height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1280, height), BG)
    return image, ImageDraw.Draw(image)


def text_box(draw: ImageDraw.ImageDraw, value: str, size: int):
    # 疑似ボールドは禁止。計測時も描画時も stroke_width=0 固定。
    return draw.textbbox((0, 0), value, font=font(size), stroke_width=0)


def text_width(draw: ImageDraw.ImageDraw, value: str, size: int) -> int:
    box = text_box(draw, value, size)
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


def rounded_line(draw, xy, fill, width: int) -> None:
    x1, y1, x2, y2 = xy
    draw.line(xy, fill=fill, width=width)
    radius = width // 2
    draw.ellipse((x1 - radius, y1 - radius, x1 + radius, y1 + radius), fill=fill)
    draw.ellipse((x2 - radius, y2 - radius, x2 + radius, y2 + radius), fill=fill)


def right_arrow(draw, start, end, color=ORANGE, width: int = 8, head: int = 20) -> None:
    x1, y = start
    x2, _ = end
    rounded_line(draw, (x1, y, x2 - head, y), color, width)
    draw.polygon(((x2 - head, y - head), (x2, y), (x2 - head, y + head)), fill=color)


def envelope(draw: ImageDraw.ImageDraw, box, address: str, mark_index: int | None = None) -> None:
    """開封表現を使わず、宛名面だけの大きな封筒を描く。"""
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=28, fill=WHITE, outline=PALE, width=3)

    # 左上の小さな差出人欄と右上の切手風ブロック。ロゴやサービス名は入れない。
    draw.rounded_rectangle((x1 + 28, y1 + 25, x1 + 142, y1 + 37), radius=6, fill=PALE)
    draw.rounded_rectangle((x1 + 28, y1 + 49, x1 + 112, y1 + 59), radius=5, fill=TINT)
    draw.rounded_rectangle((x2 - 78, y1 + 24, x2 - 28, y1 + 72), radius=12, fill=ORANGE_TINT)
    draw.ellipse((x2 - 63, y1 + 39, x2 - 43, y1 + 59), outline=ORANGE, width=3)

    size = 27
    label_x = x1 + 42
    baseline_y = y1 + 112
    put_text(draw, (label_x, baseline_y), "宛先", 17, GRAY, 54)
    address_x = x1 + 108

    if mark_index is None:
        put_text(draw, (address_x, baseline_y - 6), address, size, NAVY, x2 - address_x - 30)
    else:
        before = address[:mark_index]
        marked = address[mark_index]
        after = address[mark_index + 1 :]
        before_width = put_text(draw, (address_x, baseline_y - 6), before, size, NAVY, 120)
        marked_x = address_x + before_width
        marked_width = text_width(draw, marked, size)
        center_x = marked_x + marked_width / 2
        center_y = baseline_y + 9
        draw.ellipse(
            (center_x - 19, center_y - 22, center_x + 19, center_y + 20),
            outline=ORANGE,
            width=5,
        )
        put_text(draw, (marked_x, baseline_y - 6), marked, size, ORANGE, 32)
        put_text(draw, (marked_x + marked_width, baseline_y - 6), after, size, NAVY, 350)

    # 宛名面らしさを補う、文字と交差しない短い住所欄。
    rounded_line(draw, (x1 + 108, y1 + 157, x2 - 42, y1 + 157), PALE, 3)
    rounded_line(draw, (x1 + 108, y1 + 177, x2 - 108, y1 + 177), PALE, 3)


def render_header() -> Image.Image:
    image, draw = canvas(670)

    draw.rounded_rectangle((72, 176, 82, 242), radius=5, fill=ORANGE)
    put_text(draw, (100, 159), "メールが届かない原因、", 44, NAVY, 550)
    put_text(draw, (100, 219), "AIに調べさせたら僕でした", 44, NAVY, 580)
    put_text(draw, (72, 304), "「直して」より「何が起きたか」", 24, NAVY, 520)
    draw.rounded_rectangle((72, 351, 632, 355), radius=2, fill=ORANGE)

    # 宛名面を上下にずらす。左側のタイトル領域には入れない。
    envelope(draw, (680, 116, 1195, 334), "sample.app@example.com")
    envelope(draw, (732, 350, 1247, 568), "sanple.app@example.com", mark_index=2)

    return image


def draw_address_with_highlight(
    draw: ImageDraw.ImageDraw,
    xy,
    address: str,
    highlight_index: int | None,
    size: int = 36,
) -> None:
    x, y = xy
    if highlight_index is None:
        put_text(draw, (x, y), address, size, NAVY, 560, anchor="lm")
        return

    before = address[:highlight_index]
    marked = address[highlight_index]
    after = address[highlight_index + 1 :]
    before_width = text_width(draw, before, size)
    marked_width = text_width(draw, marked, size)
    total_width = before_width + marked_width + text_width(draw, after, size)
    if total_width > 560:
        raise ValueError(f"宛先文字幅超過: {address!r} {total_width}px > 560px")

    put_text(draw, (x, y), before, size, NAVY, 100, anchor="lm")
    marked_x = x + before_width
    draw.rounded_rectangle(
        (marked_x - 4, y - 25, marked_x + marked_width + 4, y + 25),
        radius=10,
        fill=ORANGE_TINT,
    )
    put_text(draw, (marked_x, y), marked, size, ORANGE, 34, anchor="lm")
    put_text(draw, (marked_x + marked_width, y), after, size, NAVY, 470, anchor="lm")


def render_send_log() -> Image.Image:
    image, draw = canvas(720)
    section_title(draw, "送信の記録（3回とも、仕組みは正常）", 42)

    cards = (
        (145, "10:15", "sample.app@example.com", None, "正常 → 確認完了"),
        (310, "10:19", "sanple.app@example.com", 2, "正常"),
        (475, "10:40", "sanple.app@example.com", 2, "正常"),
    )
    for y, time_value, address, highlight, result in cards:
        draw.rounded_rectangle((58, y, 1222, y + 140), radius=34, fill=WHITE, outline=PALE, width=2)
        put_text(draw, (88, y + 29), "時刻", 16, GRAY, 50)
        put_text(draw, (88, y + 83), time_value, 31, NAVY, 130, anchor="lm")

        put_text(draw, (292, y + 29), "宛先", 16, GRAY, 50)
        draw_address_with_highlight(draw, (292, y + 86), address, highlight, size=36)

        put_text(draw, (920, y + 29), "結果", 16, GRAY, 50)
        draw.rounded_rectangle((920, y + 59, 1184, y + 108), radius=24, fill=TINT)
        put_text(draw, (1052, y + 84), result, 21, GRAY, 230, anchor="mm")

    put_text(
        draw,
        (640, 683),
        "※アドレスはダミー。実物も1文字だけ違っていた",
        18,
        GRAY,
        560,
        anchor="mm",
    )
    return image


def speech_bubble(draw: ImageDraw.ImageDraw, box, value: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=28, fill=WHITE, outline=PALE, width=2)
    draw.polygon(((x1 + 76, y2), (x1 + 98, y2), (x1 + 84, y2 + 22)), fill=WHITE)
    draw.line((x1 + 75, y2, x1 + 84, y2 + 22), fill=PALE, width=2)
    draw.line((x1 + 84, y2 + 22, x1 + 99, y2), fill=PALE, width=2)
    put_text(draw, ((x1 + x2) / 2, (y1 + y2) / 2), value, 29, NAVY, x2 - x1 - 40, anchor="mm")


def render_request_comparison() -> Image.Image:
    image, draw = canvas(720)
    section_title(draw, "頼み方を「起きたこと」に変える", 42)

    left = (55, 145, 560, 655)
    right = (720, 145, 1225, 655)
    draw.rounded_rectangle(left, radius=42, fill=TINT, outline=PALE, width=2)
    draw.rounded_rectangle(right, radius=42, fill=WHITE, outline=NAVY, width=3)

    # 左：解決策を先に決めると、原因が外れた先で止まる。
    put_text(draw, (307, 189), "解決策で頼む", 28, GRAY, 300, anchor="mm")
    speech_bubble(draw, (100, 235, 515, 335), "再送ボタンを作って")
    put_text(draw, (307, 390), "原因を決めつけている", 19, GRAY, 270, anchor="mm")
    right_arrow(draw, (152, 458), (328, 458), color=GRAY, width=7, head=18)
    draw.rounded_rectangle((328, 424, 504, 492), radius=22, fill=PALE)
    put_text(draw, (416, 458), "外れた原因へ直行", 19, GRAY, 154, anchor="mm")
    # 行き止まりを示す縦棒。
    draw.rounded_rectangle((514, 414, 524, 502), radius=5, fill=GRAY)
    put_text(draw, (307, 574), "調べる前に、直す場所が決まる", 18, GRAY, 340, anchor="mm")

    # 中央：左から右へ考え方を切り替える大きな矢印。
    right_arrow(draw, (584, 401), (696, 401), color=ORANGE, width=12, head=26)

    # 右：起きたことを3点で渡し、記録の確認から始める。
    draw.rounded_rectangle((748, 165, 1197, 219), radius=27, fill=NAVY)
    put_text(draw, (972, 192), "起きたことを渡す", 28, WHITE, 330, anchor="mm")

    items = (
        ("①", "何が起きたか"),
        ("②", "本当はどうなるはずか"),
        ("③", "何を試したか"),
    )
    for index, (number, value) in enumerate(items):
        y = 268 + index * 76
        draw.ellipse((767, y - 23, 813, y + 23), fill=ORANGE_TINT)
        put_text(draw, (790, y), number, 21, ORANGE, 30, anchor="mm")
        put_text(draw, (832, y), value, 24, NAVY, 325, anchor="lm")

    right_arrow(draw, (818, 493), (1128, 493), color=ORANGE, width=7, head=18)
    draw.rounded_rectangle((790, 527, 1168, 601), radius=28, fill=NAVY)
    put_text(draw, (979, 564), "記録を確かめてから直す", 23, WHITE, 330, anchor="mm")

    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = (
        ("mail_0_ヘッダー.png", render_header, (1280, 670)),
        ("mail_1_送信記録.png", render_send_log, (1280, 720)),
        ("mail_2_頼み方の前後.png", render_request_comparison, (1280, 720)),
    )
    expected_names = {name for name, _, _ in outputs}

    # 指定フォルダには最終成果物3枚だけを残す。
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
