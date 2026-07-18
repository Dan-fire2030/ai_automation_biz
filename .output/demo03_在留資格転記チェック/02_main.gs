/**
 * エントリーポイント（メニューと3つのデモ操作）。
 *
 * ① 画像から申請書ドラフト作成 …… Driveの画像をOCR→様式のコピーに転記
 * ② 申請書サンプル（誤り入り）を作成 …… 突合デモ用の誤り3種入りサンプル
 * ③ 申請書と原本を突合チェック …… サンプル×原本画像を照合→チェック結果シート
 */

/** スプレッドシートを開いたときにメニューを追加する */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('AI書類デモ')
    .addItem('① 画像から申請書ドラフト作成', 'createDraftFromImages')
    .addItem('② 申請書サンプル（誤り入り）を作成', 'createErrorSample')
    .addItem('③ 申請書と原本を突合チェック', 'runCrossCheck')
    .addToUi();
}

/** ① 入力フォルダの画像をOCRし、様式のコピーに転記した「申請書ドラフト」を作る */
function createDraftFromImages() {
  const ui = SpreadsheetApp.getUi();
  try {
    const images = loadInputImages();
    const extracted = extractFromImages(images);

    const sheetName =
      CONFIG.DRAFT_SHEET_PREFIX +
      Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'MMdd_HHmm');
    const sheet = copyFormSheet(sheetName);
    fillFormSheet(sheet, extractedToFormValues(extracted));

    const notes = extracted.reading_notes ? '\n\n読み取りメモ: ' + extracted.reading_notes : '';
    ui.alert(
      '申請書ドラフトを作成しました',
      `シート「${sheetName}」に転記済みです。\n空欄は身分証から取れない項目（先生の記入欄）です。${notes}`,
      ui.ButtonSet.OK
    );
  } catch (e) {
    ui.alert('エラー', String(e && e.message ? e.message : e), ui.ButtonSet.OK);
    throw e;
  }
}

/** ② 突合チェックのデモ用に、誤り3種を仕込んだ申請書サンプルを作る */
function createErrorSample() {
  const ui = SpreadsheetApp.getUi();
  try {
    const existing = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SAMPLE_SHEET_NAME);
    if (existing) {
      SpreadsheetApp.getActiveSpreadsheet().deleteSheet(existing);
    }
    const sheet = copyFormSheet(CONFIG.SAMPLE_SHEET_NAME);
    fillFormSheet(sheet, SAMPLE_FORM_VALUES);
    ui.alert(
      'サンプルを作成しました',
      `シート「${CONFIG.SAMPLE_SHEET_NAME}」に誤りを3箇所仕込んであります。\n（どこかは③のチェックで見つかります）`,
      ui.ButtonSet.OK
    );
  } catch (e) {
    ui.alert('エラー', String(e && e.message ? e.message : e), ui.ButtonSet.OK);
    throw e;
  }
}

/** ③ 申請書サンプルの記載を原本画像と突合し、チェック結果シートを作る */
function runCrossCheck() {
  const ui = SpreadsheetApp.getUi();
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SAMPLE_SHEET_NAME);
    if (!sheet) {
      throw new Error(
        `シート「${CONFIG.SAMPLE_SHEET_NAME}」がありません。先に②でサンプルを作成してください。`
      );
    }
    const applicationValues = readFormSheet(sheet);
    const images = loadInputImages();
    const check = checkAgainstOriginals(applicationValues, images);
    writeCheckResults(check);

    const ngCount = check.results.filter((r) => r.verdict !== 'OK').length;
    ui.alert(
      '突合チェックが完了しました',
      `シート「${CONFIG.CHECK_SHEET_NAME}」に結果を書き出しました。\n指摘 ${ngCount} 件。${check.summary || ''}`,
      ui.ButtonSet.OK
    );
  } catch (e) {
    ui.alert('エラー', String(e && e.message ? e.message : e), ui.ButtonSet.OK);
    throw e;
  }
}
