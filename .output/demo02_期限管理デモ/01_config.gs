/**
 * 設定と定数。
 * APIキーはコードに書かず、スクリプトプロパティ ANTHROPIC_API_KEY に保存する。
 * （Apps Script エディタ → プロジェクトの設定 → スクリプト プロパティ）
 */

const CONFIG = Object.freeze({
  API_URL: 'https://api.anthropic.com/v1/messages',
  API_VERSION: '2023-06-01',
  MODEL: 'claude-haiku-4-5',
  MAX_TOKENS: 4096,
  DEADLINE_SHEET_NAME: '期限管理',
  LOG_SHEET_NAME: '催促ログ',
  ERROR_SHEET_NAME: 'エラーログ',
  // 毎朝この時刻に自動チェックする（時限トリガー）
  DAILY_TRIGGER_HOUR: 9,
  // 事務所名（催促メールの署名まわりの文脈としてClaudeに渡す。空でも可）
  OFFICE_NAME: 'じむらく行政書士事務所',
});

/**
 * 催促ステージ（期限までの残日数のしきい値）。
 * level が大きいほど緊急。残日数がしきい値以内になると、そのステージに入る。
 * 同じ案件に毎日メールを作らないよう、「前回より緊急なステージに進んだとき」だけ
 * 新しい下書きを作る（main.gs の shouldRemind 参照）。
 */
const REMINDER_STAGES = Object.freeze([
  Object.freeze({ level: 5, label: '期限超過', maxDaysLeft: -1 }),
  Object.freeze({ level: 4, label: '直前（14日以内）', maxDaysLeft: 14 }),
  Object.freeze({ level: 3, label: '30日前', maxDaysLeft: 30 }),
  Object.freeze({ level: 2, label: '60日前', maxDaysLeft: 60 }),
  Object.freeze({ level: 1, label: '90日前', maxDaysLeft: 90 }),
]);

/** 完了扱い（催促対象から外す）とみなすステータス文字列 */
const DONE_STATUSES = Object.freeze(['完了', '対応済', '対応済み', 'クローズ']);

/**
 * 期限管理シートの列。
 * 前半（顧客名〜ステータス）は利用者が入力する列。
 * 後半（残日数〜最終催促日）はスクリプトが自動更新する列。
 */
const DEADLINE_HEADERS = Object.freeze([
  '顧客名',
  '会社名・事務所名',
  'メールアドレス',
  '手続き種別',
  '期限日',
  'ステータス',
  '残日数',
  '最終催促ステージ',
  '最終催促日',
]);

/** 催促ログシートの列 */
const LOG_HEADERS = Object.freeze([
  '処理日時',
  '顧客名',
  '手続き種別',
  '期限日',
  '残日数',
  'ステージ',
  '件名',
  '下書き',
]);

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
