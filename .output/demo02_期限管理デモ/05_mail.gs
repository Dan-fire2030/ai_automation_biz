/**
 * Gmail催促下書きの作成。
 * 自動送信はしない — 「人が最終チェックして送る」前提のドラフト生成。
 */

/**
 * 催促メールの下書きを作成する（メールアドレスがない/不正な場合はスキップ）。
 * 本文の末尾に「必要書類の目安」を付け、目安である旨の注記を添える。
 * @param {{email: string}} deadlineCase
 * @param {{reminder_subject: string, reminder_body: string, document_checklist: string[]}} reminder
 * @return {boolean} 下書きを作成したか
 */
function createReminderDraft(deadlineCase, reminder) {
  if (!deadlineCase.email) {
    return false;
  }
  if (!isValidEmail(deadlineCase.email)) {
    Logger.log('メールアドレスの形式が不正なため下書きをスキップ: %s', deadlineCase.email);
    return false;
  }
  const body = buildReminderBody(reminder);
  GmailApp.createDraft(deadlineCase.email, reminder.reminder_subject, body);
  return true;
}

/**
 * 本文に必要書類の目安ブロックを付ける。
 * @param {{reminder_body: string, document_checklist: string[]}} reminder
 * @return {string}
 */
function buildReminderBody(reminder) {
  const checklist = reminder.document_checklist.map((d, i) => `  ${i + 1}. ${d}`).join('\n');
  return [
    reminder.reminder_body,
    '',
    '━━━━━━━━━━━━━━━━━━',
    '【ご準備いただく書類の目安】',
    checklist,
    '',
    '※あくまで一般的な目安です。案件により異なりますので、詳しくは面談でご確認ください。',
    '━━━━━━━━━━━━━━━━━━',
  ].join('\n');
}

/**
 * @param {string} email
 * @return {boolean}
 */
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
