/**
 * 設定と定数。
 * APIキーはコードに書かず、スクリプトプロパティ ANTHROPIC_API_KEY に保存する。
 * （Apps Script エディタ → プロジェクトの設定 → スクリプト プロパティ）
 */

const CONFIG = Object.freeze({
  API_URL: 'https://api.anthropic.com/v1/messages',
  API_VERSION: '2023-06-01',
  MODEL: 'claude-haiku-4-5',
  MAX_TOKENS: 8192,
  CASE_SHEET_NAME: '案件管理',
  ERROR_SHEET_NAME: 'エラーログ',
  // フォームの質問タイトル（フォーム側と一致させること）
  FORM_FIELDS: Object.freeze({
    NAME: 'お名前',
    COMPANY: '会社名・事務所名',
    EMAIL: 'メールアドレス',
    BODY: 'ご相談内容',
  }),
});

const CASE_SHEET_HEADERS = Object.freeze([
  '受付日時',
  'お名前',
  '会社名・事務所名',
  'メールアドレス',
  '相談分類',
  '緊急度',
  '案件サマリー',
  '論点',
  '事前質問リスト',
  '返信下書き作成',
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
