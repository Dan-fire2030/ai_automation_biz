/**
 * Claude API 呼び出し。
 * 構造化出力（output_config.format の JSON Schema）で、応答が必ず
 * 検証可能なJSONで返るようにしている。
 */

/** Claudeに返させるJSONのスキーマ（構造化出力で強制する） */
const ANALYSIS_SCHEMA = Object.freeze({
  type: 'object',
  properties: {
    category: {
      type: 'string',
      enum: ['許認可', '契約・法務', '相続', '会社設立', '労務・人手不足', '業務効率化', 'その他'],
      description: '相談内容の分類',
    },
    urgency: { type: 'string', enum: ['高', '中', '低'], description: '緊急度' },
    summary: { type: 'string', description: '案件サマリー（2〜3文、敬体）' },
    key_points: {
      type: 'array',
      items: { type: 'string' },
      description: '論点・確認事項（3〜5個）',
    },
    questions: {
      type: 'array',
      items: { type: 'string' },
      description: '初回面談前に確認すべき事前質問（3〜5個）',
    },
    reply_subject: { type: 'string', description: '返信メールの件名' },
    reply_body: { type: 'string', description: '返信メールの本文（敬体・署名なし）' },
  },
  required: [
    'category',
    'urgency',
    'summary',
    'key_points',
    'questions',
    'reply_subject',
    'reply_body',
  ],
  additionalProperties: false,
});

const SYSTEM_PROMPT = [
  'あなたは小規模事務所の新規相談受付を整理するアシスタントです。',
  '入力される相談内容から、事務所の担当者がすぐ動けるように情報を構造化してください。',
  'ルール：',
  '- 推測で断定しない。相談文に書かれていないことは質問リストに回す',
  '- 法的助言はしない（論点の整理と確認事項の列挙まで）',
  '- 返信メールは「受け付けた・いつ頃連絡する・面談で何を聞くか」が伝わる丁寧な文面にする',
  '- 返信メールに署名は含めない（担当者が追記する）',
].join('\n');

/**
 * 相談内容をClaudeで分析し、検証済みの構造化データを返す。
 * @param {{name: string, company: string, email: string, body: string}} inquiry
 * @return {{category: string, urgency: string, summary: string, key_points: string[], questions: string[], reply_subject: string, reply_body: string}}
 */
function analyzeInquiryWithClaude(inquiry) {
  const userMessage = [
    '以下の新規相談を整理してください。',
    '',
    `お名前: ${inquiry.name}`,
    `会社名・事務所名: ${inquiry.company || '（未記入）'}`,
    '相談内容:',
    inquiry.body,
  ].join('\n');

  const payload = {
    model: CONFIG.MODEL,
    max_tokens: CONFIG.MAX_TOKENS,
    system: SYSTEM_PROMPT,
    output_config: { format: { type: 'json_schema', schema: ANALYSIS_SCHEMA } },
    messages: [{ role: 'user', content: userMessage }],
  };

  const response = callClaudeApi(payload);
  return parseAnalysisResponse(response);
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
 * @return {Object} 検証済みの分析結果
 */
function parseAnalysisResponse(response) {
  if (response.stop_reason === 'refusal') {
    throw new Error('Claudeがこのリクエストへの応答を拒否しました。相談内容を確認してください。');
  }
  if (response.stop_reason === 'max_tokens') {
    throw new Error('応答がトークン上限で途切れました。CONFIG.MAX_TOKENS を増やしてください。');
  }

  const textBlock = (response.content || []).find((block) => block.type === 'text');
  if (!textBlock) {
    throw new Error('APIレスポンスにテキストが含まれていません: ' + JSON.stringify(response).slice(0, 300));
  }

  const parsed = JSON.parse(textBlock.text);
  const missing = ANALYSIS_SCHEMA.required.filter((field) => !(field in parsed));
  if (missing.length > 0) {
    throw new Error('分析結果に必須フィールドが欠けています: ' + missing.join(', '));
  }
  return parsed;
}
