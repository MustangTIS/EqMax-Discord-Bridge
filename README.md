# EqMax-Discord-Bridge v5.5.3

<p align="center">
  <img src="Assets/eq-dis.png" width="120" alt="Logo">
</p>

<p align="center">
  <b>地震監視ソフト「EqMAX」の通知を、美しく、確実に Discord へ届ける統合管理システム</b>
</p>

<div align="center">

> [!IMPORTANT]
> **最新版ダウンロード**
>
> <a href="[https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/download/v5.5/EqMax-Discord-Bridge-v5.5.3zip](https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/download/v5.5.3/EqMax-Discord-Bridge-v5.5.3.zip)">
>   <img src="https://img.shields.io/badge/Download-最新版_v5.5.3_をダウンロード-blue?style=for-the-badge&logo=github" alt="Download v5.5.3">
> </a>

</div>

---
<p align="right">Developer: MustangTIS</p>

### ■ メイン・デスクトップ
<p align="center">
<img src="Assets/A1Desktop.jpg" width="800" alt="Main Visual">
<br>
<i>▲ v5.5 統合管理ハブと進化した Startup Manager</i>
</p>

---

## 📸 動作イメージ

### ■ リアルタイム通知 & ログ連携
Discordへの通知（A2Discord.jpg）と、ボット側の処理ログ（DiscordBridgePrompt.jpg）を並べたイメージです。EEWの検知から送信完了まで、動作状況を完璧に把握できます。

| Discord通知画面 | ボット・リアルタイムログ |
| :---: | :---: |
| <img src="Assets/A2Discord.jpg" width="450"> | <img src="Assets/DiscordBridgePrompt.jpg" width="450"> |
<p align="center"><i>▲ 海域判定・津波警戒フラグが付与された最新の通知スタイル</i></p>

---

## 🚀 v5.5 の主な進化点
* **インテリジェンス・ランチャー**: Python環境や必須ライブラリを自動チェック。環境構築の手間をゼロにしました。
* **🛰️ GitHub API 連携**: 起動時に最新タグを自動照会。更新がある場合は即座に通知・誘導を行います。
* **📊 安定化監視（Watchdog）の可視化**: 1時間ごとの報告に EqMax のメモリ使用量(MB)を記録。リソース消費の推移を可視化しました。
* **🚨 津波警戒判定**: マグニチュードと震源地を解析し、海域地震時に「大津波警戒」等のフラグを自動付与します。

---

## 🛠️ 収録ツール一覧
1. **EqMAX 初期設定パッチ**: レイアウト固定、キャプチャ設定、疑似認証を自動適用。
2. **Discord 連携実装 (v5.5)**: 最大5つのWebhookを管理。embed / simple スタイル切り替え対応。
3. **メンテナンスツール**: 肥大化する画像・ログの自動掃除（Cleaner）や、メモリリーク対策（Watchdog）を完備。

---

## 💻 起動シーケンス (Startup Manager)
新設計のバッチファイルにより、準備完了からハブの起動までを視覚的にナビゲートします。

<p align="center">
<img src="Assets/01TOPHUB-Prompt.jpg" width="700" alt="Startup Prompt">
</p>

---

## 🚀 クイックスタート
1. 上記の **[最新版 v5.5 をダウンロード]** ボタンからZIPを取得して展開します。
2. フォルダ内の **`EqMax-Discord-Bridge.bat`** を実行してください。
3. 自動チェックが完了すると統合ハブが立ち上がるので、指示に従いセットアップを進めます。

> [!TIP]
> **アイコンの設定について**
> ショートカットを作成したい場合は、`Assets/eq-dis.ico` を指定して適用してください。

---

## 🖼️ 設定画面ギャラリー

### ■ メイン操作・設定
ツールの司令塔となるHUBを中心に、導入時に必要な設定ツールを並べています。

| 統合管理ハブ (v5.5) | 初期設定パッチ | Discord 連携実装 |
| :---: | :---: | :---: |
| <img src="Assets/01HUB.jpg" width="300"> | <img src="Assets/01EqSetting.jpg" width="300"> | <img src="Assets/02Bridge.jpg" width="300"> |
| アプリの開始画面 | EqMaxの設定を自動最適化 | Discord連携の管理 |

### ■ メンテナンス・補助ツール
安定運用を支えるためのクリーナーや監視、トラブル時のリセットツールです。

| ログ・画像掃除 | 動作監視 (Watchdog) | 初期化処理 |
| :---: | :---: | :---: |
| <img src="Assets/O1Cleaner.jpg" width="300"> | <img src="Assets/O2Watchdog.jpg" width="300"> | <img src="Assets/03Initialization.jpg" width="300"> |
| 不要ファイルの自動削除 | RAM超過時の自動復旧 | 困った時の設定初期化ツール |
