/**
 * スプレッドシートへの記録。
 * 「案件管理」シートに1相談＝1行で構造化して追記する。
 */

/**
 * 案件管理シートに分析結果を1行追記する。
 * @param {{name: string, company: string, email: string, submittedAt: Date}} inquiry
 * @param {{category: string, urgency: string, summary: string, key_points: string[], questions: string[]}} analysis
 */
function appendCaseRow(inquiry, analysis) {
  const sheet = getOrCreateSheet(CONFIG.CASE_SHEET_NAME, CASE_SHEET_HEADERS);
  sheet.appendRow([
    inquiry.submittedAt,
    inquiry.name,
    inquiry.company,
    inquiry.email,
    analysis.category,
    analysis.urgency,
    analysis.summary,
    analysis.key_points.map((p, i) => `${i + 1}. ${p}`).join('\n'),
    analysis.questions.map((q, i) => `Q${i + 1}. ${q}`).join('\n'),
    inquiry.email ? '済' : '−',
  ]);
}

/**
 * 指定名のシートを取得し、なければヘッダー付きで作成する。
 * @param {string} name
 * @param {ReadonlyArray<string>} headers
 * @return {GoogleAppsScript.Spreadsheet.Sheet}
 */
function getOrCreateSheet(name, headers) {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const existing = spreadsheet.getSheetByName(name);
  if (existing) {
    return existing;
  }
  const sheet = spreadsheet.insertSheet(name);
  sheet.appendRow(headers.slice());
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  sheet.setFrozenRows(1);
  return sheet;
}
