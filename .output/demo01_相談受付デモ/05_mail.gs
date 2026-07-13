/**
 * Gmail返信下書きの作成。
 * 自動送信はしない — 「人が最終チェックして送る」前提のドラフト生成。
 */

/**
 * 返信メールの下書きを作成する（メールアドレスがない場合はスキップ）。
 * @param {{name: string, email: string}} inquiry
 * @param {{reply_subject: string, reply_body: string}} analysis
 * @return {boolean} 下書きを作成したか
 */
function createReplyDraft(inquiry, analysis) {
  if (!inquiry.email) {
    return false;
  }
  if (!isValidEmail(inquiry.email)) {
    Logger.log('メールアドレスの形式が不正なため下書きをスキップ: %s', inquiry.email);
    return false;
  }
  GmailApp.createDraft(inquiry.email, analysis.reply_subject, analysis.reply_body);
  return true;
}

/**
 * @param {string} email
 * @return {boolean}
 */
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
