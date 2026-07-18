/**
 * Drive操作（入力フォルダから書類画像を読み込む）。
 */

/** Claude visionに渡せる画像形式 */
const SUPPORTED_IMAGE_TYPES = Object.freeze(['image/jpeg', 'image/png', 'image/gif', 'image/webp']);

/**
 * 入力フォルダの画像を読み込み、base64化して返す。
 * @return {Array<{name: string, mediaType: string, base64: string}>}
 */
function loadInputImages() {
  if (!CONFIG.INPUT_FOLDER_ID || CONFIG.INPUT_FOLDER_ID.indexOf('ここに') === 0) {
    throw new Error('CONFIG.INPUT_FOLDER_ID が未設定です。01_config.gs に入力フォルダのIDを設定してください。');
  }

  let folder;
  try {
    folder = DriveApp.getFolderById(CONFIG.INPUT_FOLDER_ID);
  } catch (e) {
    throw new Error('入力フォルダが開けません。CONFIG.INPUT_FOLDER_ID を確認してください: ' + CONFIG.INPUT_FOLDER_ID);
  }

  const images = [];
  const files = folder.getFiles();
  while (files.hasNext() && images.length < CONFIG.MAX_INPUT_IMAGES) {
    const file = files.next();
    const mimeType = file.getMimeType();
    if (SUPPORTED_IMAGE_TYPES.indexOf(mimeType) === -1) {
      continue;
    }
    images.push({
      name: file.getName(),
      mediaType: mimeType,
      base64: Utilities.base64Encode(file.getBlob().getBytes()),
    });
  }

  if (images.length === 0) {
    throw new Error('入力フォルダに画像（JPEG/PNG）がありません。在留カード・パスポートの見本画像を入れてください。');
  }
  return images;
}
