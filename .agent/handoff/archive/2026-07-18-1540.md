# HANDOFF - 2026-07-18 15:39

## 使用ツール
Claude Code（Fable 5）

## 現在のタスクと進捗
**7/23（水）行政書士1号との対面打ち合わせが本番。実演本体＝デモ03は完成・検証済み（11151b7）。今セッションは環境整備（Codex連携）が中心で、デモ・資料の実作業は進んでいない**

- [x] **Codexプラグイン導入完了**：openai/codex-plugin-cc を追加、Codex CLI 0.144.5（`~/.npm-global/bin/codex`）・ChatGPTログイン認証済み・setup ready:true。`codex:rescue` エージェント／`/codex:setup` が使える
- [x] **PATH問題を根本解決**：Claude Code等の非対話シェルは `~/.zshrc` を読まないため `codex` が見えなかった → `~/.zshenv` を新規作成し npm-global／.local/bin／Homebrew のPATHを設置。`~/.zshrc` 2行目の融合破損（`$DOTNET_ROOTexport`）も2文に分割修正済み
- [x] **画像生成＝必ずCodex委譲ルールを整備**：`~/.claude/skills/make_project/SKILL.md` のAGENTS.mdテンプレートと本プロジェクトの `AGENTS.md` に「画像生成ルール（必須）」を追加。①ビットマップ画像（PNG/JPEG/WebP）はCodex CLIに委譲（`codex exec --skip-git-repo-check --sandbox workspace-write "..."`）②保存先・ファイル名・サイズ形式が依頼に無ければ**AskUserQuestionで確認してから**実行 ③SVG/Mermaid等コード描画は対象外 ④codex不在時は代替せずユーザーに報告。実generation経路もテスト済み（動作OK）
- [ ] **HTMLプレゼン資料（TODO 12b）＝次の主タスク・着手指示待ちのまま**
- [ ] X小ネタ（07-16分から停止中・note④ネタ準備済み）
- [ ] 22日リハ＋バックアップ動画撮影（ユーザー）

## 試したこと・結果
- **Codex setup初回は codex:not found**→ 実体は `~/.npm-global/bin` にインストール済み（0.144.5）でPATH欠落が原因と特定。`~/.zshenv` 作成後、`zsh -c 'which codex'` で解決確認
- **Codex画像生成のE2Eテスト成功**：`codex exec --skip-git-repo-check --sandbox workspace-write` で赤い円PNGを生成→保存を確認（テストファイルは削除済み）。`codex features list` で image_generation=stable/有効も確認
- **SKILL.mdのMarkdown入れ子対策**：AGENTS.mdテンプレートのheredoc内に```bashのコマンド例を入れたため、外側フェンスを4連バッククォート````に変更してネストを成立させた
- デモ03の流れをユーザーに再解説済み（draft/sample/checkの3コマンド・隠れた見せ場2つ・当日はdraftとcheckのみ実演）

## 次のセッションで最初にやること
1. **HTMLプレゼン資料の作成**（ユーザーの号令待ち。素材：構成要点=TODO 11-12＋相場データ=phase0/22＋roadmap.htmlのデザイン型。※MD版資料23・台本24はユーザー判断で削除済み・復活させない）
2. HTML資料の前後で**X小ネタ3本**（note④ネタ：AIが誤字指摘/1回のお願いで3アプリ/指示ミスをAIが正す）を`x/日付/`に作成
3. 22日が近ければリハの声かけ（output/を空に→draft→sample→check→スマホでバックアップ動画撮影）

## 注意点・ブロッカー
- **7/23が本番**。実演環境：MacBook＋テザリング。Excelなし→LibreOffice表示（確認済み）。コマンドは `excel版/SETUP.md` 参照。実行前に `export ANTHROPIC_API_KEY` 必須（ターミナル開き直すと消える）。実演前に `excel版/output/` を空にする
- **未コミットの変更あり**：本プロジェクトの `AGENTS.md`（画像生成ルール追記）とHANDOFF関連。ユーザーのコミット指示待ち（ルール：作業単位の完了報告後にまとめてコミット）
- 今後このプロジェクトで画像を作る際はAGENTS.mdの画像生成ルールに従うこと（Codex委譲・不足情報はAskUserQuestion）
- 当日の深掘り質問（見込み客リスト02に記録済み）：月何件か／認定・変更・更新のどれが多いか／PDFはどの書類か／PC環境
- 積み残し：三井通産（2号）初回連絡／ドメインtonaria.com取得／デモ02動作確認（ユーザー側）／GAS版のPDF対応（未実装）
