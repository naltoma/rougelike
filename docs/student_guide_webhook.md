# 📖 学生向け使用ガイド - Webhook版

## 🎯 概要

ローグライク演習フレームワーク v1.2.3 Webhook版の使用方法を説明します。  
この版では、**完全無料**でセッションログを教員と共有できます！

**⚡ 特徴:**
- 🆓 完全無料（Google Cloud Console不要）
- 🚀 簡単セットアップ（認証不要）
- 📊 リアルタイム共有（Google Sheets）

---

## 🚀 初期設定（1回のみ）

### Step 1: セットアップコマンド実行

```bash
python upload_webhook.py --setup
```

### Step 2: 必要な情報を入力

プログラムが以下の情報を求めます：

#### 1. Webhook URL
```
🔗 Webhook URLを入力してください: 
```
**→ 教員から提供されたURL（長いURLです）を貼り付け**

URL例:
```
https://script.google.com/macros/s/AKfycbxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/exec
```

#### 2. 学生ID  
```
👤 学生IDを入力してください (例: 123456A):
```
**→ あなたの学生ID（6桁数字+1英字）を入力**

### Step 3: 接続テスト

設定完了後、接続テストを実行：

```bash
python upload_webhook.py --test
```

✅ 成功すると「接続テスト成功」と表示されます

---

## 📤 ログのアップロード方法

### 基本的な使用方法

#### 1. 特定のステージをアップロード
```bash
python upload_webhook.py stage01
```

#### 2. 全てのログをアップロード
```bash
python upload_webhook.py --all
```

#### 3. 設定状態の確認
```bash
python upload_webhook.py --status
```

### 高度な使用方法

#### ドライラン（テスト実行）
```bash
python upload_webhook.py stage01 --dry-run
```
**→ 実際にアップロードせず、何が送信されるかを確認**

#### 詳細ログ出力
```bash
python upload_webhook.py stage01 --verbose
```
**→ 詳しい処理内容を表示**

---

## 📊 アップロード結果の確認

### 成功例
```
✅ アップロード完了！
   アップロード済み: 45 件
   処理時間: 2.34 秒
   Webhook URL: https://script.google.com/macros/s/...

📈 アップロード統計:
   総アップロード数: 145
   成功: 142
   失敗: 3

📊 スプレッドシートで進捗を確認してください！
```

### 教員のスプレッドシートで確認

アップロード後、教員のGoogle Sheetsに以下の情報が記録されます：

| 学生ID | ステージ | 日時 | スコア | レベル | HP | アクション | ... |
|--------|----------|------|--------|--------|----|-----------|----|
| 123456A | stage01 | 2024/01/01 10:00 | 250 | 3 | 80/100 | move | ... |

---

## 🔧 よくある問題と解決方法

### 問題1: 設定がうまくいかない

**症状**: セットアップ時にエラーが出る

**解決方法**:
```bash
# 現在の設定を確認
python upload_webhook.py --status

# 設定をやり直す
python upload_webhook.py --setup
```

### 問題2: Webhook URLエラー

**症状**: 「無効なWebhook URL」エラー

**解決方法**:
- URLが `https://script.google.com/macros/s/` で始まっているか確認
- URLに余分なスペースがないか確認
- 教員に正しいURLを再度確認

### 問題3: 学生ID形式エラー

**症状**: 「無効な学生ID形式」エラー

**解決方法**:
- 6桁の数字 + 1文字のアルファベット（大文字）になっているか確認
- 例: `123456A` （○）、`12345A` （×）、`123456a` （×）

### 問題4: アップロード失敗

**症状**: 「アップロード失敗」メッセージ

**解決方法**:
```bash
# 接続テストを実行
python upload_webhook.py --test

# インターネット接続を確認
# しばらく待ってからリトライ
python upload_webhook.py stage01
```

### 問題5: ログファイルが見つからない

**症状**: 「ログファイルが見つかりません」

**解決方法**:
- まずゲームを実行してセッションログを生成
- `data/` フォルダにログファイルがあるか確認
- 正しいディレクトリでコマンドを実行しているか確認

---

## 💡 便利なコマンド集

### 毎回使うコマンド
```bash
# 演習後の基本的な流れ
python upload_webhook.py stage01     # ログアップロード
python upload_webhook.py --status    # 確認
```

### 時々使うコマンド
```bash
python upload_webhook.py --test      # 動作テスト
python upload_webhook.py --all       # 全ログアップロード
```

### トラブル時のコマンド
```bash
python upload_webhook.py --setup     # 設定のやり直し
python upload_webhook.py stage01 --dry-run  # テスト実行
python upload_webhook.py stage01 --verbose  # 詳細ログ
```

---

## 🔐 プライバシーについて

### 送信される情報

- **学生ID**: あなたの学生ID
- **ゲームデータ**: レベル、スコア、HP、位置など
- **アクションログ**: 移動、攻撃などの行動記録
- **エラーログ**: プログラムのエラー情報

### 送信されない情報

- **個人名**: 氏名は記録されません
- **ソースコード**: あなたが書いたコードは送信されません
- **システム情報**: パソコンの詳細情報は送信されません

---

## 🎮 演習の流れ

### 1. ステージ開始
```bash
# ゲームを実行
python main_stage01.py
```

### 2. プログラム作成・テスト
```python
# solve() 関数を編集
def solve():
    # あなたのロジックを実装
    move('north')
    attack()
    # ...
```

### 3. ログアップロード
```bash
# セッションログをアップロード
python upload_webhook.py stage01
```

### 4. 結果確認
- 教員のスプレッドシートに結果が表示される
- 他の学生の進捗状況も確認できる（学生IDのみ）

---

## 📞 困ったときは

### よくある質問

**Q: 何度もアップロードしても大丈夫？**  
A: はい、同じステージを何度でもアップロードできます

**Q: 他の学生のデータは見える？**  
A: 学生IDのみ表示され、個人名は表示されません

**Q: 途中でやめても大丈夫？**  
A: はい、Ctrl+Cでいつでも中断できます

### サポート

1. **まず試すこと**:
   ```bash
   python upload_webhook.py --status  # 設定確認
   python upload_webhook.py --test    # 接続テスト
   ```

2. **解決しない場合**:
   - このガイドのトラブルシューティングを確認
   - 教員に質問
   - システム管理者に相談

---

## 🎉 成功例

正しく設定できている学生の例：

```bash
$ python upload_webhook.py --status

🚀 ローグライク演習 Webhookログアップロードツール v1.2.3
   （Google Apps Script版 - 完全無料）
============================================================

📊 現在の設定状態:
🔗 Webhook URL: ✅ 設定済み
   URL: https://script.google.com/macros/s/AKfycbxxx...
👤 学生ID: ✅ 設定済み
   ID: 123456A
📝 セッションログ:
   利用可能学生: 1 名
   利用可能ステージ: 3 個
   学生ID: 123456A
   ステージ: stage01, stage02, stage03
📈 アップロード統計:
   総アップロード: 67 件
   成功: 67 件
   失敗: 0 件

🎯 アップロード準備: ✅ 完了

💡 ヒント: アップロード準備完了です
```

**この表示が出れば完璧です！** 🎉

---

**頑張って演習に取り組んでください！** 📚✨