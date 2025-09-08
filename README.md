# Python初学者向けローグライク演習フレームワーク

[![Version](https://img.shields.io/badge/version-v1.2.5-blue.svg)](VERSION_HISTORY.md)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-88.9%25-brightgreen.svg)](#🧪-テスト実行)
[![Quality](https://img.shields.io/badge/quality-優良⭐-gold.svg)](#📈-品質メトリクス)

Python初学者のための教育用ローグライクゲームフレームワークです。体験的なプログラミング学習を通じて、基礎的なプログラミングスキルを習得できます。

> **⚡ v1.2.5 7段階速度制御完了！** Continue実行をx1〜x50で調整可能・超高速デバッグ対応 - 詳細は [VERSION_HISTORY.md](VERSION_HISTORY.md) をご覧ください

## 🎯 特徴

### 🏫 教育に特化した機能
- **初学者向けエラーメッセージ**: 理解しやすく、建設的な指導
- **無限ループ自動検出**: 初学者が陥りやすい問題を早期発見
- **段階的ヒントシステム**: 学習者の進度に応じた適応的支援
- **個別学習プロファイル**: 学習者の特性を分析・最適化
- **⚡ 7段階速度制御**: x1〜x50でContinue実行速度を調整・デバッグ効率向上

### 📊 教師支援機能
- **リアルタイム学習データ収集**: 学習者の行動を詳細記録
- **Google Sheets連携**: 無料Webhook方式で簡単5分セットアップ
- **ステージ別データ管理**: 自動シート作成・上書き機能
- **個別支援推奨**: 完了フラグ・アクション数・コード行数分析

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
│   ├── webhook_uploader.py  # Webhook連携
│   ├── enemy_system.py      # 敵システム
│   ├── item_system.py       # アイテムシステム
│   ├── advanced_game_state.py # 拡張ゲーム状態
│   ├── main_game_loop.py    # メインループ
│   ├── enhanced_7stage_speed_control_manager.py # ⚡ 7段階速度制御
│   ├── ultra_high_speed_controller.py # 超高速制御
│   ├── speed_control_error_handler.py # 速度制御エラー処理
│   └── enhanced_7stage_speed_errors.py # 速度制御例外
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

### ⚡ 7段階速度制御機能 (v1.2.5)

GUIの **Execution Control** パネルで、Continue実行の速度を調整できます：

- **x1** (2.0秒) - 学習モード（ゆっくりと理解）
- **x2** (1.0秒) - 標準速度（デフォルト）
- **x3** (0.5秒) - 2倍速相当
- **x4** (0.25秒) - 4倍速
- **x5** (0.1秒) - 10倍速
- **x10** (0.05秒) - 超高速
- **x50** (0.001秒) - 最高速度（デバッグ用）

**使用例：**
1. **学習時**: x1でアルゴリズムを詳細確認
2. **デバッグ時**: x50で問題箇所を高速特定
3. **実演時**: x3〜x5で適度な速度で説明

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

## 🔗 主要機能

### ⚡ 7段階速度制御システム (v1.2.5 新機能)
Continue実行の速度をリアルタイムで調整可能：

#### 教育効果
- **x1**: 初学者向け詳細確認モード
- **x2**: デフォルト標準速度
- **x3-x5**: 実演・説明に最適
- **x10-x50**: デバッグ・高速検証

#### 技術仕様
- 高精度スリープ制御（1ms精度）
- リアルタイム速度変更
- 超高速実行対応（視認不可レベル）

### 📊 Google Sheets連携設定

**v1.2.3**: 無料Google Apps Script Webhook連携

### 🚀 教員向けセットアップ（5分）
1. **Google Apps Script設定**
   - [Code.gs](google_apps_script/Code.gs) をGoogle Apps Scriptにコピー&貼り付け
   - Webhookエンドポイントをデプロイ
   - （オプション）共有フォルダID設定

詳しくは [教員セットアップガイド](docs/teacher_setup_guide.md) を参照

### 📤 学生向けセットアップ（1分）
```bash
# 初回設定
python upload_webhook.py --setup

# ログアップロード
python upload_webhook.py stage01

# 接続テスト
python upload_webhook.py --test
```

詳しくは [学生セットアップガイド](docs/student_setup_guide.md) を参照

### 特徴
- **完全無料**: OAuth2認証不要、Google Apps Scriptの無料枠内
- **簡単セットアップ**: 複雑な設定ファイル・認証情報不要
- **自動管理**: ステージ別シート作成、同一学生データ自動上書き
- **7項目データ**: 学生ID・ステージ・終了日時・完了フラグ・アクション数・コード行数・解法コード

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

最新バージョン: **v1.2.3** (2025年9月4日)
- 🔗 Google Apps Script Webhook連携完了
- 📊 無料・簡単セットアップ（教員5分・学生1分）
- 🎯 ステージ別シート自動管理・上書き機能
- 📝 7項目教育データ（完了フラグ・アクション数・コード行数等）

詳細な変更履歴は [VERSION_HISTORY.md](VERSION_HISTORY.md) をご覧ください。

---

## 備考

AI-DLC（AI-Driven Development Life Cycle） と Spec-Driven Development（仕様駆動開発） のワークフローを設定した[cc-sdd / Claude Code Spec](https://github.com/gotalab/claude-code-spec)で作成しています。

---

**🎮 楽しく学び、効果的に指導する - Python教育の新しい形 v1.2.3**