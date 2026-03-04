# EqMax-Discord-Bridge

<p align="center">
  <img src="Assets/eq-dis.png" width="120" alt="Logo">
</p>

<p align="center">
  <b>地震監視ソフト「EqMAX」の通知を、美しく、確実に Discord へ届ける統合管理システム</b>
</p>

> [!CAUTION]
> **【重要】v6.0.0 公開一時停止のお知らせ**
> 現在、最新版 v6.0.0 においてEEW（緊急地震速報）の受信およびDiscord通知が正常に機能しないリスクが確認されたため、公開を一時停止しております。
> 
> 利用者の皆様は、以下の**安定版 v5.6**をご利用ください。

> [!IMPORTANT]
> **安定版 v5.6 パッケージ (ZIP) をダウンロード**
> <p align="center">
>   <br>
>   <a href="https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/download/v5.6/EqMax-Discord-Bridge-v5.6.zip">
>     <img src="https://img.shields.io/badge/Download-Stable_v5.6_.zip-blue?style=for-the-badge&logo=github" alt="Download ZIP">
>   </a>
> </p>

---
<p align="right">Developer: MustangTIS</p>

### ■ システム概要

本システムは、EqMAXの通知をDiscord Webhookを利用して高速転送する統合管理システムです。

* **統合管理ハブ**: 環境チェックからアップデートまでを一括管理。
* **Guardianエンジン**: メモリ監視（Private Bytes）による長期間の安定稼働。
* **クリーナー機能**: 肥大化するログや画像を自動的に整理。

---

### 💻 起動シーケンス (Startup Manager)

本システムでは、安定動作を支えるためのインテリジェントな起動シーケンスを搭載しています。

<p align="center">
  <img src="Assets/DiscordBridgePrompt.jpg" width="700" alt="Bot Boot Sequence">
</p>

<p align="center">
  <i>▲ 通知ボット：7段階の診断を経て「ALL GREEN」の状態へ</i>
</p>

【診断ステップ】
1. システムバージョンおよびコアファイルの整合性確認。
2. Private Bytes監視エンジンの初期化。
3. Discord Webhookのスタンバイ確認。

---

🚀 クイックスタート 

1. 上記の **[安定版 v5.6 をダウンロード]** ボタンからパッケージを取得して展開します。

2. フォルダ内の **`EqMax-Discord-Bridge.bat`** を実行してください。

3. 自動チェックが完了し、ハブが立ち上がったら指示に従いセットアップを進めます。

> [!TIP]
> **トラブル時の「セーフモード」**
> もし黒い画面がすぐ閉じてしまう場合は、作成された「(セーフモード)」ショートカット、または各フォルダ内のバッチファイルを直接実行して自己診断を行ってください。

---

## 🖼️ 設定画面ギャラリー

| 統合管理ハブ | 初期設定パッチ | Discord 連携実装 |
| :---: | :---: | :---: |
| <img src="Assets/01HUB.jpg" width="300"> | <img src="Assets/01EqSetting.jpg" width="300"> | <img src="Assets/02Bridge.jpg" width="300"> |
| アプリの開始画面 | EqMax設定の自動最適化 | Discord連携の管理 |

---
制作者：MustangTIS  
GitHub: [https://github.com/MustangTIS/EqMax-Discord-Bridge](https://github.com/MustangTIS/EqMax-Discord-Bridge)
