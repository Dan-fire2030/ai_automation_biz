/**
 * Claude API 呼び出し。
 * 構造化出力（output_config.format の JSON Schema）で、応答が必ず
 * 検証可能なJSONで返るようにしている。
 */

/** Claudeに返させるJSONのスキーマ（構造化出力で強制する） */
const REMINDER_SCHEMA = Object.freeze({
  type: 'object',
  properties: {
    reminder_subject: { type: 'string', description: '顧客への催促メールの件名' },
    reminder_body: {
      type: 'string',
      description: '催促メール本文（敬体・署名なし。残日数と期限を明記し、次の行動を促す）',
    },
    document_checklist: {
      type: 'array',
      items: { type: 'string' },
      description: '一般的に必要となる書類の目安（3〜6個。あくまで目安で、詳細は面談で確認する旨を本文に添える）',
    },
    internal_note: {
      type: 'string',
      description: '担当者向けの一言メモ（優先度・注意点など。顧客には送らない）',
    },
  },
  required: ['reminder_subject', 'reminder_body', 'document_checklist', 'internal_note'],
  additionalProperties: false,
});

const REMINDER_SYSTEM_PROMPT = [
  'あなたは士業事務所の期限管理アシスタントです。',
  '顧客への「更新・提出期限のリマインドメール」の下書きを作成します。',
  'ルール：',
  '- 法的助言はしない。手続きの一般的な段取りと必要書類の"目安"を示すにとどめる',
  '- 必要書類は「一般的な目安であり、詳細は面談で確認する」旨を本文に必ず添える',
  '- 期限日と残日数を本文で明確に伝え、いつまでに何をすべきか（面談予約・書類準備）を促す',
  '- トーンは残日数に応じて調整する：余裕があれば丁寧な事前案内、残りわずかや期限超過なら至急の連絡を促す',
  '- 顧客を不安にさせすぎず、「事務所がフォローする」という安心感を持たせる',
  '- 署名は含めない（担当者が追記する）。自動送信はせず、担当者が確認して送る前提',
].join('\n');

/**
 * 案件情報をClaudeに渡し、催促メールの下書き（構造化）を生成する。
 * @param {{name: string, company: string, procedure: string, dueDate: Date}} deadlineCase
 * @param {number} daysLeft
 * @param {{label: string}} stage
 * @return {{reminder_subject: string, reminder_body: string, document_checklist: string[], internal_note: string}}
 */
function generateReminderWithClaude(deadlineCase, daysLeft, stage) {
  const dueText = Utilities.formatDate(deadlineCase.dueDate, Session.getScriptTimeZone(), 'yyyy年M月d日');
  const daysText = daysLeft >= 0 ? `残り${daysLeft}日` : `期限を${Math.abs(daysLeft)}日超過`;

  const userMessage = [
    '以下の案件について、顧客へ送る期限リマインドメールの下書きを作成してください。',
    '',
    `事務所名: ${CONFIG.OFFICE_NAME || '（未設定）'}`,
    `顧客名: ${deadlineCase.name}`,
    `会社名・事務所名: ${deadlineCase.company || '（未記入）'}`,
    `手続き種別: ${deadlineCase.procedure}`,
    `期限日: ${dueText}`,
    `期限までの状況: ${daysText}（ステージ: ${stage.label}）`,
  ].join('\n');

  const payload = {
    model: CONFIG.MODEL,
    max_tokens: CONFIG.MAX_TOKENS,
    system: REMINDER_SYSTEM_PROMPT,
    output_config: { format: { type: 'json_schema', schema: REMINDER_SCHEMA } },
    messages: [{ role: 'user', content: userMessage }],
  };

  const response = callClaudeApi(payload);
  return parseReminderResponse(response);
}

/**
 * Claude API を呼ぶ（429/5xxは1回だけリトライ）。
 * @param {Object} payload
 * @return {Object} APIレスポンス（JSONパース済み）
 */
function callClaudeApi(payload) {
  const request = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'x-api-key': getApiKey(),
      'anthropic-version': CONFIG.API_VERSION,
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  let httpResponse = UrlFetchApp.fetch(CONFIG.API_URL, request);
  let status = httpResponse.getResponseCode();

  if (status === 429 || status >= 500) {
    Utilities.sleep(5000);
    httpResponse = UrlFetchApp.fetch(CONFIG.API_URL, request);
    status = httpResponse.getResponseCode();
  }

  const bodyText = httpResponse.getContentText();
  if (status !== 200) {
    throw new Error(`Claude API エラー (HTTP ${status}): ${bodyText.slice(0, 500)}`);
  }
  return JSON.parse(bodyText);
}

/**
 * APIレスポンスを検証してパースする。
 * @param {Object} response
 * @return {Object} 検証済みの下書きデータ
 */
function parseReminderResponse(response) {
  if (response.stop_reason === 'refusal') {
    throw new Error('Claudeがこのリクエストへの応答を拒否しました。案件内容を確認してください。');
  }
  if (response.stop_reason === 'max_tokens') {
    throw new Error('応答がトークン上限で途切れました。CONFIG.MAX_TOKENS を増やしてください。');
  }

  const textBlock = (response.content || []).find((block) => block.type === 'text');
  if (!textBlock) {
    throw new Error('APIレスポンスにテキストが含まれていません: ' + JSON.stringify(response).slice(0, 300));
  }

  const parsed = JSON.parse(textBlock.text);
  const missing = REMINDER_SCHEMA.required.filter((field) => !(field in parsed));
  if (missing.length > 0) {
    throw new Error('下書きデータに必須フィールドが欠けています: ' + missing.join(', '));
  }
  return parsed;
}
