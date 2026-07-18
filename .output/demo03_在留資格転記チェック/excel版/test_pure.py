#!/usr/bin/env python3
"""純関数＋Excel入出力の単体検証（APIを呼ばない）。

実行: python3 test_pure.py
"""

import copy
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import openpyxl

from config import CHECK_FIELDS, SAMPLE_FORM_VALUES
from excel_io import create_form_copy, fill_form_sheet, get_form_sheet, read_form_sheet
from pure import (
    build_application_values,
    clean_text,
    extracted_to_form_values,
    join_date_text,
    media_type_for,
    positive_or_none,
)

PASSED = 0


def test(name, fn):
    global PASSED
    fn()
    PASSED += 1
    print("  ok -", name)


EXTRACTED_FIXTURE = {
    "residence_card": {
        "found": True,
        "name_roman": " TURNER ELIZABETH ",
        "birth_date": {"year": 1985, "month": 12, "day": 31},
        "sex": "女",
        "nationality_region": "米国",
        "status_of_residence": "留学",
        "period_of_stay": "4年3月",
        "stay_expiration": {"year": 2027, "month": 2, "day": 22},
        "card_number": "AB12345678CD",
    },
    "passport": {
        "found": True,
        "surname": "TRAVELER",
        "given_names": "HAPPY",
        "passport_number": "E00007734",
        "expiration": {"year": 2030, "month": 10, "day": 14},
    },
    "reading_notes": "",
}


def main():
    # --- join_date_text / clean_text / positive_or_none / media_type_for ---
    test("join_date_text: 通常の日付を結合する", lambda: (
        assert_eq(join_date_text("1985", "12", "31"), "1985年12月31日")))
    test("join_date_text: 数値でも結合できる", lambda: (
        assert_eq(join_date_text(2027, 2, 22), "2027年2月22日")))
    test("join_date_text: どれかが空なら空文字", lambda: (
        assert_eq(join_date_text("", "12", "31"), ""),
        assert_eq(join_date_text("1985", None, "31"), ""),
    ))
    test("clean_text: stripしてNoneは空文字", lambda: (
        assert_eq(clean_text("  米国 "), "米国"),
        assert_eq(clean_text(None), ""),
        assert_eq(clean_text(123), "123"),
    ))
    test("positive_or_none: 0や非整数はNone", lambda: (
        assert_eq(positive_or_none(1985), 1985),
        assert_eq(positive_or_none(0), None),
        assert_eq(positive_or_none("1985"), None),
        assert_eq(positive_or_none(True), None),
    ))
    test("media_type_for: 拡張子判定", lambda: (
        assert_eq(media_type_for("a.PNG"), "image/png"),
        assert_eq(media_type_for("b.jpeg"), "image/jpeg"),
        assert_eq(media_type_for("c.txt"), None),
        assert_eq(media_type_for("noext"), None),
    ))

    # --- extracted_to_form_values ---
    def t_normal():
        v = extracted_to_form_values(EXTRACTED_FIXTURE)
        assert_eq(v["name"], "TURNER ELIZABETH")
        assert_eq(v["birth_year"], 1985)
        assert_eq(v["sex"], "女")
        assert_eq(v["passport_number"], "E00007734")
        assert_eq(v["stay_exp_year"], 2027)
        assert_eq(v["card_number"], "AB12345678CD")
    test("extracted_to_form_values: 通常ケース", t_normal)

    def t_no_passport():
        fixture = copy.deepcopy(EXTRACTED_FIXTURE)
        fixture["passport"]["found"] = False
        v = extracted_to_form_values(fixture)
        assert_eq(v["passport_number"], "")
        assert_eq(v["passport_exp_year"], None)
    test("extracted_to_form_values: 旅券なしなら旅券項目は空", t_no_passport)

    def t_unreadable_date():
        fixture = copy.deepcopy(EXTRACTED_FIXTURE)
        fixture["residence_card"]["birth_date"] = {"year": 1985, "month": 0, "day": 0}
        v = extracted_to_form_values(fixture)
        assert_eq(v["birth_month"], None)
        assert_eq(v["birth_day"], None)
    test("extracted_to_form_values: 読めない日付(0)はNone", t_unreadable_date)

    def t_immutable():
        snapshot = copy.deepcopy(EXTRACTED_FIXTURE)
        extracted_to_form_values(EXTRACTED_FIXTURE)
        assert_eq(EXTRACTED_FIXTURE, snapshot)
    test("extracted_to_form_values: 入力を破壊しない", t_immutable)

    # --- build_application_values ---
    raw = {
        "nationality": "米国", "birth_year": 1986, "birth_month": 12, "birth_day": 31,
        "name": "TURNER ELISABETH", "sex": "女",
        "passport_number": "E00007734", "passport_exp_year": 2030, "passport_exp_month": 10, "passport_exp_day": 14,
        "status_of_residence": "留学", "period_of_stay": "4年3月",
        "stay_exp_year": 2027, "stay_exp_month": 2, "stay_exp_day": 22,
        "card_number": "AB12345678CB",
    }

    def t_build():
        values = build_application_values(raw)
        assert_eq(len(values), len(CHECK_FIELDS))
        by_key = {v["key"]: v for v in values}
        assert_eq(by_key["birth_date"]["value"], "1986年12月31日")
        assert_eq(by_key["name"]["value"], "TURNER ELISABETH")
        assert_eq(by_key["card_number"]["value"], "AB12345678CB")
        assert_eq(by_key["passport_number"]["source"], "パスポート")
    test("build_application_values: 全項目・日付結合・誤り値保持", t_build)

    # --- Excel入出力の往復（転記→読み戻し） ---
    def t_roundtrip():
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roundtrip.xlsx"
            wb = create_form_copy(path)
            fill_form_sheet(get_form_sheet(wb), dict(SAMPLE_FORM_VALUES))
            wb.save(path)

            wb2 = openpyxl.load_workbook(path)
            values = read_form_sheet(get_form_sheet(wb2))
            by_key = {v["key"]: v["value"] for v in values}
            assert_eq(by_key["name"], "TURNER ELISABETH")
            assert_eq(by_key["birth_date"], "1986年12月31日")
            assert_eq(by_key["card_number"], "AB12345678CB")
            assert_eq(by_key["sex"], "女")  # ハイライトの読み戻し
            assert_eq(by_key["passport_number"], "E00007734")
            assert_eq(by_key["stay_expiration"], "2027年2月22日")
    test("Excel往復: 様式コピー→転記→保存→読み戻しが一致（性別ハイライト含む）", t_roundtrip)

    print(f"\n{PASSED} tests passed")


def assert_eq(actual, expected):
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


if __name__ == "__main__":
    main()
