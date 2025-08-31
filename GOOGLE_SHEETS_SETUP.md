# Google Sheets統合セットアップガイド

本システムでは学生の学習データをGoogle Sheetsにリアルタイムでアップロードし、教師が学習状況を監視・分析できます。

## 📋 機能概要

### 教師向け機能
- **リアルタイムデータ収集**: 学生の学習行動を自動記録
- **クラス全体監視**: 複数学生の進捗を一元管理
- **学習パターン分析**: 問題のある学習行動を早期発見
- **個別支援特定**: 支援が必要な学生を自動識別

### アップロードされるデータ
1. **学生進捗**: セッション時間、成功率、学習段階など
2. **セッションログ**: API呼び出し履歴、エラー記録
3. **コード分析**: 複雑度、保守性指数、品質メトリクス
4. **学習パターン**: 無限ループ、壁衝突パターンなど

## 🚀 セットアップ手順

### ステップ1: Google Cloud Console設定

1. [Google Cloud Console](https://console.cloud.google.com) にアクセス
2. 新しいプロジェクトを作成（または既存プロジェクト選択）
3. **APIライブラリ** で「Google Sheets API」を検索して有効化

### ステップ2: サービスアカウント作成

1. **IAM > サービスアカウント** へ移動
2. 「サービスアカウントを作成」をクリック
3. 名前: `rougelike-data-uploader`（任意）
4. 説明: `学習データアップロード用サービスアカウント`
5. 作成完了

### ステップ3: 認証キー取得

1. 作成したサービスアカウントをクリック
2. 「キー」タブ → 「キーを追加」 → 「新しいキーを作成」
3. **JSON形式**を選択してダウンロード
4. ダウンロードしたファイルを `config/service-account.json` に配置

### ステップ4: スプレッドシート準備

1. [Google スプレッドシート](https://sheets.google.com)で新規作成
2. 適切な名前を設定（例: `プログラミング授業_学習データ`）
3. URLからスプレッドシートIDを取得
   ```
   https://docs.google.com/spreadsheets/d/【ここがスプレッドシートID】/edit
   ```
4. サービスアカウントのメールアドレスと共有（編集権限）
   - スプレッドシート右上の「共有」をクリック
   - サービスアカウントのメール（`xxx@yyy.iam.gserviceaccount.com`）を追加
   - **編集者**権限で共有

### ステップ5: 設定ファイル作成

1. `config/google_sheets_sample.json` を `config/google_sheets.json` にコピー
2. 以下の項目を更新:
   ```json
   {
     "enabled": true,
     "service_account_path": "config/service-account.json",
     "spreadsheet_id": "取得したスプレッドシートID"
   }
   ```

### ステップ6: Pythonライブラリインストール

```bash
pip install gspread oauth2client
```

## 🧪 動作テスト

設定完了後、以下でテストを実行:

```python
python test_google_sheets.py
```

成功例:
```
✅ Google Sheets統合システムテスト成功！
🎉 全てのテストが合格しました
```

## 📊 使用方法

### 基本的な使用
```python
from engine.api import *

# 初期化
initialize_api("cui", enable_progression=True)
set_student_id("student_001")

# 学習活動...
initialize_stage("stage01")
move()  # 自動的にデータがアップロードキューに追加

# 手動アップロード
upload_student_data()
force_sheets_upload()
```

### 状態確認
```python
# Google Sheets統合状態を表示
show_sheets_status()

# クラス全体レポート生成
class_students = ["student_001", "student_002", "student_003"]
show_class_report(class_students)
```

## 📈 生成されるワークシート

システムが自動的に以下のワークシートを作成:

### 1. 学生進捗 (学生進捗)
- 日時、学生ID、ステージID、セッション時間
- 成功率、失敗回数、ヒント使用回数
- コード行数、複雑度、学習段階

### 2. セッション記録 (セッション記録) 
- 日時、セッションID、学生ID、API呼び出し
- 成功/失敗、実行時間、エラーメッセージ

### 3. コード分析 (コード分析)
- 日時、学生ID、ステージID
- 総行数、論理行数、複雑度、関数数
- 保守性指数、重複率

### 4. 学習パターン (学習パターン)
- 日時、学生ID、パターンタイプ
- 信頼度、頻度、説明、推奨アクション

## 🔧 トラブルシューティング

### よくある問題

**問題**: `gspread` が見つからない
```
解決: pip install gspread oauth2client
```

**問題**: 認証エラー
```
解決: 
1. service-account.json ファイルパスを確認
2. スプレッドシートの共有設定を確認
3. Google Sheets APIが有効化されているか確認
```

**問題**: スプレッドシートに書き込めない
```
解決:
1. サービスアカウントにスプレッドシートの編集権限があるか確認
2. スプレッドシートIDが正しいか確認
```

### デバッグ方法

```python
# 詳細な状態確認
status = get_sheets_status()
print(f"詳細状態: {status}")

# テスト実行
python test_google_sheets.py
```

## 🎯 教育効果

### 教師のメリット
1. **リアルタイム監視**: 学生の学習状況を即座に把握
2. **早期介入**: 問題のあるパターンを早期発見
3. **データドリブン指導**: 客観的データに基づく指導
4. **効率的クラス管理**: 複数学生を同時監視

### 学生のメリット
1. **個別最適化**: 学習パターンに応じた個別指導
2. **適切なタイミング**: データに基づく最適な支援
3. **学習可視化**: 自身の学習状況を客観視
4. **継続的改善**: 学習行動の継続的な改善

## ⚙️ 高度な設定

### アップロード頻度の調整
```json
{
  "update_frequency": 300,  // 5分間隔
  "batch_size": 50         // 50件ずつまとめて送信
}
```

### カスタムワークシート名
```json
{
  "worksheets": {
    "student_progress": "カスタム進捗シート名",
    "session_logs": "カスタムログシート名"
  }
}
```

このシステムにより、Python初学者の教育がデータドリブンで効率的に行えます。