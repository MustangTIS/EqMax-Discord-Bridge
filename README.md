<div align="center">

<table>
<tr>
<td rowspan="2" align="center" valign="middle">
<img src="Assets/eq-dis.png" width="120" alt="Logo">
</td>
<td align="left">
<h1>EqMax-Discord-Bridge v11.0.0</h1>
<h3>(The Blue Horizon - Bluesky Integration)</h3>
</td>
</tr>
<tr>
<td align="left">
<p><em>「分断された世界を、再び繋ぐ。」 — 待望のBluesky連携、ついに正式解禁。</em></p>
</td>
</tr>
</table>

【最新版パッケージ (ZIP) を直接ダウンロード】

<p align="center">
<a href="https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/download/v11.0.0/EqMax-Discord-Bridge_v11.0.0.zip">
<img src="https://img.shields.io/badge/Download-Latest_v11.0.0_.zip-0085ff?style=for-the-badge&logo=github" alt="Download ZIP">
</a>
</p>

<div align="right">Developer: MustangTIS</div>

<img src="Assets/MegaQuake2011.jpg" alt="Main Visual" width="100%">

～2026/03/11 — 震災から15年目の節目を超えて～

</div>

東日本大震災から15年。「正確な情報の価値」を追求し続けてきた本プロジェクトは、大きな転換点を迎えました。
X(旧Twitter)のAPI環境が激変する中、新たな「情報の避難先」として **Bluesky** への完全対応を果たし、**v11.0.0** へと到達しました。

「揺れる前」から「揺れた後」まで、そしてDiscordからBlueskyまで。
あらゆる場所へ情報を届ける、真の「統合型防災通知ハブ」としての地平を切り拓きます。

<div align="right">2026/04/29 MustangTIS</div>

---

## 🦋 v11.0.0 の核心：『情報の分散化と安定性』

本バージョンでは、単なる新SNS対応に留まらない「堅牢さ」を追求しました。

* **Bluesky 連携 (AT Protocol)**: 独自のAPI連携により、地震速報を迅速にBlueskyのタイムラインへ流し込みます。
* **オートパス判別ブーター**: 実行環境に合わせ `python` または `py` コマンドを自動選択。環境構築の「動かない」を最小限にします。
* **Embed 4000文字拡張**: Discordへの情報出力を上限の4000文字まで引き上げ、大規模地震時の膨大な確定報も余さず伝えます。

## 🚀 主なアップデート内容

### 📢 Bluesky 投稿機能の実装
X(旧Twitter)の代替として注目されるBlueskyへ、EEW・確定報・津波情報を自動投稿。ATプロトコルによる低遅延な通知を実現しました。

### 🛠️ 導入UXの改善
Pythonパスの自動判別機能により、インストーラーや起動バッチの成功率が向上。初心者でもより確実に「配置」ができるようになりました。

### 🎨 HTMLマニュアルの刷新
Bluesky特有のアカウントハンドル取得やアプリパスワード発行手順を、画像付きで分かりやすく解説した最新マニュアルを同梱。

---

💻 動作環境・スペック

<img src="Assets/Desktop.png" alt="Desktop Image" width="100%">

開発＆動作確認: Windows 11 / Windows Server 2025
推奨環境: Windows 10/11, Windows Server 2022/2025 (x64専用)
必要ソフト: EqMax (強震モニタ表示ソフト), Python 3.10-3.14推奨

🛠️ 収録ツール紹介

<table width="100%">
<tr>
<td width="33.3%" align="center" valign="top">
<img src="Assets/HUB.jpg" width="100%"><br>
<strong>総合ハブ (TOP_HUB)</strong><br>
<small>2カラム化された最新UI</small>
</td>
<td width="33.3%" align="center" valign="top">
<img src="Assets/EEWTest.jpg" width="100%"><br>
<strong>テストユニット (Test)</strong><br>
<small>Blueskyへのテスト送信も対応</small>
</td>
<td width="33.3%" align="center" valign="top">
<img src="Assets/Cleaner.jpg" width="100%"><br>
<strong>掃除ツール (Cleaner)</strong><br>
<small>ログ・画像の自動整理</small>
</td>
</tr>
</table>

⚠️ 免責事項

本ツールの利用により生じた損害について、作者は一切の責任を負いません。防災の際は、必ず気象庁や自治体の公式発表を確認してください。

制作者：MustangTIS
GitHub: https://github.com/MustangTIS/EqMax-Discord-Bridge
