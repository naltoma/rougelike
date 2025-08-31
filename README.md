# Python初学者向けローグライク演習フレームワーク

[![Version](https://img.shields.io/badge/version-v1.0.1-blue.svg)](VERSION_HISTORY.md)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-88.9%25-brightgreen.svg)](#🧪-テスト実行)
[![Quality](https://img.shields.io/badge/quality-優良⭐-gold.svg)](#📈-品質メトリクス)

Python初学者のための教育用ローグライクゲームフレームワークです。体験的なプログラミング学習を通じて、基礎的なプログラミングスキルを習得できます。

> **🔧 v1.0.1 pytest対応！** 高機能テストシステム搭載 - 詳細は [VERSION_HISTORY.md](VERSION_HISTORY.md) をご覧ください

## 🎯 特徴

### 🏫 教育に特化した機能
- **初学者向けエラーメッセージ**: 理解しやすく、建設的な指導
- **無限ループ自動検出**: 初学者が陥りやすい問題を早期発見
- **段階的ヒントシステム**: 学習者の進度に応じた適応的支援
- **個別学習プロファイル**: 学習者の特性を分析・最適化

### 📊 教師支援機能
- **リアルタイム学習データ収集**: 学習者の行動を詳細記録
- **Google Sheets連携**: クラス全体の進捗を一元管理
- **自動学習パターン分析**: 問題行動の早期発見
- **個別支援推奨**: データに基づく指導提案

### 🎮 豊富なゲーム要素
- **高度な敵AIシステム**: 巡回、追跡、警備、ハンター
- **包括的アイテムシステム**: 装備、消耗品、エンチャント
- **戦闘・ドロップシステム**: 戦略的思考を促進
- **拡張可能ステージ**: カスタム学習シナリオ

## 📁 プロジェクト構造

```
rougelike/
├── engine/                    # コアエンジン
│   ├── __init__.py           # 基本データモデル
│   ├── api.py               # 学生向けAPI
│   ├── game_state.py        # ゲーム状態管理
│   ├── commands.py          # コマンドパターン
│   ├── renderer.py          # 描画システム
│   ├── stage_loader.py      # ステージ読み込み
│   ├── progression.py       # 進捗管理
│   ├── session_logging.py   # セッションログ
│   ├── educational_errors.py # 教育的エラー処理
│   ├── quality_assurance.py # 品質保証
│   ├── progress_analytics.py # 進歩分析
│   ├── educational_feedback.py # 教育フィードバック
│   ├── data_uploader.py     # データアップロード
│   ├── enemy_system.py      # 敵システム
│   ├── item_system.py       # アイテムシステム
│   ├── advanced_game_state.py # 拡張ゲーム状態
│   └── main_game_loop.py    # メインループ
├── stages/                  # ステージファイル
├── tests/                   # テストスイート
├── data/                    # データ保存
├── config/                  # 設定ファイル
├── docs/                    # ドキュメント
└── scripts/                 # ユーティリティ
```

## 🚀 クイックスタート

### 基本的な使用方法

```python
import engine.api as game

# ゲーム初期化
game.initialize_stage("stage01")
game.set_student_id("your_student_id")

# 基本的な移動
game.move()        # 前進
game.turn_left()   # 左回転
game.turn_right()  # 右回転

# 環境確認
game.see()         # 周囲を確認

# アクション
game.attack()      # 攻撃
game.pickup()      # アイテム拾得

# ゲーム状態確認
if game.is_game_finished():
    result = game.get_game_result()
    print(f"ゲーム結果: {result}")
```

### 学習支援機能

```python
# 進捗確認
game.show_progress_summary()

# ヒント要求
hint = game.request_hint()
print(f"ヒント: {hint}")

# 学習フィードバック
game.show_learning_feedback()

# エラー時のヘルプ
game.show_error_help()
```

## 🧪 テスト実行

フレームワークは**pytest**対応の高機能テストシステムを搭載しています。

### 基本テスト実行
```bash
# 推奨: pytest統合実行（失敗分析・再実行機能付き）
python run_tests.py

# または直接pytest実行
pytest -v
```

### 高度なテスト実行
```bash
# 失敗したテストのみ再実行
pytest --lf -v

# 特定テストファイルのみ
pytest tests/test_api.py -v

# GUIテスト以外を実行（pygame不要）
pytest -m "not gui" -v

# 単体テストのみ
pytest -m unit -v

# 統合テストのみ  
pytest -m integration -v

# パターンマッチでテスト実行
pytest -k "progression" -v
```

### Makefileによる便利実行
```bash
# 全テスト実行
make test

# 失敗テストのみ再実行
make test-failed

# GUIテスト以外
make test-no-gui

# カバレッジ付きテスト
make test-coverage

# 並列テスト実行（高速化）
make test-parallel
```

### テスト結果の活用
pytest統合実行では以下の機能を提供：

- **失敗テスト分析**: どのテストが失敗したか詳細表示
- **再実行コマンド**: 失敗したテストのみ実行するコマンドを自動出力
- **品質評価**: テスト成功率による品質判定
- **実行時間**: パフォーマンス測定

```bash
# 例: 実行結果
📊 テスト実行結果サマリー
🎯 総合結果: 23/26 テスト成功  
📈 成功率: 88.5%
⭐ 品質評価: 良好

❌ 失敗したテスト (3個):
   • tests/test_api.py::test_initialize_stage
   • tests/test_renderer.py::test_gui_renderer

🔄 失敗したテストのみ再実行:
   pytest tests/test_api.py -v
   pytest tests/test_renderer.py -v
```

## 📊 Google Sheets連携設定

教師向け学習データ管理機能を使用する場合:

1. **Google Cloud Console設定**
   ```bash
   # 必要なライブラリをインストール
   pip install gspread oauth2client
   ```

2. **設定ファイル作成**
   ```bash
   # サンプル設定をコピー
   cp config/google_sheets_sample.json config/google_sheets.json
   ```

3. **詳細なセットアップ手順**
   
   詳しくは [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) を参照してください。

## 🎓 教育的価値

### 学習者が習得できるスキル

**プログラミング基礎**
- 変数、データ型、制御構造の理解
- 関数とモジュールの使用方法
- オブジェクト指向プログラミングの基礎

**問題解決能力**
- 論理的思考とアルゴリズム設計
- デバッグ技術とエラー対処法
- 段階的問題分解アプローチ

**コード品質意識**
- 可読性とコードスタイルの重要性
- テストとリファクタリングの概念
- ドキュメント作成の習慣

### 教師向け指導支援

**データドリブン指導**
- 学習者の行動パターン分析
- 個別学習特性の把握
- 効果的な介入タイミングの判定

**効率的クラス管理**
- リアルタイム進捗監視
- 自動的な支援必要性検出
- 学習成果の可視化

## 🔧 開発環境

### 必要要件
- Python 3.8+
- **(推奨) pytest** (高機能テスト実行用)
- (オプション) pygame (GUI機能用)
- (オプション) gspread, oauth2client (Google Sheets連携用)

### 開発セットアップ
```bash
# リポジトリクローン
git clone [repository-url]
cd rougelike

# 仮想環境作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール（pytest含む）
pip install -r requirements.txt

# テスト実行
python run_tests.py

# または高機能pytest実行
make test
```

## 📈 品質メトリクス

最新の品質評価：

- **機能カバレッジ**: 100% (11/11機能)
- **テスト成功率**: 88.9% (pytest対応)
- **エンジンファイル**: 18個 (11,149行)
- **テストファイル**: 26個 (pytest対応)
- **テストフレームワーク**: pytest + マーカー + 失敗分析
- **総合品質評価**: 優良 ⭐

## 📚 ドキュメント

- **[バージョン履歴](VERSION_HISTORY.md)** - リリース履歴と変更点
- [進捗管理ガイド](PROGRESSION_GUIDE.md) - 進捗機能の使用方法
- [セッションログガイド](SESSION_LOGGING_GUIDE.md) - ログ機能の詳細
- [Google Sheets設定](GOOGLE_SHEETS_SETUP.md) - データ連携設定
- [GUI使用方法](GUI_USAGE.md) - 視覚的インターフェース

## 🔄 既知の問題

- **pygame依存関係**: GUIレンダラー機能にpygameが必要
- **一部APIメソッド**: メソッド名の不一致による互換性問題

## 🤝 貢献

プロジェクトへの貢献を歓迎します：

1. イシュー報告
2. 機能提案
3. プルリクエスト
4. ドキュメント改善

## 📄 ライセンス

このプロジェクトは教育目的で作成されています。

## 🙏 謝辞

Python初学者教育の向上を目指して開発されました。教育現場での実践的な学習支援を通じて、次世代のプログラマー育成に貢献することを願っています。

---

## 📋 更新履歴

最新バージョン: **v1.0.1** (2025年8月31日)
- 🧪 pytest対応テストシステム実装
- 🔄 失敗テストの分析・再実行機能
- 📊 テストマーカーとMakefile対応
- ⚡ 並列テスト実行とカバレッジ対応

詳細な変更履歴は [VERSION_HISTORY.md](VERSION_HISTORY.md) をご覧ください。

---

## 備考

AI-DLC（AI-Driven Development Life Cycle） と Spec-Driven Development（仕様駆動開発） のワークフローを設定した[cc-sdd / Claude Code Spec](https://github.com/gotalab/claude-code-spec)で作成しています。

---

**🎮 楽しく学び、効果的に指導する - Python教育の新しい形 v1.0.1**