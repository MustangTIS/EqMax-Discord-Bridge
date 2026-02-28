---

# EqMax-Discord-Bridge v5.0

<p align="center">
<img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/eq-dis.png](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/eq-dis.png)" width="120" alt="Logo">





<b>地震監視ソフト「EqMAX」の通知を、美しく、確実に Discord へ届ける統合管理システム</b>
</p>

> [!TIP]
> ### 📥 最新バージョンのダウンロード
> 
> 
> **[EqMax-Discord-Bridge v5.0 をダウンロード (Releases)](https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/tag/v5.0)**
> ※ `Source code (zip)` をダウンロードして展開してください。

---

<p align="center">
<img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/A1Desktop.jpg](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/A1Desktop.jpg)" width="800" alt="Main Visual">





<i>▲ v5.0 より導入された、全ての機能を一括管理する「統合管理ハブ」とリアルタイムログ。</i>
</p>

---

## 🎨 v5.0 の主な進化点

今回のアップデートは、内部システムの刷新、UIの再設計、および運用安定性を向上させるための新機能を追加したメジャーアップデート版です。

* **統合管理ハブ (00-TOP_HUB.py)**: 全てのツールを一つの画面から呼び出し可能。重要度や用途に応じた色分け（推奨手順・トラブル・メンテナンス）を採用。
* **インテリジェンス・ログ**: 起動状況や時刻をプロンプトに詳細出力。システムの動作状況をリアルタイムに把握できるようになりました。
* **自動更新確認システム**: 起動時に GitHub API を通じて最新リリースの有無を自動チェック。
* **初期設定プリセット (INI導入)**: 用途に合わせた2つの構成テンプレート（Full/Server）を導入しました。

## 🛠️ 収録ツール一覧

1. **EqMAX 初期設定パッチ**: レイアウト固定、キャプチャ設定、疑似認証を自動適用。
2. **Discord 連携実装**: 最大5つのWebhookを同時管理。柔軟な通知システムを完成させます。
3. **EqMAX 初期化処理**: 困った時のリセット機能。リスクヘッジのため、ショートカット削除は手動で行う安全仕様へ変更。
4. **メンテナンスツール**: 溜まった画像やログの掃除（Cleaner）や、メモリリーク対策の監視（Watchdog）を同梱。

## 🚀 クイックスタート

1. リポジトリを展開し、ルート直下の **`EqMax-Discord-Bridge.bat`** を実行してください。
* ※ 起動バッチは Python 環境の有無を自動チェックし、必要に応じてライブラリの修復を試みます。


2. 立ち上がったハブ画面の指示に従ってセットアップを進めます。

> [!IMPORTANT]
> **アイコンの設定について**
> 本ツールはデスクトップを汚さないよう、自動的なショートカット作成は行いません。常に手元に置きたい場合は、`EqMax-Discord-Bridge.bat` のショートカットを作成し、プロパティから `Assets/eq-dis.ico` を指定して適用してください。

## 📸 スクリーンショット

### ■ メイン・ハブ & プロンプト

| 統合管理ハブ (GUI) | リアルタイムログ (Prompt) |
| --- | --- |
| <img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/01HUB.jpg](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/01HUB.jpg)" width="400"> | <img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/A1-Prompt.jpg](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/A1-Prompt.jpg)" width="400"> |

### ■ 各種設定・通知

| 初期設定パッチ | Discord 連携実装 | 通知イメージ |
| --- | --- | --- |
| <img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/01EqSetting.jpg](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/01EqSetting.jpg)" width="260"> | <img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/02Bridge.jpg](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/02Bridge.jpg)" width="260"> | <img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/A2Discord.jpg](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/A2Discord.jpg)" width="260"> |

### ■ メンテナンス & リセット

| ログ・画像掃除 | 動作監視 (Watchdog) | 初期化処理 |
| --- | --- | --- |
| <img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/O1Cleaner.jpg](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/O1Cleaner.jpg)" width="260"> | <img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/O2Watchdog.jpg](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/O2Watchdog.jpg)" width="260"> | <img src="[https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/03Initialization.jpg](https://www.google.com/search?q=https://github.com/MustangTIS/EqMax-Discord-Bridge/raw/main/Assets/03Initialization.jpg)" width="260"> |

---

**© 2026 Mustang_TIS**
不具合報告やフィードバックは、GitHub の Issues までお寄せください。