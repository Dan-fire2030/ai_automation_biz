---
name: note-draft-post
description: note記事を「公開直前」まで一発で仕上げるエンドツーエンド手順。原稿確定→図解/ヘッダー画像のCodex生成→Chrome自動操作でnoteに下書き作成（本文＋画像＋アイキャッチ設定）→検証まで。note公式MCP/APIは存在しないためこの手順を使う。「noteに下書きを作って」「note公開直前まで」「note一発投稿」で発動。
---

# note公開直前まで一発投稿スキル（2026-07-18確立・実績あり）

ローカルの記事MD＋画像を、note.comの下書き（アイキャッチ設定済み・公開ボタンを押すだけの状態）まで自動で仕上げる確立手順。
実績：note⑤「AIは、毎回『記憶喪失』で出勤してくる」（下書きID: n7ddf80b1e1df）／note⑥「パワポを1枚も触らずに…」（下書きID: n0140f6415550・2026-07-19公開）／note⑦「頭の中の『やらなきゃ』を…」（下書きID: ne561036eb96a・2026-07-19公開・3回目の実戦でほぼ手順どおり一発）。

## 一発実行フロー（原稿確定後、ユーザー確認なしで最後まで走る）

原稿がOKになったら、以下を**途中で質問せず**一気に実行する（既定値は下記で確立済みのため確認不要）：

1. **画像生成（Codex委譲）**：本文図解 **1600×900**・ヘッダー **1280×670**、いずれもPNG・やわらかフラットイラスト調（クリーム背景＋淡い水色/オレンジ・丸ロボット）。保存先 `note/images/YYYY-MM-DD/`、命名 `◯◯NN_0_ヘッダー.png`／`◯◯NN_1_内容.png`…。2枚目以降は既存PNGの絶対パスをプロンプトに列挙してトーン統一。生成ごとに`sips`でサイズ確認＋Readで文字化け目視
2. **note下書き作成（Chrome自動操作）**：手順1〜4（タイトル→本文HTML paste→画像を正位置に挿入→保存）
3. **アイキャッチ設定**：手順5
4. **最終検証**：強制リロード→本文画像2枚＋アイキャッチ残存・文字数・画像位置（figureのprev/next）を確認してから完了報告
5. **ユーザーに残す作業はハッシュタグ設定と公開ボタンだけ**、と報告に明記する。ハッシュタグ案が確定している場合（note-brainstormスキル経由など）はコピペできる形で報告に再掲する

完了条件：リロード後のエディタで「タイトル・本文全文・本文画像（正位置）・アイキャッチ」が全て残っていること。トースト表示だけで完了と判断しない。

## 前提

- ユーザーのChromeがnoteにログイン済みであること（作業前に確認を依頼）
- 公開ボタンは絶対に押さない。**下書き保存まで**
- 原稿末尾の「公開前チェックリスト」ブロックと〔画像N：...〕プレースホルダ行は貼らない
- ハッシュタグ設定・公開はユーザー作業として残す（アイキャッチは手順0で生成→手順5で設定まで自動化できる）

## 手順0. ヘッダー画像（アイキャッチ）の用意

- **noteのヘッダー画像推奨サイズは 1280×670**（2026年7月時点）
- **⚠️ヘッダーのデザインはシリーズ全記事で統一する（2026-07-19ユーザー指摘・1敗）**：クリーム背景＋パステル水色/淡いオレンジの雲＋白い丸ロボット＋濃い茶色の丸ゴシック体タイトル。**記事のテーマに引っ張られて別テイスト（例：紺のコンサル調）にしない**。プロンプトには必ず**直前記事のヘッダーPNGの絶対パス**（例：`note/images/2026-07-18/knowhow01_0_ヘッダー.png`）を参照指定し「シリーズとして並んだとき同一シリーズに見えること最優先」と書く。記事テーマの要素はイラストの小物（ロボットが持つ物・周りに置く物）で表現する
- AGENTS.mdの画像生成ルールに従い**Codexに委譲**して生成し、本文画像と同じ `note/images/YYYY-MM-DD/` に `◯◯_0_ヘッダー.png` の連番0で保存する（例：`knowhow01_0_ヘッダー.png`）
- プロンプトには「記事タイトル文字を大きく配置」「日本語の文字化け・存在しない漢字を作らない」を明記
- ※本文図解・本文掲載画像は記事内容に合わせたテイストでよい（統一必須なのはヘッダーのみ）。アイキャッチを差し替える場合は、既存アイキャッチ右上の×で削除→カメラアイコンから再設定でOK
- 生成後に `sips -g pixelWidth -g pixelHeight` でサイズ確認＋Readで文字化け目視
- note側への設定は手順5で自動化する

## 手順

### 1. エディタを開く

`https://note.com/notes/new` へ navigate（`editor.note.com/notes/nXXXX/edit/` にリダイレクトされる）。
本文エディタは `.ProseMirror`（contenteditable）。タイトルはエディタ上部の「記事タイトル」をクリックして computer type で入力。

### 2. 本文はHTML変換してpasteイベントで貼る

Markdown直貼りはNG（`##`や`>`が文字のまま残る）。MDを自分でHTMLに変換し、javascript_toolで貼る：

```js
const editor = document.querySelector('.ProseMirror');
editor.focus();
const html = `<p>…</p><h2>…</h2>…`;  // ## → h2, ### → h3, **→strong, 引用→blockquote, --- → hr, 段落内改行→<br>
const dt = new DataTransfer();
dt.setData('text/html', html);
dt.setData('text/plain', 'x');
editor.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
```

見出し（目次に反映）・太字・ul/ol・blockquote・hrまで正しく再現される。
画像位置で本文を分割し、「前半→画像1→中盤→画像2→後半」の順に流し込む。

### 3. 画像挿入（⚠️最重要・1敗した箇所）

**NG：「＋メニュー→画像」のfile inputへ直接アップロード**。画面には表示されるが**下書き保存に画像が含まれず、リロードで消える**。

**OK：クリップボード画像貼り付けと同じ経路に流す**：

1. 自作の隠しinputをページに追加：
   ```js
   const inp = document.createElement('input'); inp.type='file'; inp.id='claude-file-src';
   inp.style.cssText='display:block;position:fixed;top:0;left:0;width:140px;height:24px;z-index:99999;';
   document.body.appendChild(inp);
   ```
2. `find`ツールで「file input at top left corner」を検索→refを取得→`file_upload`でローカル画像を載せる
3. **挿入位置の確定（ここも1敗）**：
   - 対象段落を`find`で探して**実クリック**（ProseMirrorの内部カーソルを動かすため。JSのselection変更だけでは同期しない）
   - JSでDOM選択を段落末尾へ：`range.selectNodeContents(p); range.collapse(false)`
   - **約1秒waitしてから**（ProseMirrorがselectionchangeを取り込むのを待つ。待たないと文末に入る）
4. pasteイベントでFileを渡す：
   ```js
   const file = document.getElementById('claude-file-src').files[0];
   const dt = new DataTransfer(); dt.items.add(file);
   document.querySelector('.ProseMirror').dispatchEvent(
     new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
   ```
5. 5秒ほど待ち、`img.src`が`https://assets.st-note.com/...`になったこと＋`closest('figure')`の前後要素で位置を確認
6. 位置を間違えたら：画像を実クリックで選択→`cmd+x`→正しい位置に実クリック＋選択セット＋1秒wait→`cmd+v`で移動できる
7. **連続画像はpaste連打でOK（2026-07-19発見）**：画像paste後のカーソルは挿入されたfigureの直後に自動で来るため、1→2→3枚目と続けて貼る場合はクリックし直し不要
8. **⚠️文末がfigureのときの追記（2026-07-19・1敗）**：文書末尾が画像のとき、HTML pasteや「図の下の余白クリック」は**figcaption（キャプション）に入ってしまう**（text/plainの'x'がキャプション混入。cmd+zで復旧可）。正解＝**画像を実クリックしてノード選択→ArrowRight→Returnで図の直後に空段落を作ってから**pasteする

### 4. 保存と検証（トーストを信じない）

1. 「下書き保存」クリック→「下書きを保存しました」トースト確認
2. **強制リロードで再検証**：保存済みでも離脱ダイアログ（Leave site?）が出て、JSの`location.reload()`や通常navigateはブロックされる。**navigateツールに`force: true`を付けて**同URLへ（クエリ`?v=N`を変えると確実）
3. リロード後に `performance.timeOrigin` で本当に再読み込みされたか確認（**過去にリロードされておらず検証が無効だったことがある**）
4. `.ProseMirror img` の残存と前後要素、文字数を確認して完了報告

### 5. アイキャッチ（ヘッダー画像）の設定（2026-07-18自動化成功）

1. エディタ最上部の画像アイコン（タイトルの上・カメラマーク）を実クリック→メニューが開く（「画像をアップロード 推奨サイズ：1280×670px」の表記あり）
2. **先にclickサプレッションパッチを入れておく**（本文画像と同じ`HTMLInputElement.prototype.click`の上書き）→「画像をアップロード」をクリック→inputが捕獲される
3. 捕獲inputをDOMに追加・可視化→`find`でref取得→`file_upload`でヘッダーPNGを渡す
4. **切り抜きダイアログ**が開く（1280×670ぴったりならそのまま）→「保存」ボタンをクリック。**1回で反応しないことがある**ので、スクショでダイアログが閉じたか確認し、閉じてなければもう一度クリック
5. タイトル上にヘッダーが表示されたら「下書き保存」→強制リロード→アイキャッチ（`rectangle_large`を含むassets.st-note.comのimg）が残っているか確認。**この経路は保存が持続する**（本文画像と違いinput直接アップロードでOK。アイキャッチは記事本文と別管理のため）

### 6. 後片付け

- 自作input（`#claude-file-src`）を`remove()`
- `HTMLInputElement.prototype.click`等にパッチを当てた場合はリロードで復元

## 落とし穴まとめ

| 症状 | 原因 | 対策 |
|---|---|---|
| 記法が文字のまま | MD直貼り | HTML変換してtext/htmlでpaste |
| 画像が保存後に消える | ＋メニューのinput経由 | clipboardData.filesでpasteイベント |
| 画像が文末に入る | PM内部カーソル未同期 | 実クリック→JS選択→1秒wait→paste |
| リロードできない | 離脱ダイアログ | navigate force:true |
| 検証したつもりが未リロード | reload()が黙って失敗 | performance.timeOriginで確認 |
| 貼った文字がキャプションに混入 | 文末figure直下へのpaste/余白クリックはfigcaptionに入る | 画像実クリック→ArrowRight→Returnで空段落を作ってからpaste |
| 直前のfigureが消える | 画像直後に作った空段落へのHTML paste時、PMのNodeSelectionが残っているとfigureごと置換される（note⑦で1敗） | paste後に必ず`editor.querySelectorAll('img').length`を数えて前後確認。消えていたら挿入位置の段落末尾に実クリック＋JS選択→1秒wait→画像を再paste |
| cmd+Downで文末に行くとキャプションに入る | 文書末尾がfigureだとcmd+Downの着地点はfigcaption | 文末が画像のときはcmd+Downを使わず、画像実クリック→ArrowRight→Return |
| クリック座標がズレる | JSのgetBoundingClientRect座標とスクショ座標はスケールが違う（例:innerWidth=2560 vs スクショ幅1558） | クリック座標はスクショを見て直接決める。JSのwindow.scrollはエディタに打ち消される→computerのscrollアクションを使う |
| 分割pasteで境界の段落が結合する（2026-07-20・2箇所で発生） | 本文を複数回に分けてHTML pasteすると、後続pasteの先頭ブロック（<p>や<ul>の最初の<li>）がカーソルのある直前段落にマージされる | paste完了後に各境界の段落を必ず検証（innerTextに次ブロックの文が混ざっていないか）。結合していたら該当範囲（段落〜ul）を実クリック→JSでrange選択→1秒wait→正しいHTMLをpasteすると選択範囲ごと置換で直せる |
