#!/usr/bin/env python3
"""デモ03（Excel版）：在留資格申請書の転記＋原本突合チェック。

使い方（このフォルダで実行）:
  python3 demo03.py draft    … input/ の画像・PDFをOCR → 公式様式に転記した「申請書ドラフト_*.xlsx」を output/ に作る
  python3 demo03.py sample   … 誤り3種入りの「申請書サンプル（誤り入り）.xlsx」を output/ に作る
  python3 demo03.py check    … サンプルの記載を原本画像と突合 → 同じxlsxに「チェック結果」シートを追加

日本語エイリアス: ドラフト / サンプル / チェック
事前に: export ANTHROPIC_API_KEY="sk-ant-..."
"""

import base64
import sys
from datetime import datetime
from pathlib import Path

import openpyxl

from claude_client import check_against_originals, extract_from_images
from config import CONFIG
from excel_io import create_form_copy, fill_form_sheet, get_form_sheet, read_form_sheet, write_check_results
from pure import extracted_to_form_values, media_type_for
from config import SAMPLE_FORM_VALUES

COMMAND_ALIASES = {
    "draft": "draft", "ドラフト": "draft", "ドラフト作成": "draft",
    "sample": "sample", "サンプル": "sample", "サンプル作成": "sample",
    "check": "check", "チェック": "check", "突合": "check",
}


def load_input_images():
    """input/ フォルダの画像・PDFを読み込み、base64化して返す。"""
    input_dir = Path(CONFIG["INPUT_DIR"])
    if not input_dir.exists():
        raise RuntimeError(f"入力フォルダがありません: {input_dir}")

    images = []
    for path in sorted(input_dir.iterdir()):
        if len(images) >= CONFIG["MAX_INPUT_IMAGES"]:
            break
        media_type = media_type_for(path.name)
        if not path.is_file() or media_type is None:
            continue
        images.append({
            "name": path.name,
            "media_type": media_type,
            "base64": base64.b64encode(path.read_bytes()).decode("ascii"),
        })

    if not images:
        raise RuntimeError(f"入力フォルダに画像・PDF（JPEG/PNG/PDF）がありません: {input_dir}")
    return images


def run_draft():
    """① 画像・PDFから申請書ドラフトを作る。"""
    print("入力ファイルを読み込み中…")
    images = load_input_images()
    for img in images:
        print(f"  - {img['name']}")

    print("AIが書類を読み取り中…（十数秒かかります）")
    extracted = extract_from_images(images)

    output_path = Path(CONFIG["OUTPUT_DIR"]) / f"申請書ドラフト_{datetime.now():%m%d_%H%M}.xlsx"
    workbook = create_form_copy(output_path)
    fill_form_sheet(get_form_sheet(workbook), extracted_to_form_values(extracted))
    workbook.save(output_path)

    print(f"\n✅ 申請書ドラフトができました: {output_path}")
    print("   空欄は身分証から取れない項目（先生の記入欄）です。")
    if extracted.get("reading_notes"):
        print(f"   読み取りメモ: {extracted['reading_notes']}")
    return output_path


def run_sample():
    """② 誤り3種入りの申請書サンプルを作る。"""
    output_path = Path(CONFIG["OUTPUT_DIR"]) / CONFIG["SAMPLE_FILE_NAME"]
    workbook = create_form_copy(output_path)
    fill_form_sheet(get_form_sheet(workbook), dict(SAMPLE_FORM_VALUES))
    workbook.save(output_path)
    print(f"✅ サンプルができました: {output_path}")
    print("   誤りを3箇所仕込んであります（どこかは check で見つかります）。")
    return output_path


def run_check():
    """③ サンプルの記載を原本画像と突合し、チェック結果シートを追加する。"""
    sample_path = Path(CONFIG["OUTPUT_DIR"]) / CONFIG["SAMPLE_FILE_NAME"]
    if not sample_path.exists():
        raise RuntimeError(f"サンプルがありません。先に `python3 demo03.py sample` を実行してください: {sample_path}")

    print(f"申請書を読み取り中… {sample_path.name}")
    workbook = openpyxl.load_workbook(sample_path)
    application_values = read_form_sheet(get_form_sheet(workbook))

    print("入力ファイルを読み込み中…")
    images = load_input_images()

    print("AIが原本と突合中…（十数秒かかります）")
    check = check_against_originals(application_values, images)

    write_check_results(workbook, check)
    workbook.save(sample_path)

    ng = [r for r in check["results"] if r["verdict"] != "OK"]
    print(f"\n✅ 突合チェック完了。「{CONFIG['CHECK_SHEET_NAME']}」シートを {sample_path.name} に追加しました。")
    print(f"   指摘 {len(ng)} 件 / 全{len(check['results'])}項目")
    for r in ng:
        print(f"   🔴 {r['item']}: {r['application_value']} ⇔ 原本: {r['original_value']}　{r['comment']}")
    print(f"   まとめ: {check.get('summary', '')}")
    return sample_path


def main(argv):
    command = COMMAND_ALIASES.get(argv[1]) if len(argv) > 1 else None
    if command is None:
        print(__doc__)
        return 1
    try:
        {"draft": run_draft, "sample": run_sample, "check": run_check}[command]()
        return 0
    except RuntimeError as e:
        print(f"\n❌ エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
