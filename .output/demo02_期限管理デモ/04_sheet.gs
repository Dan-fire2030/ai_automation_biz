/**
 * スプレッドシートの読み書き。
 * 「期限管理」シートを入力、「催促ログ」シートを出力として使う。
 * 列は見出し名で引く（列順が多少変わっても壊れないように）。
 */

/**
 * 期限管理シートを読み、案件オブジェクトの配列を返す。
 * 各オブジェクトはシート参照と行番号を持ち、後で自動更新列を書き戻せる。
 * @return {Array<{name, company, email, procedure, dueDate: Date, status, lastStageLevel: number, sheet, row, colIndex}>}
 */
function readDeadlineCases() {
  const sheet = getOrCreateSheet(CONFIG.DEADLINE_SHEET_NAME, DEADLINE_HEADERS);
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    return [];
  }
  const colIndex = buildHeaderIndex(values[0]);
  const cases = [];

  for (let r = 1; r < values.length; r++) {
    const row = values[r];
    const procedure = String(row[colIndex['手続き種別']] || '').trim();
    const rawDue = row[colIndex['期限日']];
    // 手続き種別も期限日もない行は空行とみなしてスキップ
    if (!procedure && !rawDue) {
      continue;
    }
    const dueDate = parseDate(rawDue);
    if (!dueDate) {
      logError(new Error(`期限日を日付として解釈できません: "${rawDue}"`), `行${r + 1}`);
      continue;
    }
    cases.push({
      name: String(row[colIndex['顧客名']] || '').trim(),
      company: String(row[colIndex['会社名・事務所名']] || '').trim(),
      email: String(row[colIndex['メールアドレス']] || '').trim(),
      procedure: procedure,
      dueDate: dueDate,
      status: String(row[colIndex['ステータス']] || '').trim(),
      lastStageLevel: parseStageLevel(row[colIndex['最終催促ステージ']]),
      sheet: sheet,
      row: r + 1, // 1始まりの行番号
      colIndex: colIndex,
    });
  }
  return cases;
}

/**
 * 見出し行から「見出し名 → 0始まり列インデックス」のマップを作る。
 * 必須の見出しが欠けていればエラーで落とす。
 * @param {Array} headerRow
 * @return {Object<string, number>}
 */
function buildHeaderIndex(headerRow) {
  const index = {};
  headerRow.forEach((h, i) => {
    index[String(h).trim()] = i;
  });
  const missing = DEADLINE_HEADERS.filter((h) => !(h in index));
  if (missing.length > 0) {
    throw new Error(
      '期限管理シートの見出しが不足しています: ' + missing.join(', ') +
      '（1行目の見出しを DEADLINE_HEADERS と一致させてください）'
    );
  }
  return index;
}

/** 残日数の列を更新する（0始まり列インデックス→1始まり列番号に変換） */
function updateDaysLeft(deadlineCase, daysLeft) {
  const col = deadlineCase.colIndex['残日数'] + 1;
  deadlineCase.sheet.getRange(deadlineCase.row, col).setValue(daysLeft);
}

/** 最終催促ステージ・最終催促日を書き込む */
function markReminded(deadlineCase, stage, today) {
  const stageCol = deadlineCase.colIndex['最終催促ステージ'] + 1;
  const dateCol = deadlineCase.colIndex['最終催促日'] + 1;
  deadlineCase.sheet.getRange(deadlineCase.row, stageCol).setValue(`${stage.level}:${stage.label}`);
  deadlineCase.sheet.getRange(deadlineCase.row, dateCol).setValue(today);
}

/** 催促ログシートに1行追記する（何をやったかの証跡＝デモで見せる価値） */
function appendLogRow(deadlineCase, daysLeft, stage, reminder, draftCreated) {
  const sheet = getOrCreateSheet(CONFIG.LOG_SHEET_NAME, LOG_HEADERS);
  const checklist = reminder.document_checklist.map((d, i) => `${i + 1}. ${d}`).join('\n');
  const draftText = draftCreated
    ? reminder.reminder_body + '\n\n【必要書類の目安】\n' + checklist
    : '（メールアドレス未登録のため下書きは作成せず）\n' + reminder.reminder_body;
  sheet.appendRow([
    new Date(),
    deadlineCase.name,
    deadlineCase.procedure,
    deadlineCase.dueDate,
    daysLeft,
    stage.label,
    reminder.reminder_subject,
    draftText,
  ]);
}

/** 指定ステータスが「完了扱い」か */
function isDoneStatus(status) {
  return DONE_STATUSES.indexOf(String(status).trim()) !== -1;
}

/**
 * 指定名のシートを取得し、なければ見出し付きで作成する。
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

/** 見出し行を残してデータ行（2行目以降）を消す（ダミー再投入用） */
function clearDataRows(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clearContent();
  }
}

/* ---------- 日付ヘルパー ---------- */

/** 時刻を切り落として日付だけにする（比較を安定させる） */
function toDateOnly(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

/**
 * セルの値（Date or 文字列）を日付に変換する。解釈できなければ null。
 * @param {*} value
 * @return {Date|null}
 */
function parseDate(value) {
  if (value instanceof Date && !isNaN(value.getTime())) {
    return toDateOnly(value);
  }
  const text = String(value || '').trim();
  if (!text) {
    return null;
  }
  const parsed = new Date(text.replace(/年|月/g, '/').replace(/日/g, ''));
  return isNaN(parsed.getTime()) ? null : toDateOnly(parsed);
}

/** from から to までの日数（to が未来なら正、過去なら負） */
function daysBetween(from, to) {
  const MS_PER_DAY = 24 * 60 * 60 * 1000;
  return Math.round((toDateOnly(to).getTime() - toDateOnly(from).getTime()) / MS_PER_DAY);
}

/** 「最終催促ステージ」列の値（例 "3:30日前"）からlevel数値を取り出す。未通知は0 */
function parseStageLevel(value) {
  const text = String(value || '').trim();
  if (!text) {
    return 0;
  }
  const level = parseInt(text.split(':')[0], 10);
  return isNaN(level) ? 0 : level;
}
