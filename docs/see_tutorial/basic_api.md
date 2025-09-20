# see()関数とget_stage_info()API基礎

## 1. はじめに

### see()関数とは？
`see()`関数は、ローグライクゲームで**現在の状況を確認する**ための情報取得専用関数です。プレイヤーの位置、周囲の環境、敵の状態など、戦略を立てるために必要な情報をすべて取得できます。

**see()関数の特徴：**
- **ターンを消費しない** - 何度呼び出してもゲームが進行しません
- **ステップ実行で一時停止しない** - リアルタイムに情報確認できます
- **完全な状況把握** - プレイヤー、敵、アイテム、ゲーム状態をすべて取得

### このチュートリアルの目標
このチュートリアルを完了すると、以下のことができるようになります：

1. **see()の基本的な使い方を理解する**
   - 関数の呼び出し方法
   - 返却される情報の構造を理解

2. **get_stage_info()でステージ情報を動的取得**
   - ハードコーディング回避の重要性
   - 汎用的なコード設計の基礎

3. **他ステージでも応用できる考え方を習得**
   - 動的情報取得による問題解決アプローチ
   - デバッグスキルの向上

### 必要な前提知識
- **Python基本文法** - 辞書（dict）、リスト（list）の基本的な使い方
- **ローグライクゲームの基本** - turn_left、turn_right、moveの使用経験
- **座標系の理解** - [x, y]形式の位置表現（x:横、y:縦）

**注意：** このチュートリアルでは、既存の`main_*.py`ファイルを編集しません。すべての例は理解を深めるためのものです。

## 2. see()関数の基礎

### 基本的な呼び出し方法
see()関数は非常にシンプルに使用できます：

```python
# 目的: 現在の状況を全て確認する（デフォルト視界範囲2）
info = see()
print(info)  # 全情報を表示

# 目的: 視界範囲を指定して観測する
info = see(1)    # 隣接セルのみ観測
info = see(3)    # より広範囲の観測

# 期待結果: 辞書形式で現在のゲーム状態が返される
# 解説: see()を呼び出すだけで、必要な情報がすべて取得できます
```

### 視界範囲制御
see()関数にはvision_rangeパラメータで観測範囲を制御できます：

- **vision_range=1**: 隣接する4セルのみ観測（省視野モード）
- **vision_range=2**: マンハッタン距離2以内のセルを観測（デフォルト、敵の視界と同等）
- **vision_range=3**: より広範囲の戦略的観測が可能

```python
# 目的: 視界範囲による情報量の違いを理解する
info_narrow = see(1)     # 狭い視界
info_normal = see(2)     # 標準視界（推奨）
info_wide = see(3)       # 広い視界

# vision_mapに含まれる座標の数が異なります
print(f"狭い視界の観測セル数: {len(info_narrow['vision_map'])}")
print(f"標準視界の観測セル数: {len(info_normal['vision_map'])}")
print(f"広い視界の観測セル数: {len(info_wide['vision_map'])}")
```

### 返却データの構造解説
see()が返す情報は、以下の6つの主要な要素で構成されています：

#### 1. プレイヤー情報 (`info["player"]`)
```python
# 目的: プレイヤーの現在状態を確認する
player_info = info["player"]
print(f"位置: {player_info['position']}")    # 現在位置 [x, y]
print(f"向き: {player_info['direction']}")   # 向き (N/S/E/W)
print(f"HP: {player_info['hp']}")            # 現在のHP
# 期待結果: 位置: [0, 0], 向き: N, HP: 100
# 解説: プレイヤーの基本情報がすべて含まれています
```

#### 2. 周囲情報 (`info["surroundings"]`)
```python
# 目的: プレイヤーの前後左右の状況を確認する（従来互換性）
surroundings = info["surroundings"]
print(f"正面: {surroundings['front']}")
print(f"左: {surroundings['left']}")
print(f"右: {surroundings['right']}")
print(f"後ろ: {surroundings['back']}")
# 期待結果: "empty", "wall", "boundary", または辞書形式の敵/アイテム情報
# 解説: 各方向の状況が文字列または詳細情報として取得できます
```

#### 3. 視界マップ (`info["vision_map"]`)
```python
# 目的: 視界範囲内の全セル情報を座標で取得する
vision_map = info["vision_map"]
for coord, cell_data in vision_map.items():
    position = cell_data["position"]
    distance = cell_data["distance"]
    content = cell_data["content"]
    print(f"座標 {coord}: 位置{position}, 距離{distance}, 内容{content}")

# 期待結果: "1,0": {"position": [1,0], "distance": 1, "content": "empty"}
# 解説: 座標をキーとして、その位置の詳細情報を取得できます

# 実用例: 特定座標の確認
if "2,1" in vision_map:
    cell_info = vision_map["2,1"]
    print(f"座標[2,1]の内容: {cell_info['content']}")
```

#### 4. 敵情報 (`info["enemies"]`)
```python
# 目的: すべての敵の状態を確認する
enemies = info["enemies"]
print(f"敵の数: {len(enemies)}")
for enemy in enemies:
    print(f"敵位置: {enemy['position']}, HP: {enemy['hp']}")
# 期待結果: 敵がいない場合は空のリスト []
# 解説: すべての敵の詳細情報がリスト形式で取得できます
```

#### 5. アイテム情報 (`info["items"]`)
```python
# 目的: フィールド上のアイテムを確認する
items = info["items"]
print(f"アイテム数: {len(items)}")
for item in items:
    print(f"アイテム: {item['name']}, 位置: {item['position']}")
# 期待結果: アイテムがない場合は空のリスト []
# 解説: 取得可能なアイテムの情報がすべて分かります
```

#### 6. ゲーム状況 (`info["game_status"]`)
```python
# 目的: ゲームの進行状況を確認する
status = info["game_status"]
print(f"現在ターン: {status['turn']}")
print(f"残りターン: {status['remaining_turns']}")
print(f"ゴール到達: {status['is_goal_reached']}")
# 期待結果: 現在ターン: 1, 残りターン: 19, ゴール到達: False
# 解説: ゲームの進行状況とクリア状態が分かります
```

### よく使用する情報の取得方法

#### 現在位置の確認
```python
# 目的: プレイヤーの現在位置を取得する
info = see()
current_pos = info["player"]["position"]
print(f"現在位置: x={current_pos[0]}, y={current_pos[1]}")
# 期待結果: 現在位置: x=0, y=1
# 解説: [x, y]形式で位置が取得できます
```

#### 移動可能方向の確認
```python
# 目的: どの方向に移動できるかを確認する
info = see()
surroundings = info["surroundings"]
movable_directions = []
for direction, obj in surroundings.items():
    if obj == "empty" or obj == "goal":
        movable_directions.append(direction)
print(f"移動可能方向: {movable_directions}")
# 期待結果: 移動可能方向: ['front', 'left', 'right']
# 解説: "empty"や"goal"の方向に移動できます
```

### 次のステップ
基礎を理解したら、次はget_stage_info()でステージ情報を取得し、その後実際のStage01でsee()を使ってみましょう。

## 3. get_stage_info()によるステージ情報取得

ハードコーディングを排除するために、ステージ情報を動的に取得するAPIが利用できます。

### get_stage_info()の基本的な使い方

```python
# 目的: 現在のステージの基本情報を取得する
stage_info = get_stage_info()
print(f"ステージID: {stage_info['stage_id']}")
print(f"ボードサイズ: {stage_info['board']['size']}")
print(f"ゴール位置: {stage_info['goal']['position']}")
print(f"利用可能API: {stage_info['constraints']['allowed_apis']}")
print(f"最大ターン数: {stage_info['constraints']['max_turns']}")

# 期待結果:
# ステージID: stage01
# ボードサイズ: [5, 5]
# ゴール位置: [4, 4]
# 利用可能API: ['turn_left', 'turn_right', 'move', 'see', 'get_stage_info']
# 最大ターン数: 20
```

### 実践的な活用例

```python
# 目的: ステージ情報を使って戦略を立案する
def plan_strategy():
    stage_info = get_stage_info()
    player_info = see()["player"]

    start_pos = player_info["position"]
    goal_pos = stage_info["goal"]["position"]  # 正しい構造で取得

    # 距離計算
    dx = goal_pos[0] - start_pos[0]
    dy = goal_pos[1] - start_pos[1]

    print(f"開始位置: {start_pos}")
    print(f"ゴール位置: {goal_pos}")
    print(f"必要移動: 東{dx}マス、南{dy}マス")
    print(f"推定最短距離: {abs(dx) + abs(dy)}マス")
    print(f"制限ターン: {stage_info['constraints']['max_turns']}")

    return {"dx": dx, "dy": dy, "goal": goal_pos}

# 使用例
strategy = plan_strategy()
# この情報を使って動的にルートを決定できます
```

**ハードコーディングとの比較:**
```python
# ❌ ハードコーディング（特定ステージ専用）
goal_pos = [4, 4]

# ✅ 動的取得（汎用的）
stage_info = get_stage_info()
goal_pos = stage_info["goal"]["position"]
```

これにより、どのステージでも同じコードが動作するようになります。

## 4. Stage01を例にした実践

### Stage01の構造解析
Stage01は最も基本的な移動ステージです。まずはget_stage_info()で構造を理解しましょう。

```python
# 目的: Stage01の基本情報を動的に取得する
stage_info = get_stage_info()
print(f"ステージ: {stage_info['stage_id']}")
print(f"ボードサイズ: {stage_info['board']['size']}")
print(f"ゴール位置: {stage_info['goal']['position']}")
print(f"制約: {stage_info['constraints']}")
```

**Stage01の基本情報（get_stage_info()で取得）：**
- **ボードサイズ**: 5×5マス
- **プレイヤー開始位置**: [0, 0]（左上角）
- **プレイヤー初期向き**: N（北向き）
- **ゴール位置**: [4, 4]（右下角）- get_stage_info()で動的取得
- **最大ターン数**: 20ターン
- **使用可能API**: turn_left, turn_right, move, see, get_stage_info

**ボード構造の視覚化：**
```
  0 1 2 3 4  (x座標)
0 P . . . .
1 . . . . .
2 . . # . .  (中央に壁)
3 . . . . .
4 . . . . G
(y座標)

P = プレイヤー開始位置 [0,0]
G = ゴール [4,4]
# = 壁 [2,2]
. = 空きマス
```

### see()を使った情報収集手順
実際にStage01でsee()を使って情報を収集してみましょう。

#### ゲーム開始直後の状況確認
```python
# 目的: ゲーム開始時の初期状態を確認する
info = see()

# プレイヤー状態の確認
player = info["player"]
print(f"開始位置: {player['position']}")  # [0, 0]
print(f"向き: {player['direction']}")      # N (北向き)

# 周囲の状況確認
surroundings = info["surroundings"]
print(f"正面: {surroundings['front']}")   # boundary (北向きなので上が正面、ボード外)
print(f"右: {surroundings['right']}")     # empty (東側)
print(f"後ろ: {surroundings['back']}")    # empty (南側)
print(f"左: {surroundings['left']}")      # boundary (西側、ボード外)

# ゲーム状況の確認
status = info["game_status"]
print(f"現在ターン: {status['turn']}")     # 1
print(f"残りターン: {status['remaining_turns']}")  # 19
```

**実行結果例：**
```
開始位置: [0, 0]
向き: N
正面: boundary
右: empty
後ろ: empty
左: boundary
現在ターン: 1
残りターン: 19
```

### アクション決定のための情報活用
see()で得た情報をもとに、どのようにアクションを決定するかを学びましょう。

#### 基本的な判断フロー
```python
# 目的: see()とget_stage_info()の情報を使って次のアクションを決定する
def decide_next_action():
    info = see()
    stage_info = get_stage_info()  # 動的にゴール取得

    # 現在位置とゴール位置の確認
    current_pos = info["player"]["position"]
    goal_pos = stage_info["goal"]["position"]  # ハードコーディング廃止

    print(f"現在位置: {current_pos}")
    print(f"ゴール位置: {goal_pos}")
    print(f"ゴールまでの距離: x方向={goal_pos[0] - current_pos[0]}, y方向={goal_pos[1] - current_pos[1]}")

    # 周囲の安全確認
    surroundings = info["surroundings"]
    safe_directions = []
    for direction, obj in surroundings.items():
        if obj == "empty" or obj == "goal":
            safe_directions.append(direction)

    print(f"移動可能方向: {safe_directions}")

    # アクション決定ロジック（例）
    if "right" in safe_directions and current_pos[0] < goal_pos[0]:
        return "東（右）に移動してx座標を増やす"
    elif "front" in safe_directions and current_pos[1] < goal_pos[1]:
        return "南（前）に移動してy座標を増やす"
    else:
        return "向きを変えて移動可能方向を探す"
```

この基本的なアプローチを使って、動的な情報取得に基づいた戦略立案ができるようになります。