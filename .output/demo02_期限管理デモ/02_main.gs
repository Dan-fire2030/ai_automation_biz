/**
 * エントリポイント。
 * - installTrigger():        初回に1度だけ手動実行して「毎朝の自動チェック」を設置
 * - checkDeadlinesHandler(): 毎朝自動実行される本体（手動実行でもデモ可）
 * - seedDummyData():         デモ用のダミー案件を期限管理シートに投入（本番データは使わない）
 * - testRun():               seedDummyData → checkDeadlinesHandler を続けて実行（デモ練習用）
 */

/** 初回セットアップ：毎朝の時限トリガーを設置する（1度だけ手動実行） */
function installTrigger() {
  const alreadyInstalled = ScriptApp.getProjectTriggers().some(
    (t) => t.getHandlerFunction() === 'checkDeadlinesHandler'
  );
  if (alreadyInstalled) {
    Logger.log('トリガーは設置済みです。');
    return;
  }
  ScriptApp.newTrigger('checkDeadlinesHandler')
    .timeBased()
    .everyDays(1)
    .atHour(CONFIG.DAILY_TRIGGER_HOUR)
    .create();
  Logger.log('毎朝%s時の自動チェックを設置しました。', CONFIG.DAILY_TRIGGER_HOUR);
}

/**
 * 本体：期限管理シートを走査し、催促が必要な案件の下書きを作る。
 * 1. 各行の残日数を再計算してシートに反映
 * 2. 完了案件はスキップ
 * 3. 前回より緊急なステージに入った案件だけClaudeで催促文を生成
 * 4. Gmail下書き作成 ＋ ログ記録 ＋ 行の「最終催促ステージ/日」を更新
 */
function checkDeadlinesHandler() {
  const today = toDateOnly(new Date());
  let cases;
  try {
    cases = readDeadlineCases();
  } catch (error) {
    logError(error, '期限管理シートの読み込み');
    return;
  }

  let remindedCount = 0;
  cases.forEach((deadlineCase) => {
    try {
      const daysLeft = daysBetween(today, deadlineCase.dueDate);
      updateDaysLeft(deadlineCase, daysLeft);

      if (isDoneStatus(deadlineCase.status)) {
        return;
      }
      const stage = determineStage(daysLeft);
      if (!shouldRemind(stage, deadlineCase.lastStageLevel)) {
        return;
      }

      const reminder = generateReminderWithClaude(deadlineCase, daysLeft, stage);
      const draftCreated = createReminderDraft(deadlineCase, reminder);
      appendLogRow(deadlineCase, daysLeft, stage, reminder, draftCreated);
      markReminded(deadlineCase, stage, today);
      remindedCount += 1;
    } catch (error) {
      logError(error, `案件処理: ${deadlineCase.name} / ${deadlineCase.procedure}`);
    }
  });

  Logger.log('チェック完了: 対象%s件中、新たに催促を作成したのは%s件', cases.length, remindedCount);
}

/**
 * 残日数からステージを判定する。しきい値以内で最も緊急な（levelが大きい）ものを返す。
 * どのステージにも該当しない（=まだ余裕がある）場合は null。
 * @param {number} daysLeft
 * @return {{level: number, label: string, maxDaysLeft: number}|null}
 */
function determineStage(daysLeft) {
  // level降順に見て、残日数がしきい値以内なら最初に一致したものを採用する
  const stages = REMINDER_STAGES.slice().sort((a, b) => b.level - a.level);
  for (const stage of stages) {
    if (daysLeft <= stage.maxDaysLeft) {
      return stage;
    }
  }
  return null;
}

/**
 * 催促を作るべきか。ステージに入っていて、かつ前回通知したステージより緊急なときだけ true。
 * これで「毎日同じ案件にメールを作る」スパムを防ぐ。
 * @param {{level: number}|null} stage
 * @param {number} lastStageLevel 前回通知したステージのlevel（未通知は0）
 * @return {boolean}
 */
function shouldRemind(stage, lastStageLevel) {
  if (!stage) {
    return false;
  }
  return stage.level > lastStageLevel;
}

/** デモ練習用：ダミー投入 → チェックを続けて実行 */
function testRun() {
  seedDummyData();
  checkDeadlinesHandler();
}

/**
 * デモ用のダミー案件を投入する。既存のデータ行は消してから入れ直す（本番データは扱わない）。
 * 自分のメールアドレスを入れた行は、実際にGmail下書きが確認できる。
 */
function seedDummyData() {
  const sheet = getOrCreateSheet(CONFIG.DEADLINE_SHEET_NAME, DEADLINE_HEADERS);
  clearDataRows(sheet);

  const myEmail = 'haruto.t1224@gmail.com'; // 下書きを確認したくない行は空にする
  const daysFromNow = (n) => {
    const d = toDateOnly(new Date());
    d.setDate(d.getDate() + n);
    return d;
  };

  // 残日数の異なる4件で、ステージ判定と文面のトーン変化を一度に見せる
  const dummyRows = [
    ['田中 建設', '田中建設株式会社', myEmail, '建設業許可の更新', daysFromNow(25), '未対応', '', '', ''],
    ['グエン様', 'さくら製作所（受入企業）', myEmail, '在留期間更新許可（技術・人文知識・国際業務）', daysFromNow(10), '未対応', '', '', ''],
    ['山本 運輸', '山本運輸有限会社', '', '産業廃棄物収集運搬業の更新', daysFromNow(80), '対応中', '', '', ''],
    ['佐藤商店', '佐藤商店', myEmail, '定期報告書の提出', daysFromNow(-3), '未対応', '', '', ''],
  ];
  sheet.getRange(2, 1, dummyRows.length, DEADLINE_HEADERS.length).setValues(dummyRows);
  Logger.log('ダミー案件を%s件投入しました。', dummyRows.length);
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
