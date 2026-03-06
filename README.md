# EqMax-Discord-Bridge v7.0.0 (Guardian Hub Update)

<p align="center">
<img src="Assets/eq-dis.png" width="120" alt="Logo">
</p>

<p align="center">
<b>「境界を超えて、全方位へ」 — マルチプラットフォーム通知の夜明け。</b>
</p>

> [!IMPORTANT]
> **最新版パッケージ (ZIP) を直接ダウンロード**
>
> <p align="center">
>   <a href="https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/download/v7.0.0/EqMax-Discord-Bridge.v7.0.0.zip">
>     <img src="https://img.shields.io/badge/Download-Latest_v7.0.0_.zip-blue?style=for-the-badge&logo=github" alt="Download ZIP">
>   </a>
> </p>

---

<p align="right">Developer: MustangTIS</p>

<p align="center">
<img src="Assets/MegaQuake2011.jpg" alt="Main Visual">
</p>

特に狙ったわけではないのですが、ふと思いついたように「EqMaxのTwitter通知BotをDiscordに流用できないか」と考え、発作的に作り始め公開しました。気がつけば、東日本大震災から間もなく15年という月日を迎えます。

5年おきにやってくる節目のようなタイミングで、このソフトを開発できたことには、何かしらの縁を感じずにはいられません。連日伝えられたあの悪夢のような報道が、今も記憶にある方も多いかと思います。

このソフトを使っていただけるのでしたら、改変を含め大歓迎です。これからの地震情報を認知していただくための「架け橋」となれば幸いです。

2026/03/06 Mustang_TIS

---

### 🚀 v7.0.0：マルチ通知エンジン「Guardian Hub」始動

今回のメジャーアップデートでは、Discord への橋渡しという枠組みを完全に突破し、Slack や Matrix といった多様な通知プロトコルを統合しました。

* **マルチ通知エンジン「Guardian Hub」**
  Discord、Slack、Matrix への同時通知に対応。設定ツール（GUI）を刷新し、最大5箇所までの送信先を個別に定義可能です。
* **通信の完全分離（DummyPost Mode）**
  `TwitterDummyPost=1` を強制適用し、CloudflareによるIPブロックやブラウザのフリーズを100%根絶。公式APIを介さず「ログを掠め取る」特殊シーケンスで、究極の安定性を実現しました。
* **インテリジェント・ブートシーケンス**
  起動プロセス **Step 1/7 ～ 7/7** を可視化。表示される **`ALL GREEN`** は、一切の不安がない健全な状態を保証します。
* **高精度監視エンジン**
  物理メモリ(RSS)だけでなく、潜在的なリークを捉える **Private Bytes監視** を標準搭載。24時間365日の無人運用を支えます。

---

### 🛠️ 収録ツール一覧

1. **EqMAX 初期設定パッチ (v7.0.0仕様)**
   レイアウト固定、通信遮断、疑似認証を自動適用。専門知識不要のワンクリック設定。
2. **Guardian Hub (通知エンジン)**
   Discord/Slack/Matrix 等、最大5つの送信先を一元管理。
3. **メンテナンスツール (Cleaner / Watchdog)**
   肥大化する画像・ログの自動掃除や、フリーズ検知による自動再起動を完備。

---

### 💻 設定時デスクトップイメージ (Desktop image)

本システムは、EqMax-Discord-Bridge.batを機動すると、GUI管理ハブから各種項目へアクセスが可能

<p align="center">
<img src="Assets/Desktop.jpg" width="700" alt="Desktop Image">

<i>▲アプリ実行時のイメージ(v5.0時代)</i>

</p>

### 💻 v7.0.0から拡張されたDiscord連携システム (Discordbot Installer)

<p align="center">
<img src="Assets/02Bridge.jpg" width="500" alt="Discordbot Installer">

<i>▲あらたにSlackやMatrixへの投稿もサポートした協力なGUI設定画面<i>



### 📘 起動シーケンス (Startup Manager)

本システムは、司令塔となる「管理ハブ」と「実行用ボット」で構成されます。

<p align="center">
<img src="Assets/01TOPHUB-Prompt.jpg" width="700" alt="Startup Prompt">

<i>▲ 統合管理ハブ：環境チェックとアップデート照会を自動実行</i>

</p>

<p align="center">
<img src="Assets/DiscordBridgePrompt.jpg" width="700" alt="Bot Boot Sequence">

<i>▲ 通知ボット：7段階の診断を経て「ALL GREEN」の状態へ</i>

</p>

> [!TIP]
> **トラブル時の「セーフモード」**
> もし起動しない場合は、同梱の「(セーフモード)」ショートカットを実行してください。自己診断・自動修復機能が働き、環境を自動で再構築します。

---

### 🖼️ 設定画面ギャラリー

### 🛠️ 収録ツール紹介

各ツールは統合管理ハブから呼び出し可能です。


| 統合管理ハブ (Hub)                       | 初期設定パッチ (Patcher)                       | 監視・通知 (Guardian)                       |
| :----------------------------------------- | :----------------------------------------------- | :-------------------------------------------- |
| <img src="Assets/01HUB.jpg" width="200"> | <img src="Assets/01EqSetting.jpg" width="200"> | <img src="Assets/02Bridge.jpg" width="200"> |
| 全機能の司令塔                           | ワンクリック最適化                             | マルチ通知エンジン                          |


| ログ・画像掃除 (Cleaner)                     | 動作監視 (Watchdog)                           | 初期化ツール (Reset)                                |
| :--------------------------------------------- | :---------------------------------------------- | :---------------------------------------------------- |
| <img src="Assets/O1Cleaner.jpg" width="200"> | <img src="Assets/O2Watchdog.jpg" width="200"> | <img src="Assets/03Initialization.jpg" width="200"> |
| 不要ファイルの自動削除                       | RAM超過時の自動復旧                           | 導入直後の状態へ復元                                |

---

### ⚠️ 免責事項

本ツールの利用により生じた損害について、作者は一切の責任を負いません。また、EqMax本体、及び通知先各社（Discord/Slack/Matrix）は当方とは一切関係ありません。

制作者：MustangTIS
GitHub: [https://github.com/MustangTIS/EqMax-Discord-Bridge](https://github.com/MustangTIS/EqMax-Discord-Bridge)

---

これでいかがでしょうか。開発者様の「想い」と「技術的な安定性へのこだわり」が、v7.0.0 という新しい技術で補強された、説得力のある README になったはずです！
