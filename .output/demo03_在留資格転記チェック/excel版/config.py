"""設定と定数（GAS版 01_config.gs の移植）。

APIキーはコードに書かず、環境変数 ANTHROPIC_API_KEY で渡す。
セル位置の根拠は ../00_セルマッピング.md 参照。
"""

from pathlib import Path
from types import MappingProxyType

BASE_DIR = Path(__file__).resolve().parent

CONFIG = MappingProxyType({
    "API_URL": "https://api.anthropic.com/v1/messages",
    "API_VERSION": "2023-06-01",
    # vision対応。haikuは指摘コメントの説明が不正確だったため sonnet に引き上げ（2026-07-18・E2Eで確認）
    "MODEL": "claude-sonnet-5",
    "MAX_TOKENS": 4096,
    # 書類画像（在留カード・パスポート）を入れるフォルダ
    "INPUT_DIR": BASE_DIR / "input",
    # 生成物の出力先
    "OUTPUT_DIR": BASE_DIR / "output",
    # 公式様式（入管庁のxlsxをそのまま同梱）
    "TEMPLATE_PATH": BASE_DIR / "様式" / "在留期間更新許可申請書_技人国.xlsx",
    "FORM_SHEET_NAME": "申請人用（更新）１",
    "SAMPLE_FILE_NAME": "申請書サンプル（誤り入り）.xlsx",
    "CHECK_SHEET_NAME": "チェック結果",
    # 1回の実行で読み込む画像の上限（誤爆防止）
    "MAX_INPUT_IMAGES": 4,
    # 性別の○囲みの代替として塗るハイライト色（ARGBなし6桁）
    "SEX_HIGHLIGHT_COLOR": "FFF2A8",
})

# 申請書（申請人等作成用1）の入力セル。結合セルの左上を指定。
FORM_CELLS = MappingProxyType({
    "NATIONALITY": "G15",
    "BIRTH_YEAR": "W15",
    "BIRTH_MONTH": "AC15",
    "BIRTH_DAY": "AG15",
    "NAME": "G18",
    "SEX_MALE": "E21",
    "SEX_FEMALE": "G21",
    "PASSPORT_NUMBER": "I33",
    "PASSPORT_EXP_YEAR": "X33",
    "PASSPORT_EXP_MONTH": "AD33",
    "PASSPORT_EXP_DAY": "AH33",
    "STATUS_OF_RESIDENCE": "I36",
    "PERIOD_OF_STAY": "Z36",
    "STAY_EXP_YEAR": "I39",
    "STAY_EXP_MONTH": "O39",
    "STAY_EXP_DAY": "S39",
    "CARD_NUMBER": "I42",
})

# 突合チェックの対象項目。source = どちらの原本と突き合わせるか
# （公開見本は人物が別のため、カード由来はカードとだけ、旅券由来は旅券とだけ比較する）
CHECK_FIELDS = (
    MappingProxyType({"key": "nationality", "label": "国籍・地域", "source": "在留カード"}),
    MappingProxyType({"key": "birth_date", "label": "生年月日", "source": "在留カード"}),
    MappingProxyType({"key": "name", "label": "氏名（ローマ字）", "source": "在留カード"}),
    MappingProxyType({"key": "sex", "label": "性別", "source": "在留カード"}),
    MappingProxyType({"key": "status_of_residence", "label": "在留資格", "source": "在留カード"}),
    MappingProxyType({"key": "period_of_stay", "label": "在留期間", "source": "在留カード"}),
    MappingProxyType({"key": "stay_expiration", "label": "在留期間の満了日", "source": "在留カード"}),
    MappingProxyType({"key": "card_number", "label": "在留カード番号", "source": "在留カード"}),
    MappingProxyType({"key": "passport_number", "label": "旅券番号", "source": "パスポート"}),
    MappingProxyType({"key": "passport_expiration", "label": "旅券有効期限", "source": "パスポート"}),
)

# チェック結果シートの列
CHECK_HEADERS = ("項目", "突合先", "申請書の記載", "原本の記載", "判定", "指摘コメント")

# 判定ごとの背景色（チェック結果シート・ARGBなし6桁）
VERDICT_COLORS = MappingProxyType({
    "不一致": "F8CBCB",
    "要確認": "FDF3C0",
})

# デモ用サンプル（誤り入り）の値。公式見本画像の記載がベース。
# わざと仕込んだ誤り3種：
#  1. 氏名のローマ字違い（ELIZABETH → ELISABETH）
#  2. 生年月日の年ズレ（1985 → 1986。和暦変換の取り違え想定）
#  3. 在留カード番号の1文字違い（AB12345678CD → AB12345678CB）
SAMPLE_FORM_VALUES = MappingProxyType({
    "nationality": "米国",
    "birth_year": 1986,  # 誤り②
    "birth_month": 12,
    "birth_day": 31,
    "name": "TURNER ELISABETH",  # 誤り①
    "sex": "女",
    "passport_number": "E00007734",
    "passport_exp_year": 2030,
    "passport_exp_month": 10,
    "passport_exp_day": 14,
    "status_of_residence": "留学",
    "period_of_stay": "4年3月",
    "stay_exp_year": 2027,
    "stay_exp_month": 2,
    "stay_exp_day": 22,
    "card_number": "AB12345678CB",  # 誤り③
})
