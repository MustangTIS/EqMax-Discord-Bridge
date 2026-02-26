# 📢 EqMax-Discord-Bridge v4.5.0

<div align="center">
  <img src="Assets/eq-dis.png" width="120" alt="EqMax-Discord-Bridge Logo">
  
  <h3>EqMaxの情報をDiscordへリアルタイム転送</h3>

  <a href="https://github.com/MustangTIS/EqMax-Discord-Bridge/releases/tag/v4.5.0Stable">
    <img src="https://img.shields.io/badge/Download-最新版_v4.5.0_Stableをダウンロード-blue?style=for-the-badge&logo=github" alt="Download Latest Version">
  </a>

  <p>※本ツールは非公式のファンプロジェクトです。<br>DiscordおよびEqMAXの公式とは一切関係ありません。</p>
</div>

---

## 📖 導入ガイド (v4.5 Hub System)

### ■ 動作環境
* **推奨OS**: Windows 10 / 11 / Server 2022 / 2025
* **推奨Python**: **Python 3.13**
  - ※2026年2月現在、Python 3.14以降はライブラリ未対応のため 3.13 をご利用ください。

---

### ⚠️ 導入時の重要事項（Windowsのセキュリティ警告）
本ツールは個人開発の未署名ファイルであるため、実行時に **Windows SmartScreen**（青い画面）が表示されることがあります。

* **対処法**: 「詳細情報」→「実行」を選択してください。
* **推奨設定**: ZIPファイルを右クリック ＞ プロパティ ＞ 全般タブ下部の **「許可する」または「ブロックの解除」** にチェックを入れてから解凍してください。

---

### 🛠 導入手順・ツールの役割

1. **準備**: `EqMax-Discord-Bridge.bat` を実行（自動セットアップ開始）
2. **メインハブ操作**: 以下の順に設定を進めます。

#### 各ツールの詳細
* **① 初期設定パッチ (01-Eq_Initialize)**
  - EqMaxを「Discord連携モード」へ自動構成します。
* **② ボット配置ツール (02-Eq_Discord)**
  - 最大5件のWebhook、Embed（リッチ）/ Simple通知の切り替えが可能です。
  - v4.0より、フリーズ監視・メモリ対策の「見張り番」機能が統合されました。
* **③ 初期化・修復ツール (03-Eq_Reset)**
  - 設定ミス時の最終手段。EqMaxをインストール直後の状態へ戻します。
* **④ ログ・画像クリーナー (O01-Eq_Cleaner)**
  - 肥大化したログや画像を掃除し、PCを軽く保ちます。

---

### ✨ 更新履歴 (v4.5.0 抜粋)
* **不具合修正**: v4.0で発生した速報通知の不具合を修正。
* **全自動エスコート**: `EqMax.ini` がない場合、自動でEqMaxを起動し生成をサポート。
* **アイコン実装**: タスクバーやショートカットに専用アイコンを表示。
* **プロセスマネジメント**: ファイルロックを防ぐための強制終了ロジックを強化。

---

## 🔗 関連リンク・免責事項
* **[EqMax 配布元公式サイト]**: [https://melanion.info/eqmax/](https://melanion.info/eqmax/)
* **免責事項**: 本ツールは個人が開発した非公式ツールです。本ツールの使用によって生じた損害について、開発者は一切の責任を負いません。

<div align="right">
  Developed by MustangTIS
</div>
