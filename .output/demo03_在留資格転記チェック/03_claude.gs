/**
 * Claude API 呼び出し（vision＋構造化出力）。
 * 応答は output_config.format の JSON Schema で必ず検証可能なJSONにする。
 */

/** 日付（西暦）の共通スキーマ */
const DATE_SCHEMA = Object.freeze({
  type: 'object',
  properties: {
    year: { type: 'integer', description: '西暦4桁。読めなければ0' },
    month: { type: 'integer', description: '1〜12。読めなければ0' },
    day: { type: 'integer', description: '1〜31。読めなければ0' },
  },
  required: ['year', 'month', 'day'],
  additionalProperties: false,
});

/** OCR抽出結果のスキーマ */
const EXTRACT_SCHEMA = Object.freeze({
  type: 'object',
  properties: {
    residence_card: {
      type: 'object',
      description: '在留カードから読み取った内容。カードが無ければ found=false',
      properties: {
        found: { type: 'boolean' },
        name_roman: { type: 'string', description: '氏名（カード表記のローマ字のまま）' },
        birth_date: DATE_SCHEMA,
        sex: { type: 'string', enum: ['男', '女', '不明'] },
        nationality_region: { type: 'string', description: '国籍・地域（カード表記のまま。例: 米国）' },
        status_of_residence: { type: 'string', description: '在留資格（例: 留学、技術・人文知識・国際業務）' },
        period_of_stay: { type: 'string', description: '在留期間（例: 4年3月）。満了日は含めない' },
        stay_expiration: DATE_SCHEMA,
        card_number: { type: 'string', description: '在留カード番号（英数12桁。例: AB12345678CD）' },
      },
      required: [
        'found',
        'name_roman',
        'birth_date',
        'sex',
        'nationality_region',
        'status_of_residence',
        'period_of_stay',
        'stay_expiration',
        'card_number',
      ],
      additionalProperties: false,
    },
    passport: {
      type: 'object',
      description: 'パスポートから読み取った内容。無ければ found=false',
      properties: {
        found: { type: 'boolean' },
        surname: { type: 'string' },
        given_names: { type: 'string' },
        passport_number: { type: 'string' },
        expiration: DATE_SCHEMA,
      },
      required: ['found', 'surname', 'given_names', 'passport_number', 'expiration'],
      additionalProperties: false,
    },
    reading_notes: {
      type: 'string',
      description: '読み取りに自信がない箇所・注意点（無ければ空文字）',
    },
  },
  required: ['residence_card', 'passport', 'reading_notes'],
  additionalProperties: false,
});

const EXTRACT_SYSTEM_PROMPT = [
  'あなたは行政書士事務所の書類読み取りアシスタントです。',
  '在留カードとパスポートの画像から、在留期間更新許可申請書に転記する項目を正確に読み取ります。',
  'ルール：',
  '- 記載を一字一句そのまま読み取る。推測で補完しない（読めない箇所は reading_notes に書く）',
  '- 氏名はカード・旅券の表記（ローマ字大文字）のまま。勝手にカナや漢字へ変換しない',
  '- 日付はすべて西暦の数値に変換する（和暦表記があれば西暦へ）',
  '- 番号類（在留カード番号・旅券番号）は英数字を1文字ずつ慎重に読む',
  '- 見本・SPECIMEN の透かしは無視してよい（公開見本を使ったデモである）',
  '- マイナンバー・個人番号らしき記載を見つけても絶対に出力しない',
].join('\n');

/** 突合チェック結果のスキーマ */
const CHECK_SCHEMA = Object.freeze({
  type: 'object',
  properties: {
    results: {
      type: 'array',
      description: '項目ごとの突合結果。渡された全項目について必ず1件ずつ返す',
      items: {
        type: 'object',
        properties: {
          item: { type: 'string', description: '項目名（渡されたラベルをそのまま使う）' },
          source: { type: 'string', description: '突合先（在留カード または パスポート）' },
          application_value: { type: 'string', description: '申請書の記載（そのまま）' },
          original_value: { type: 'string', description: '原本画像から読み取った記載' },
          verdict: { type: 'string', enum: ['OK', '不一致', '要確認'] },
          comment: {
            type: 'string',
            description: '指摘コメント。不一致なら「どこがどう違うか」を具体的に（例: 7文字目 Z→S）。OKなら空文字',
          },
        },
        required: ['item', 'source', 'application_value', 'original_value', 'verdict', 'comment'],
        additionalProperties: false,
      },
    },
    summary: { type: 'string', description: '全体の一言まとめ（例: 3件の不一致。氏名・生年月日・カード番号を要修正）' },
  },
  required: ['results', 'summary'],
  additionalProperties: false,
});

const CHECK_SYSTEM_PROMPT = [
  'あなたは行政書士事務所の申請書チェックアシスタントです。',
  '作成済みの在留期間更新許可申請書の記載を、原本（在留カード・パスポートの画像）と項目ごとに突合します。',
  'ルール：',
  '- 各項目は指定された突合先の書類とだけ比較する（カード由来の項目はカード、旅券由来の項目は旅券）',
  '- 表記ゆれ（全角/半角・スペース）は不一致にしない。文字・数字そのものの違いだけを指摘する',
  '- 不一致は「どの文字がどう違うか」まで具体的に指摘する（ミスの発見が目的）',
  '- 原本が不鮮明で断定できない項目は「要確認」にして理由を書く',
  '- 判定を偽らない。全項目OKならOKと返す',
].join('\n');

/**
 * 書類画像から申請書転記用の項目を抽出する。
 * @param {Array<{name: string, mediaType: string, base64: string}>} images
 * @return {Object} EXTRACT_SCHEMA 形式の抽出結果
 */
function extractFromImages(images) {
  const content = buildImageContent(images);
  content.push({
    type: 'text',
    text: '上の書類画像から、在留期間更新許可申請書に転記する項目を読み取ってください。',
  });

  const payload = {
    model: CONFIG.MODEL,
    max_tokens: CONFIG.MAX_TOKENS,
    system: EXTRACT_SYSTEM_PROMPT,
    output_config: { format: { type: 'json_schema', schema: EXTRACT_SCHEMA } },
    messages: [{ role: 'user', content: content }],
  };

  const parsed = parseStructuredResponse(callClaudeApi(payload), EXTRACT_SCHEMA);
  if (!parsed.residence_card.found) {
    throw new Error('画像の中に在留カードが見つかりませんでした。入力フォルダの画像を確認してください。');
  }
  return parsed;
}

/**
 * 申請書の記載を原本画像と突合する。
 * @param {Array<{key: string, label: string, source: string, value: string}>} applicationValues
 * @param {Array<{name: string, mediaType: string, base64: string}>} images
 * @return {{results: Array<Object>, summary: string}}
 */
function checkAgainstOriginals(applicationValues, images) {
  const lines = applicationValues.map(
    (f) => `- ${f.label}（突合先: ${f.source}）: ${f.value === '' ? '（空欄）' : f.value}`
  );
  const content = buildImageContent(images);
  content.push({
    type: 'text',
    text: [
      '上の原本画像と、以下の申請書の記載を項目ごとに突合してください。',
      '全項目について必ず結果を返してください。',
      '',
      '【申請書の記載】',
      ...lines,
    ].join('\n'),
  });

  const payload = {
    model: CONFIG.MODEL,
    max_tokens: CONFIG.MAX_TOKENS,
    system: CHECK_SYSTEM_PROMPT,
    output_config: { format: { type: 'json_schema', schema: CHECK_SCHEMA } },
    messages: [{ role: 'user', content: content }],
  };

  return parseStructuredResponse(callClaudeApi(payload), CHECK_SCHEMA);
}

/**
 * 画像リストをAPIのcontentブロック列に変換する（各画像の前にファイル名を添える）。
 * @param {Array<{name: string, mediaType: string, base64: string}>} images
 * @return {Array<Object>}
 */
function buildImageContent(images) {
  const content = [];
  images.forEach((img) => {
    content.push({ type: 'text', text: `ファイル名: ${img.name}` });
    content.push({
      type: 'image',
      source: { type: 'base64', media_type: img.mediaType, data: img.base64 },
    });
  });
  return content;
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
 * APIレスポンスを検証し、スキーマの必須フィールドを確認してパースする。
 * @param {Object} response
 * @param {Object} schema 必須フィールド検証に使うスキーマ
 * @return {Object}
 */
function parseStructuredResponse(response, schema) {
  if (response.stop_reason === 'refusal') {
    throw new Error('Claudeがこのリクエストへの応答を拒否しました。入力画像を確認してください。');
  }
  if (response.stop_reason === 'max_tokens') {
    throw new Error('応答がトークン上限で途切れました。CONFIG.MAX_TOKENS を増やしてください。');
  }

  const textBlock = (response.content || []).find((block) => block.type === 'text');
  if (!textBlock) {
    throw new Error('APIレスポンスにテキストが含まれていません: ' + JSON.stringify(response).slice(0, 300));
  }

  const parsed = JSON.parse(textBlock.text);
  const missing = (schema.required || []).filter((field) => !(field in parsed));
  if (missing.length > 0) {
    throw new Error('応答データに必須フィールドが欠けています: ' + missing.join(', '));
  }
  return parsed;
}
