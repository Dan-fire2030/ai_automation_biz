---
name: note-draft-post
description: note記事を「公開直前」まで一発で仕上げるエンドツーエンド手順。原稿確定→図解/ヘッダー画像のCodex生成→Chrome自動操作でnoteに下書き作成（本文＋画像＋アイキャッチ設定）→検証まで。note公式MCP/APIは存在しないためこの手順を使う。「noteに下書きを作って」「note公開直前まで」「note一発投稿」で発動。
---

# note公開直前まで一発投稿スキル（2026-07-18確立・実績あり）

ローカルの記事MD＋画像を、note.comの下書き（アイキャッチ設定済み・公開ボタンを押すだけの状態）まで自動で仕上げる確立手順。
実績：note⑤「AIは、毎回『記憶喪失』で出勤してくる」（下書きID: n7ddf80b1e1df）／note⑥「パワポを1枚も触らずに…」（下書きID: n0140f6415550・2026-07-19公開）／note⑦「頭の中の『やらなきゃ』を…」（下書きID: ne561036eb96a・2026-07-19公開・3回目の実戦でほぼ手順どおり一発）／**note⑩「「大事なメール教えて」は効かない」（nd36f8c8d8f9a・2026-07-21公開・3,729字/画像4枚。全文1回pasteの新方式を確立し、分割pasteを廃止）**。

## 分業（2026-07-25）：入稿はnote-posterサブエージェントに委譲する

工程ごとにモデルを分けるため、以下で役割を分ける（`.claude/agents/note-poster.md`）：

- **メイン（Opus）**：ネタ出し（note-brainstorm）→原稿確定（承認ゲート）→**手順0/手順1のCodex画像生成まで**。画像は `note/images/YYYY-MM-DD/` に生成し、`ls`＋`sips`＋Read目視で実在・文字化けを確認する
- **note-posterサブエージェント（Sonnet固定）**：確定原稿MD＋生成済み画像PNGを受け取り、**手順1「エディタを開く」〜手順6のChrome入稿と検証**を実行

委譲するときは Agent ツールで `subagent_type: "note-poster"` を呼び、①「ユーザー承認済み（原稿確定）」の明示 ②原稿MDの絶対パス ③画像PNGの絶対パス（枚数・命名）④ハッシュタグ案 を渡す。**このSKILL.mdはサブエージェントが読む実行手順書**なので、以下の手順は入稿担当が参照する前提で書かれている。

## 一発実行フロー（原稿確定後、ユーザー確認なしで最後まで走る）

原稿がOKになったら、以下を**途中で質問せず**一気に実行する（既定値は下記で確立済みのため確認不要）。**手順1（Codex画像生成）はメインで、手順2以降のChrome入稿はnote-posterサブエージェントで**走らせる：

1. **画像生成（Codex委譲）**：本文図解 **1600×900**・ヘッダー **1280×670**、いずれもPNG・やわらかフラットイラスト調（クリーム背景＋淡い水色/オレンジ・丸ロボット）。保存先 `note/images/YYYY-MM-DD/`、命名 `◯◯NN_0_ヘッダー.png`／`◯◯NN_1_内容.png`…。2枚目以降は既存PNGの絶対パスをプロンプトに列挙してトーン統一。生成ごとに`sips`でサイズ確認＋Readで文字化け目視

   **⚠️Codex呼び出しの定型（2026-07-21に4つ踏んだ・この形以外で書かない）**：
   ```bash
   ~/.npm-global/bin/codex exec --skip-git-repo-check --sandbox workspace-write "$(cat <プロンプトファイル>)"
   ```
   - **フルパス必須**。`codex` はPATHに無く `command not found` になる
   - **`--dangerously-bypass-approvals-and-sandbox` は使用不可**（auto modeクラシファイアにブロックされる）
   - **プロンプト冒頭に「`codex exec` を入れ子で呼ぶな。あなた自身がこのセッション内で生成しろ」を必ず書く**。書かないとCodexが自分自身を再帰起動して `failed to initialize in-process app-server client: Operation not permitted (os error 1)` で落ち、1枚も生成されないまま正常終了する
   - **`| tail -N` でパイプしない**（バックグラウンド実行で出力がバッファされ進捗が見えない）
   - プロンプトは Writeツールでscratchpadに書いて `"$(cat ...)"` で渡す（ヒアドキュメントはブロックされることがある）
   - 完了後は必ず `ls` でファイル実在を確認する。**Codexは1枚も作らずに exit 0 で終わることがある**
2. **note下書き作成（Chrome自動操作）**：手順1〜4（タイトル→**本文を全文1回paste**→画像を正位置に挿入→保存）
3. **アイキャッチ設定**：手順5
4. **最終検証**：強制リロード→**本文画像が全枚数残っているか＋アイキャッチ＋文字数＋見出し/引用/preの数＋画像位置（figureのprev/next）**を実測してから完了報告
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

**⚠️タイトル入力は「入ったこと」を必ず確認する（2026-07-26・vol.16で発覚）**。座標クリック→typeの1回目が反映されず、DOM上はプレースホルダ「記事タイトル」のまま・タブタイトルも変わらないことがある（新規ドラフト作成直後に起きやすい）。**タイプ後にタブタイトルが記事名に変わったかを必ず見る**。反映されていなければ `find` ツールで textbox 要素を明示的に特定し、その ref をクリックしてから type し直すと通る。

**既存の公開済み記事のタイトルを書き換える場合は `form_input` を使う（2026-07-26確立）**。座標クリック＋`cmd+a`＋type は、**フォーカスが本文側に乗っていると本文に文字列を挿入してしまう**（実際に1回やらかした。保存前に `cmd+z` で取り消し、`navigate force:true` で未保存状態を破棄して復旧）。`find` でタイトル textbox の ref を取り、`form_input(ref, 新タイトル)` で直接値をセットすれば本文に一切触れず原子的に置き換わる。**ref はページ遷移のたびに変わるので、navigate 後は毎回 find し直すこと**（古い ref を使い回すと上記の事故が起きる）。

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

見出し（目次に反映）・太字・ul/ol・blockquote・hr・pre/codeまで正しく再現される。

**⚠️本文は「全文を1回でpaste」する。画像位置で分割してはいけない（2026-07-21にnote⑩で新方式を確立・分割方式は廃止）**

- 旧方式（分割paste：前半→画像1→中盤→画像2→後半）は、**後続pasteの先頭ブロックがカーソル直前の段落にマージされる事故が原理的に起きる**（note⑧で2箇所発生・落とし穴表参照）。もう使わない
- 新方式＝**①タイトル入力 → ②本文を全文1回paste → ③画像を後から正位置に挿入（手順3）**。段落・見出し・引用・コードブロックがそのまま入り、境界の検証作業そのものが不要になる
- paste直後に構造を数えて検証する（想定値と突き合わせる）：
  ```js
  const ed = document.querySelector('.ProseMirror');
  JSON.stringify({paras: ed.querySelectorAll('p').length, h2: ed.querySelectorAll('h2').length,
    quotes: ed.querySelectorAll('blockquote').length, pre: ed.querySelectorAll('pre').length,
    links: ed.querySelectorAll('a').length, chars: ed.innerText.length});
  ```
- 長い本文はJS文字列としてそのまま渡せる（note⑩は3,700字を1回で成功）。原稿の「公開前チェックリスト」ブロックと〔画像N：…〕プレースホルダ行は含めない
- 内部リンクは `<a href="...">` で埋め込む。**過去記事の実URLは `.spec/TODO.md`・`.spec/archive/`・`.agent/handoff/archive/` をgrepすれば拾える**（`grep -rn "note.com/tonaria_ai/n/"`）。仮URLのまま入稿しない

### 3. 画像挿入（⚠️最重要・1敗した箇所）

**NG：「＋メニュー→画像」のfile inputへ直接アップロード**。画面には表示されるが**下書き保存に画像が含まれず、リロードで消える**。

**OK：クリップボード画像貼り付けと同じ経路に流す**。ただし経路が2つある。**先にどちらか決めてから進むこと**。

---

#### ⚠️ 最初に `file_upload` の生死を1回だけ確かめる（2026-08-08・ここで40分溶かした）

`file_upload` は**セッションによって壊れている**ことがある。壊れているときは、パスの内容に関係なく必ずこのエラーが返る：

```
Invalid arguments for tool file_upload:
expected array, received undefined (path: paths)
```

**`paths` を正しく配列で渡していてもこうなる。パスが原因ではない。**
2026-08-08に以下すべてで同じエラーを確認した：リポジトリ内の日本語パス／スクラッチパッドのASCII名／`/private/tmp` 配下。

**したがって、パスを変えて試す切り分け実験は全部無駄。1回落ちたら即ルートBへ切り替える。**
（この日はサブエージェントが「リポジトリ配下のパスだから落ちる」という誤った結論に到達するまで88ツールコール・約15分を使った。誤りである）

- **ルートA** ＝ `file_upload` が生きている → 下の 1〜9
- **ルートB** ＝ `file_upload` が死んでいる → 「3-B. ルートB」へ

#### ルートA（file_upload が使えるとき）

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
8. **ブロック要素（pre / ul）の直後に画像を入れたいとき（2026-07-21 note⑩で確立、2026-07-26 vol.16でul も同じと確認）**：そのブロックの中にカーソルを置こうとしない。**次の段落を実クリック→JSで `range.collapse(true)`（段落の"先頭"）→1秒wait→paste** すると、ブロックとその段落の間にfigureが入る。副作用としてブロックとfigureの間に空段落が1つ残るが、見た目は自然な余白なので**消さない**（消そうとするとブロックを壊すリスクがある）。**ul（箇条書き）直後でも手順・副作用ともまったく同じ**で、li の数も変化しない（vol.16で4ul/12li が維持されたことを実測）
9. **⚠️文末がfigureのときの追記（2026-07-19・1敗）**：文書末尾が画像のとき、HTML pasteや「図の下の余白クリック」は**figcaption（キャプション）に入ってしまう**（text/plainの'x'がキャプション混入。cmd+zで復旧可）。正解＝**画像を実クリックしてノード選択→ArrowRight→Returnで図の直後に空段落を作ってから**pasteする

### 3-B. ルートB：OSクリップボード経由（2026-08-08確立・vol.20で実戦成功）

`file_upload` が死んでいるときはこちら。**ページ内にFileを作る必要がなく、noteのCDNへ正規にアップロードされる。**

1. **BashでOSクリップボードにPNGを載せる**（macOS）:
   ```bash
   osascript -e 'set the clipboard to (read (POSIX file "/絶対パス/img.png") as «class PNGf»)'
   osascript -e 'clipboard info'   # 「«class PNGf», <バイト数>」が出れば成功
   ```
   日本語ファイル名でも問題ない。**ただしBash側で `ls` の出力をそのままコピーして使う**（手打ち厳禁・既出の教訓）
2. **挿入先の見出し／段落をビューポート中央へ**（JS）:
   ```js
   t.scrollIntoView({ block:'center', behavior:'instant' });  // ← 'instant' 必須
   ```
   **`behavior` を省くとsmoothスクロールになり、直後の `getBoundingClientRect()` がスクロール前の座標を返す**（2026-08-08に1回踏んだ。y=3255 が返ってきた）
3. **スクリーンショットを撮って座標スケールを確認する**。vol.20では **スクショ1470×746 = CSS座標と1:1** だった。過去に記録した0.609倍は環境依存なので**毎回スクショで確かめる**
4. **見出し／段落の行末を実クリック**。テキストの右端より先（ブロックの右端付近）をクリックしてよい。同じ行の末尾にカーソルが入る
   - **見出しが2行に折り返しているときは2行目の中央のy**を狙う（`top + h*0.75` あたり）
5. **カーソル位置をJSで検証してから進む**（ここを飛ばさない）:
   ```js
   const s=getSelection(), blk=(s.anchorNode.nodeType===3?s.anchorNode.parentElement:s.anchorNode).closest('h1,h2,h3,p');
   ({tag:blk.tagName, text:blk.textContent.slice(0,30), offset:s.anchorOffset, len:s.anchorNode.textContent.length})
   ```
   `offset === len` なら行末に付いている
6. **`computer` の `key` アクションで `cmd+v`**。CDN経由の正規アップロードが走り、`assets.st-note.com` のURLになる
7. `img` の件数と `prev`/`next` の隣接テキストで位置を検証（URL文字列は返さない・既出）

**試して無駄だった代替（もうやらないこと）**：

| 手段 | 結果 |
|---|---|
| ローカルHTTPサーバー（`http://127.0.0.1:PORT`）から `fetch` / `<img>` | **ブラウザのプライベートネットワーク遮断でリクエストが飛ばず、Promiseが永久にpending**。rejectすらしない。サーバー側のアクセスログにも残らない |
| `navigator.clipboard.read()` | **権限プロンプトが出ないまま永久pending**。`document.hasFocus()` は true でも解決しない |

※ どちらも「非同期が動いていないのでは」と疑いたくなるが、`setTimeout` と microtask は正常に発火する。**pendingのまま返ってきたらその経路は諦める**。

### 4. 保存と検証（トーストを信じない）

1. 「下書き保存」クリック→「下書きを保存しました」トースト確認。**保存成功の✓マークは数秒で消える**（2026-07-25にnote⑮で「保存ボタンがグレーアウトしないことがある」と判明した件の続報・2026-07-26 vol.16）。`disabled`属性はfalseのままなので当てにならない。**スクリーンショットは保存ボタンをクリックした直後に撮る**こと。撮り遅れると✓もトーストも消えていて「保存されていない」と誤判定する
2. **強制リロードで再検証**：保存済みでも離脱ダイアログ（Leave site?）が出て、JSの`location.reload()`や通常navigateはブロックされる。**navigateツールに`force: true`を付けて**同URLへ（クエリ`?v=N`を変えると確実）
3. リロード後に `performance.timeOrigin` で本当に再読み込みされたか確認（**過去にリロードされておらず検証が無効だったことがある**）
4. `.ProseMirror img` の残存と前後要素、文字数を確認して完了報告
5. **画像枚数は `figure` ではなく `img` の数で数える（2026-07-27 vol.18で判明）**。noteは引用ブロックを `<figure><blockquote>…</blockquote><figcaption></figcaption></figure>` として保存するため、**「今日の1個」の引用が figure として1件カウントされ、画像が1枚多いように見える**。`querySelectorAll('img').length` で判定すること

### 5. アイキャッチ（ヘッダー画像）の設定（2026-07-18自動化成功）

1. エディタ最上部の画像アイコン（タイトルの上・カメラマーク）を実クリック→メニューが開く（「画像をアップロード 推奨サイズ：1280×670px」の表記あり）
2. **先にclickサプレッションパッチを入れておく**（本文画像と同じ`HTMLInputElement.prototype.click`の上書き）→「画像をアップロード」をクリック→inputが捕獲される
3. 捕獲inputをDOMに追加・可視化→`find`でref取得→`file_upload`でヘッダーPNGを渡す
4. **切り抜きダイアログ**が開く（1280×670ぴったりならそのまま）→「保存」ボタンをクリック。**1回で反応しないことがある**ので、スクショでダイアログが閉じたか確認し、閉じてなければもう一度クリック
5. タイトル上にヘッダーが表示されたら「下書き保存」→強制リロード→アイキャッチ（`rectangle_large`を含むassets.st-note.comのimg）が残っているか確認。**この経路は保存が持続する**（本文画像と違いinput直接アップロードでOK。アイキャッチは記事本文と別管理のため）

#### アイキャッチのルートB（file_upload が死んでいるとき・2026-08-08確立）

アイキャッチのメニューは**ネイティブのファイル選択ダイアログしか入口がない**（`記事にあう画像を選ぶ` はnote側のおすすめ画像で、記事内の画像は選べない）。`file_upload` が使えないときは、**一度本文に貼ってCDNに載せてから回収する**：

1. **ヘッダーPNGを本文の一時的な位置にpaste**（ルートBの手順で）→ `assets.st-note.com` のURLが得られる。`window.__headerSrc` などに退避しておく
   - **⚠️どのimgを掴むかを位置で決めてはいけない（2026-08-11・vol.21で1敗）**。`querySelectorAll('img')` は**文書順**で返るため、本文画像を先に入れてから文書の先頭付近にヘッダーを一時貼りすると、`imgs[imgs.length-1]` は**本文の最後の画像**を掴む。vol.21では実際にこれで本文画像3枚目（フロー図）がアイキャッチとして保存され、削除して再設定する羽目になった
   - **正しい掴み方＝寸法で照合する**。ヘッダーは1280×670、本文画像は1200×800など別寸法なので確実に判別できる：
     ```js
     const target=[...document.querySelectorAll('.ProseMirror img')]
       .find(im=>im.naturalWidth===1280 && im.naturalHeight===670);
     window.__headerSrc = target.src;
     ```
   - 寸法が本文画像と被る場合は、**一時貼りを本文の最後尾にしてから** `imgs[imgs.length-1]` を使う（位置を保証してから位置で掴む）
2. **そのCDN URLを `fetch` して File を作る**。note のCDNはCORSを許可しているので通る：
   ```js
   fetch(window.__headerSrc).then(r=>r.blob()).then(b=>{
     window.__headerFile = new File([b],'header.png',{type:'image/png'});
   });
   ```
   ※ note側で再圧縮されるためバイト数は元より小さくなるが、**ピクセル寸法(1280×670)は保たれる**（vol.20で確認：185KB→63KB・寸法は不変）
3. **`HTMLInputElement.prototype.click` をフック**してネイティブダイアログを開かせない：
   ```js
   const orig = HTMLInputElement.prototype.click;
   HTMLInputElement.prototype.click = function(){ if(this.type==='file'){ window.__captured=this; return; } return orig.apply(this,arguments); };
   ```
   `showPicker` も同様に潰しておく。**復元用に `orig` を保持しておくこと**
4. カメラアイコン→「画像をアップロード」を実クリック → `window.__captured` にinputが入る（**inputはクリックした瞬間に生成される**ので、事前にDOMを探しても見つからない）
5. `DataTransfer` でFileを載せて `change` を発火：
   ```js
   const dt=new DataTransfer(); dt.items.add(window.__headerFile);
   window.__captured.files = dt.files;
   window.__captured.dispatchEvent(new Event('change',{bubbles:true}));
   ```
6. 切り抜きダイアログ → 「保存」
7. **本文に一時的に貼ったヘッダー画像を消す**：画像を実クリック→出てくるツールバーの**ゴミ箱アイコン**をクリック。**削除後に空段落が1つ残ることがある**ので、その場で `Backspace` をもう一度押して段落数を元に戻す（2026-08-11）
7b. **保存したアイキャッチが正しいか、必ず寸法で検証してから次へ進む**（`rectangle_large` を含むimgの `naturalWidth/Height` がヘッダーの寸法と一致するか）。違う画像が入っていたら、アイキャッチ画像右上の**×アイコン**で削除してから1に戻る（削除は正常に機能する・2026-08-11実証）
8. **フックを元に戻す**（`HTMLInputElement.prototype.click = orig`）。戻さないとユーザーが手で画像を追加できなくなる

### 6. 後片付け

- 自作input（`#claude-file-src`）を`remove()`
- `HTMLInputElement.prototype.click`等にパッチを当てた場合は**その場で復元する**（リロード任せにしない。リロードが離脱ダイアログで弾かれることがあるため）
- ルートBを使った場合：**OSクリップボードを空にする**（`osascript -e 'set the clipboard to ""'`）、スクラッチパッドにコピーした画像を削除、ローカルサーバーを起動していたら停止
- 本文に一時的に貼った画像（アイキャッチ回収用）が残っていないか、`img` の数で最終確認する
- **⚠️編集タブを「未保存の変更あり」のまま残さない（2026-09-25・5回連続で残った）**。最後に✓とトーストを確認してから**そのタブを閉じる**。残すと、メインの独立検証が離脱ダイアログで止まり、ユーザーが誤って古い状態で保存する危険がある

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
| 分割pasteで境界の段落が結合する（2026-07-20・2箇所で発生） | 本文を複数回に分けてHTML pasteすると、後続pasteの先頭ブロック（<p>や<ul>の最初の<li>）がカーソルのある直前段落にマージされる | **→2026-07-21に分割paste自体を廃止（手順2）。全文1回pasteなら発生しない**。やむを得ず分割した場合は各境界の段落を検証し、結合していたら該当範囲を実クリック→JSでrange選択→1秒wait→正しいHTMLをpasteして置換 |
| 保存したのに離脱ダイアログが出続ける／保存ボタンが有効のまま | 画像・アイキャッチ操作の直後は保存が完了しきっていないことがある | **画面右上に✓（チェックマーク）が出て「下書き保存」がグレーアウトするまで押す**。note⑩では3回押して確定した。✓を確認してから `force:true` でリロードする（確認せずforceすると未保存分を失う） |
| アイキャッチ保存後、ボタンがグレーアウトしない（2026-07-25・note⑮） | アイキャッチ設定直後は `disabled: false` のまま見た目も通常のクリック可能状態だったが、実際には保存されていた | **グレーアウトだけを合図にしない**。「右上の✓マーク」と「保存トースト」の**両方**を確認する運用にする（note⑮では2回押して✓＋トーストを両方確認してから `force:true` に進み、リロード後もアイキャッチ残存を確認できた） |
| `fetch('/api/v3/notes/<key>')` での保存検証が使えない | Chrome拡張側で cookie/query string を含むレスポンスがブロックされる（`[BLOCKED: Cookie/query string data]`） | API検証は諦め、**強制リロード＋DOM実測**（img数・h2数・pre数・links数・chars・figureのprev/next）で検証する |
| **DOM実測の戻り値までブロックされる（2026-07-26・vol.17で新規）** | `javascript_tool` で `img.src` の配列をそのまま返すと、署名付きURLのクエリ文字列が原因で**戻り値まるごと**が `[BLOCKED: Cookie/query string data]` になる。fetchだけの問題ではない | **URL文字列を返さない**。`src.includes('assets.st-note.com')` の真偽値や件数など、**評価済みの値に変換してから返す** |
| **保存済みなのに「Leave site?」が毎回出る（2026-07-26・vol.17で再確認）** | 本文保存時・アイキャッチ保存時とも、✓とトーストが出たあとの `navigate force:true` で毎回離脱ダイアログが出て「破棄」扱いの警告になる | **警告文は無視してよい**。✓とトーストの両方を確認済みなら、リロード後のDOM実測で本文・画像・アイキャッチとも正しく持続している（vol.17で両方とも確認）。**ただし✓とトーストの確認を省いてforceするのは従来どおり厳禁** |
| **⚠️Markdownの表がまるごと1段落に潰れる（2026-07-28・vol.19で初発覚）** | noteのProseMirrorスキーマは `<table>` ノードを持たない。`<table>` を含むHTMLをpasteすると、**全セルのテキストが区切りなしで1つの `<p>` に連結される**（`table:0` になり、読める形では一切残らない） | **原稿に表がある場合は、HTML変換の前にMD側で箇条書き（`<ul><li>`）へ落とす**。1行1項目で「項目名 — 列1：値／列2：値／判定：値」の形にすると表の情報がそのまま入る。事故った場合は該当段落を選択→削除→ul形式でpasteし直す。**表を図解画像にしている記事でも、本文側のテキスト版は必ずulにする** |
| **画像の挿入位置がh2見出しの直後のとき、空段落が1つ残る（2026-07-28）** | pre/ul直後への挿入と同じ副作用。h2ケースは未記載だったが挙動は同じ | **見た目に影響しないので削除不要**。検証時に段落数がずれても異常ではない |
| **日本語ファイル名の手打ちで誤字（2026-07-28・vol.19で1敗）** | アップロード時にファイル名をUnicodeエスケープで手打ちし、「頼」(U+983C) を「頃」(U+9803) と誤記してアップロード失敗 | **`ls` の出力文字列をそのままコピーして使う**。手打ちしない。怪しいときは `xxd` でバイト列を確認する |
| **⚠️`file_upload` が `expected array, received undefined (path: paths)` で必ず落ちる（2026-08-08・vol.20で40分溶かした）** | セッション側の不具合で `paths` 引数が落ちる。**パスの内容とは無関係**（リポジトリ内・スクラッチパッド・ASCII名・日本語名すべて同じ） | **1回落ちたら切り分けをせず、即ルートB（OSクリップボード＋`cmd+v`）へ**。パスを変えて試すのは全部無駄 |
| **`scrollIntoView` の直後の座標がズレる（2026-08-08）** | `behavior` 省略時にsmoothスクロールになり、`getBoundingClientRect()` がスクロール前の値を返す | **`{ block:'center', behavior:'instant' }` を必ず指定する** |
| **`fetch`/`clipboard.read()` が永久にpending（2026-08-08）** | `http://127.0.0.1` はプライベートネットワーク遮断でリクエスト自体が飛ばない。`navigator.clipboard.read()` は権限プロンプトが出ないまま止まる。**どちらもrejectしない** | `setTimeout`とmicrotaskは正常に動くので「非同期が壊れている」と誤診しない。**pendingで返ったらその経路は即諦める** |
| **`navigate force:true` でも離脱ダイアログを抜けられない（2026-08-08）** | 保存済みでもnote側のbeforeunloadが残り、`force` が効かないことがある。`beforeunload` をJSで潰しても抜けられなかった | **新しいタブで同じ編集URLを開いて検証する**（元タブは触らない）。検証後にそのタブを閉じる。これが一番速い |
| `navigate` の `force` がスキーマに載っていない（2026-07-28） | ToolSearchが返す `navigate` のJSONスキーマには `url` と `tabId` しか出ないが、`force: true` は実際に機能する | **スキーマに無くても `force: true` を渡してよい**。離脱ダイアログを破棄して遷移できる |
| **⚠️複数行の引用が1行目しか引用ブロックに入らない（2026-08-14・入稿に36分かかった主因）** | **noteのblockquoteスキーマは1段落のみ**。`<p>`×3や`<br>`区切りの引用をHTML pasteすると、1行目だけがblockquote内に残り、**2行目以降は無装飾の独立段落としてこぼれ落ちる**（vol.3本目で3箇所とも発生） | blockquote内の`<p>`末尾に実クリック→JSで`collapse(false)`→**キーボードのEnterを実打鍵**（`computer.key: Return`。pasteではない）で同一`<p>`内に`<br>`が入る。続けて`type`で次行を打つ。**「今日の1個」を複数行にする回は毎回起きるので、最初からこの手順で入れる** |
| **⚠️境界をまたぐRange選択のpaste置換で、中身が黙ってすり替わる（2026-08-14）** | blockquote(figure)＋直後の孤立段落をまたぐ範囲をJS Rangeで選択してHTML pasteすると、ProseMirrorが `TypeError: Cannot read properties of null (reading 'lastChild') at handlePaste` を投げる。**paste自体は例外を出さずに完了し、中身だけがtext/plainのフォールバックにすり替わる**＝ツール側からは成功に見える | **ブロック境界をまたぐ選択でのpaste置換はしない**。やった場合は必ず `read_console_messages` で例外を確認する |
| **⚠️冒頭の引用ブロックがpaste直後に `<p>` へ分離する（2026-09-25・5回連続）** | 本文先頭がblockquoteだと、HTML pasteで独立した`<p>`＋空のfigureに分かれる | 分離した段落と空figureを削除し、行頭で **`> ` のMarkdownショートカット＋`type`** で作り直す（確実に直る）。**先頭がblockquoteの原稿では毎回起きる前提で、paste直後に最初に確認する** |
| **⚠️`shift+End` が文書末まで選択する（2026-09-25・本文がほぼ全消えした）** | 既存の選択が非collapsedのまま `shift+End` を打つと、行末ではなく文書末まで選択が伸びることがある | **`shift+End` は使わない**。`Home` でcollapseを確認してから `shift+Right` を文字数ぶん `repeat` する。消えたら即 `cmd+z` |
| **手打ちの `Return` が段落分割にならず `<br>` になる（2026-09-25）** | 段落を割るつもりのEnterが同一`<p>`内の改行になり、段落が結合する | 段落を割るときは、対象段落をJSのRangeで選択→`<p>…</p><p>…</p>` をtext/htmlでpasteして置換する（ブロック境界はまたがない） |
| **⚠️アイキャッチ保存後のプレビューの「×」は削除ボタン（2026-09-25・1敗）** | 閉じる／キャンセルに見えるが、押すとヘッダー画像そのものが外れる | **押さない**。保存だけで終える。検証でアイキャッチ（1280×670のimg）の有無を必ず数える |
