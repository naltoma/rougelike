# see() 関数 & get_stage_info() API 完全リファレンス (v1.2.10対応)

## 概要

### see() 関数
`see()` 関数は周囲の状況を確認する情報取得専用関数です。
- **ターンを消費しません**
- **ステップ実行で一時停止しません**
- **リアルタイムな状況確認が可能**
- **視界範囲を指定可能** (vision_range パラメータ)

### get_stage_info() 関数
`get_stage_info()` 関数はステージの静的情報を取得する関数です。
- **ステージ構造の動的取得**
- **ハードコーディング回避**
- **汎用的なコード設計の基盤**

## 基本的な使用方法

### see() 関数
```python
# デフォルト視界範囲(2)での観測
info = see()
print(info)  # 全情報を表示

# 視界範囲を指定
info_narrow = see(1)    # 隣接セルのみ
info_wide = see(3)      # 広範囲観測

# 特定情報のみ取得
player_pos = info["player"]["position"]
enemy_count = len(info["enemies"])
```

### get_stage_info() 関数
```python
# ステージ情報の取得
stage_info = get_stage_info()
print(f"ステージID: {stage_info['stage_id']}")
print(f"ボードサイズ: {stage_info['board']['size']}")
print(f"ゴール位置: {stage_info['goal']['position']}")
print(f"最大ターン数: {stage_info['constraints']['max_turns']}")
print(f"利用可能API: {stage_info['constraints']['allowed_apis']}")
```

## see() 関数 返却データ構造

### 1. プレイヤー情報 (`info["player"]`)
```python
{
    "position": [x, y],           # 現在位置
    "direction": "N"|"S"|"E"|"W", # 向き
    "hp": 100,                    # 現在HP
    "attack_power": 20            # 攻撃力
}
```

### 2. 周囲情報 (`info["surroundings"]`)
各方向（front, left, right, back）の詳細情報：

**基本形式：**
```python
{
    "front": "wall"|"goal"|"empty"|"boundary"|"forbidden"|{敵情報}|{アイテム情報},
    "left": ...,
    "right": ...,
    "back": ...
}
```

**敵がいる場合の詳細情報：**
```python
{
    "front": {
        "type": "enemy",
        "enemy_type": "normal"|"large_2x2"|"large_3x3"|"special_2x3",
        "position": [x, y],
        "hp": 980,
        "max_hp": 1000,
        "attack_power": 1000,
        "direction": "N"|"S"|"E"|"W",
        "is_alive": true,
        "alerted": false  # 怒りモード判定用（false=平常, true=警戒・怒り）
    }
}
```

**アイテムがある場合：**
```python
{
    "front": {
        "type": "item",
        "item_type": "weapon"|"key",
        "name": "sword"
    }
}
```

### 3. 敵情報 (`info["enemies"]`)
全ての敵の詳細情報：
```python
[
    {
        "type": "normal"|"large_2x2"|"large_3x3"|"special_2x3",
        "position": [x, y],
        "hp": 980,
        "max_hp": 1000,
        "attack_power": 1000,
        "direction": "N"|"S"|"E"|"W",
        "is_alive": true,
        "alerted": false,
        
        # Stage11専用情報（該当する場合のみ）
        "stage11_state": "normal"|"rage_triggered"|"attacking"|"cooldown",
        "hp_ratio": 0.98,
        "area_attack_active": false
    }
]
```

### 4. アイテム情報 (`info["items"]`)
全てのアイテムの情報：
```python
[
    {
        "name": "sword",
        "type": "weapon",
        "position": [x, y],
        "effect": 10,
        "auto_equip": true
    }
]
```

### 5. ゲーム状況 (`info["game_status"]`)
```python
{
    "turn": 15,           # 現在ターン
    "max_turns": 100,     # 最大ターン数
    "remaining_turns": 85, # 残りターン数
    "status": "playing",  # ゲーム状態
    "is_goal_reached": false
}
```

### 6. 視界マップ (`info["vision_map"]`) - v1.2.10追加
```python
{
    "1,0": {
        "position": [1, 0],
        "distance": 1,
        "content": "empty"
    },
    "2,1": {
        "position": [2, 1],
        "distance": 2,
        "content": "wall"
    },
    "3,2": {
        "position": [3, 2],
        "distance": 3,
        "content": {
            "type": "enemy",
            "enemy_type": "normal",
            # ... 敵の詳細情報
        }
    }
}
```

## get_stage_info() 関数 返却データ構造

### ステージ情報
```python
{
    "stage_id": "stage01",
    "board": {
        "size": [5, 5]           # ボードサイズ [width, height]
    },
    "goal": {
        "position": [4, 4]       # ゴール位置
    },
    "constraints": {
        "max_turns": 20,         # 最大ターン数
        "allowed_apis": [        # 使用可能API一覧
            "turn_left",
            "turn_right",
            "move",
            "see",
            "get_stage_info"
        ]
    },
    "enemies": [                 # 初期敵配置（存在する場合）
        {
            "position": [2, 3],
            "type": "normal",
            "hp": 1000
        }
    ],
    "walls": [                   # 壁の位置一覧
        [2, 2]
    ],
    "items": [                   # 初期アイテム配置（存在する場合）
        {
            "position": [1, 3],
            "type": "weapon",
            "name": "sword"
        }
    ]
}
```

## 全ステージ共通機能

### 敵状態判定（怒りモード等）
```python
info = see()

# 方向ベースでの敵状態確認
front_enemy = info["surroundings"]["front"]
if isinstance(front_enemy, dict) and front_enemy["type"] == "enemy":
    if front_enemy["alerted"]:
        print("🔥 正面の敵は警戒状態（怒りモード）です")
    else:
        print("😴 正面の敵は平常状態です")
        
# 全方向の敵状態を確認
for direction in ["front", "left", "right", "back"]:
    obj = info["surroundings"][direction]
    if isinstance(obj, dict) and obj["type"] == "enemy":
        state = "警戒中" if obj["alerted"] else "平常"
        hp_percent = (obj["hp"] / obj["max_hp"]) * 100
        print(f"{direction}: {obj['enemy_type']} HP{hp_percent:.1f}% {state}")
```

### Stage11での使用例
```python
def check_enemy_rage_mode():
    """敵の怒りモード判定"""
    info = see()
    front_enemy = info["surroundings"]["front"]
    
    if isinstance(front_enemy, dict) and front_enemy["type"] == "enemy":
        hp_ratio = front_enemy["hp"] / front_enemy["max_hp"]
        
        if not front_enemy["alerted"] and hp_ratio > 0.5:
            print("😴 敵は平常モード（HP50%超）")
        elif front_enemy["alerted"] and hp_ratio < 0.5:
            print("🔥 敵は怒りモード（HP50%未満で警戒中）")
            print("⚠️ 次ターンで範囲攻撃の可能性あり")
            return True
    return False

# 使用例
if check_enemy_rage_mode():
    # 安全な場所に退避
    turn_left()
    move()
```

## 実用例

### 1. ハードコーディング回避設計
```python
def get_dynamic_goal():
    """動的にゴール位置を取得"""
    stage_info = get_stage_info()
    return stage_info["goal"]["position"]

def is_api_available(api_name):
    """指定APIが使用可能かチェック"""
    stage_info = get_stage_info()
    return api_name in stage_info["constraints"]["allowed_apis"]

# 使用例
goal_pos = get_dynamic_goal()  # ハードコーディング [4,4] を回避
if is_api_available("attack"):
    attack()  # 攻撃可能ステージでのみ実行
```

### 2. 視界マップ活用 (v1.2.10)
```python
def analyze_surroundings():
    """視界範囲内の詳細分析"""
    info = see(3)  # 広範囲観測
    vision_map = info["vision_map"]

    enemies_in_sight = []
    walls_in_sight = []

    for coord, cell_data in vision_map.items():
        content = cell_data["content"]
        position = cell_data["position"]
        distance = cell_data["distance"]

        if content == "wall":
            walls_in_sight.append(position)
        elif isinstance(content, dict) and content["type"] == "enemy":
            enemies_in_sight.append({
                "position": position,
                "distance": distance,
                "hp": content["hp"],
                "alerted": content["alerted"]
            })

    return enemies_in_sight, walls_in_sight

# 使用例
enemies, walls = analyze_surroundings()
print(f"視界内敵数: {len(enemies)}, 壁数: {len(walls)}")
```

### 3. 安全確認
```python
def is_safe_to_move():
    info = see()
    front = info["surroundings"]["front"]
    
    # 文字列の場合（壁、空きマス等）
    if isinstance(front, str):
        return front not in ["wall", "boundary", "forbidden"]
    
    # 辞書の場合（敵、アイテム）
    if isinstance(front, dict):
        return front["type"] != "enemy"  # 敵以外は安全
    
    return True

if is_safe_to_move():
    move()
```

### 2. 敵HP監視（方向ベース）
```python
def monitor_front_enemy():
    info = see()
    front = info["surroundings"]["front"]
    
    if isinstance(front, dict) and front["type"] == "enemy":
        hp_percent = (front["hp"] / front["max_hp"]) * 100
        print(f"正面の敵HP: {hp_percent:.1f}%")
        
        if hp_percent <= 51 and not front["alerted"]:
            print("⚠️ 注意：敵があと1攻撃で怒りモードに突入する可能性")
        return front
    return None

enemy = monitor_front_enemy()
```

### 3. 戦術判断
```python
def should_retreat():
    info = see()
    
    # 全方向の敵を確認
    for direction in ["front", "left", "right", "back"]:
        obj = info["surroundings"][direction]
        if isinstance(obj, dict) and obj["type"] == "enemy":
            if obj["alerted"]:  # 警戒状態の敵がいる
                return True
    return False

if should_retreat():
    # 安全な場所に移動
    turn_left()
    move()
```

## 注意事項

### see() 関数
1. **リアルタイム情報**：see()は現在の状況を返します
2. **ターン非消費**：何度呼び出してもターンは進みません
3. **座標系**：[x, y] 形式（x:横, y:縦）
4. **敵状態判定**：`alerted`フラグで警戒・怒りモードを判定（全ステージ共通）
5. **方向ベース参照**：`info["surroundings"]["front"]`で正面の敵情報を直接取得
6. **型チェック重要**：辞書型の場合のみ詳細情報が含まれます
7. **視界範囲制御**：vision_rangeパラメータで観測範囲を調整可能

### get_stage_info() 関数
1. **静的情報**：ゲーム開始時の初期状態情報を返します
2. **ターン非消費**：see()同様、ターンを消費しません
3. **汎用性の重要さ**：ハードコーディングを避け、動的に情報取得することで複数ステージ対応可能
4. **初期化データ**：enemies、items等は初期配置情報（現在状態はsee()で確認）

## デバッグ用途
```python
import json

# see()の全情報を整形表示
info = see()
print("=== see() 情報 ===")
print(json.dumps(info, indent=2))

# get_stage_info()の全情報を整形表示
stage_info = get_stage_info()
print("\n=== get_stage_info() 情報 ===")
print(json.dumps(stage_info, indent=2))

# 特定情報のみ表示
print(f"\n=== 要約情報 ===")
print(f"ステージ: {stage_info['stage_id']}")
print(f"プレイヤー位置: {info['player']['position']}")
print(f"ゴール位置: {stage_info['goal']['position']}")
print(f"敵数: {len(info['enemies'])}")
print(f"視界内セル数: {len(info['vision_map'])}")
```

## v1.2.10での新機能・変更点

1. **vision_map の追加**: 座標ベースでの詳細な視界情報取得が可能
2. **get_stage_info() の標準化**: 全チュートリアルでハードコーディング回避を推奨
3. **視界範囲制御の活用**: 戦略に応じた観測範囲の調整