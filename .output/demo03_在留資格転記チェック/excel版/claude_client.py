"""Claude API 呼び出し（vision＋構造化出力）。GAS版 03_claude.gs の移植。

依存は標準ライブラリのみ（urllib）。応答は output_config.format の
JSON Schema で必ず検証可能なJSONにする。
"""

import json
import os
import time
import urllib.error
import urllib.request

from config import CONFIG

# 日付（西暦）の共通スキーマ
DATE_SCHEMA = {
    "type": "object",
    "properties": {
        "year": {"type": "integer", "description": "西暦4桁。読めなければ0"},
        "month": {"type": "integer", "description": "1〜12。読めなければ0"},
        "day": {"type": "integer", "description": "1〜31。読めなければ0"},
    },
    "required": ["year", "month", "day"],
    "additionalProperties": False,
}

EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "residence_card": {
            "type": "object",
            "description": "在留カードから読み取った内容。カードが無ければ found=false",
            "properties": {
                "found": {"type": "boolean"},
                "name_roman": {"type": "string", "description": "氏名（カード表記のローマ字のまま）"},
                "birth_date": DATE_SCHEMA,
                "sex": {"type": "string", "enum": ["男", "女", "不明"]},
                "nationality_region": {"type": "string", "description": "国籍・地域（カード表記のまま。例: 米国）"},
                "status_of_residence": {"type": "string", "description": "在留資格（例: 留学、技術・人文知識・国際業務）"},
                "period_of_stay": {"type": "string", "description": "在留期間（例: 4年3月）。満了日は含めない"},
                "stay_expiration": DATE_SCHEMA,
                "card_number": {"type": "string", "description": "在留カード番号（英数12桁。例: AB12345678CD）"},
            },
            "required": [
                "found", "name_roman", "birth_date", "sex", "nationality_region",
                "status_of_residence", "period_of_stay", "stay_expiration", "card_number",
            ],
            "additionalProperties": False,
        },
        "passport": {
            "type": "object",
            "description": "パスポートから読み取った内容。無ければ found=false",
            "properties": {
                "found": {"type": "boolean"},
                "surname": {"type": "string"},
                "given_names": {"type": "string"},
                "passport_number": {"type": "string"},
                "expiration": DATE_SCHEMA,
            },
            "required": ["found", "surname", "given_names", "passport_number", "expiration"],
            "additionalProperties": False,
        },
        "reading_notes": {"type": "string", "description": "読み取りに自信がない箇所・注意点（無ければ空文字）"},
    },
    "required": ["residence_card", "passport", "reading_notes"],
    "additionalProperties": False,
}

EXTRACT_SYSTEM_PROMPT = "\n".join([
    "あなたは行政書士事務所の書類読み取りアシスタントです。",
    "在留カードとパスポートの画像から、在留期間更新許可申請書に転記する項目を正確に読み取ります。",
    "ルール：",
    "- 記載を一字一句そのまま読み取る。推測で補完しない（読めない箇所は reading_notes に書く）",
    "- 氏名はカード・旅券の表記（ローマ字大文字）のまま。勝手にカナや漢字へ変換しない",
    "- 日付はすべて西暦の数値に変換する（和暦表記があれば西暦へ）",
    "- 番号類（在留カード番号・旅券番号）は英数字を1文字ずつ慎重に読む",
    "- 見本・SPECIMEN の透かしは無視してよい（公開見本を使ったデモである）",
    "- マイナンバー・個人番号らしき記載を見つけても絶対に出力しない",
])

CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "description": "項目ごとの突合結果。渡された全項目について必ず1件ずつ返す",
            "items": {
                "type": "object",
                "properties": {
                    "item": {"type": "string", "description": "項目名（渡されたラベルをそのまま使う）"},
                    "source": {"type": "string", "description": "突合先（在留カード または パスポート）"},
                    "application_value": {"type": "string", "description": "申請書の記載（そのまま）"},
                    "original_value": {"type": "string", "description": "原本画像から読み取った記載"},
                    "verdict": {"type": "string", "enum": ["OK", "不一致", "要確認"]},
                    "comment": {
                        "type": "string",
                        "description": "指摘コメント。不一致なら「どこがどう違うか」を具体的に（例: 7文字目 Z→S）。OKなら空文字",
                    },
                },
                "required": ["item", "source", "application_value", "original_value", "verdict", "comment"],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string", "description": "全体の一言まとめ（例: 3件の不一致。氏名・生年月日・カード番号を要修正）"},
    },
    "required": ["results", "summary"],
    "additionalProperties": False,
}

CHECK_SYSTEM_PROMPT = "\n".join([
    "あなたは行政書士事務所の申請書チェックアシスタントです。",
    "作成済みの在留期間更新許可申請書の記載を、原本（在留カード・パスポートの画像）と項目ごとに突合します。",
    "ルール：",
    "- 各項目は指定された突合先の書類とだけ比較する（カード由来の項目はカード、旅券由来の項目は旅券）",
    "- 表記ゆれ（全角/半角・スペース）は不一致にしない。文字・数字そのものの違いだけを指摘する",
    "- 不一致は「どの文字がどう違うか」まで具体的に指摘する（ミスの発見が目的）",
    "- 原本が不鮮明で断定できない項目は「要確認」にして理由を書く",
    "- 判定を偽らない。全項目OKならOKと返す",
])


def get_api_key():
    """環境変数からAPIキーを取得する。未設定なら明確なエラーで落とす。"""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY が未設定です。ターミナルで\n"
            '  export ANTHROPIC_API_KEY="sk-ant-..."\n'
            "を実行してから再度お試しください。"
        )
    return key


def extract_from_images(images):
    """書類画像から申請書転記用の項目を抽出する。

    images: [{"name": str, "media_type": str, "base64": str}, ...]
    """
    content = build_image_content(images)
    content.append({
        "type": "text",
        "text": "上の書類画像から、在留期間更新許可申請書に転記する項目を読み取ってください。",
    })
    payload = {
        "model": CONFIG["MODEL"],
        "max_tokens": CONFIG["MAX_TOKENS"],
        "system": EXTRACT_SYSTEM_PROMPT,
        "output_config": {"format": {"type": "json_schema", "schema": EXTRACT_SCHEMA}},
        "messages": [{"role": "user", "content": content}],
    }
    parsed = parse_structured_response(call_claude_api(payload), EXTRACT_SCHEMA)
    if not parsed["residence_card"]["found"]:
        raise RuntimeError("画像の中に在留カードが見つかりませんでした。input フォルダの画像を確認してください。")
    return parsed


def check_against_originals(application_values, images):
    """申請書の記載を原本画像と突合する。"""
    lines = [
        f"- {f['label']}（突合先: {f['source']}）: {f['value'] if f['value'] else '（空欄）'}"
        for f in application_values
    ]
    content = build_image_content(images)
    content.append({
        "type": "text",
        "text": "\n".join([
            "上の原本画像と、以下の申請書の記載を項目ごとに突合してください。",
            "全項目について必ず結果を返してください。",
            "",
            "【申請書の記載】",
            *lines,
        ]),
    })
    payload = {
        "model": CONFIG["MODEL"],
        "max_tokens": CONFIG["MAX_TOKENS"],
        "system": CHECK_SYSTEM_PROMPT,
        "output_config": {"format": {"type": "json_schema", "schema": CHECK_SCHEMA}},
        "messages": [{"role": "user", "content": content}],
    }
    return parse_structured_response(call_claude_api(payload), CHECK_SCHEMA)


def build_image_content(images):
    """入力ファイル（画像・PDF）をAPIのcontentブロック列に変換する（各ファイルの前にファイル名を添える）。

    PDFは document ブロックとして送る（Claude APIのPDFネイティブ対応。スキャンPDFも読める）。
    """
    content = []
    for img in images:
        content.append({"type": "text", "text": f"ファイル名: {img['name']}"})
        block_type = "document" if img["media_type"] == "application/pdf" else "image"
        content.append({
            "type": block_type,
            "source": {"type": "base64", "media_type": img["media_type"], "data": img["base64"]},
        })
    return content


def call_claude_api(payload):
    """Claude API を呼ぶ（429/5xxは1回だけリトライ）。"""
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "x-api-key": get_api_key(),
        "anthropic-version": CONFIG["API_VERSION"],
    }

    last_error = ""
    for attempt in range(2):
        request = urllib.request.Request(CONFIG["API_URL"], data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")[:500]
            last_error = f"Claude API エラー (HTTP {e.code}): {error_body}"
            if e.code == 429 or e.code >= 500:
                if attempt == 0:
                    time.sleep(5)
                    continue
            raise RuntimeError(last_error) from e
        except urllib.error.URLError as e:
            last_error = f"ネットワークエラー: {e.reason}（テザリング/回線を確認してください）"
            if attempt == 0:
                time.sleep(5)
                continue
            raise RuntimeError(last_error) from e
    raise RuntimeError(last_error)


def parse_structured_response(response, schema):
    """APIレスポンスを検証し、スキーマの必須フィールドを確認してパースする。"""
    if response.get("stop_reason") == "refusal":
        raise RuntimeError("Claudeがこのリクエストへの応答を拒否しました。入力画像を確認してください。")
    if response.get("stop_reason") == "max_tokens":
        raise RuntimeError("応答がトークン上限で途切れました。CONFIG['MAX_TOKENS'] を増やしてください。")

    text_block = next((b for b in response.get("content", []) if b.get("type") == "text"), None)
    if text_block is None:
        raise RuntimeError("APIレスポンスにテキストが含まれていません: " + json.dumps(response)[:300])

    parsed = json.loads(text_block["text"])
    missing = [field for field in schema.get("required", []) if field not in parsed]
    if missing:
        raise RuntimeError("応答データに必須フィールドが欠けています: " + ", ".join(missing))
    return parsed
