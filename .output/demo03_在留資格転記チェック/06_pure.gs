/**
 * 純関数（GASのAPIに依存しない）。ローカルnodeで単体検証できるよう分離している。
 * 検証スクリプト: このファイルを読み込んで実行する（SETUP.md参照）。
 */

/**
 * OCR抽出結果（EXTRACT_SCHEMA形式）を、シート転記用の値（SAMPLE_FORM_VALUES形式）に変換する。
 * 日付の0（読めなかった印）は undefined にして「書き込まない」扱いにする。
 * @param {Object} extracted
 * @return {Object}
 */
function extractedToFormValues(extracted) {
  const card = extracted.residence_card || {};
  const passport = extracted.passport || {};
  const passportFound = passport.found === true;

  return {
    nationality: textOrEmpty(card.nationality_region),
    birthYear: positiveOrUndefined(card.birth_date && card.birth_date.year),
    birthMonth: positiveOrUndefined(card.birth_date && card.birth_date.month),
    birthDay: positiveOrUndefined(card.birth_date && card.birth_date.day),
    name: textOrEmpty(card.name_roman),
    sex: card.sex === '男' || card.sex === '女' ? card.sex : '',
    passportNumber: passportFound ? textOrEmpty(passport.passport_number) : '',
    passportExpYear: passportFound ? positiveOrUndefined(passport.expiration && passport.expiration.year) : undefined,
    passportExpMonth: passportFound ? positiveOrUndefined(passport.expiration && passport.expiration.month) : undefined,
    passportExpDay: passportFound ? positiveOrUndefined(passport.expiration && passport.expiration.day) : undefined,
    statusOfResidence: textOrEmpty(card.status_of_residence),
    periodOfStay: textOrEmpty(card.period_of_stay),
    stayExpYear: positiveOrUndefined(card.stay_expiration && card.stay_expiration.year),
    stayExpMonth: positiveOrUndefined(card.stay_expiration && card.stay_expiration.month),
    stayExpDay: positiveOrUndefined(card.stay_expiration && card.stay_expiration.day),
    cardNumber: textOrEmpty(card.card_number),
  };
}

/**
 * シートから読んだ生の記載（文字列）を、突合チェックに渡す項目リストに組み立てる。
 * CHECK_FIELDS の全項目を、日付は「YYYY年M月D日」に結合して返す。
 * @param {Object} raw readFormSheet が読んだ値（すべて表示文字列）
 * @return {Array<{key: string, label: string, source: string, value: string}>}
 */
function buildApplicationValues(raw) {
  const valueByKey = {
    nationality: cleanText(raw.nationality),
    birth_date: joinDateText(raw.birthYear, raw.birthMonth, raw.birthDay),
    name: cleanText(raw.name),
    sex: cleanText(raw.sex),
    status_of_residence: cleanText(raw.statusOfResidence),
    period_of_stay: cleanText(raw.periodOfStay),
    stay_expiration: joinDateText(raw.stayExpYear, raw.stayExpMonth, raw.stayExpDay),
    card_number: cleanText(raw.cardNumber),
    passport_number: cleanText(raw.passportNumber),
    passport_expiration: joinDateText(raw.passportExpYear, raw.passportExpMonth, raw.passportExpDay),
  };

  return CHECK_FIELDS.map((field) => ({
    key: field.key,
    label: field.label,
    source: field.source,
    value: valueByKey[field.key] !== undefined ? valueByKey[field.key] : '',
  }));
}

/**
 * 年・月・日の文字列を「YYYY年M月D日」に結合する。どれかが空なら空文字。
 * @param {string|number} year
 * @param {string|number} month
 * @param {string|number} day
 * @return {string}
 */
function joinDateText(year, month, day) {
  const y = cleanText(year);
  const m = cleanText(month);
  const d = cleanText(day);
  if (y === '' || m === '' || d === '') {
    return '';
  }
  return `${y}年${m}月${d}日`;
}

/**
 * 値を整形済みテキストにする（trim。null/undefinedは空文字）。
 * @param {*} value
 * @return {string}
 */
function cleanText(value) {
  if (value === undefined || value === null) {
    return '';
  }
  return String(value).trim();
}

/**
 * 正の整数ならそのまま、それ以外（0＝読めなかった印を含む）は undefined。
 * @param {*} value
 * @return {number|undefined}
 */
function positiveOrUndefined(value) {
  return typeof value === 'number' && value > 0 ? value : undefined;
}

/**
 * テキストならtrimして返し、空なら空文字。
 * @param {*} value
 * @return {string}
 */
function textOrEmpty(value) {
  return typeof value === 'string' ? value.trim() : '';
}
