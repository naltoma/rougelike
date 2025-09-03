# GUI レンダラー使用ガイド

Python初学者向けローグライクフレームワークのGUI機能使用方法

## 概要

このフレームワークは以下の2つの表示モードをサポートしています：

- **CUIモード**: テキストベースの表示（デフォルト）
- **GUIモード**: pygame を使用した視覚的な表示

## 必要条件

GUIモードを使用するには pygame が必要です：

```bash
# Conda環境での pygame インストール
conda activate prog-exe
conda install pygame
```

または

```bash
pip install pygame
```

## 使用方法

### 1. main.py での実行

```bash
# GUIモードで実行
python main.py --gui

# CUIモードで実行  
python main.py --cui

# 自動選択（pygame利用可能時はGUI、そうでなければCUI）
python main.py
```

### 2. student_example.py での実行

```bash
# スクリプト実行（pygame利用可能時は自動的にGUIモード）
python student_example.py
```

### 3. プログラム内での切り替え

```python
from engine.api import initialize_api, initialize_stage

# GUIモードで初期化
initialize_api("gui")

# CUIモードで初期化
initialize_api("cui")

# ステージを初期化して開始
initialize_stage("stage01")
```

### 4. student_example.py の関数使用

```python
# GUIモードで実行
solve(use_gui=True)
solve_interactive(use_gui=True)
solve_stage02(use_gui=True)
demonstrate_features(use_gui=True)

# CUIモードで実行
solve(use_gui=False)  # または solve()
```

## GUI画面の操作方法

### 🎮 実行制御ボタン（v1.2.1新機能）

GUIウィンドウ下部に実行制御ボタンが配置されています：

- **🔍 Step**: solve()内の1アクションを実行（連続押下可能）
- **▶️ Continue**: solve()を連続実行（一定間隔で自動実行）
- **⏸️ Pause**: 連続実行中に次のアクション境界で一時停止
- **🔄 Reset**: ゲーム状態を初期状態に完全リセット

### キーボードショートカット

- **スペースキー**: Stepボタンと同等（1アクション実行）
- **Enterキー**: Continueボタンと同等（連続実行）
- **Pキー**: Pauseボタンと同等（一時停止要求）
- **Rキー**: Resetボタンと同等（リセット実行）
- **ESC**: ゲーム終了
- **F1**: デバッグモード切り替え（FPS表示など）
- **F2**: グリッド線の表示/非表示
- **F3**: 座標表示の切り替え

### 画面構成

GUIモードでは以下の要素が表示されます：

1. **ゲームエリア**: 
   - 5x5 または 10x10 のゲームフィールド
   - カラフルなセル表示（プレイヤー=青、ゴール=金、壁=グレーなど）
   - プレイヤーの向きを示す白い矢印

2. **サイドバー**: 
   - プレイヤー情報（位置、向き、HP、攻撃力）
   - ゲーム情報（ターン数、状態、ゴールまでの距離）
   - カラー凡例

3. **下部情報エリア**: 
   - 現在の状態メッセージ
   - キーボード操作のヒント
   - デバッグ情報（デバッグモード時）

## カラーパレット

- 🔵 **プレイヤー**: 青
- 🟨 **ゴール**: 金
- ⬛ **壁**: ダークグレー
- 🔴 **敵**: 赤
- 🟢 **アイテム**: 緑
- 🟣 **移動禁止**: 紫
- ⬜ **空きマス**: 白

## トラブルシューティング

### pygame が見つからない場合

```
⚠️ pygame が見つかりません。GUIレンダラーは使用できません。
```

**解決策**: pygame をインストールしてください

```bash
conda activate prog-exe
conda install pygame
```

### GUI画面が応答しない場合

- ESCキーを押してゲームを終了してください
- プログラムを強制終了する場合は Ctrl+C を使用してください

### 画面サイズの問題

GUI画面のサイズは自動的に計算されますが、小さなディスプレイの場合は：

- デバッグモード（F1）を無効にする
- グリッド表示（F2）を無効にする
- 座標表示（F3）を無効にする

## 実装の詳細

### レンダラーアーキテクチャ

```python
# 基底クラス
class Renderer(ABC):
    def initialize(self, width: int, height: int) -> None: pass
    def render_frame(self, game_state: GameState) -> None: pass
    def update_display(self) -> None: pass
    def cleanup(self) -> None: pass

# CUI実装
class CuiRenderer(Renderer): pass

# GUI実装
class GuiRenderer(Renderer): pass

# ファクトリー
class RendererFactory:
    @staticmethod
    def create_renderer(renderer_type: str) -> Renderer: pass
```

### APIの統合

```python
# グローバルAPI初期化
from engine.api import initialize_api

initialize_api("gui")  # GUIモード
initialize_api("cui")  # CUIモード
```

## 学習用の活用方法

1. **視覚的デバッグ**: GUIモードでプレイヤーの動きを視覚的に確認
2. **アルゴリズム理解**: 迷路探索や経路探索の動作を目で見て理解
3. **状態遷移の把握**: ゲーム状態の変化をリアルタイムで確認
4. **インタラクティブ学習**: GUIとコンソール出力を組み合わせた学習

## サンプルコード

```python
#!/usr/bin/env python3
"""GUIモードでのサンプル"""

from engine.api import initialize_api, initialize_stage, turn_right, move, show_current_state

def gui_sample():
    # GUIモードで初期化
    initialize_api("gui")
    
    # ステージ開始
    if initialize_stage("stage01"):
        print("🎮 GUIでゲーム開始！")
        
        # 簡単な動作
        turn_right()  # 東を向く
        move()        # 移動
        move()        # 移動
        
        print("✅ GUIモードでの動作完了")

if __name__ == "__main__":
    gui_sample()
```

このGUI機能により、Python初学者がより直感的にプログラミングとアルゴリズムを学習できるようになります。