# Stage01向けシンプルアルゴリズム実践

## はじめに

このチュートリアルでは、**Stage01を確実にクリアできる**シンプルなアルゴリズムを学習します。汎用性よりも「動作する確実な解法」を重視し、プログラミング初学者がアルゴリズムの考え方と実装方法を理解することを目的としています。

### 対象読者
- `see()`と`get_stage_info()`の基本的な使い方を理解している
- Stage01を手動でクリア経験がある
- Python基本文法（if文、for文、関数定義）を理解している

### 学習目標
1. **問題分析からアルゴリズムへの思考過程**を体験する
2. **複数のアプローチを比較検討**する方法を学ぶ
3. **実装→テスト→修正**のサイクルを実践する

## Stage01の構造再確認

### 基本情報
```python
# Stage01の構造を確認
stage_info = get_stage_info()
print(f"ボードサイズ: {stage_info['board']['size']}")  # [5, 5]
print(f"ゴール位置: {stage_info['goal']['position']}")  # [4, 4]
print(f"最大ターン数: {stage_info['constraints']['max_turns']}")  # 20

# 初期状態確認
info = see()
print(f"開始位置: {info['player']['position']}")  # [0, 0]
print(f"開始向き: {info['player']['direction']}")  # N
```

### マップ構造
```
  0 1 2 3 4  (x座標)
0 P . . . .
1 . . . . .
2 . . # . .  ← 中央に壁[2,2]
3 . . . . .
4 . . . . G
(y座標)

P = プレイヤー [0,0]
G = ゴール [4,4]
# = 壁 [2,2]
. = 空きマス
```

### クリアに必要な要素
- **移動距離**: [0,0]→[4,4] = 8マス（最短）
- **迂回必要**: 壁[2,2]により直線移動は不可
- **ターン制限**: 20ターン以内

## アルゴリズム候補の検討

Stage01をクリアするための異なるアプローチを比較してみましょう。

### アプローチ1: 時計回り外周ルート
```
経路: [0,0] → [4,0] → [4,4]
手順: 東に4回移動 → 南に4回移動
利点: シンプル、必ず成功
欠点: 8手必要（効率は良いがStage01特化、他ステージで通用しない）
```

### アプローチ2: 対角線（壁回避）ルート
```
経路: [0,0] → [1,0] → [1,2] → [4,2] → [4,4]
手順: 東1回転+移動 → 南2回転+移動 → 東3回転+移動 → 南2回転+移動
実際の手数: 移動8手 + 回転数手 = 10手以上
利点: 壁を効率的に回避
欠点: 実装が複雑、回転コストで手数増加
```

### アプローチ3: 右下優先ルート
```
基本戦略: 可能な限り右（東）または下（南）に移動
壁対策: 壁にぶつかったら迂回
利点: 理解しやすい、様々なマップに対応可能
欠点: 最短距離保証なし
```

**このチュートリアルでは、理解しやすく実装しやすい「アプローチ3: 右下優先ルート」を採用します。**

## アルゴリズム詳細設計

### 基本戦略
1. **ゴール方向判定**: 現在位置とゴールを比較し、必要な移動方向を決定
2. **優先順位付け移動**: 東→南の順で移動を試行
3. **障害物回避**: 移動できない場合は迂回ルートを探索
4. **ゴール確認**: 毎ターン後にゴール到達をチェック

### システム構成概要

この`stage01_simple_clear()`システムは4つの主要関数で構成されます。各関数の役割と入出力を理解してから、詳細な実装に進みましょう。

```python
def stage01_simple_clear():
    """Stage01専用のシンプルクリアアルゴリズム"""
    while True:
        # 1. 現在状況の確認
        info = see()
        current_pos = info["player"]["position"]

        # ゴール到達チェック
        if info["game_status"]["is_goal_reached"]:
            return True

        # 2. 目標方向の決定 → target_direction = "E" or "S"
        target_direction = decide_move_direction(current_pos)

        # 3. 方向転換 → 指定方向を向くまで回転
        turn_to_direction(target_direction)

        # 4. 移動実行と障害物対応
        if can_move_forward():  # → True/False
            move()
        else:
            handle_obstacle()  # 壁回避ロジック
```

**📝 学習ポイント**: ここでは4つの独立した関数を組み合わせて全体のアルゴリズムを構築します。各関数を個別に理解し、その後統合することで複雑な問題を段階的に解決します。

## 実装: 段階的構築

### Step 1: 基本的な方向判定

#### 実装方針
現在位置とゴール位置を比較し、次に進むべき方向を決定する関数です。Stage01では「右下優先」戦略により、まず東方向、次に南方向の順で移動します。

**関数設計**:
```python
# 入力例: current_pos = [1, 2] (現在位置)
# ゴール: [4, 4] (get_stage_info()で取得)
# 処理: dx = 4-1 = 3, dy = 4-2 = 2
# 出力: "E" (まだ東方向に3マス移動が必要)
```

**プログラミング初学者向けのポイント**:
- **座標計算**: 目標位置 - 現在位置 = 必要移動距離
- **優先順位の実装**: if-elif-else文での順序制御
- **None返却**: 移動不要時の適切な値返却

```python
def decide_move_direction(current_pos):
    """
    現在位置に基づいて次の移動方向を決定する

    Args:
        current_pos (list): 現在位置 [x, y]

    Returns:
        str: 目標方向 "E"(東) または "S"(南)、移動不要時はNone

    実装例:
        現在位置[1,2] → ゴール[4,4]: "E"を返す (東優先)
        現在位置[4,2] → ゴール[4,4]: "S"を返す (南のみ)
        現在位置[4,4] → ゴール[4,4]: None を返す (到達済み)
    """
    stage_info = get_stage_info()
    goal_pos = stage_info["goal"]["position"]

    # ゴールとの距離計算
    dx = goal_pos[0] - current_pos[0]  # x方向の残り距離
    dy = goal_pos[1] - current_pos[1]  # y方向の残り距離

    print(f"現在位置: {current_pos}")
    print(f"ゴールまで: x方向 {dx}, y方向 {dy}")

    # 優先順位: 東→南（右下優先戦略）
    if dx > 0:  # まだ東に移動が必要
        print("判定: 東方向に移動")
        return "E"
    elif dy > 0:  # x方向完了、南に移動
        print("判定: 南方向に移動")
        return "S"
    else:
        print("判定: ゴール到達済み")
        return None

# テスト例1: 東方向移動が必要
current_pos = [1, 2]
direction = decide_move_direction(current_pos)
# 実行結果:
# 現在位置: [1, 2]
# ゴールまで: x方向 3, y方向 2
# 判定: 東方向に移動

# テスト例2: 南方向のみ移動が必要
current_pos = [4, 2]
direction = decide_move_direction(current_pos)
# 実行結果:
# 現在位置: [4, 2]
# ゴールまで: x方向 0, y方向 2
# 判定: 南方向に移動
```

### Step 2: 方向転換ロジック

#### 実装方針
プレイヤーの現在の向きから目標の向きまで効率的に回転する関数です。時計回りの回転のみを使い、どの方向からでも確実に目標方向を向けるようにします。

**関数設計**:
```python
# 入力例: target_direction = "E" (東向きになりたい)
# 現在の向き: "N" (北向き)
# 期待出力: 1回のturn_right()実行後、東向きになる

# 入力例: target_direction = "S" (南向きになりたい)
# 現在の向き: "N" (北向き)
# 期待出力: 2回のturn_right()実行後、南向きになる
```

**プログラミング初学者向けのポイント**:
- **剰余演算(%)の活用**: 円形配列（N→E→S→W→N...）での位置計算
- **配列インデックス**: 方向を数値として扱い計算を簡潔にする
- **エラーハンドリング**: target_directionがNoneの場合の処理

```python
def turn_to_direction(target_direction):
    """
    指定された方向を向くまで回転する

    Args:
        target_direction (str): 目標方向 "N", "E", "S", "W"

    実装例:
        入力: target_direction="E", 現在向き="N"
        処理: 1回右回転
        結果: 東向きになる
    """
    if target_direction is None:
        return  # 移動不要

    info = see()
    current_direction = info["player"]["direction"]

    print(f"現在向き: {current_direction} → 目標向き: {target_direction}")

    # 既に正しい方向を向いている場合
    if current_direction == target_direction:
        print("すでに正しい方向を向いています")
        return

    # 方向を配列のインデックスとして扱う
    directions = ["N", "E", "S", "W"]  # 時計回り順序
    current_index = directions.index(current_direction)
    target_index = directions.index(target_direction)

    # 時計回りの回転数を計算
    # 例: N(0) → E(1) = (1-0) % 4 = 1回転
    # 例: E(1) → N(0) = (0-1) % 4 = 3回転
    rotations = (target_index - current_index) % 4

    print(f"必要回転数: {rotations}回")

    # 回転実行
    for i in range(rotations):
        turn_right()
        new_info = see()
        new_direction = new_info["player"]["direction"]
        print(f"回転{i+1}: {new_direction}向きになりました")

# テスト例
# 現在N向き、東に向きたい場合
turn_to_direction("E")  # 1回右回転してE向きになる

# 実行結果例:
# 現在向き: N → 目標向き: E
# 必要回転数: 1回
# 回転1: E向きになりました
```

### Step 3: 移動可能性チェック

#### 実装方針
プレイヤーの正面に障害物があるかを確認し、安全に移動できるかを判定する関数です。see()のsurroundings情報を使い、移動前の安全確認を行います。

**関数設計**:
```python
# 入力: なし（see()で現在状況を取得）
# 処理: info["surroundings"]["front"]をチェック
# 出力例1: front_content="empty" → return True
# 出力例2: front_content="wall" → return False
# 出力例3: front_content="goal" → return True
```

**プログラミング初学者向けのポイント**:
- **文字列判定**: 特定の文字列値での条件分岐
- **早期リターン**: 条件が満たされた場合の即座の処理終了
- **安全性の重要さ**: 移動前の事前確認によるエラー回避

```python
def can_move_forward():
    """
    前方に移動できるかチェックする

    Returns:
        bool: 移動可能ならTrue、不可能ならFalse

    動作例:
        正面が"empty": True を返す
        正面が"wall": False を返す
        正面が"goal": True を返す
        正面が"boundary": False を返す
    """
    info = see()
    front_content = info["surroundings"]["front"]

    print(f"前方の状況: {front_content}")

    # 移動可能な状況のチェック
    # "empty": 空きマス、"goal": ゴール地点
    if front_content in ["empty", "goal"]:
        print("✅ 移動可能")
        return True
    else:
        # "wall": 壁、"boundary": マップ境界、敵やアイテム
        print(f"❌ 移動不可: {front_content}")
        return False

# 使用例: 安全確認付きの移動
if can_move_forward():
    move()
    print("移動完了")
else:
    print("障害物のため移動できません")

# 実行結果例1（移動可能）:
# 前方の状況: empty
# ✅ 移動可能
# 移動完了

# 実行結果例2（移動不可）:
# 前方の状況: wall
# ❌ 移動不可: wall
# 障害物のため移動できません
```

### Step 4: 障害物回避ロジック

#### 実装方針
前方に障害物がある場合の迂回処理を行う関数です。Stage01の壁[2,2]の特性を活用した専用回避ロジックと、一般的な回避ロジックを組み合わせます。

**関数設計**:
```python
# 入力: なし（see()で現在状況を取得）
# 処理1: Stage01専用 - 壁[2,2]の位置関係で迂回方向決定
# 処理2: 一般的回避 - 時計回りで移動可能方向を探索
# 出力: 迂回移動の実行
```

**プログラミング初学者向けのポイント**:
- **条件分岐の優先順位**: 特殊ケース → 一般ケースの順で処理
- **座標計算**: プレイヤー位置と障害物位置の関係判定
- **フォールバック処理**: 特殊ケースで解決できない場合の代替処理

```python
def handle_obstacle():
    """
    障害物に遭遇した場合の迂回処理
    Stage01の壁[2,2]専用の回避ロジック + 一般的回避

    動作例1: 位置[2,1]で東向き → 南に迂回
    動作例2: 位置[1,2]で南向き → 東に迂回
    動作例3: その他の位置 → 時計回りで空き方向を探索
    """
    info = see()
    current_pos = info["player"]["position"]
    current_direction = info["player"]["direction"]

    print(f"=== 障害物回避 ===")
    print(f"位置: {current_pos}, 向き: {current_direction}")

    # Stage01特有の壁[2,2]回避パターン
    # パターン1: x=2で東向き（壁の手前で東方向に進めない）
    if current_pos[0] == 2 and current_direction == "E":
        print("壁回避: 南に迂回します（壁[2,2]を避けて下方向へ）")
        turn_to_direction("S")
        if can_move_forward():
            move()
            print("迂回成功: 南に移動しました")

    # パターン2: y=2で南向き（壁の手前で南方向に進めない）
    elif current_pos[1] == 2 and current_direction == "S":
        print("壁回避: 東に迂回します（壁[2,2]を避けて右方向へ）")
        turn_to_direction("E")
        if can_move_forward():
            move()
            print("迂回成功: 東に移動しました")

    else:
        # 一般的な回避: 時計回りで空いている方向を探す
        print("一般的回避: 他の方向を探索します")
        original_direction = current_direction

        for attempt in range(4):  # 最大4方向チェック
            turn_right()
            new_direction = see()["player"]["direction"]
            print(f"方向変更 {attempt+1}: {new_direction}向きを確認")

            if can_move_forward():
                move()
                print(f"迂回成功: {new_direction}方向に移動しました")
                break
        else:
            print("⚠️ すべての方向が塞がっています（デッドロック状態）")

# テスト例1（壁の手前東向き）
# 位置[2,1]で東向き、前方に壁[2,2]がある場合
handle_obstacle()
# 期待結果: 南に迂回して壁を回避

# 実行結果例:
# === 障害物回避 ===
# 位置: [2, 1], 向き: E
# 壁回避: 南に迂回します（壁[2,2]を避けて下方向へ）
# ✅ 移動可能
# 迂回成功: 南に移動しました

# テスト例2（予期しない障害物）
# 位置[1,1]で北向き、前方に境界がある場合
handle_obstacle()
# 期待結果: 時計回りで移動可能方向を探索
```

## 完全実装

上記の部品を組み合わせた完全なアルゴリズム：

```python
def stage01_simple_clear(max_turns=20):
    """
    Stage01専用のシンプルクリアアルゴリズム

    基本戦略: 右下優先移動 + 壁回避

    Returns:
        bool: クリア成功時True、失敗時False
    """
    print("🎮 Stage01シンプルクリアアルゴリズム開始")

    for turn in range(max_turns):
        print(f"\n--- ターン {turn + 1} ---")

        # 現在状況確認
        info = see()
        current_pos = info["player"]["position"]

        # ゴール到達チェック
        if info["game_status"]["is_goal_reached"]:
            print("🎉 ゴール到達！クリア成功！")
            return True

        # 移動方向決定
        target_direction = decide_move_direction(current_pos)

        if target_direction is None:
            print("移動不要: すでにゴール位置")
            continue

        # 方向転換
        turn_to_direction(target_direction)

        # 移動試行
        if can_move_forward():
            move()
            new_info = see()
            new_pos = new_info["player"]["position"]
            print(f"移動完了: {current_pos} → {new_pos}")
        else:
            # 障害物回避
            handle_obstacle()

    print("❌ ターン制限内でクリアできませんでした")
    return False

def decide_move_direction(current_pos):
    """現在位置に基づいて次の移動方向を決定"""
    stage_info = get_stage_info()
    goal_pos = stage_info["goal"]["position"]

    dx = goal_pos[0] - current_pos[0]
    dy = goal_pos[1] - current_pos[1]

    print(f"現在位置: {current_pos}, ゴールまで: x{dx}, y{dy}")

    # 優先順位: 東→南
    if dx > 0:
        print("判定: 東方向に移動")
        return "E"
    elif dy > 0:
        print("判定: 南方向に移動")
        return "S"
    else:
        return None

def turn_to_direction(target_direction):
    """指定方向を向くまで回転"""
    if target_direction is None:
        return

    info = see()
    current_direction = info["player"]["direction"]

    if current_direction == target_direction:
        return

    directions = ["N", "E", "S", "W"]
    current_index = directions.index(current_direction)
    target_index = directions.index(target_direction)

    rotations = (target_index - current_index) % 4

    for i in range(rotations):
        turn_right()

def can_move_forward():
    """前方移動可能性チェック"""
    info = see()
    front_content = info["surroundings"]["front"]

    return front_content in ["empty", "goal"]

def handle_obstacle():
    """障害物回避処理（Stage01専用）"""
    info = see()
    current_pos = info["player"]["position"]
    current_direction = info["player"]["direction"]

    print("障害物回避中...")

    # Stage01の壁[2,2]専用回避
    if current_pos[0] == 2 and current_direction == "E":
        turn_to_direction("S")
        if can_move_forward():
            move()
    elif current_pos[1] == 2 and current_direction == "S":
        turn_to_direction("E")
        if can_move_forward():
            move()
    else:
        # 一般的回避: 空いている方向を探す
        for _ in range(4):
            turn_right()
            if can_move_forward():
                move()
                break

# 実行
success = stage01_simple_clear()
if success:
    print("✅ Stage01クリア成功！")
else:
    print("❌ クリア失敗")
```

## 実行例とデバッグ

### 期待される実行結果
```
🎮 Stage01シンプルクリアアルゴリズム開始

--- ターン 1 ---
現在位置: [0, 0], ゴールまで: x4, y4
判定: 東方向に移動
移動完了: [0, 0] → [1, 0]

--- ターン 2 ---
現在位置: [1, 0], ゴールまで: x3, y4
判定: 東方向に移動
移動完了: [1, 0] → [2, 0]

--- ターン 3 ---
現在位置: [2, 0], ゴールまで: x2, y4
判定: 東方向に移動
障害物回避中...  # 将来的に壁[2,2]に近づいた時

--- ターン 8 ---
現在位置: [4, 3], ゴールまで: x0, y1
判定: 南方向に移動
移動完了: [4, 3] → [4, 4]
🎉 ゴール到達！クリア成功！
✅ Stage01クリア成功！
```

### よくある問題と対処法

#### 問題1: 無限ループ
```python
# 症状: 同じ場所を行ったり来たり
# 原因: 障害物回避ロジックの不備

# 対処法: ループ検出機能を追加
def detect_loop(move_history, threshold=3):
    """簡易ループ検出"""
    if len(move_history) < threshold:
        return False

    recent_positions = move_history[-threshold:]
    return len(set(tuple(pos) for pos in recent_positions)) == 1

# 使用例
move_history = []  # グローバルで管理
move_history.append(current_pos)

if detect_loop(move_history):
    print("⚠️ ループ検出 - ランダム移動に切り替え")
    turn_right()  # 強制的に方向変更
```

#### 問題2: ターン制限オーバー
```python
# 症状: 20ターン以内にクリアできない
# 原因: 効率の悪い移動経路

# 対処法: 移動効率の確認
def analyze_efficiency():
    """移動効率の分析"""
    info = see()
    current_pos = info["player"]["position"]
    turn = info["game_status"]["turn"]

    manhattan_distance = abs(4 - current_pos[0]) + abs(4 - current_pos[1])
    remaining_turns = 20 - turn

    print(f"残り距離: {manhattan_distance}, 残りターン: {remaining_turns}")

    if manhattan_distance > remaining_turns:
        print("⚠️ ターン不足の可能性")
        return False
    return True
```

## 学習のまとめ

### このアルゴリズムで学んだこと

1. **問題の分解**: 複雑な問題を小さな関数に分割
2. **優先順位の設定**: 東→南の明確な順序で判断を単純化
3. **例外処理**: 障害物という予期しない状況への対応
4. **段階的実装**: 基本機能→応用機能の順で開発

### Stage01特化の利点と制限

**利点**:
- 確実にクリア可能
- 理解しやすい実装
- デバッグしやすい構造

**制限**:
- Stage01にのみ特化（汎用性なし）
- 最短経路保証なし
- 動的な障害物に対応不可

### 次のステップ

このシンプルアルゴリズムを理解したら：

1. **他のステージでテスト**: このアルゴリズムが他のステージでどこまで通用するか
2. **汎用化への挑戦**: Stage01特化部分を汎用的に改良
3. **効率化の検討**: 最短経路アルゴリズムの学習
4. **高度な回避ロジック**: 複雑な障害物パターンへの対応

**重要**: 完璧なアルゴリズムより「動作するアルゴリズム」から始めることが、プログラミング学習では重要です。このシンプルな実装を足がかりに、より高度なアルゴリズムに挑戦してください。