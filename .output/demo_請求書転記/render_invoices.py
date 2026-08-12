"""note新シリーズ1本目「請求書の転記」用のダミー請求書を3枚生成する。

すべて架空の会社・架空の金額。実在の取引先・実データは1件も使わない。

3枚はわざとレイアウトと表記を変えてある（実務では取引先ごとにバラバラなため）。
記事の主題「金額を間違えられたらどう確かめるか」が成立するよう、
人間もAIも引っかかる箇所を意図的に仕込んでいる：

  1. ミナトデザイン … 税込総額のみ表示。西暦。素直な1枚
  2. カワセ工材     … 値引き行あり（合計を再計算すると見落とす）。小計/消費税/合計の3段
  3. サクラ配送     … 税抜表記＋消費税別記。和暦。桁が1つ大きい

出力：同ディレクトリの invoices/請求書0N_〇〇.pdf
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "invoices"

# A4相当（150dpi）
PAGE_W, PAGE_H = 1240, 1754

FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

INK = (34, 34, 34)
GRAY = (110, 110, 110)
LINE = (170, 170, 170)
LIGHT = (238, 238, 238)


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if weight == "bold" else FONT_REGULAR
    return ImageFont.truetype(path, size)


def new_page() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    return image, ImageDraw.Draw(image)


def width_of(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=text_font)
    return box[2] - box[0]


def right_text(draw, text, right_x, y, text_font, fill=INK) -> None:
    draw.text((right_x - width_of(draw, text, text_font), y), text, font=text_font, fill=fill)


def center_text(draw, text, center_x, y, text_font, fill=INK) -> None:
    draw.text((center_x - width_of(draw, text, text_font) / 2, y), text, font=text_font, fill=fill)


def yen(value: int) -> str:
    return f"¥{value:,}"


# ---------------------------------------------------------------- 請求書1

def render_minato() -> Image.Image:
    """株式会社ミナトデザイン：税込総額のみ・西暦・素直なレイアウト。"""
    image, draw = new_page()
    left, right = 100, PAGE_W - 100

    qty_x, unit_x, amount_x = left + 660, left + 860, right - 16

    center_text(draw, "請 求 書", PAGE_W / 2, 110, font(52, "bold"))

    right_text(draw, "請求日：2026年7月31日", right, 200, font(24), GRAY)
    right_text(draw, "請求書番号：MD-2026-0731", right, 238, font(24), GRAY)

    # 発行元
    right_text(draw, "株式会社ミナトデザイン", right, 296, font(28, "bold"))
    right_text(draw, "〒231-0023 横浜市中区山下町5-1", right, 340, font(20), GRAY)
    right_text(draw, "TEL 045-000-0000", right, 372, font(20), GRAY)
    right_text(draw, "登録番号 T0000000000000", right, 404, font(20), GRAY)

    draw.text((left, 300), "サンライズ商事 株式会社  御中", font=font(32, "bold"), fill=INK)
    draw.line([(left, 352), (left + 520, 352)], fill=INK, width=2)

    draw.text((left, 420), "下記のとおりご請求申し上げます。", font=font(24), fill=INK)

    # 請求金額（税込のみ）
    draw.rectangle([left, 470, left + 620, 560], fill=LIGHT)
    draw.text((left + 24, 502), "ご請求金額（税込）", font=font(26, "bold"), fill=INK)
    right_text(draw, "¥264,000", left + 596, 490, font(40, "bold"))

    # 明細
    top = 650
    draw.rectangle([left, top, right, top + 52], fill=LIGHT)
    draw.text((left + 16, top + 14), "品目", font=font(24, "bold"), fill=INK)
    right_text(draw, "数量", qty_x, top + 14, font(24, "bold"))
    right_text(draw, "単価", unit_x, top + 14, font(24, "bold"))
    right_text(draw, "金額", amount_x, top + 14, font(24, "bold"))

    rows = (
        ("コーポレートサイト リニューアル", "1式", 180000, 180000),
        ("バナー制作（5点）", "5点", 8000, 40000),
        ("撮影ディレクション費", "1式", 20000, 20000),
    )
    y = top + 52
    for name, qty, unit, amount in rows:
        draw.line([(left, y), (right, y)], fill=LINE, width=1)
        draw.text((left + 16, y + 16), name, font=font(24), fill=INK)
        right_text(draw, qty, qty_x, y + 16, font(24))
        right_text(draw, yen(unit), unit_x, y + 16, font(24))
        right_text(draw, yen(amount), amount_x, y + 16, font(24))
        y += 62

    draw.line([(left, y), (right, y)], fill=LINE, width=1)
    y += 34
    for label, value, bold in (("小計", 240000, False), ("消費税（10%）", 24000, False), ("合計", 264000, True)):
        weight = "bold" if bold else "regular"
        right_text(draw, label, unit_x, y, font(24, weight))
        right_text(draw, yen(value), amount_x, y, font(26 if bold else 24, weight))
        if bold:
            draw.line([(unit_x - 200, y - 12), (amount_x, y - 12)], fill=INK, width=2)
        y += 48

    draw.text((left, y + 60), "お支払期限：2026年8月31日", font=font(26, "bold"), fill=INK)
    draw.text((left, y + 106), "お振込先：みなと銀行 山下町支店 普通 1234567 カ）ミナトデザイン", font=font(22), fill=INK)
    draw.text((left, y + 146), "※振込手数料は御社にてご負担をお願いいたします。", font=font(20), fill=GRAY)
    return image


# ---------------------------------------------------------------- 請求書2

def render_kawase() -> Image.Image:
    """有限会社カワセ工材：値引き行あり・「発行日」「支払期日」表記・罫線多め。"""
    image, draw = new_page()
    left, right = 90, PAGE_W - 90

    draw.rectangle([left, 90, right, 170], outline=INK, width=3)
    center_text(draw, "御 請 求 書", PAGE_W / 2, 108, font(46, "bold"))

    draw.text((left, 210), "発行日  2026/07/28", font=font(24), fill=INK)
    draw.text((left, 250), "請求No.  K-4471", font=font(24), fill=INK)

    right_text(draw, "有限会社カワセ工材", right, 200, font(28, "bold"))
    right_text(draw, "埼玉県川口市本町2-8-14", right, 244, font(20), GRAY)
    right_text(draw, "FAX 048-000-0000 / 登録番号 T1111111111111", right, 276, font(20), GRAY)

    draw.text((left, 330), "サンライズ商事株式会社 御中", font=font(30, "bold"), fill=INK)
    draw.text((left, 380), "件名：6月度 資材納入分", font=font(24), fill=INK)

    top = 440
    draw.rectangle([left, top, right, top + 50], outline=INK, width=2)
    draw.text((left + 14, top + 12), "内容", font=font(23, "bold"), fill=INK)
    right_text(draw, "数量", left + 700, top + 12, font(23, "bold"))
    right_text(draw, "単価", left + 870, top + 12, font(23, "bold"))
    right_text(draw, "金額", right - 14, top + 12, font(23, "bold"))

    rows = (
        ("鋼製束 S-300", "40", 1250, 50000),
        ("コンパネ 12mm 3x6", "120", 1480, 177600),
        ("垂木 45x45 4m", "80", 890, 71200),
        ("ビス 4.2x75 (箱)", "24", 1100, 26400),
        ("配送費", "1", 12000, 12000),
    )
    y = top + 50
    for name, qty, unit, amount in rows:
        draw.rectangle([left, y, right, y + 54], outline=LINE, width=1)
        draw.text((left + 14, y + 14), name, font=font(23), fill=INK)
        right_text(draw, qty, left + 700, y + 14, font(23))
        right_text(draw, yen(unit), left + 870, y + 14, font(23))
        right_text(draw, yen(amount), right - 14, y + 14, font(23))
        y += 54

    # 値引き行（合計を再計算すると見落としやすい）
    draw.rectangle([left, y, right, y + 54], outline=LINE, width=1)
    draw.text((left + 14, y + 14), "お値引き（継続取引分）", font=font(23), fill=INK)
    right_text(draw, "-¥15,000", right - 14, y + 14, font(23))
    y += 90

    for label, value, bold in (
        ("小計", 322200, False),
        ("消費税（10%）", 32220, False),
        ("合計金額", 354420, True),
    ):
        weight = "bold" if bold else "regular"
        right_text(draw, label, left + 870, y, font(23, weight))
        right_text(draw, yen(value), right - 14, y, font(28 if bold else 23, weight))
        if bold:
            draw.line([(left + 700, y - 10), (right, y - 10)], fill=INK, width=2)
        y += 48

    draw.text((left, y + 60), "支払期日  2026/09/10", font=font(26, "bold"), fill=INK)
    draw.text((left, y + 106), "振込先  川口信用金庫 本店 当座 0099887 ユ）カワセコウザイ", font=font(22), fill=INK)
    return image


# ---------------------------------------------------------------- 請求書3

def render_sakura() -> Image.Image:
    """サクラ配送サービス：税抜表記＋消費税別記・和暦・桁が1つ大きい。"""
    image, draw = new_page()
    left, right = 120, PAGE_W - 120

    center_text(draw, "請求書", PAGE_W / 2, 140, font(56, "bold"))
    draw.line([(PAGE_W / 2 - 120, 220), (PAGE_W / 2 + 120, 220)], fill=INK, width=2)

    draw.text((left, 300), "サンライズ商事 株式会社", font=font(30, "bold"), fill=INK)
    draw.text((left, 346), "経理ご担当者様", font=font(24), fill=INK)

    right_text(draw, "令和8年7月31日", right, 300, font(24))
    right_text(draw, "サクラ配送サービス", right, 350, font(28, "bold"))
    right_text(draw, "代表 桜井 一郎", right, 394, font(22), GRAY)
    right_text(draw, "千葉県船橋市前原西1-1-1", right, 428, font(20), GRAY)

    # 判子欄
    draw.ellipse([right - 110, 470, right - 20, 560], outline=(190, 60, 60), width=3)
    center_text(draw, "桜", right - 65, 492, font(34, "bold"), (190, 60, 60))

    draw.text((left, 500), "件名：6月分 配送業務委託料", font=font(26, "bold"), fill=INK)

    top = 600
    draw.line([(left, top), (right, top)], fill=INK, width=2)
    draw.text((left, top + 18), "摘要", font=font(24, "bold"), fill=INK)
    right_text(draw, "金額（税抜）", right, top + 18, font(24, "bold"))
    draw.line([(left, top + 62), (right, top + 62)], fill=LINE, width=1)

    rows = (
        ("定期便（首都圏ルート）　22日分", 780000),
        ("スポット便　14件", 210000),
        ("待機料　6時間", 90000),
    )
    y = top + 62
    for name, amount in rows:
        draw.text((left, y + 20), name, font=font(24), fill=INK)
        right_text(draw, yen(amount), right, y + 20, font(24))
        draw.line([(left, y + 66), (right, y + 66)], fill=LINE, width=1)
        y += 66

    y += 40
    right_text(draw, "小計（税抜）", right - 260, y, font(24))
    right_text(draw, "¥1,080,000", right, y, font(24))
    y += 46
    right_text(draw, "消費税", right - 260, y, font(24))
    right_text(draw, "¥108,000", right, y, font(24))
    y += 60
    draw.line([(right - 420, y - 14), (right, y - 14)], fill=INK, width=2)
    right_text(draw, "ご請求金額", right - 260, y, font(28, "bold"))
    right_text(draw, "¥1,188,000", right, y, font(32, "bold"))

    draw.text((left, y + 120), "お支払期日：令和8年8月20日", font=font(26, "bold"), fill=INK)
    draw.text((left, y + 166), "お振込先：船橋中央信用組合 前原支店 普通 5544332 サクライイチロウ", font=font(22), fill=INK)
    draw.text((left, y + 210), "※本請求書はインボイス制度の登録事業者ではありません。", font=font(20), fill=GRAY)
    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = (
        ("請求書01_ミナトデザイン.pdf", render_minato()),
        ("請求書02_カワセ工材.pdf", render_kawase()),
        ("請求書03_サクラ配送.pdf", render_sakura()),
    )
    for name, image in pages:
        path = OUTPUT_DIR / name
        image.save(path, "PDF", resolution=150.0)
        print(f"saved: {path}")


if __name__ == "__main__":
    main()
