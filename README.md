# EqMax-Discord-Bridge v5.0

<p align="center">
  <img src="Assets/eq-dis.png" width="120" alt="Logo">
  <br>
  <b>地震監視ソフト「EqMAX」の通知を、美しく、確実に Discord へ届ける統合管理システム</b>
</p>

> [!TIP]
> ### 📥 最新バージョンのダウンロード
> **[EqMax-Discord-Bridge v5.0 をダウンロード (Releases)](https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/tag/v5.0)**
> ※ `Source code (zip)` をダウンロードして展開してください。

---

<p align="center">
  <img src="Assets/A1Desktop.jpg" width="800" alt="Main Visual">
  <br>
  <i>▲ v5.0 より導入された、全ての機能を一括管理する「統合管理ハブ」とリアルタイムログ。</i>
</p>

---

## 🎨 v5.0 の主な進化点
* **統合管理ハブ (00-TOP_HUB.py)**: 全てのツールを一つの画面から呼び出し可能。
* **インテリジェンス・ログ**: 起動状況や時刻をプロンプトに詳細出力。
* **自動更新確認システム**: 起動時に GitHub API を通じて最新リリースの有無を自動チェック。
* **初期設定プリセット**: 用途に合わせた2つの構成テンプレート（Full/Server）を導入。

## 🛠️ 収録ツール一覧
1. **EqMAX 初期設定パッチ**: レイアウト固定、キャプチャ設定、疑似認証を自動適用。
2. **Discord 連携実装**: 最大5つのWebhookを同時管理。
3. **EqMAX 初期化処理**: 困った時のリセット機能。ショートカット削除は手動で行う安全仕様。
4. **メンテナンスツール**: 画像掃除（Cleaner）や、メモリリーク対策の監視（Watchdog）を同梱。

## 🚀 クイックスタート
1. リポジトリを展開し、ルート直下の **`EqMax-Discord-Bridge.bat`** を実行してください。
2. 立ち上がったハブ画面の指示に従ってセットアップを進めます。

> [!IMPORTANT]
> **アイコンの設定について**
> 本ツールはデスクトップを汚さないよう、自動的なショートカット作成は行いません。ショートカットを作成したい場合は、`Assets/eq-dis.ico` を指定して適用してください。

## 📸 スクリーンショット

### ■ メイン・ハブ & プロンプト
| 統合管理ハブ (GUI) | リアルタイムログ (Prompt) |
| :---: | :---: |
| <img src="Assets/01HUB.jpg" width="400"> | <img src="Assets/A1-Prompt.jpg" width="400"> |

### ■ 各種設定・通知
| 初期設定パッチ | Discord 連携実装 | 通知イメージ |
| :---: | :---: | :---: |
| <img src="Assets/01EqSetting.jpg" width="260"> | <img src="Assets/02Bridge.jpg" width="260"> | <img src="Assets/A2Discord.jpg" width="260"> |

### ■ メンテナンス & リセット
| ログ・画像掃除 | 動作監視 (Watchdog) | 初期化処理 |
| :---: | :---: | :---: |
| <img src="Assets/O1Cleaner.jpg" width="260"> | <img src="Assets/O2Watchdog.jpg" width="260"> | <img src="Assets/03Initialization.jpg" width="260"> |

---
**© 2026 Mustang_TIS**