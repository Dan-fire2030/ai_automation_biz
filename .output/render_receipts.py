# -*- coding: utf-8 -*-
"""ダミーレシート4枚を生成する（note 8本目・経費精算のレシート読み取り）。

架空の店・架空の金額のみ。実在の企業・商標は使わない。
金額の検算は .output/demo_レシート読み取り/正解表.md と一致していること。
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

OUT_DIR = Path(__file__).resolve().parent / "demo_レシート読み取り"

PAPER = (250, 250, 248)
INK = (43, 43, 43)
FAINT = (120, 120, 118)
SEAL = (192, 57, 43)


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def text_size(draw, text, f):
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0], box[3] - box[1]


def draw_dashes(draw, y, left, right, color=FAINT):
    x = left
    while x < right:
        draw.line([(x, y), (min(x + 8, right), y)], fill=color, width=1)
        x += 14


# --------------------------------------------------------------------------
# 感熱紙レシート（1・3・4枚目）
# --------------------------------------------------------------------------
def render_thermal(rows, size, out_path):
    img = Image.new("RGB", size, PAPER)
    draw = ImageDraw.Draw(img)
    left, right = 48, size[0] - 48
    y = 70

    for row in rows:
        kind = row[0]
        if kind == "gap":
            y += row[1]
        elif kind == "sep":
            draw_dashes(draw, y + 8, left, right)
            y += 26
        elif kind == "center":
            _, text, fs, bold = row
            f = font(fs, bold)
            w, _h = text_size(draw, text, f)
            draw.text(((size[0] - w) / 2, y), text, font=f, fill=INK)
            y += fs + 12
        elif kind == "left":
            _, text, fs, bold = row
            draw.text((left, y), text, font=font(fs, bold), fill=INK)
            y += fs + 12
        elif kind == "lr":
            _, ltext, rtext, fs, bold = row
            f = font(fs, bold)
            draw.text((left, y), ltext, font=f, fill=INK)
            w, _h = text_size(draw, rtext, f)
            draw.text((right - w, y), rtext, font=f, fill=INK)
            y += fs + 12

    img.save(out_path)
    return y


ROWS_1 = [
    ("center", "フジヤマ商店 新川店", 38, True),
    ("center", "東京都新川3-2-1  TEL 03-XXXX-XXXX", 22, False),
    ("gap", 14),
    ("left", "2026年9月3日(木) 14:22   レジNo.03", 24, False),
    ("sep",),
    ("lr", "菓子折 詰合せ ※", "1,200", 28, False),
    ("lr", "緑茶ティーバッグ ※", "500", 28, False),
    ("lr", "コピー用紙A4 500枚", "620", 28, False),
    ("lr", "油性ボールペン 3本", "280", 28, False),
    ("sep",),
    ("lr", "小計", "2,600", 28, False),
    ("lr", "  8%対象  1,700  消費税", "136", 24, False),
    ("lr", "  10%対象   900  消費税", "90", 24, False),
    ("gap", 6),
    ("lr", "合計", "2,826", 34, True),
    ("sep",),
    ("lr", "お預かり", "3,000", 28, False),
    ("lr", "お釣り", "174", 28, False),
    ("gap", 20),
    ("left", "※印は軽減税率対象商品", 22, False),
]

ROWS_3 = [
    ("center", "カフェ・ノルド 駅前店", 38, True),
    ("center", "東京都新川1-1-9  TEL 03-XXXX-XXXX", 22, False),
    ("gap", 14),
    ("left", "2026年9月5日(金) 16:08", 24, False),
    ("sep",),
    ("lr", "ブレンドコーヒー  ×2", "960", 28, False),
    ("lr", "サンドイッチ      ×1", "680", 28, False),
    ("sep",),
    ("lr", "小計", "1,640", 28, False),
    ("lr", "ポイント値引き", "-200", 28, False),
    ("gap", 6),
    ("lr", "合計", "1,440", 34, True),
    ("left", "  (内 10%対象 1,440 消費税 130)", 24, False),
    ("sep",),
    ("lr", "お預かり", "2,000", 28, False),
    ("lr", "お釣り", "560", 28, False),
]

ROWS_4 = [
    ("center", "ミドリ電機 新川店", 38, True),
    ("center", "東京都新川5-4-2  TEL 03-XXXX-XXXX", 22, False),
    ("gap", 14),
    ("left", "2026年9月8日(火) 11:35", 24, False),
    ("sep",),
    ("lr", "USBメモリ 32GB  ×1", "1,980", 28, False),
    ("sep",),
    ("lr", "小計", "1,980", 28, False),
    ("lr", "消費税(10%)", "198", 28, False),
    ("gap", 6),
    ("lr", "合計", "2,178", 34, True),
    ("sep",),
    ("lr", "クレジット", "2,178", 28, False),
]


# --------------------------------------------------------------------------
# 手書き領収書（2枚目）
# --------------------------------------------------------------------------
def paste_slanted(base, text, f, xy, fill, angle=-2.0):
    """手書きらしく見せるため、わずかに傾けて貼る。"""
    tmp = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text(xy, text, font=f, fill=fill)
    base.alpha_composite(tmp.rotate(angle, resample=Image.BICUBIC, center=xy))


def render_receipt_2(out_path):
    size = (1200, 760)
    img = Image.new("RGBA", size, PAPER + (255,))
    draw = ImageDraw.Draw(img)

    # 外枠
    draw.rectangle([40, 40, size[0] - 40, size[1] - 40], outline=(150, 150, 148), width=2)

    # 表題
    f_title = font(52, True)
    w, _ = text_size(draw, "領 収 証", f_title)
    draw.text(((size[0] - w) / 2, 80), "領 収 証", font=f_title, fill=INK)

    # 日付（右上）
    f_small = font(26)
    date = "2026年9月5日"
    w, _ = text_size(draw, date, f_small)
    draw.text((size[0] - 90 - w, 100), date, font=f_small, fill=INK)

    # 宛名
    draw.text((90, 190), "マルシン工業 御中", font=font(34), fill=INK)
    draw.line([(88, 236), (520, 236)], fill=(170, 170, 168), width=1)

    # 金額欄
    draw.rectangle([88, 270, 760, 366], outline=(170, 170, 168), width=1)
    draw.text((110, 300), "金", font=font(32), fill=INK)
    paste_slanted(img, "￥8,000 −", font(52, True), (190, 288), INK)

    # 但し書き
    draw.text((110, 410), "但し", font=font(30), fill=INK)
    paste_slanted(img, "お品代", font(40), (190, 400), INK)
    draw.text((360, 410), "として", font=font(30), fill=INK)
    draw.line([(186, 458), (350, 458)], fill=(170, 170, 168), width=1)

    draw.text((110, 486), "上記正に領収いたしました", font=font(28), fill=INK)

    # 発行者
    draw.text((760, 560), "割烹 みなと", font=font(32, True), fill=INK)
    draw.text((760, 610), "東京都新川2-8-4", font=font(22), fill=FAINT)
    draw.text((760, 644), "TEL 03-XXXX-XXXX", font=font(22), fill=FAINT)

    # 角印風
    cx, cy, r = 1075, 618, 52
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=SEAL, width=3)
    f_seal = font(26, True)
    w, h = text_size(draw, "みなと", f_seal)
    draw.text((cx - w / 2, cy - h / 2 - 4), "みなと", font=f_seal, fill=SEAL)

    img.convert("RGB").save(out_path)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    render_thermal(ROWS_1, (720, 800), OUT_DIR / "receipt_1_フジヤマ商店.png")
    render_receipt_2(OUT_DIR / "receipt_2_割烹みなと.png")
    render_thermal(ROWS_3, (720, 660), OUT_DIR / "receipt_3_カフェノルド.png")
    render_thermal(ROWS_4, (720, 560), OUT_DIR / "receipt_4_ミドリ電機.png")
    print("done")


if __name__ == "__main__":
    main()
