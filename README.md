# Python初学者向けローグライク演習フレームワーク

[![Version](https://img.shields.io/badge/version-v1.2.12-blue.svg)](VERSION_HISTORY.md)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-88.9%25-brightgreen.svg)](#🧪-テスト実行)
[![Quality](https://img.shields.io/badge/quality-優良⭐-gold.svg)](#📈-品質メトリクス)

Python初学者のための教育用ローグライクゲームフレームワークです。体験的なプログラミング学習を通じて、基礎的なプログラミングスキルを習得できます。

> **💊 v1.2.12 高度アイテムシステム完成！** 不利アイテム・is_available/dispose API・ポーション回復・包括的ドキュメント・プロジェクト整理で学習体験を大幅向上 - 詳細は [docs/v1.2.12.md](docs/v1.2.12.md) をご覧ください

## 🎯 特徴

### 🏫 教育に特化した機能
- **初学者向けエラーメッセージ**: 理解しやすく、建設的な指導
- **無限ループ自動検出**: 初学者が陥りやすい問題を早期発見
- **段階的ヒントシステム**: 学習者の進度に応じた適応的支援
- **個別学習プロファイル**: 学習者の特性を分析・最適化
- **📚 包括的チュートリアル体系**: 4段階学習システム（基礎→実践→応用→参照）
- **🚫 ハードコーディング排除**: get_stage_info()による動的設計教育
- **👁️ 拡張視界システム**: vision_map・vision_range制御で戦略的思考育成
- **⚡ 7段階速度制御**: x1〜x50でContinue実行速度を調整・デバッグ効率向上
- **⚔️ 戦闘ベース学習**: Stage04-07で攻撃システムを通じた戦略的思考習得
- **🛡️ wait()API**: Stage08-10で戦術的待機・敵行動観察・タイミング判断学習
- **👁️ 敵AI視覚システム**: 方向性視覚・壁遮蔽・警戒追跡で高度な戦略学習
- **🤖 大型敵システム**: Stage11-13で2x2/3x3/2x3敵・怒りモード・条件付き撃破学習
- **🏆 最終ボス複合戦**: 交互怒りパターン検出・総合戦略思考・最高難易度挑戦
- **🎯 ランダムステージ生成**: 5種類のステージタイプ自動生成・A*解法探索・無限学習コンテンツ
- **🎨 GUI Enhancement**: 動的ステージ名表示・ステータス変化強調表示・ステップ実行維持
- **💊 高度アイテムシステム**: 不利アイテム(bomb)・is_available/dispose API・ポーションHP回復機能
- **📚 包括的ドキュメント**: 全15ステージ詳細解説・段階的学習ガイド・プロジェクト構造最適化

### 📊 教師支援機能
- **リアルタイム学習データ収集**: 学習者の行動を詳細記録
- **Google Sheets連携**: 無料Webhook方式で簡単5分セットアップ
- **ステージ別データ管理**: 自動シート作成・上書き機能
- **個別支援推奨**: 完了フラグ・アクション数・コード行数分析

### 🎮 豊富なゲーム要素
- **攻撃・戦闘システム**: プレイヤー攻撃、敵カウンター攻撃、ターン制戦闘
- **wait()戦術システム**: 待機による敵行動観察・タイミング戦略
- **高度な敵AI視覚システム**: 方向性視覚・壁遮蔽・警戒追跡・メモリ機能
- **大型敵システム**: 2x2/3x3/2x3マス占有敵・怒りモード・範囲攻撃
- **特殊条件付き撃破**: 交互怒りパターン検出・自動撃破システム
- **ステージ毎設定システム**: プレイヤーHP・攻撃力の柔軟調整
- **包括的アイテムシステム**: 装備、消耗品、エンチャント
- **戦闘・ドロップシステム**: 戦略的思考を促進
- **13段階学習ステージ**: 基礎移動→戦闘→プログラミング構造→高度戦術→最終ボス複合戦（Stage01-13対応）

## 📁 プロジェクト構造

```
rougelike/
├── engine/                    # コアエンジン
│   ├── gui_enhancement/      # 🎨 GUI Enhancement (v1.2.11)
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
├── src/                     # 🎯 ランダムステージ生成システム
│   ├── stage_generator/     # ステージ生成ライブラリ
│   ├── stage_validator/     # ステージ検証・解法探索
│   └── yaml_manager/        # YAML管理ライブラリ
├── scripts/                 # CLIツール
│   ├── generate_stage.py    # 🎯 ランダムステージ生成CLI
│   └── validate_stage.py    # 🎯 ステージ検証・解法探索CLI
├── stages/                  # ステージファイル
├── tests/                   # テストスイート
├── data/                    # データ保存
├── config/                  # 設定ファイル
└── docs/                    # ドキュメント
    ├── see_tutorial/        # 📚 v1.2.10 包括的seeチュートリアル体系
    │   ├── README.md        # 学習ガイド・チュートリアル一覧
    │   ├── basic_api.md     # API基礎習得（353行）
    │   ├── simple_algorithm.md # Stage01特化アルゴリズム（522行）
    │   ├── general_purpose.md # 汎用プレイヤー構築（1620行）
    │   └── see_description.md # API完全リファレンス（414行）
    │   └── see_description.md # API完全リファレンス（414行）
    ├── STAGES.md           # ステージ一覧
    └── v1.2.10.md          # v1.2.10リリースノート
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

# 環境確認・戦術
info = game.see()         # 周囲を確認（デフォルト視界範囲2）
info = game.see(3)        # 広範囲観測（視界範囲3）
stage_info = game.get_stage_info()  # ステージ情報取得（v1.2.10新機能）
game.wait()               # 1ターン待機（敵行動観察）

# アクション
game.attack()      # 攻撃
game.pickup()      # アイテム拾得

# ゲーム状態確認
if game.is_game_finished():
    result = game.get_game_result()
    print(f"ゲーム結果: {result}")
```

### 🎯 ランダムステージ生成 (v1.2.9 新機能)

無限の学習コンテンツを自動生成できます：

```bash
# 基本移動ステージ生成（stage01-03相当）
python scripts/generate_stage.py --type move --seed 123

# 攻撃ステージ生成（stage04-06相当）
python scripts/generate_stage.py --type attack --seed 456

# 収集ステージ生成（stage07-09相当）
python scripts/generate_stage.py --type pickup --seed 789

# 巡回ステージ生成（stage10相当）
python scripts/generate_stage.py --type patrol --seed 101

# 特殊ステージ生成（stage11-13相当）
python scripts/generate_stage.py --type special --seed 202

# 生成と同時に検証
python scripts/generate_stage.py --type attack --seed 456 --validate

# 既存ステージの解法探索
python scripts/validate_stage.py --file stages/stage01.yml --solution

# 制限無し完全探索
python scripts/validate_stage.py --file stages/stage01.yml --solution --max-nodes unlimited
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

### メインドキュメント
- **[v1.2.11リリースノート](docs/v1.2.11.md)** - 最新アップデート詳細
- **[v1.2.10リリースノート](docs/v1.2.10.md)** - seeチュートリアル体系化
- **[バージョン履歴](VERSION_HISTORY.md)** - リリース履歴と変更点

### 📚 学習チュートリアル (v1.2.10 新機能)
- **[seeチュートリアル体系](docs/see_tutorial/)** - 4段階学習システム
  - [学習ガイド](docs/see_tutorial/README.md) - 推奨学習パス・チュートリアル一覧
  - [基本API習得](docs/see_tutorial/basic_api.md) - see()・get_stage_info()の基礎
  - [シンプルアルゴリズム実践](docs/see_tutorial/simple_algorithm.md) - Stage01確実クリア手法
  - [汎用的プレイヤー構築](docs/see_tutorial/general_purpose.md) - 複数ステージ対応設計
  - [API完全リファレンス](docs/see_tutorial/see_description.md) - v1.2.10対応仕様書

### システム詳細
- [進捗管理ガイド](PROGRESSION_GUIDE.md) - 進捗機能の使用方法
- [セッションログガイド](SESSION_LOGGING_GUIDE.md) - ログ機能の詳細
- [Google Sheets設定](GOOGLE_SHEETS_SETUP.md) - データ連携設定
- [GUI使用方法](GUI_USAGE.md) - 視覚的インターフェース

## 🔄 既知の問題

- **pygame依存関係**: GUIレンダラー機能にpygameが必要（オプション）
- **背景プロセス**: 一部のデバッグプロセスが稼働中の場合あり（影響なし）

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

最新バージョン: **v1.2.12** (2025年9月29日)
- 💊 高度アイテムシステム - 不利アイテム(bomb)・is_available/dispose API・ポーションHP回復
- 📚 包括的ドキュメント - 全15ステージ詳細解説・段階的学習ガイド
- 🧹 プロジェクト整理 - ファイル構造最適化・テスト環境統合
- 📈 学習効率向上 - 戦略的思考育成・包括的学習支援体制
- 🔧 システム安定化 - A*パスファインディング修正・品質保証完成

詳細な変更履歴は [VERSION_HISTORY.md](VERSION_HISTORY.md) をご覧ください。

---

## 備考

- 〜 v1.2.8までは、AI-DLC（AI-Driven Development Life Cycle） と Spec-Driven Development（仕様駆動開発） のワークフローを設定した[cc-sdd / Claude Code Spec](https://github.com/gotalab/claude-code-spec)で作成しました。
- v1.2.9からは、[spec kit](https://github.com/github/spec-kit)で作成しています。

---
