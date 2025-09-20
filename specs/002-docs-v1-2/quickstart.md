# Quickstart: see()関数チュートリアル検証手順

## 前提条件確認

### システム要件
- [ ] Python 3.11+がインストール済み
- [ ] ローグライクフレームワークが動作可能
- [ ] stage01.ymlが存在し、正常に読み込める

### ファイル確認
```bash
# 必要ファイルの存在確認
ls stages/stage01.yml        # Stage01設定ファイル
ls SeeDescription.md         # 既存リファレンス
ls main.py                   # 基本実行ファイル（編集禁止）
```

## チュートリアル作成検証

### Step 1: 基本構造作成確認
```bash
# チュートリアルファイル作成
touch docs/tutorial_see.md

# 基本セクション構造確認
grep -E "^#+ " docs/tutorial_see.md
# 期待結果: 6つのメインセクション見出しが表示される
```

### Step 2: Stage01解析検証
```python
# Stage01の基本情報確認
import yaml
with open('stages/stage01.yml', 'r', encoding='utf-8') as f:
    stage_data = yaml.safe_load(f)

print("ボードサイズ:", stage_data['board']['size'])
print("プレイヤー開始位置:", stage_data['player']['start'])
print("ゴール位置:", stage_data['goal']['position'])
print("使用可能API:", stage_data['constraints']['allowed_apis'])
```

### Step 3: see()関数動作確認
```python
# ゲーム開始時のsee()実行テスト
# 注意: 実際のゲームセッション内で実行する必要がある

info = see()
print("プレイヤー位置:", info["player"]["position"])
print("プレイヤー向き:", info["player"]["direction"])
print("周囲の状況:")
for direction, obj in info["surroundings"].items():
    print(f"  {direction}: {obj}")
```

### Step 4: 完全クリア手順検証
```python
# Stage01クリアまでの基本手順
def validate_stage01_solution():
    """Stage01の解法を段階的に検証"""

    # 初期状態確認
    info = see()
    start_pos = info["player"]["position"]
    goal_pos = [4, 4]  # stage01.ymlから

    print(f"開始位置: {start_pos}")
    print(f"目標位置: {goal_pos}")

    # 基本移動戦略検証
    # 右に移動 -> 下に移動のパターン
    steps = []

    # 東へ移動（x座標増加）
    for _ in range(goal_pos[0] - start_pos[0]):
        if info["surroundings"]["right"] == "empty":
            turn_right()
            move()
            steps.append("右移動")
        info = see()

    # 南へ移動（y座標増加）
    for _ in range(goal_pos[1] - start_pos[1]):
        if info["surroundings"]["front"] == "empty":
            move()
            steps.append("前進")
        info = see()

    print("実行手順:", steps)
    return info["game_status"]["is_goal_reached"]
```

## 検証チェックリスト

### ドキュメント品質確認
- [ ] 初心者向けの言葉遣いになっている
- [ ] 専門用語に説明が付いている
- [ ] コード例が実行可能である
- [ ] 期待結果が明記されている
- [ ] エラーケースへの対応がある

### 技術的整合性確認
- [ ] SeeDescription.mdとの情報一致
- [ ] Stage01の実際の構成と説明の一致
- [ ] see()の返却値構造と説明の一致
- [ ] main_*.pyファイルを編集していない

### 学習効果確認
- [ ] 段階的学習フローが明確
- [ ] 理論から実践への流れが自然
- [ ] 応用への橋渡しができている
- [ ] 独立学習が可能な内容になっている

## エラー対応

### よくある問題と対処法

**問題1: see()が実行できない**
```
原因: ゲームセッション外での実行
対処: main_*.pyファイル内でのみsee()を実行する
```

**問題2: 期待結果と異なる出力**
```
原因: ゲーム状態の違い
対処: 初期状態からの手順を正確に再現する
```

**問題3: Stage01がクリアできない**
```
原因: 移動経路の理解不足
対処: see()で各段階の周囲状況を詳細確認
```

## 成功基準

### 最小限の成功基準
1. チュートリアルを読んだ初心者がsee()の基本を理解できる
2. Stage01を例にしたコード例が全て実行できる
3. 独力でStage01をクリアするための戦略を立案できる

### 理想的な成功基準
1. 他のステージでも応用できる考え方を習得できる
2. デバッグスキルが身についている
3. 既存ドキュメントとの使い分けができる

## 次のステップ

### チュートリアル完成後
1. 実際の初心者による検証テスト実施
2. フィードバックに基づく改善
3. システム全体への統合確認
4. ドキュメントバージョン管理への反映

### 継続的改善
1. 学習者からの質問パターン分析
2. よくある間違いの追加収集
3. 説明方法の継続的改善
4. 他ステージチュートリアルへの展開検討