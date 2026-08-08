from pathlib import Path
import math

from PIL import Image, ImageCms, ImageDraw, ImageFont


OUT = Path(
    "/Users/haruto/Documents/起業/ai-automation-biz/"
    "note/images/2026-08-01/knowhow13_1_浮いた時間の行き先.png"
)

NAVY = "#12305C"
GROUND = "#F4F8FC"
WHITE = "#FFFFFF"
GRAY = "#5A6675"
ORANGE = "#D9772F"

FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"
FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

if not Path(FONT_HEAVY).exists():
    FONT_HEAVY = FONT_BOLD


def font(size: int, weight: str = "bold") -> ImageFont.FreeTypeFont:
    path = {
        "heavy": FONT_HEAVY,
        "bold": FONT_BOLD,
        "regular": FONT_REGULAR,
    }[weight]
    return ImageFont.truetype(path, size)


def text_size(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont):
    box = draw.textbbox((0, 0), text, font=text_font)
    return box[2] - box[0], box[3] - box[1]


def centered(draw, text, center_x, y, text_font, fill):
    width, _ = text_size(draw, text, text_font)
    draw.text((center_x - width / 2, y), text, font=text_font, fill=fill)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(
        box, radius=radius, fill=fill, outline=outline, width=width
    )


def arrow(draw, start, end, color=NAVY, width=10, head=22):
    draw.line([start, end], fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    for delta in (2.55, -2.55):
        point = (
            end[0] + head * math.cos(angle + delta),
            end[1] + head * math.sin(angle + delta),
        )
        draw.line([end, point], fill=color, width=width)


def make_cycle():
    image = Image.new("RGB", (1200, 800), GROUND)
    draw = ImageDraw.Draw(image)

    centered(draw, "浮いた時間の行き先", 600, 35, font(58, "heavy"), NAVY)

    # 矢印はカードより先に描画する。2本目だけ、矢尻がオレンジカードの
    # 上辺（y=385）に隠れないよう終点を y=376 に置く。
    arrow(draw, (450, 238), (745, 238), NAVY, 9, 24)
    arrow(draw, (960, 322), (878, 376), NAVY, 9, 24)
    arrow(draw, (360, 450), (225, 320), NAVY, 9, 24)

    cards = [
        ((65, 155, 445, 315), NAVY, "AIに頼む", "下書き・情報の整理"),
        ((755, 155, 1135, 315), NAVY, "作業が減る", "時間が浮く"),
        (
            (300, 385, 900, 555),
            ORANGE,
            "浮いた時間で新機能を触る",
            "スクショを撮って、次の機能へ",
        ),
    ]

    for box, color, heading, description in cards:
        rounded(draw, box, 22, WHITE, color, 3)
        heading_size = 42 if len(heading) <= 8 else 39
        centered(
            draw,
            heading,
            (box[0] + box[2]) / 2,
            box[1] + 27,
            font(heading_size, "heavy"),
            color,
        )
        centered(
            draw,
            description,
            (box[0] + box[2]) / 2,
            box[1] + 94,
            font(28, "regular"),
            GRAY,
        )

    rounded(draw, (70, 600, 1130, 680), 22, NAVY)
    centered(
        draw,
        "AIで浮かせた時間を、そのままAIに返していた",
        600,
        614,
        font(44, "heavy"),
        WHITE,
    )
    centered(
        draw,
        "差し引きゼロどころか、触った分だけマイナス",
        600,
        703,
        font(34, "bold"),
        ORANGE,
    )

    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    image.save(OUT, "PNG", icc_profile=srgb, dpi=(144, 144), optimize=True)


if __name__ == "__main__":
    make_cycle()
