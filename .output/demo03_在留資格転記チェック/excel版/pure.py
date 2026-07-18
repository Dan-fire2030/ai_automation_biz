"""純関数（外部I/Oなし。GAS版 06_pure.gs の移植）。test_pure.py で単体検証する。"""

from config import CHECK_FIELDS


def extracted_to_form_values(extracted):
    """OCR抽出結果（EXTRACT_SCHEMA形式）をシート転記用の値に変換する。

    日付の0（読めなかった印）は None にして「書き込まない」扱いにする。
    入力は変更しない（新しいdictを返す）。
    """
    card = extracted.get("residence_card") or {}
    passport = extracted.get("passport") or {}
    passport_found = passport.get("found") is True
    birth = card.get("birth_date") or {}
    stay_exp = card.get("stay_expiration") or {}
    pass_exp = passport.get("expiration") or {}

    return {
        "nationality": text_or_empty(card.get("nationality_region")),
        "birth_year": positive_or_none(birth.get("year")),
        "birth_month": positive_or_none(birth.get("month")),
        "birth_day": positive_or_none(birth.get("day")),
        "name": text_or_empty(card.get("name_roman")),
        "sex": card.get("sex") if card.get("sex") in ("男", "女") else "",
        "passport_number": text_or_empty(passport.get("passport_number")) if passport_found else "",
        "passport_exp_year": positive_or_none(pass_exp.get("year")) if passport_found else None,
        "passport_exp_month": positive_or_none(pass_exp.get("month")) if passport_found else None,
        "passport_exp_day": positive_or_none(pass_exp.get("day")) if passport_found else None,
        "status_of_residence": text_or_empty(card.get("status_of_residence")),
        "period_of_stay": text_or_empty(card.get("period_of_stay")),
        "stay_exp_year": positive_or_none(stay_exp.get("year")),
        "stay_exp_month": positive_or_none(stay_exp.get("month")),
        "stay_exp_day": positive_or_none(stay_exp.get("day")),
        "card_number": text_or_empty(card.get("card_number")),
    }


def build_application_values(raw):
    """シートから読んだ生の記載を、突合チェックに渡す項目リストに組み立てる。

    CHECK_FIELDS の全項目を、日付は「YYYY年M月D日」に結合して返す。
    """
    value_by_key = {
        "nationality": clean_text(raw.get("nationality")),
        "birth_date": join_date_text(raw.get("birth_year"), raw.get("birth_month"), raw.get("birth_day")),
        "name": clean_text(raw.get("name")),
        "sex": clean_text(raw.get("sex")),
        "status_of_residence": clean_text(raw.get("status_of_residence")),
        "period_of_stay": clean_text(raw.get("period_of_stay")),
        "stay_expiration": join_date_text(raw.get("stay_exp_year"), raw.get("stay_exp_month"), raw.get("stay_exp_day")),
        "card_number": clean_text(raw.get("card_number")),
        "passport_number": clean_text(raw.get("passport_number")),
        "passport_expiration": join_date_text(
            raw.get("passport_exp_year"), raw.get("passport_exp_month"), raw.get("passport_exp_day")
        ),
    }

    return [
        {
            "key": field["key"],
            "label": field["label"],
            "source": field["source"],
            "value": value_by_key.get(field["key"], ""),
        }
        for field in CHECK_FIELDS
    ]


def join_date_text(year, month, day):
    """年・月・日を「YYYY年M月D日」に結合する。どれかが空なら空文字。"""
    y = clean_text(year)
    m = clean_text(month)
    d = clean_text(day)
    if y == "" or m == "" or d == "":
        return ""
    return f"{y}年{m}月{d}日"


def clean_text(value):
    """値を整形済みテキストにする（strip。None は空文字。数値はそのまま文字列化）。"""
    if value is None:
        return ""
    return str(value).strip()


def positive_or_none(value):
    """正の整数ならそのまま、それ以外（0＝読めなかった印を含む）は None。"""
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def text_or_empty(value):
    """テキストならstripして返し、それ以外は空文字。"""
    return value.strip() if isinstance(value, str) else ""


def media_type_for(filename):
    """拡張子から入力ファイルのmedia_typeを返す（画像＋PDF）。対象外は None。"""
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "pdf": "application/pdf",
    }.get(suffix)
