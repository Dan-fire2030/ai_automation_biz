"""note記事「全部OK、は たまたまだった」用のPNG画像を3枚生成する。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "note" / "images" / "2026-09-25"
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
    r = width // 2
    draw.ellipse((x1 - r, y1 - r, x1 + r, y1 + r), fill=fill)
    draw.ellipse((x2 - r, y2 - r, x2 + r, y2 + r), fill=fill)


def arrow(draw: ImageDraw.ImageDraw, start, end, color=ORANGE, width: int = 8, head: int = 18) -> None:
    x1, y1 = start
    x2, y2 = end
    # 今回は横・縦・斜めの短い接続線だけなので、線分末端に三角を置く。
    import math

    angle = math.atan2(y2 - y1, x2 - x1)
    bx = x2 - head * math.cos(angle)
    by = y2 - head * math.sin(angle)
    rounded_line(draw, (x1, y1, bx, by), color, width)
    spread = head * 0.7
    left = (bx + spread * math.sin(angle), by - spread * math.cos(angle))
    right = (bx - spread * math.sin(angle), by + spread * math.cos(angle))
    draw.polygon((left, (x2, y2), right), fill=color)


def check_mark(draw: ImageDraw.ImageDraw, center, color=GREEN, alpha: int = 255, scale: float = 1.0) -> None:
    cx, cy = center
    points = (
        (cx - 31 * scale, cy - 1 * scale),
        (cx - 8 * scale, cy + 22 * scale),
        (cx + 37 * scale, cy - 29 * scale),
    )
    draw.line(points, fill=(*color, alpha), width=max(4, int(11 * scale)), joint="curve")


def cross_mark(draw: ImageDraw.ImageDraw, center, color=ORANGE, alpha: int = 255, scale: float = 1.0) -> None:
    cx, cy = center
    d = 27 * scale
    w = max(4, int(9 * scale))
    draw.line((cx - d, cy - d, cx + d, cy + d), fill=(*color, alpha), width=w)
    draw.line((cx + d, cy - d, cx - d, cy + d), fill=(*color, alpha), width=w)


def render_header() -> Image.Image:
    image, draw = canvas(670)

    draw.rounded_rectangle((72, 170, 82, 242), radius=5, fill=ORANGE)
    put_text(draw, (100, 154), "全部OK、は", 52, NAVY, 470)
    put_text(draw, (100, 222), "たまたまだった", 52, NAVY, 520)
    put_text(draw, (72, 318), "3回に1回だけ引っかかる確認の直し方", 24, NAVY, 560)
    draw.rounded_rectangle((72, 366, 632, 370), radius=2, fill=ORANGE)

    xs = (742, 925, 1108)
    for index, x in enumerate(xs):
        draw.rounded_rectangle((x - 70, 214, x + 70, 354), radius=34, fill=WHITE, outline=PALE, width=3)
        draw.rounded_rectangle((x - 36, 248, x + 36, 320), radius=18, fill=GREEN_TINT, outline=GREEN, width=3)
        if index < 2:
            check_mark(draw, (x, 284), GREEN, 255, 0.72)
        else:
            # 判定が揺れる様子を、半透明のずれた記号と短い揺れ線で示す。
            check_mark(draw, (x - 7, 284), GREEN, 125, 0.72)
            cross_mark(draw, (x + 8, 284), ORANGE, 120, 0.72)
            for offset in (-1, 1):
                yy = 258 + (offset + 1) * 26
                draw.arc((x + 47, yy - 13, x + 79, yy + 13), 250, 110, fill=(*GRAY, 150), width=3)
    put_text(draw, (925, 414), "3つのうち、最後だけ判定が揺れた", 22, GRAY, 460, anchor="mm")

    return image


def render_suspects() -> Image.Image:
    image, draw = canvas(720)
    section_title(draw, "疑った相手と、本当の相手", 42)

    left = (45, 210, 360, 570)
    center = (420, 184, 780, 596)
    right = (840, 160, 1235, 620)
    draw.rounded_rectangle(left, radius=34, fill=TINT, outline=PALE, width=2)
    draw.rounded_rectangle(center, radius=38, fill=WHITE, outline=NAVY, width=3)
    draw.rounded_rectangle(right, radius=38, fill=WHITE, outline=GREEN, width=3)

    put_text(draw, (202, 258), "疑った相手", 25, GRAY, 230, anchor="mm")
    put_text(draw, (202, 302), "ほかの確認", 32, NAVY, 240, anchor="mm")
    cross_mark(draw, (202, 382), ORANGE, 255, 0.82)
    put_text(draw, (202, 474), "ぶつかって", 22, GRAY, 220, anchor="mm")
    put_text(draw, (202, 510), "いなかった", 22, GRAY, 220, anchor="mm")

    draw.rounded_rectangle((452, 214, 748, 272), radius=28, fill=NAVY)
    put_text(draw, (600, 243), "確認（数えている係）", 24, WHITE, 270, anchor="mm")
    draw.rounded_rectangle((472, 334, 728, 450), radius=28, fill=ORANGE_TINT)
    put_text(draw, (600, 392), "2回のはずが3回？", 30, ORANGE, 252, anchor="mm")
    put_text(draw, (600, 526), "数だけを見ると、原因を取り違える", 18, GRAY, 300, anchor="mm")

    put_text(draw, (1037, 211), "本当の相手", 25, GREEN, 270, anchor="mm")
    put_text(draw, (1037, 260), "裏で動いていた", 29, NAVY, 310, anchor="mm")
    put_text(draw, (1037, 302), "アプリ本体", 29, NAVY, 310, anchor="mm")
    draw.ellipse((1007, 342, 1067, 402), fill=GREEN_TINT, outline=GREEN, width=3)
    check_mark(draw, (1037, 372), GREEN, 255, 0.55)
    put_text(draw, (1037, 455), "いつもどおりの仕事が、", 21, INK, 330, anchor="mm")
    put_text(draw, (1037, 492), "確認の最中に届いた", 21, INK, 330, anchor="mm")

    # 左は否定された仮説なので薄い点線、右は中央へ割り込む太い矢印。
    for x in range(360, 410, 15):
        draw.line((x, 392, min(x + 8, 410), 392), fill=(*GRAY, 90), width=4)
    arrow(draw, (858, 392), (792, 392), color=GREEN, width=10, head=22)
    put_text(draw, (823, 350), "割り込み", 17, GREEN, 76, anchor="mm")

    return image


def render_fork() -> Image.Image:
    image, draw = canvas(720)
    section_title(draw, "直す前の分かれ道", 42)

    draw.rounded_rectangle((522, 134, 758, 194), radius=30, fill=ORANGE_TINT)
    put_text(draw, (640, 164), "引っかかった", 28, ORANGE, 200, anchor="mm")
    rounded_line(draw, (640, 194, 640, 222), ORANGE, 6)

    draw.rounded_rectangle((410, 222, 870, 302), radius=28, fill=NAVY)
    put_text(draw, (640, 262), "白黒がつく確認を1つ足す", 28, WHITE, 400, anchor="mm")

    # 分岐。線はカードの外で止め、矢印だけを最後にカードへ向ける。
    rounded_line(draw, (640, 302, 640, 336), PALE, 8)
    rounded_line(draw, (640, 336, 330, 336), PALE, 8)
    rounded_line(draw, (640, 336, 950, 336), GREEN, 8)
    arrow(draw, (330, 336), (330, 378), color=GRAY, width=8, head=18)
    arrow(draw, (950, 336), (950, 378), color=GREEN, width=8, head=18)

    left = (85, 378, 575, 652)
    right = (705, 378, 1195, 652)
    draw.rounded_rectangle(left, radius=38, fill=WHITE, outline=PALE, width=3)
    draw.rounded_rectangle(right, radius=38, fill=WHITE, outline=GREEN, width=3)

    put_text(draw, (330, 430), "中身（仕事）を直す", 30, NAVY, 390, anchor="mm")
    cross_mark(draw, (330, 500), ORANGE, 255, 0.72)
    draw.rounded_rectangle((138, 548, 522, 614), radius=28, fill=ORANGE_TINT)
    put_text(draw, (330, 581), "正しく動いていたものを壊す", 22, ORANGE, 340, anchor="mm")

    put_text(draw, (950, 430), "確かめ方を直す", 30, NAVY, 390, anchor="mm")
    check_mark(draw, (950, 500), GREEN, 255, 0.72)
    draw.rounded_rectangle((758, 548, 1142, 614), radius=28, fill=GREEN_TINT)
    put_text(draw, (950, 581), "6回続けて通った", 24, GREEN, 330, anchor="mm")

    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = (
        ("allok_0_ヘッダー.png", render_header, (1280, 670)),
        ("allok_1_疑った相手.png", render_suspects, (1280, 720)),
        ("allok_2_直す前の分かれ道.png", render_fork, (1280, 720)),
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
