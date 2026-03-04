# EqMax-Discord-Bridge v5.6

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
> [![Download v5.6](https://img.shields.io/badge/Download-最新版_v5.6_をダウンロード-blue?style=for-the-badge&logo=github)](https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/latest)

</div>

---
<p align="right">Developer: MustangTIS</p>

### ■ メイン・デスクトップ

<p align="center">
<img src="Assets/A1Desktop.jpg" width="800" alt="Main Visual">





<i>▲ v5.6 統合管理ハブと刷新されたブートシーケンス</i>
</p>

---

🚀 v5.6 の主な進化点：透明性と信頼性の追求 

* 
**インテリジェント・ブートシーケンス (Step 1/7 ～ 7/7)** 


* 起動プロセスを完全に可視化し、ライブラリや環境パス、Webhookの状態を一つずつチェックします 。全てのチェックを通過した際の **`ALL GREEN`** 表示は、確かなシステム健全性の証です 。




* 
**監視エンジンの再設計 (Private Bytes 移行)** 


* 従来の物理メモリ監視では検知しきれなかった「予約領域」を含む **Private Bytes** の監視を採用しました 。これにより、真の意味でのメモリリーク対策が可能になりました 。




* 
**セーフモード診断機能の導入** 


* 起動トラブル時、バッチファイルから直接環境の自己診断・修復を行える構造を強化しました 。OS移行や環境移行直後でもスムーズな復旧をサポートします 。




* 
**プロフェッショナルな情報表示への洗練** 


* 定時報告の表記を **`ReportEvery`** へ刷新しました 。`Seconds` 表記の統一など、管理者にとってより直感的で整理されたコンソール出力を提供します 。





---

🛠️ 収録ツール一覧 

1. 
**EqMAX 初期設定パッチ** 


* レイアウト固定、キャプチャ設定、疑似認証を自動適用。


2. 
**Discord 連携実装 / Guardian (v5.6)** 


* 最大5つのWebhookを管理。Private Bytes監視エンジンを標準搭載し、長期間の無人運用を支えます 。




3. 
**メンテナンスツール (Cleaner / Watchdog)** 


* 肥大化する画像・ログの自動掃除や、単体動作に特化した監視ボットを完備しています 。





---

💻 起動シーケンス (Startup Manager) 

新設計の診断シーケンスにより、準備完了からハブの起動までを完璧にナビゲートします。 

<p align="center">
<img src="Assets/01TOPHUB-Prompt.jpg" width="700" alt="Startup Prompt">





<i>▲ v5.6 より導入された ALL GREEN ダッシュボード</i>
</p>

---

🚀 クイックスタート 

1. 上記の **[最新版 v5.6 をダウンロード]** ボタンから最新のリリースを取得して展開します。 


2. フォルダ内の **`EqMax-Discord-Bridge.bat`** を実行してください。 


3. 
**Step 1/7 ～ 7/7** の自動チェックが完了し、ハブが立ち上がったら指示に従いセットアップを進めます。 



> [!TIP]
> 
> 
> **トラブル時の「セーフモード」** もし黒い画面がすぐ閉じてしまう場合は、作成された「(セーフモード)」ショートカット、または各フォルダ内のバッチファイルを直接実行して自己診断を行ってください。 
> 
> 

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
