/**
 * エントリポイント。
 * - installTrigger(): 初回に1度だけ手動実行してフォーム送信トリガーを設置
 * - onFormSubmitHandler(e): フォーム送信時に自動実行される本体
 * - testWithDummyData(): フォームなしでダミーデータで動作確認（デモ練習用）
 */

/** 初回セットアップ：フォーム送信トリガーを設置する（1度だけ手動実行） */
function installTrigger() {
  const alreadyInstalled = ScriptApp.getProjectTriggers().some(
    (t) => t.getHandlerFunction() === 'onFormSubmitHandler'
  );
  if (alreadyInstalled) {
    Logger.log('トリガーは設置済みです。');
    return;
  }
  ScriptApp.newTrigger('onFormSubmitHandler')
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onFormSubmit()
    .create();
  Logger.log('フォーム送信トリガーを設置しました。');
}

/**
 * フォーム送信時に呼ばれる本体。
 * フォーム回答 → Claudeで整理 → 案件管理シートに記録 ＋ 返信メール下書き作成
 * @param {GoogleAppsScript.Events.SheetsOnFormSubmit} e
 */
function onFormSubmitHandler(e) {
  try {
    const inquiry = parseFormSubmission(e);
    processInquiry(inquiry);
  } catch (error) {
    logError(error, e && e.namedValues ? JSON.stringify(e.namedValues) : '(no event data)');
  }
}

/**
 * フォーム送信イベントを検証し、相談内容オブジェクトに変換する。
 * @param {GoogleAppsScript.Events.SheetsOnFormSubmit} e
 * @return {{name: string, company: string, email: string, body: string, submittedAt: Date}}
 */
function parseFormSubmission(e) {
  if (!e || !e.namedValues) {
    throw new Error('フォーム送信イベントが不正です（namedValues がありません）。');
  }
  const pick = (title) => {
    const values = e.namedValues[title];
    return values && values[0] ? String(values[0]).trim() : '';
  };
  const inquiry = {
    name: pick(CONFIG.FORM_FIELDS.NAME),
    company: pick(CONFIG.FORM_FIELDS.COMPANY),
    email: pick(CONFIG.FORM_FIELDS.EMAIL),
    body: pick(CONFIG.FORM_FIELDS.BODY),
    submittedAt: new Date(),
  };
  if (!inquiry.name || !inquiry.body) {
    throw new Error(
      '必須項目（お名前・ご相談内容）が取得できません。フォームの質問タイトルと CONFIG.FORM_FIELDS が一致しているか確認してください。'
    );
  }
  return inquiry;
}

/**
 * 相談1件を処理する（Claude呼び出し → シート記録 → メール下書き）。
 * @param {{name: string, company: string, email: string, body: string, submittedAt: Date}} inquiry
 */
function processInquiry(inquiry) {
  const analysis = analyzeInquiryWithClaude(inquiry);
  appendCaseRow(inquiry, analysis);
  const draftCreated = createReplyDraft(inquiry, analysis);
  Logger.log(
    '処理完了: %s（分類: %s / 緊急度: %s / 下書き: %s）',
    inquiry.name,
    analysis.category,
    analysis.urgency,
    draftCreated ? '作成済み' : 'スキップ（メールアドレスなし）'
  );
}

/** デモ練習用：ダミーデータで一連の流れを実行する（本番データは使わない） */
function testWithDummyData() {
  const dummyInquiry = {
    name: '山田 太郎',
    company: '株式会社ダミー建設',
    email: 'haruto.t1224@gmail.com',  // 空にするとGmail下書きはスキップされる。自分のアドレスを入れれば下書きも確認できる
    body:
      '建設業の許可更新が近いのですが、必要書類が分からず困っています。' +
      '決算報告も毎年ぎりぎりで、事務員が先月退職してしまい手が回りません。' +
      '来月には新しい現場も始まるので、早めに相談したいです。',
    submittedAt: new Date(),
  };
  processInquiry(dummyInquiry);
}

/**
 * エラーをログシートとLoggerの両方に記録する。
 * @param {Error} error
 * @param {string} context
 */
function logError(error, context) {
  Logger.log('エラー: %s\n%s', error.message, error.stack || '');
  try {
    const sheet = getOrCreateSheet(CONFIG.ERROR_SHEET_NAME, ['日時', 'エラー内容', 'コンテキスト']);
    sheet.appendRow([new Date(), error.message, context]);
  } catch (sheetError) {
    Logger.log('エラーログシートへの記録にも失敗: %s', sheetError.message);
  }
}
