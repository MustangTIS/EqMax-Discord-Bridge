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
> <a href="[https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/download/v5.6/EqMax-Discord-Bridge-v5.6.zip](https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/download/v5.6/EqMax-Discord-Bridge-v5.6.zip)">
> <img src="[https://img.shields.io/badge/Download-最新版_v5.6_をダウンロード-blue?style=for-the-badge&logo=github](https://img.shields.io/badge/Download-最新版_v5.6_をダウンロード-blue?style=for-the-badge&logo=github)" alt="Download v5.6">
> </a>

</div>

---

<p align="right">Developer: MustangTIS</p>

### ■ メイン・デスクトップ

<p align="center">
<img src="Assets/A1Desktop.jpg" width="800" alt="Main Visual">





<i>▲ v5.6 統合管理ハブと刷新されたブートシーケンス</i>
</p>

---

## 🚀 v5.6 の主な進化点：透明性と信頼性の追求

* 
**インテリジェント・ブートシーケンス (Step 1/7 ～ 7/7)** 


* 起動プロセスを完全に可視化 。全てのチェックを通過した際の **`ALL GREEN`** 表示は、確かなシステム健全性の証です 。




* 
**監視エンジンの再設計 (Private Bytes 移行)** 


* 従来の物理メモリ監視では検知しきれなかった「予約領域」を含む **Private Bytes** の監視を採用 。真の意味でのメモリリーク対策を実現しました 。




* 
**セーフモード診断機能の導入** 


* 起動トラブル時、バッチファイルから直接環境の自己診断・修復を行える構造を強化 。OS移行やPython環境の変化にも柔軟に対応します。




* 
**プロフェッショナルな情報表示への洗練** 


* 定時報告の表記を **`ReportEvery`** へ刷新し、管理者にとってより直感的で整理されたコンソール出力を提供します 。





---

## 🛠️ 収録ツール一覧

1. 
**EqMAX 初期設定パッチ** 


* レイアウト固定、キャプチャ設定、疑似認証を自動適用。


2. 
**Discord 連携実装 / Guardian (v5.6)** 


* 最大5つのWebhookを管理。Private Bytes監視エンジンを標準搭載し、長期間の無人運用を支えます 。




3. 
**メンテナンスツール (Cleaner / Watchdog)** 


* 肥大化する画像・ログの自動掃除や、単体動作に特化した監視ボットを完備 。





---

## 💻 起動シーケンス (Startup Manager)

新設計の診断シーケンスにより、ライブラリの整合性からWebhookの待機状態までを完璧にナビゲートします。

<p align="center">
<img src="Assets/01TOPHUB-Prompt.jpg" width="700" alt="Startup Prompt">





<i>▲ v5.6 より導入された ALL GREEN ダッシュボード</i>
</p>

---

## 🚀 クイックスタート

1. 上記の **[最新版 v5.6 をダウンロード]** ボタンからZIPを取得して展開します。
2. フォルダ内の **`EqMax-Discord-Bridge.bat`** を実行してください 。


3. **Step 1/7 ～ 7/7** の自動チェックが完了し、ハブが立ち上がったら指示に従いセットアップを進めます。

> [!TIP]
> **トラブル時の「セーフモード」**
> もし黒い画面がすぐ閉じてしまう場合は、作成された「(セーフモード)」ショートカット、または各フォルダ内のバッチファイルを直接実行して自己診断を行ってください 。
> 
> 

---

### 修正のポイント

* **バージョンの統一**: 全ての記述を `v5.5` から `v5.6` へ更新しました。
* 
**新機能の強調**: ChangeLog  に基づき、**Private Bytes 監視** や **ALL GREEN**、**ReportEvery** といった v5.6 の象徴的な機能を「主な進化点」としてまとめました。


* 
**ReadMe.txt との整合性**: ユーザーがダウンロード後に読む `ReadMe.txt`  と用語や手順（セーフモード診断など）を合わせることで、混乱を防いでいます。