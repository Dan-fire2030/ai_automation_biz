"""note記事「AIの議事録がきれいすぎて確かめられない」の画像4枚を生成する。

直前記事 render_awareness01.py の配色・書体・カード・余白を継承する。
日本語と図形をすべてPillowで決定的に描画し、あとから微修正できる形で残す。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "note" / "images" / "2026-08-26"

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


def assert_fits(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, max_width: int) -> None:
    actual = width_of(draw, text, f)
    if actual > max_width:
        raise ValueError(f"Text exceeds width: {text!r} ({actual}px > {max_width}px)")


def centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    center_x: float,
    y: float,
    f: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
) -> None:
    draw.text((center_x - width_of(draw, text, f) / 2, y), text, font=f, fill=fill)


def new_canvas(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), BG)
    return image, ImageDraw.Draw(image)


def draw_title(draw: ImageDraw.ImageDraw, title: str) -> None:
    draw.rounded_rectangle([60, 60, 68, 110], radius=4, fill=ORANGE)
    title_font = font(38, "heavy")
    assert_fits(draw, title, title_font, 1100)
    draw.text((88, 56), title, font=title_font, fill=NAVY)


def draw_speech_bubble(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=13, fill=CARD, outline=NAVY, width=3)
    tail_y = y1 + 36
    draw.polygon([(x2 - 2, tail_y - 9), (x2 + 15, tail_y), (x2 - 2, tail_y + 9)], fill=CARD)
    draw.line([(x2 - 1, tail_y - 9), (x2 + 15, tail_y), (x2 - 1, tail_y + 9)], fill=NAVY, width=3)
    draw.rounded_rectangle([x1 + 18, y1 + 19, x2 - 24, y1 + 29], radius=5, fill=TINT)
    draw.rounded_rectangle([x1 + 18, y1 + 40, x2 - 50, y1 + 50], radius=5, fill=TINT)


def draw_header_motif(draw: ImageDraw.ImageDraw) -> None:
    """吹き出し3つと議事録4行を対応させ、未接続の1行だけ強調する。"""
    bubbles = (
        (784, 154, 914, 218),
        (784, 266, 914, 330),
        (784, 378, 914, 442),
    )
    for bubble in bubbles:
        draw_speech_bubble(draw, bubble)

    paper = (1014, 132, 1206, 478)
    draw.rounded_rectangle(paper, radius=16, fill=CARD, outline=NAVY, width=4)
    draw.rounded_rectangle([1050, 166, 1168, 179], radius=6, fill=NAVY)
    draw.line([(1040, 201), (1180, 201)], fill=BORDER, width=2)

    row_centers = (239, 304, 369, 434)
    for index, cy in enumerate(row_centers):
        if index == 2:
            draw.rounded_rectangle([1035, cy - 20, 1185, cy + 20], radius=9, outline=ORANGE, width=3)
            draw.rounded_rectangle([1052, cy - 6, 1168, cy + 6], radius=6, fill=ORANGE)
        else:
            draw.rounded_rectangle([1052, cy - 6, 1168, cy + 6], radius=6, fill=TINT)

    # 対応線は行の外側で折り、互いに交差させない。
    line_specs = (
        ((929, 190), (970, 190), (970, 239), (1010, 239)),
        ((929, 302), (982, 302), (982, 304), (1010, 304)),
        ((929, 414), (970, 414), (970, 434), (1010, 434)),
    )
    for points in line_specs:
        draw.line(points, fill=NAVY, width=3, joint="curve")
        ex, ey = points[-1]
        draw.polygon([(ex, ey), (ex - 11, ey - 6), (ex - 11, ey + 6)], fill=NAVY)


def render_header() -> Image.Image:
    image, draw = new_canvas(1280, 670)
    left = 92
    draw.rounded_rectangle([left, 178, left + 8, 246], radius=4, fill=ORANGE)
    title_font = font(46, "heavy")
    line1 = "AIの議事録が"
    line2 = "きれいすぎて確かめられない"
    assert_fits(draw, line1, title_font, 655)
    assert_fits(draw, line2, title_font, 655)
    draw.text((left + 30, 169), line1, font=title_font, fill=NAVY)
    draw.text((left + 30, 239), line2, font=title_font, fill=NAVY)
    draw.line([(left, 366), (left + 650, 366)], fill=BORDER, width=2)

    subcopy = "要約ではなく「言った通り」を抜き書きさせる"
    subcopy_font = font(27, "bold")
    assert_fits(draw, subcopy, subcopy_font, 670)
    draw.text((left, 398), subcopy, font=subcopy_font, fill=ORANGE)

    reader = "中小企業のバックオフィスと、ひとり社長のためのAI活用"
    reader_font = font(20)
    assert_fits(draw, reader, reader_font, 650)
    draw.text((left, 452), reader, font=reader_font, fill=GRAY)
    draw_header_motif(draw)
    return image


def draw_transcript_line(
    draw: ImageDraw.ImageDraw,
    y: int,
    speaker: str,
    utterance: str,
    indent: bool = False,
) -> None:
    speaker_font = font(27, "bold")
    body_font = font(27)
    if indent:
        assert_fits(draw, utterance, body_font, 1020)
        draw.text((190, y), utterance, font=body_font, fill=INK)
        return
    draw.text((120, y), speaker, font=speaker_font, fill=NAVY)
    body_x = 120 + width_of(draw, speaker, speaker_font) + 12
    assert_fits(draw, utterance, body_font, 1110 - body_x)
    draw.text((body_x, y), utterance, font=body_font, fill=INK)


def render_transcript() -> Image.Image:
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "文字起こし（全部ダミーです）")
    draw.rounded_rectangle([60, 138, 1220, 650], radius=18, fill=CARD, outline=BORDER, width=2)

    draw_transcript_line(draw, 178, "山田：", "まあねえ。じゃあ、あの、いきなり全部切り替えるんじゃなくて、")
    draw_transcript_line(draw, 218, "", "まずどんなもんか調べましょうか。", indent=True)
    draw_transcript_line(draw, 278, "佐藤：", "分かりました。")
    draw_transcript_line(draw, 338, "山田：", "うん、入れる方向では考えたいんですけどね。")
    draw_transcript_line(draw, 378, "", "ただ現場が回らないと意味ないので。", indent=True)
    draw_transcript_line(draw, 438, "田中：", "資料って誰が集めます？")
    draw_transcript_line(draw, 498, "山田：", "あー、まあ誰か見といてもらって。")

    note = "※ 架空の会社・架空の会議です"
    note_font = font(19)
    note_x = 1180 - width_of(draw, note, note_font)
    draw.text((note_x, 605), note, font=note_font, fill=GRAY)
    return image


def render_plain_minutes() -> Image.Image:
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "素で「議事録にして」と頼んだ結果")
    draw.rounded_rectangle([60, 138, 1220, 607], radius=18, fill=CARD, outline=BORDER, width=2)

    draw.text((105, 176), "決定事項", font=font(32, "heavy"), fill=NAVY)
    draw.line([(105, 224), (1175, 224)], fill=BORDER, width=2)

    item_font = font(27)
    line1 = "・支払日を翌月10日 → 15日に変更（9月末締め分から）"
    assert_fits(draw, line1, item_font, 1050)
    draw.text((105, 258), line1, font=item_font, fill=INK)

    prefix = "・勤怠システムは "
    highlight = "導入を前提に"
    suffix = "、まず各社の資料を集めて比較検討する"
    full = prefix + highlight + suffix
    assert_fits(draw, full, item_font, 1050)
    y = 326
    draw.text((105, y), prefix, font=item_font, fill=INK)
    hx = 105 + width_of(draw, prefix, item_font)
    hw = width_of(draw, highlight, item_font)
    draw.rounded_rectangle([hx - 5, y - 3, hx + hw + 5, y + 38], radius=6, fill=ORANGE_TINT)
    draw.text((hx, y), highlight, font=item_font, fill=ORANGE)
    draw.text((hx + hw, y), suffix, font=item_font, fill=INK)

    line3 = "・2階エアコンの業者を手配する"
    draw.text((105, 394), line3, font=item_font, fill=INK)

    # ハイライト直下の行間を右へ通し、本文の右外側で吹き出しへ下ろす。
    anchor_x = hx + hw / 2
    elbow_y = 376
    bubble_tip_x, bubble_tip_y = 902, 466
    draw.line(
        [
            (anchor_x, y + 38),
            (anchor_x, elbow_y),
            (bubble_tip_x, elbow_y),
            (bubble_tip_x, bubble_tip_y),
        ],
        fill=ORANGE,
        width=3,
        joint="curve",
    )
    draw.ellipse([anchor_x - 5, y + 33, anchor_x + 5, y + 43], fill=ORANGE)
    bubble = (780, 482, 1020, 548)
    draw.rounded_rectangle(bubble, radius=14, fill=CARD, outline=ORANGE, width=3)
    draw.polygon([(888, 482), (902, 466), (916, 482)], fill=CARD)
    draw.line([(888, 482), (902, 466), (916, 482)], fill=ORANGE, width=3)
    centered(draw, "誰も言っていない", 900, 497, font(23, "bold"), INK)

    footer = "他にも「9月中目安」「次回月次まで」「例年」など、発言にない語が3か所"
    footer_font = font(21)
    assert_fits(draw, footer, footer_font, 1160)
    draw.text((60, 641), footer, font=footer_font, fill=GRAY)
    return image


ROWS = (
    ("資料集めの担当", "発言なし"),
    ("支払日変更の案内の期限", "発言なし"),
    ("勤怠システムの導入時期", "発言なし"),
    ("健康診断の今年の実施日", "発言なし"),
    ("支払日の開始時期", "9月末締め分から"),
)


def render_extract_minutes() -> Image.Image:
    image, draw = new_canvas(1280, 720)
    draw_title(draw, "「要約しないでください」と足した結果")
    draw.rounded_rectangle([60, 138, 1220, 650], radius=18, fill=CARD, outline=BORDER, width=2)

    table_x1, table_x2 = 92, 825
    row_top, row_h = 174, 78
    label_font = font(25)
    value_font = font(25, "bold")
    for index, (label, value) in enumerate(ROWS):
        y1 = row_top + index * row_h
        y2 = y1 + row_h - 8
        if value == "発言なし":
            draw.rounded_rectangle([table_x1, y1, table_x2, y2], radius=10, fill=ORANGE_TINT)
        if index:
            draw.line([(table_x1 + 14, y1 - 4), (table_x2 - 14, y1 - 4)], fill=BORDER, width=2)
        draw.text((116, y1 + 18), label, font=label_font, fill=INK)
        value_color = ORANGE if value == "発言なし" else INK
        draw.text((590, y1 + 18), value, font=value_font, fill=value_color)

    draw.line([(858, 182), (858, 596)], fill=BORDER, width=2)
    count_font = font(92, "heavy")
    count_x, count_y = 918, 274
    draw.text((count_x, count_y), "18", font=count_font, fill=ORANGE)
    unit_x = count_x + width_of(draw, "18", count_font) + 12
    draw.text((unit_x, count_y + 55), "か所", font=font(27, "bold"), fill=NAVY)
    centered(draw, "「発言なし」が", 1038, 402, font(21), GRAY)
    centered(draw, "出てきた数", 1038, 438, font(21), GRAY)
    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = (
        ("minutes_0_ヘッダー.png", render_header()),
        ("minutes_1_文字起こし.png", render_transcript()),
        ("minutes_2_素で頼んだ版.png", render_plain_minutes()),
        ("minutes_3_抜き書き版.png", render_extract_minutes()),
    )
    for name, image in pages:
        path = OUTPUT_DIR / name
        image.save(path, format="PNG")
        print(f"saved: {path}  {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
