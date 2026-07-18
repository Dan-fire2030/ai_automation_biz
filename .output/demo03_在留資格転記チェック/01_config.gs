/**
 * 設定と定数。
 * APIキーはコードに書かず、スクリプトプロパティ ANTHROPIC_API_KEY に保存する。
 * （Apps Script エディタ → プロジェクトの設定 → スクリプト プロパティ）
 */

const CONFIG = Object.freeze({
  API_URL: 'https://api.anthropic.com/v1/messages',
  API_VERSION: '2023-06-01',
  // vision対応。haikuは指摘コメントの説明が不正確だったためsonnetに引き上げ（Excel版E2Eでの知見・2026-07-18）
  MODEL: 'claude-sonnet-5',
  MAX_TOKENS: 4096,
  // 書類画像（在留カード・パスポート）を入れるDriveフォルダのID
  // （フォルダを開いたときのURL https://drive.google.com/drive/folders/XXXX の XXXX 部分）
  INPUT_FOLDER_ID: 'ここに入力フォルダのIDを貼る',
  // 公式様式（xlsxをSheets変換したもの）のシート名
  FORM_SHEET_NAME: '申請人用（更新）１',
  // 生成するシートの名前
  DRAFT_SHEET_PREFIX: '申請書ドラフト_',
  SAMPLE_SHEET_NAME: '申請書サンプル（誤り入り）',
  CHECK_SHEET_NAME: 'チェック結果',
  // 1回の実行で読み込む画像の上限（誤爆防止）
  MAX_INPUT_IMAGES: 4,
  // 性別の○囲みの代替として塗るハイライト色
  SEX_HIGHLIGHT_COLOR: '#fff2a8',
});

/**
 * 申請書（申請人等作成用1）の入力セル。結合セルの左上を指定。
 * 出典・根拠は 00_セルマッピング.md 参照。
 */
const FORM_CELLS = Object.freeze({
  NATIONALITY: 'G15',
  BIRTH_YEAR: 'W15',
  BIRTH_MONTH: 'AC15',
  BIRTH_DAY: 'AG15',
  NAME: 'G18',
  SEX_MALE: 'E21',
  SEX_FEMALE: 'G21',
  PASSPORT_NUMBER: 'I33',
  PASSPORT_EXP_YEAR: 'X33',
  PASSPORT_EXP_MONTH: 'AD33',
  PASSPORT_EXP_DAY: 'AH33',
  STATUS_OF_RESIDENCE: 'I36',
  PERIOD_OF_STAY: 'Z36',
  STAY_EXP_YEAR: 'I39',
  STAY_EXP_MONTH: 'O39',
  STAY_EXP_DAY: 'S39',
  CARD_NUMBER: 'I42',
});

/**
 * 突合チェックの対象項目。
 * source = どちらの原本と突き合わせるか（人物が別の公開見本でも成立するよう、
 * カード由来の項目はカードとだけ、旅券由来の項目は旅券とだけ比較する）。
 */
const CHECK_FIELDS = Object.freeze([
  Object.freeze({ key: 'nationality', label: '国籍・地域', source: '在留カード' }),
  Object.freeze({ key: 'birth_date', label: '生年月日', source: '在留カード' }),
  Object.freeze({ key: 'name', label: '氏名（ローマ字）', source: '在留カード' }),
  Object.freeze({ key: 'sex', label: '性別', source: '在留カード' }),
  Object.freeze({ key: 'status_of_residence', label: '在留資格', source: '在留カード' }),
  Object.freeze({ key: 'period_of_stay', label: '在留期間', source: '在留カード' }),
  Object.freeze({ key: 'stay_expiration', label: '在留期間の満了日', source: '在留カード' }),
  Object.freeze({ key: 'card_number', label: '在留カード番号', source: '在留カード' }),
  Object.freeze({ key: 'passport_number', label: '旅券番号', source: 'パスポート' }),
  Object.freeze({ key: 'passport_expiration', label: '旅券有効期限', source: 'パスポート' }),
]);

/** チェック結果シートの列 */
const CHECK_HEADERS = Object.freeze([
  '項目',
  '突合先',
  '申請書の記載',
  '原本の記載',
  '判定',
  '指摘コメント',
]);

/**
 * デモ用サンプル（誤り入り）の値。公式見本画像の記載がベース。
 * わざと仕込んだ誤り3種：
 *  1. 氏名のローマ字違い（ELIZABETH → ELISABETH）
 *  2. 生年月日の和暦→西暦変換ズレ（1985 → 1986。昭和60年を61年と取り違えた想定）
 *  3. 在留カード番号の1文字違い（AB12345678CD → AB12345678CB）
 */
const SAMPLE_FORM_VALUES = Object.freeze({
  nationality: '米国',
  birthYear: 1986, // 誤り②
  birthMonth: 12,
  birthDay: 31,
  name: 'TURNER ELISABETH', // 誤り①
  sex: '女',
  passportNumber: 'E00007734',
  passportExpYear: 2030,
  passportExpMonth: 10,
  passportExpDay: 14,
  statusOfResidence: '留学',
  periodOfStay: '4年3月',
  stayExpYear: 2027,
  stayExpMonth: 2,
  stayExpDay: 22,
  cardNumber: 'AB12345678CB', // 誤り③
});

/**
 * スクリプトプロパティからAPIキーを取得する。未設定なら明確なエラーで落とす。
 * @return {string}
 */
function getApiKey() {
  const key = PropertiesService.getScriptProperties().getProperty('ANTHROPIC_API_KEY');
  if (!key) {
    throw new Error(
      'ANTHROPIC_API_KEY が未設定です。Apps Script の「プロジェクトの設定 → スクリプト プロパティ」で設定してください。'
    );
  }
  return key;
}
