/**
 * シート操作（様式のコピー・転記・読み取り・チェック結果の書き出し）。
 * セル位置の根拠は 00_セルマッピング.md 参照。
 */

/** 判定ごとの背景色（チェック結果シート） */
const VERDICT_COLORS = Object.freeze({
  '不一致': '#f8cbcb',
  '要確認': '#fdf3c0',
});

/**
 * 公式様式シートをコピーして新しいシートを作る。
 * @param {string} newName 新しいシート名
 * @return {GoogleAppsScript.Spreadsheet.Sheet}
 */
function copyFormSheet(newName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const formSheet = ss.getSheetByName(CONFIG.FORM_SHEET_NAME);
  if (!formSheet) {
    throw new Error(
      `様式シート「${CONFIG.FORM_SHEET_NAME}」が見つかりません。公式様式（xlsx）をSheets変換したファイルで実行してください。`
    );
  }
  const copied = formSheet.copyTo(ss);
  copied.setName(newName);
  ss.setActiveSheet(copied);
  return copied;
}

/**
 * 申請書シートに値を転記する。空の値は書き込まない（先生の記入欄を汚さない）。
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet
 * @param {Object} v SAMPLE_FORM_VALUES と同じ形の値
 */
function fillFormSheet(sheet, v) {
  setCellIfPresent(sheet, FORM_CELLS.NATIONALITY, v.nationality);
  setCellIfPresent(sheet, FORM_CELLS.BIRTH_YEAR, v.birthYear);
  setCellIfPresent(sheet, FORM_CELLS.BIRTH_MONTH, v.birthMonth);
  setCellIfPresent(sheet, FORM_CELLS.BIRTH_DAY, v.birthDay);
  setCellIfPresent(sheet, FORM_CELLS.NAME, v.name);
  setCellIfPresent(sheet, FORM_CELLS.PASSPORT_NUMBER, v.passportNumber);
  setCellIfPresent(sheet, FORM_CELLS.PASSPORT_EXP_YEAR, v.passportExpYear);
  setCellIfPresent(sheet, FORM_CELLS.PASSPORT_EXP_MONTH, v.passportExpMonth);
  setCellIfPresent(sheet, FORM_CELLS.PASSPORT_EXP_DAY, v.passportExpDay);
  setCellIfPresent(sheet, FORM_CELLS.STATUS_OF_RESIDENCE, v.statusOfResidence);
  setCellIfPresent(sheet, FORM_CELLS.PERIOD_OF_STAY, v.periodOfStay);
  setCellIfPresent(sheet, FORM_CELLS.STAY_EXP_YEAR, v.stayExpYear);
  setCellIfPresent(sheet, FORM_CELLS.STAY_EXP_MONTH, v.stayExpMonth);
  setCellIfPresent(sheet, FORM_CELLS.STAY_EXP_DAY, v.stayExpDay);
  setCellIfPresent(sheet, FORM_CELLS.CARD_NUMBER, v.cardNumber);

  // 性別は○囲み式のため、該当セルのハイライトで代替する
  if (v.sex === '男') {
    sheet.getRange(FORM_CELLS.SEX_MALE).setBackground(CONFIG.SEX_HIGHLIGHT_COLOR);
  } else if (v.sex === '女') {
    sheet.getRange(FORM_CELLS.SEX_FEMALE).setBackground(CONFIG.SEX_HIGHLIGHT_COLOR);
  }
}

/**
 * 値が空でなければセルに書き込む。
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet
 * @param {string} a1 セル位置（A1形式）
 * @param {string|number|undefined} value
 */
function setCellIfPresent(sheet, a1, value) {
  if (value === undefined || value === null || value === '' || value === 0) {
    return;
  }
  sheet.getRange(a1).setValue(value);
}

/**
 * 申請書シートから突合対象の記載を読み取る。
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet
 * @return {Array<{key: string, label: string, source: string, value: string}>}
 */
function readFormSheet(sheet) {
  const cell = (a1) => sheet.getRange(a1).getDisplayValue();
  const raw = {
    nationality: cell(FORM_CELLS.NATIONALITY),
    birthYear: cell(FORM_CELLS.BIRTH_YEAR),
    birthMonth: cell(FORM_CELLS.BIRTH_MONTH),
    birthDay: cell(FORM_CELLS.BIRTH_DAY),
    name: cell(FORM_CELLS.NAME),
    sex: readSexSelection(sheet),
    passportNumber: cell(FORM_CELLS.PASSPORT_NUMBER),
    passportExpYear: cell(FORM_CELLS.PASSPORT_EXP_YEAR),
    passportExpMonth: cell(FORM_CELLS.PASSPORT_EXP_MONTH),
    passportExpDay: cell(FORM_CELLS.PASSPORT_EXP_DAY),
    statusOfResidence: cell(FORM_CELLS.STATUS_OF_RESIDENCE),
    periodOfStay: cell(FORM_CELLS.PERIOD_OF_STAY),
    stayExpYear: cell(FORM_CELLS.STAY_EXP_YEAR),
    stayExpMonth: cell(FORM_CELLS.STAY_EXP_MONTH),
    stayExpDay: cell(FORM_CELLS.STAY_EXP_DAY),
    cardNumber: cell(FORM_CELLS.CARD_NUMBER),
  };
  return buildApplicationValues(raw);
}

/**
 * 性別欄のハイライト（○囲みの代替）からどちらが選択されているかを読む。
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet
 * @return {string} '男' | '女' | ''
 */
function readSexSelection(sheet) {
  const highlight = CONFIG.SEX_HIGHLIGHT_COLOR.toLowerCase();
  if (sheet.getRange(FORM_CELLS.SEX_MALE).getBackground().toLowerCase() === highlight) {
    return '男';
  }
  if (sheet.getRange(FORM_CELLS.SEX_FEMALE).getBackground().toLowerCase() === highlight) {
    return '女';
  }
  return '';
}

/**
 * チェック結果シートを（作り直して）書き出す。
 * @param {{results: Array<Object>, summary: string}} check
 */
function writeCheckResults(check) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const existing = ss.getSheetByName(CONFIG.CHECK_SHEET_NAME);
  if (existing) {
    ss.deleteSheet(existing);
  }
  const sheet = ss.insertSheet(CONFIG.CHECK_SHEET_NAME);

  const rows = check.results.map((r) => [
    r.item,
    r.source,
    r.application_value,
    r.original_value,
    r.verdict,
    r.comment,
  ]);
  sheet.getRange(1, 1, 1, CHECK_HEADERS.length).setValues([CHECK_HEADERS.slice()]).setFontWeight('bold');
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, CHECK_HEADERS.length).setValues(rows);
    check.results.forEach((r, i) => {
      const color = VERDICT_COLORS[r.verdict];
      if (color) {
        sheet.getRange(2 + i, 1, 1, CHECK_HEADERS.length).setBackground(color);
      }
    });
  }
  sheet.getRange(rows.length + 3, 1).setValue('まとめ: ' + (check.summary || ''));

  sheet.setFrozenRows(1);
  sheet.setColumnWidths(1, 2, 130);
  sheet.setColumnWidths(3, 2, 200);
  sheet.setColumnWidth(5, 70);
  sheet.setColumnWidth(6, 320);
  ss.setActiveSheet(sheet);
}
