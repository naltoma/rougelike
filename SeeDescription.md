# see() 関数使用マニュアル

## 概要
`see()` 関数は周囲の状況を確認する情報取得専用関数です。
- **ターンを消費しません**
- **ステップ実行で一時停止しません**
- **リアルタイムな状況確認が可能**

## 基本的な使用方法
```python
info = see()
print(info)  # 全情報を表示

# 特定情報のみ取得
player_pos = info["player"]["position"]
enemy_count = len(info["enemies"])
```

## 返却データ構造

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

### 1. 安全確認
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

1. **リアルタイム情報**：see()は現在の状況を返します
2. **ターン非消費**：何度呼び出してもターンは進みません
3. **座標系**：[x, y] 形式（x:横, y:縦）
4. **敵状態判定**：`alerted`フラグで警戒・怒りモードを判定（全ステージ共通）
5. **方向ベース参照**：`info["surroundings"]["front"]`で正面の敵情報を直接取得
6. **型チェック重要**：辞書型の場合のみ詳細情報が含まれます

## デバッグ用途
```python
import json
info = see()
print(json.dumps(info, indent=2))  # 全情報を整形表示
```