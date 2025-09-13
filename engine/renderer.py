"""
レンダラー基盤とCUI/GUI実装
Rendererベースクラス、テキスト表示機能、pygame GUI機能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import sys
from datetime import datetime
from . import GameState, Position, Direction, GameStatus
from .layout_constraint_manager import LayoutConstraintManager, LayoutConstraintViolation
from .event_processing_engine import EventProcessingEngine, EventPriority

# pygame のインポート（オプショナル）
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️ pygame が見つかりません。GUIレンダラーは使用できません。")


class Renderer(ABC):
    """レンダラーベースクラス"""
    
    def __init__(self):
        self.width = 0
        self.height = 0
        self.observers: List[callable] = []
    
    @abstractmethod
    def initialize(self, width: int, height: int) -> None:
        """レンダラーを初期化"""
        pass
    
    @abstractmethod
    def render_frame(self, game_state: GameState) -> None:
        """フレームを描画"""
        pass
    
    @abstractmethod
    def update_display(self) -> None:
        """ディスプレイを更新"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        pass
    
    def add_observer(self, callback: callable) -> None:
        """状態変更の観測者を追加"""
        self.observers.append(callback)
    
    def notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        """観測者に通知"""
        for callback in self.observers:
            try:
                callback(event, data)
            except Exception as e:
                print(f"Observer error: {e}")


class CuiRenderer(Renderer):
    """CUIテキストレンダラー"""
    
    def __init__(self):
        super().__init__()
        self.symbol_map = {
            'empty': '.',
            'wall': '#',
            'player': 'P',
            'goal': 'G',
            'enemy': 'E',
            'item': 'I',
            'forbidden': 'X'
        }
        self.direction_symbols = {
            Direction.NORTH: '↑',
            Direction.EAST: '→',
            Direction.SOUTH: '↓',
            Direction.WEST: '←'
        }
        self.current_frame: List[List[str]] = []
        self.show_debug = False
    
    def initialize(self, width: int, height: int) -> None:
        """CUIレンダラーを初期化"""
        self.width = width
        self.height = height
        self.current_frame = [['.' for _ in range(width)] for _ in range(height)]
        print("📺 CUIレンダラー初期化完了")
    
    def render_frame(self, game_state: GameState) -> None:
        """ゲーム状態をテキストフレームに描画"""
        # フレームをクリア
        for y in range(self.height):
            for x in range(self.width):
                self.current_frame[y][x] = self.symbol_map['empty']
        
        # 壁を描画
        for wall_pos in game_state.board.walls:
            if self._is_valid_position(wall_pos):
                self.current_frame[wall_pos.y][wall_pos.x] = self.symbol_map['wall']
        
        # 移動禁止マスを描画
        for forbidden_pos in game_state.board.forbidden_cells:
            if self._is_valid_position(forbidden_pos):
                self.current_frame[forbidden_pos.y][forbidden_pos.x] = self.symbol_map['forbidden']
        
        # ゴールを描画
        if game_state.goal_position and self._is_valid_position(game_state.goal_position):
            self.current_frame[game_state.goal_position.y][game_state.goal_position.x] = self.symbol_map['goal']
        
        # アイテムを描画
        for item in game_state.items:
            if self._is_valid_position(item.position):
                self.current_frame[item.position.y][item.position.x] = self.symbol_map['item']
        
        # 敵を描画
        for enemy in game_state.enemies:
            occupied_positions = enemy.get_occupied_positions()
            for pos in occupied_positions:
                if self._is_valid_position(pos):
                    self.current_frame[pos.y][pos.x] = self.symbol_map['enemy']
        
        # プレイヤーを描画（最後に描画して他の要素より優先）
        player_pos = game_state.player.position
        if self._is_valid_position(player_pos):
            # プレイヤーの向きを考慮した表示
            if self.show_debug:
                player_symbol = self.direction_symbols[game_state.player.direction]
            else:
                player_symbol = self.symbol_map['player']
            self.current_frame[player_pos.y][player_pos.x] = player_symbol
    
    def update_display(self) -> None:
        """フレームをコンソールに出力"""
        # 画面をクリア（簡易版）
        print("\n" + "=" * (self.width * 2 + 3))
        
        # フレームを出力
        for y in range(self.height):
            line = "| "
            for x in range(self.width):
                line += self.current_frame[y][x] + " "
            line += "|"
            print(line)
        
        print("=" * (self.width * 2 + 3))
    
    def render_game_info(self, game_state: GameState) -> None:
        """ゲーム情報を表示"""
        print(f"🎮 ターン: {game_state.turn_count}/{game_state.max_turns}")
        print(f"📍 位置: ({game_state.player.position.x}, {game_state.player.position.y})")
        print(f"🧭 向き: {game_state.player.direction.value}")
        print(f"❤️  HP: {game_state.player.hp}/{game_state.player.max_hp}")
        print(f"⚔️ 攻撃力: {game_state.player.attack_power}")
        print(f"🎯 状態: {game_state.status.value}")
        
        if game_state.goal_position:
            goal_pos = game_state.goal_position
            player_pos = game_state.player.position
            distance = int(player_pos.distance_to(goal_pos))
            print(f"🏁 ゴールまでの距離: {distance}")
        
        print()
    
    def render_legend(self) -> None:
        """凡例を表示"""
        print("📋 凡例:")
        print(f"  {self.symbol_map['player']} = プレイヤー")
        print(f"  {self.symbol_map['goal']} = ゴール")
        print(f"  {self.symbol_map['wall']} = 壁")
        print(f"  {self.symbol_map['enemy']} = 敵")
        print(f"  {self.symbol_map['item']} = アイテム")
        print(f"  {self.symbol_map['forbidden']} = 移動禁止")
        print(f"  {self.symbol_map['empty']} = 空きマス")
        
        if self.show_debug:
            print("🧭 方向記号:")
            for direction, symbol in self.direction_symbols.items():
                print(f"  {symbol} = {direction.value}")
        print()
    
    def render_complete_view(self, game_state: GameState, show_legend: bool = True) -> None:
        """完全なビューを描画"""
        self.render_frame(game_state)
        self.update_display()
        self.render_game_info(game_state)
        
        if show_legend:
            self.render_legend()
    
    def render_game_result(self, game_state: GameState) -> None:
        """ゲーム結果を表示"""
        print("🏁 " + "=" * 30)
        print("   ゲーム終了！")
        print("=" * 32)
        
        status_messages = {
            GameStatus.WON: "🎉 ゲームクリア！",
            GameStatus.FAILED: "💀 ゲーム失敗",
            GameStatus.TIMEOUT: "⏰ 時間切れ",
            GameStatus.ERROR: "❌ エラー発生"
        }
        
        message = status_messages.get(game_state.status, "❓ 不明な状態")
        print(f"結果: {message}")
        print(f"使用ターン: {game_state.turn_count}/{game_state.max_turns}")
        
        if game_state.status == GameStatus.WON:
            efficiency = (game_state.max_turns - game_state.turn_count) / game_state.max_turns * 100
            print(f"効率性: {efficiency:.1f}%")
        
        print("=" * 32)
    
    def set_debug_mode(self, enabled: bool) -> None:
        """デバッグモードの切り替え"""
        self.show_debug = enabled
        if enabled:
            print("🔧 デバッグモード: ON（方向記号表示）")
        else:
            print("🔧 デバッグモード: OFF（通常表示）")
    
    def render_action_history(self, actions: List[str], limit: int = 10) -> None:
        """アクション履歴を表示"""
        print("📜 最近のアクション:")
        recent_actions = actions[-limit:] if len(actions) > limit else actions
        
        for i, action in enumerate(recent_actions, 1):
            print(f"  {i}. {action}")
        
        if len(actions) > limit:
            print(f"  ... (他 {len(actions) - limit} 件)")
        print()
    
    def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        print("📺 CUIレンダラー終了")
    
    def _is_valid_position(self, pos: Position) -> bool:
        """座標が有効範囲内かチェック"""
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height


class GuiRenderer(Renderer):
    """pygame を使用したGUIレンダラー"""
    
    def __init__(self):
        super().__init__()
        if not PYGAME_AVAILABLE:
            raise ImportError("pygame が必要ですが、インストールされていません")
        
        # pygame 初期化
        pygame.init()
        
        # 画面設定
        self.cell_size = 32  # 各マスのサイズ（ピクセル）
        self.screen = None
        self.clock = pygame.time.Clock()
        self.font = None
        self.small_font = None
        
        # カラーパレット
        self.colors = {
            'background': (240, 240, 240),      # 薄いグレー
            'wall': (64, 64, 64),               # ダークグレー
            'empty': (255, 255, 255),           # 白
            'player': (0, 120, 255),            # 青
            'goal': (255, 215, 0),              # 金
            'enemy': (255, 0, 0),               # 赤
            'item': (0, 255, 0),                # 緑
            'forbidden': (128, 0, 128),         # 紫
            'grid': (200, 200, 200),            # 薄いグレー（グリッド線）
            'text': (0, 0, 0),                  # 黒（テキスト）
            'text_bg': (255, 255, 255),         # 白（テキスト背景）
            'vision_normal': (255, 100, 100),   # 敵視野（薄い赤）- 敵が非警戒状態の視野範囲
            'vision_alerted': (255, 50, 50),    # 警戒中敵視野（濃い赤）- プレイヤー発見後の警戒状態視野
            # v1.2.8 特殊条件付きステージ - 敵モード別色定義
            'enemy_calm': (255, 0, 0),          # 平常モード（通常の赤）
            'enemy_rage': (255, 100, 0),        # 怒りモード（オレンジ）
            'enemy_transitioning': (255, 150, 0), # 状態遷移中（薄いオレンジ）
            'enemy_hunting': (150, 0, 150),     # 追跡モード（紫）
            'enemy_special': (255, 0, 255),     # 特殊敵（マゼンタ）
            'area_attack_range': (255, 200, 0), # 範囲攻撃範囲（黄色）
        }
        
        # UI設定（文字省略防止のため大幅拡大）
        self.sidebar_width = 150  # サイドバー幅を半分に縮小（300→150）
        self.info_height = 70     # 情報エリア高さを半分に縮小（140→70）
        self.margin = 10
        
        # アニメーション用
        self.animation_duration = 200  # ミリ秒
        self.last_update = 0
        
        # 描画オプション
        self.show_grid = True
        self.show_coordinates = False
        self.debug_mode = False
        self.show_enemy_vision = True  # 敵の視野を常に表示する
        
        # 🚀 v1.2.5: 7段階速度制御対応UI設定
        self.control_panel_height = 90  # 3段構成に拡張（55→90）
        self.button_width = 50  # Continueボタン文字収容のため+5px拡張（45→50）
        self.button_height = 25 # ボタン高さを少し拡大（22→25）
        self.button_margin = 5  # ボタン間隔を縮小（6→5）
        self.speed_button_width = 40  # 速度ボタン専用幅
        self.speed_button_height = 20 # 速度ボタン専用高さ
        
        # ボードサイズ変更対応のための追加マージン
        self.dynamic_margin_bottom = 10  # 情報パネルとの最小間隔
        
        # 🚀 v1.2.5: 7段階速度制御対応ボタン色定義
        self.button_colors = {
            'step': (100, 180, 100),        # 緑（ステップ実行）
            'continue': (100, 150, 255),    # 青（連続実行）
            'pause': (255, 150, 100),       # オレンジ（一時停止）
            'stop': (255, 100, 100),        # 赤（停止）
            'reset': (150, 150, 255),       # ライトブルー（リセット）
            'exit': (200, 100, 100),        # ライトレッド（終了）
            'speed_standard': (200, 200, 100),    # 黄（標準速度 x1-x5）
            'speed_ultra': (255, 165, 0),         # オレンジ（超高速 x10, x50）
            'speed_selected': (255, 215, 0),      # 金色（選択中速度）
            'disabled': (150, 150, 150),    # グレー（無効）
            'button_text': (255, 255, 255), # 白（ボタンテキスト）
            'button_text_dark': (0, 0, 0),  # 黒（濃いボタン用テキスト）
        }
        
        # 実行制御コールバック
        self.execution_controller = None
        self.button_rects = {}  # ボタン矩形管理
        
        # 🚀 v1.2.5: 7段階速度制御システム
        self._7stage_speed_manager = None
        self._ultra_speed_controller = None
        self.current_speed_multiplier = 2  # デフォルトをx2に変更
        self.speed_button_rects = {}  # 速度ボタン矩形管理
        self.speed_warning_display = False  # 超高速警告表示フラグ
        
        # レイアウト制約管理（v1.2新機能）
        self.layout_constraint_manager = LayoutConstraintManager()
        
        # イベント処理エンジン（v1.2新機能）
        self.event_processing_engine = EventProcessingEngine(debug_mode=False)
        
        # ボタン登録フラグ
        self._buttons_registered = False
        
        print("🎮 GUIレンダラー初期化完了（実行制御UI・レイアウト制約管理・イベント処理エンジン対応）")
    
    def setup_7stage_speed_control(self, speed_manager, ultra_controller):
        """
        7段階速度制御システム統合
        
        Args:
            speed_manager: Enhanced7StageSpeedControlManager
            ultra_controller: UltraHighSpeedController
        """
        self._7stage_speed_manager = speed_manager
        self._ultra_speed_controller = ultra_controller
        if speed_manager:
            self.current_speed_multiplier = speed_manager.get_current_speed_multiplier()
        print("✅ GUI: 7段階速度制御システム統合完了")
    
    def initialize(self, width: int, height: int) -> None:
        """GUIレンダラーを初期化"""
        self.width = width
        self.height = height
        
        # 画面サイズ計算
        game_area_width = self.width * self.cell_size
        game_area_height = self.height * self.cell_size
        
        # サイドバーに必要な最小高さを計算（動的計算用の初期値）
        # 初期化時はゲーム状態が不明なので、最大ケースを想定
        # ヘッダー(30) + プレイヤー情報(130) + 敵情報(最大2体×90=180) + 凡例(最大9項目×18=162) + 余裕(50)
        min_sidebar_height = 30 + 130 + 180 + 162 + 50  # 合計552px
        
        # 情報パネル・コントロールパネルの720px幅を考慮した画面サイズ計算
        info_control_width = 720  # 情報パネルとコントロールパネルの幅
        screen_width = max(game_area_width + self.sidebar_width + self.margin * 3, info_control_width + self.sidebar_width + self.margin * 3)
        
        # サイドバーの高さも考慮したウィンドウ高さを計算
        base_height = game_area_height + self.info_height + self.control_panel_height + self.margin * 4
        sidebar_required_height = min_sidebar_height + self.control_panel_height + self.margin * 3  # コントロールパネルとマージンも考慮
        screen_height = max(base_height, sidebar_required_height)
        
        # pygame 画面初期化
        pygame.display.init()  # ディスプレイ明示的初期化
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Python初学者向けローグライク - GUI版")
        
        # ウィンドウをアクティブにする（macOS対応）
        import os
        if os.name == 'posix':  # macOS/Linux
            pygame.display.flip()
            
        # フォント初期化
        pygame.font.init()  # フォント明示的初期化
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # レイアウト制約設定（v1.2新機能）
        self.layout_constraint_manager.set_layout_constraint(
            game_width=self.width,
            game_height=self.height, 
            sidebar_width=self.sidebar_width,
            info_height=self.info_height,
            control_panel_height=self.control_panel_height,
            margin=self.margin,
            cell_size=self.cell_size
        )
        
        print(f"📺 GUI画面初期化完了: {screen_width}x{screen_height}")
        print(f"🖥️ pygame version: {pygame.version.ver}")
        print(f"🎮 ウィンドウハンドル: {pygame.display.get_surface() is not None}")
        print(f"🔧 レイアウト制約管理初期化完了")
    
    def render_frame(self, game_state: GameState) -> None:
        """ゲーム状態をGUI画面に描画"""
        if not self.screen:
            return
        
        # 背景をクリア
        self.screen.fill(self.colors['background'])
        
        # ゲームエリアの描画
        self._draw_game_area(game_state)
        
        # サイドバーの描画
        self._draw_sidebar(game_state)
        
        # 下部情報エリアの描画
        self._draw_info_area(game_state)
        
        # 実行制御パネルの描画（v1.2.5: 7段階速度制御対応）
        self._draw_control_panel()
        
        # 🚀 v1.2.5: 7段階速度表示更新
        self.update_7stage_speed_display()
        
        # イベント処理
        self._handle_events()
    
    def _draw_game_area(self, game_state: GameState) -> None:
        """ゲームエリアを描画"""
        start_x = self.margin + self.sidebar_width + self.margin  # サイドバーの右側に配置
        start_y = self.margin + self.control_panel_height + self.margin  # Execution Controlパネルの下に配置
        
        # 各セルを描画
        for y in range(self.height):
            for x in range(self.width):
                cell_x = start_x + x * self.cell_size
                cell_y = start_y + y * self.cell_size
                cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                
                # セルの種類を判定
                pos = Position(x, y)
                cell_type = self._get_cell_type(pos, game_state)
                
                # セルを描画
                pygame.draw.rect(self.screen, self.colors[cell_type], cell_rect)
                
                # グリッド線を描画
                if self.show_grid:
                    pygame.draw.rect(self.screen, self.colors['grid'], cell_rect, 1)
                
                # 座標表示
                if self.show_coordinates:
                    coord_text = self.small_font.render(f"{x},{y}", True, self.colors['text'])
                    text_rect = coord_text.get_rect()
                    text_rect.topleft = (cell_x + 2, cell_y + 2)
                    self.screen.blit(coord_text, text_rect)
        
        # 敵の視野範囲を描画（半透明オーバーレイ）
        if self.show_enemy_vision:
            self._draw_enemy_vision(game_state, start_x, start_y)
        
        # 範囲攻撃範囲を描画（半透明オーバーレイ）- v1.2.8特殊条件付きステージ
        self._draw_area_attack_range(game_state, start_x, start_y)
        
        # プレイヤーの向きを矢印で表示
        self._draw_player_direction(game_state.player, start_x, start_y)
        
        # 敵の向きを矢印で表示とインデックス表示
        for i, enemy in enumerate(game_state.enemies):
            if enemy.is_alive():
                self._draw_enemy_direction(enemy, start_x, start_y)
                self._draw_enemy_index(enemy, i + 1, start_x, start_y)
    
    def _get_cell_type(self, pos: Position, game_state: GameState) -> str:
        """位置のセル種類を取得"""
        # プレイヤー位置チェック
        if pos == game_state.player.position:
            return 'player'
        
        # 壁チェック
        if pos in game_state.board.walls:
            return 'wall'
        
        # 移動禁止マスチェック
        if pos in game_state.board.forbidden_cells:
            return 'forbidden'
        
        # ゴール位置チェック
        if game_state.goal_position and pos == game_state.goal_position:
            return 'goal'
        
        # 敵チェック（v1.2.8: モード別色分け対応）
        for enemy in game_state.enemies:
            if pos in enemy.get_occupied_positions():
                # 敵のモードに基づいて色を決定
                if hasattr(enemy, 'enemy_mode'):
                    from . import EnemyMode, EnemyType
                    if enemy.enemy_type == EnemyType.SPECIAL_2X3:
                        return 'enemy_special'
                    elif enemy.enemy_mode == EnemyMode.RAGE:
                        return 'enemy_rage'
                    elif enemy.enemy_mode == EnemyMode.TRANSITIONING:
                        return 'enemy_transitioning'
                    elif enemy.enemy_mode == EnemyMode.HUNTING:
                        return 'enemy_hunting'
                    else:  # CALM mode
                        return 'enemy_calm'
                else:
                    return 'enemy'
        
        # アイテムチェック
        for item in game_state.items:
            if pos == item.position:
                return 'item'
        
        # 通常の空きマス
        return 'empty'
    
    def _draw_player_direction(self, player, start_x: int, start_y: int) -> None:
        """プレイヤーの向きを矢印で表示"""
        player_x = start_x + player.position.x * self.cell_size + self.cell_size // 2
        player_y = start_y + player.position.y * self.cell_size + self.cell_size // 2
        
        # 向きに応じた矢印の先端位置計算
        arrow_length = self.cell_size // 4
        direction_offsets = {
            Direction.NORTH: (0, -arrow_length),
            Direction.EAST: (arrow_length, 0),
            Direction.SOUTH: (0, arrow_length),
            Direction.WEST: (-arrow_length, 0)
        }
        
        if player.direction in direction_offsets:
            dx, dy = direction_offsets[player.direction]
            end_x = player_x + dx
            end_y = player_y + dy
            
            # 矢印を描画（太い線）
            pygame.draw.line(self.screen, (255, 255, 255), 
                           (player_x, player_y), (end_x, end_y), 3)
    
    def _draw_enemy_direction(self, enemy, start_x: int, start_y: int) -> None:
        """敵の向きを矢印で表示"""
        enemy_x = start_x + enemy.position.x * self.cell_size + self.cell_size // 2
        enemy_y = start_y + enemy.position.y * self.cell_size + self.cell_size // 2
        
        # 向きに応じた矢印の先端位置計算
        arrow_length = self.cell_size // 4
        direction_offsets = {
            Direction.NORTH: (0, -arrow_length),
            Direction.EAST: (arrow_length, 0),
            Direction.SOUTH: (0, arrow_length),
            Direction.WEST: (-arrow_length, 0)
        }
        
        if enemy.direction in direction_offsets:
            dx, dy = direction_offsets[enemy.direction]
            end_x = enemy_x + dx
            end_y = enemy_y + dy
            
            # 敵の矢印を描画（黄色で表示）
            pygame.draw.line(self.screen, (255, 255, 0), 
                           (enemy_x, enemy_y), (end_x, end_y), 2)
    
    def _draw_enemy_index(self, enemy, index: int, start_x: int, start_y: int) -> None:
        """敵のインデックス番号を右下に表示"""
        enemy_x = start_x + enemy.position.x * self.cell_size
        enemy_y = start_y + enemy.position.y * self.cell_size
        
        # セルの右下にインデックス番号を表示
        index_text = str(index)
        index_surface = self.small_font.render(index_text, True, (255, 255, 255))
        
        # 右下の位置に配置（少し内側にマージンを取る）
        text_x = enemy_x + self.cell_size - index_surface.get_width() - 3
        text_y = enemy_y + self.cell_size - index_surface.get_height() - 2
        
        # 背景色で可読性を高める（小さな背景矩形）
        bg_rect = pygame.Rect(text_x - 2, text_y - 1, 
                             index_surface.get_width() + 4, 
                             index_surface.get_height() + 2)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)  # 黒背景
        
        # インデックス番号を描画
        self.screen.blit(index_surface, (text_x, text_y))
    
    def _get_dynamic_legend_items(self, game_state: GameState) -> List[Tuple[str, Tuple[int, int, int], str]]:
        """ゲーム状態に応じて動的に凡例項目を生成"""
        legend_items = [
            ("■", self.colors['player'], "Player"),
            ("■", self.colors['goal'], "Goal"),
        ]
        
        # 壁の存在チェック
        if game_state.board.walls:
            legend_items.append(("■", self.colors['wall'], "Wall"))
        
        # 敵の存在チェック
        alive_enemies = [enemy for enemy in game_state.enemies if enemy.is_alive()]
        if alive_enemies:
            legend_items.append(("■", self.colors['enemy'], "Enemy"))
            
            # 敵視野項目は敵がいる場合のみ表示
            legend_items.extend([
                ("▢", self.colors['vision_normal'], "Enemy Vision"),
                ("▦", self.colors['vision_alerted'], "Alert Vision"),
            ])
        
        # アイテムの存在チェック
        if game_state.items:
            legend_items.append(("■", self.colors['item'], "Item"))
        
        # 禁止マスの存在チェック
        if game_state.board.forbidden_cells:
            legend_items.append(("■", self.colors['forbidden'], "Blocked"))
        
        # 空マスは常に表示
        legend_items.append(("■", self.colors['empty'], "Empty"))
        
        return legend_items

    def _calculate_dynamic_sidebar_height(self, game_state: GameState) -> int:
        """ゲーム状態に基づいてサイドバーの必要高さを計算"""
        base_height = 30  # ヘッダー
        base_height += 130  # プレイヤー情報
        
        # 敵情報の高さを動的計算
        alive_enemies = [enemy for enemy in game_state.enemies if enemy.is_alive()]
        max_displayed_enemies = min(len(alive_enemies), 2)  # 最大2体まで表示
        enemy_section_height = 30  # "Enemy Info"ヘッダー
        for i in range(max_displayed_enemies):
            enemy = alive_enemies[i]
            lines_per_enemy = 5  # 基本情報: type, pos, dir, hp, atk
            if hasattr(enemy, 'enemy_mode'):
                lines_per_enemy += 1  # Mode情報
                if hasattr(enemy, 'rage_state') and enemy.rage_state and enemy.rage_state.is_active:
                    lines_per_enemy += 1  # Rage情報
            enemy_section_height += lines_per_enemy * 18 + 5  # 敵間スペース
        base_height += enemy_section_height
        
        # 凡例の高さを動的計算
        legend_items = self._get_dynamic_legend_items(game_state)
        legend_height = 30 + len(legend_items) * 18  # "Legend"ヘッダー + 各項目
        base_height += legend_height
        
        base_height += 50  # 余裕のマージン
        
        return base_height

    def _draw_sidebar(self, game_state: GameState) -> None:
        """サイドバーを描画（左側に配置）- 動的高さ調整対応"""
        sidebar_x = self.margin  # 左側に配置
        sidebar_y = self.margin + self.control_panel_height + self.margin  # ゲームエリアと同じY座標
        
        # ステージ情報を左上に表示
        stage_info_text = "Stage: stage01"  # ステージファイル名
        stage_info_surface = self.small_font.render(stage_info_text, True, self.colors['text'])
        self.screen.blit(stage_info_surface, (self.margin, self.margin + 5))
        
        # サイドバー背景（動的高さ計算）
        dynamic_sidebar_height = self._calculate_dynamic_sidebar_height(game_state)
        calculated_height = self.height * self.cell_size
        sidebar_height = max(calculated_height, dynamic_sidebar_height)
        sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, 
                                 self.sidebar_width, 
                                 sidebar_height)
        pygame.draw.rect(self.screen, self.colors['text_bg'], sidebar_rect)
        pygame.draw.rect(self.screen, self.colors['grid'], sidebar_rect, 2)
        
        # プレイヤー情報
        y_offset = sidebar_y + 10
        self._draw_text("Player Info", sidebar_x + 10, y_offset, self.font)
        y_offset += 30
        
        player_info = [
            f"Pos: ({game_state.player.position.x}, {game_state.player.position.y})",
            f"Dir: {game_state.player.direction.value}",
            f"HP: {game_state.player.hp}/{game_state.player.max_hp}",
            f"ATK: {game_state.player.attack_power}"
        ]
        
        for info in player_info:
            self._draw_text(info, sidebar_x + 20, y_offset, self.small_font)
            y_offset += 20
        
        y_offset += 20
        
        # 敵情報
        self._draw_text("Enemy Info", sidebar_x + 10, y_offset, self.font)
        y_offset += 30
        
        alive_enemies = [(i, enemy) for i, enemy in enumerate(game_state.enemies) if enemy.is_alive()]
        if alive_enemies:
            for original_index, (list_index, enemy) in enumerate(alive_enemies[:2]):  # 最大2体まで表示
                # 元のリスト内でのインデックス（1から始まる）を使用
                display_index = list_index + 1
                # v1.2.8: 敵モード状態情報追加
                enemy_info = [
                    f"Enemy {display_index}: {enemy.enemy_type.value}",
                    f"Pos: ({enemy.position.x}, {enemy.position.y})",
                    f"Dir: {enemy.direction.value}",
                    f"HP: {enemy.hp}/{enemy.max_hp}",
                    f"ATK: {enemy.attack_power}"
                ]
                
                # 敵モード情報追加
                if hasattr(enemy, 'enemy_mode'):
                    mode_display = self._get_enemy_mode_display(enemy)
                    enemy_info.append(f"Mode: {mode_display}")
                    
                    # 怒りモード詳細情報
                    if hasattr(enemy, 'rage_state') and enemy.rage_state:
                        if enemy.rage_state.is_active:
                            hp_ratio = enemy.hp / enemy.max_hp
                            enemy_info.append(f"Rage: {hp_ratio:.0%} HP")
                
                for info in enemy_info:
                    self._draw_text(info, sidebar_x + 20, y_offset, self.small_font)
                    y_offset += 18
                y_offset += 5  # 敵間のスペース
        else:
            self._draw_text("No enemies alive", sidebar_x + 20, y_offset, self.small_font)
            y_offset += 20
        
        y_offset += 10
        
        # 凡例（動的生成）
        self._draw_text("Legend", sidebar_x + 10, y_offset, self.font)
        y_offset += 30
        
        # ゲーム状態に基づいて動的に凡例項目を生成
        legend_items = self._get_dynamic_legend_items(game_state)
        
        for symbol, color, description in legend_items:
            # カラーボックスを描画
            color_rect = pygame.Rect(sidebar_x + 20, y_offset + 2, 12, 12)
            
            # 視野系の色は半透明効果を表現
            if description in ["Enemy Vision", "Alert Vision"]:
                # 背景（白）を先に描画
                pygame.draw.rect(self.screen, (255, 255, 255), color_rect)
                # 半透明サーフェスを作成
                vision_surface = pygame.Surface((12, 12))
                vision_surface.set_alpha(80)  # マップと同じ透明度
                vision_surface.fill(color)
                self.screen.blit(vision_surface, color_rect.topleft)
                
                # Alert Visionの場合は太い枠線を追加
                if description == "Alert Vision":
                    pygame.draw.rect(self.screen, (200, 0, 0), color_rect, 2)  # 濃い赤の太い枠線
            else:
                pygame.draw.rect(self.screen, color, color_rect)
            
            pygame.draw.rect(self.screen, self.colors['text'], color_rect, 1)
            
            # 説明テキスト
            self._draw_text(f" {description}", sidebar_x + 40, y_offset, self.small_font)
            y_offset += 18
    
    def _draw_info_area(self, game_state: GameState) -> None:
        """下部情報エリアを描画（LayoutConstraintManager使用でサイドバー重複完全防止）"""
        try:
            # LayoutConstraintManagerで厳密な境界計算
            info_rect = self.layout_constraint_manager.calculate_info_panel_bounds()
            
            # レイアウト制約検証
            self.layout_constraint_manager.validate_layout_constraints(info_rect)
            
            # 720px幅を強制使用（安全境界適用をスキップ）
            safe_info_rect = info_rect
            
        except LayoutConstraintViolation as e:
            # 制約違反時はフォールバック表示
            print(f"⚠️ レイアウト制約違反: {e}")
            info_y = self.height * self.cell_size + self.margin * 2
            safe_info_rect = pygame.Rect(self.margin, info_y, 200, self.info_height)
        
        # 背景描画
        pygame.draw.rect(self.screen, self.colors['text_bg'], safe_info_rect)
        pygame.draw.rect(self.screen, self.colors['grid'], safe_info_rect, 2)
        
        # ステータスメッセージ（1行目）- 拡張された情報パネルで完全表示
        status_text = self._get_status_message(game_state)
        self._draw_text(status_text, safe_info_rect.x + 10, safe_info_rect.y + 10, self.font)
        
        # 操作ヒント（2行目）- 拡張された情報パネルで完全表示
        hint_text = "Controls: Space=Step, Enter=Continue, Esc=Stop"
        self._draw_text(hint_text, safe_info_rect.x + 10, safe_info_rect.y + 35, self.small_font)
        
        # 3行目用のスペース確保（将来の追加情報用）
        # ここに追加情報を表示する場合は y + 55 を使用
        
        # デバッグ情報（デバッグモード時）
        if self.debug_mode:
            debug_text = f"FPS: {self.clock.get_fps():.1f}"
            self._draw_text(debug_text, info_rect.x + 10, info_rect.y + 65, self.small_font)
    
    def _get_status_message(self, game_state: GameState) -> str:
        """状態に応じたメッセージを取得（短縮版）"""
        if game_state.status == GameStatus.WON:
            return "🎉 Game Clear! Congratulations!"
        elif game_state.status == GameStatus.FAILED:
            return "💀 Game Failed. Try again!"
        elif game_state.status == GameStatus.TIMEOUT:
            return "⏰ Time's up! Be more efficient."
        elif game_state.status == GameStatus.ERROR:
            return "❌ An error occurred."
        else:
            remaining_turns = game_state.max_turns - game_state.turn_count
            return f"🎮 Playing... Turns: {remaining_turns}/{game_state.max_turns}"
    
    def _draw_text(self, text: str, x: int, y: int, font: pygame.font.Font, color: Tuple[int, int, int] = None) -> None:
        """テキストを描画"""
        if color is None:
            color = self.colors['text']
        
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def _handle_events(self) -> None:
        """pygame イベントを処理（EventProcessingEngine使用で信頼性向上）"""
        # メインスレッドチェック（NSInternalInconsistencyException回避）
        import threading
        if threading.current_thread() is not threading.main_thread():
            return  # バックグラウンドスレッドからの呼び出しは無視
            
        pygame_events = pygame.event.get()
        
        # システム終了イベントの個別処理
        for event in pygame_events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                elif event.key == pygame.K_F2:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_F3:
                    self.show_coordinates = not self.show_coordinates
                elif event.key == pygame.K_F4:
                    self.show_enemy_vision = not self.show_enemy_vision
                    print(f"🔧 敵視野表示: {'ON' if self.show_enemy_vision else 'OFF'}")
        
        # EventProcessingEngineでマウス・キーボードイベントを処理
        mouse_events = self.event_processing_engine.process_mouse_events(pygame_events)
        keyboard_events = self.event_processing_engine.handle_keyboard_shortcuts(pygame_events)
        
        # イベント優先順位に基づいて処理
        all_events = mouse_events + keyboard_events
        prioritized_events = self.event_processing_engine.ensure_event_priority(all_events)
        
        # デバッグ情報出力（必要に応じて）
        if self.debug_mode and prioritized_events:
            print(f"🔧 処理イベント数: {len(prioritized_events)}")
            for event in prioritized_events[:3]:  # 最初の3件のみ表示
                print(f"   {event.event_type.value}: {event.success}")
    
    def update_display(self) -> None:
        """ディスプレイを更新"""
        if self.screen:
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
    
    def render_complete_view(self, game_state: GameState, show_legend: bool = True) -> None:
        """完全なビューを描画"""
        self.render_frame(game_state)
        self.update_display()
    
    def render_game_result(self, game_state: GameState) -> None:
        """ゲーム結果を表示"""
        if not self.screen:
            return
        
        # 半透明オーバーレイ
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 結果メッセージ
        result_messages = {
            GameStatus.WON: "🎉 ゲームクリア！",
            GameStatus.FAILED: "💀 ゲーム失敗",
            GameStatus.TIMEOUT: "⏰ 時間切れ",
            GameStatus.ERROR: "❌ エラー発生"
        }
        
        message = result_messages.get(game_state.status, "ゲーム終了")
        
        # 大きなフォントで結果表示
        big_font = pygame.font.Font(None, 48)
        result_text = big_font.render(message, True, (255, 255, 255))
        text_rect = result_text.get_rect(center=(self.screen.get_width() // 2, 
                                               self.screen.get_height() // 2))
        self.screen.blit(result_text, text_rect)
        
        # 詳細情報
        details = [
            f"使用ターン: {game_state.turn_count}/{game_state.max_turns}",
            "ESCキーで終了"
        ]
        
        y_offset = text_rect.bottom + 30
        for detail in details:
            detail_text = self.font.render(detail, True, (255, 255, 255))
            detail_rect = detail_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(detail_text, detail_rect)
            y_offset += 30
        
        pygame.display.flip()
        
        # 結果表示の待機
        waiting = True
        while waiting:
            # メインスレッドチェック（NSInternalInconsistencyException回避）
            import threading
            if threading.current_thread() is not threading.main_thread():
                break  # バックグラウンドスレッドからの呼び出しは終了
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False
            self.clock.tick(60)
    
    def render_legend(self) -> None:
        """凡例を表示（GUIではコンソール出力）"""
        print("📋 凡例:")
        print("  🔵 = プレイヤー")
        print("  🟨 = ゴール")
        print("  ⬛ = 壁")
        print("  🔴 = 敵")
        print("  🟢 = アイテム")
        print("  🟣 = 移動禁止")
        print("  ⬜ = 空きマス")
        print()
        print("🎮 キー操作:")
        print("  F1: デバッグモード切り替え")
        print("  F2: グリッド表示切り替え")
        print("  F3: 座標表示切り替え")
        print("  F4: 敵視野表示切り替え")
        print("  ESC: 終了")
        print()
    
    def render_action_history(self, actions: List[str], limit: int = 10) -> None:
        """アクション履歴を表示（GUIではコンソール出力）"""
        print("📜 最近のアクション:")
        recent_actions = actions[-limit:] if len(actions) > limit else actions
        
        for i, action in enumerate(recent_actions, 1):
            print(f"  {i}. {action}")
        
        if len(actions) > limit:
            print(f"  ... (他 {len(actions) - limit} 件)")
        print()
    
    def render_game_info(self, game_state: GameState) -> None:
        """ゲーム情報を表示（GUIではコンソール出力）"""
        print(f"🎮 ターン: {game_state.turn_count}/{game_state.max_turns}")
        print(f"📍 位置: ({game_state.player.position.x}, {game_state.player.position.y})")
        print(f"🧭 向き: {game_state.player.direction.value}")
        print(f"❤️  HP: {game_state.player.hp}/{game_state.player.max_hp}")
        print(f"⚔️ 攻撃力: {game_state.player.attack_power}")
        print(f"🎯 状態: {game_state.status.value}")
        
        if game_state.goal_position:
            goal_pos = game_state.goal_position
            player_pos = game_state.player.position
            distance = int(player_pos.distance_to(goal_pos))
            print(f"🏁 ゴールまでの距離: {distance}")
        
        print()
    
    def set_debug_mode(self, enabled: bool) -> None:
        """デバッグモードの切り替え"""
        self.debug_mode = enabled
        print(f"🔧 GUIデバッグモード: {'ON' if enabled else 'OFF'}")
    
    def set_execution_controller(self, controller) -> None:
        """ExecutionControllerを設定（EventProcessingEngineにも同時設定）"""
        self.execution_controller = controller
        
        # EventProcessingEngineにもexecution_controllerを設定（v1.2新機能）
        if hasattr(self, 'event_processing_engine'):
            self.event_processing_engine.execution_controller = controller
            print("🔧 EventProcessingEngineにExecutionController連携完了")
    
    def _draw_control_panel(self) -> None:
        """🚀 v1.2.5: 3段構成拡張実行制御パネルを描画"""
        if not self.screen:
            return
        
        # パネル領域の計算（幅を拡大して7ボタン対応）
        panel_y = self.margin
        panel_width = 500  # 7ボタン対応で幅を拡大（400→500）
        
        # パネル背景（サイドバーの右側に配置）
        control_x = self.margin + self.sidebar_width + self.margin
        panel_rect = pygame.Rect(control_x, panel_y, panel_width, self.control_panel_height)
        pygame.draw.rect(self.screen, (230, 230, 230), panel_rect)
        pygame.draw.rect(self.screen, (180, 180, 180), panel_rect, 2)
        
        # 🚀 v1.2.5: 3段構成レイアウト
        self._draw_enhanced_3tier_control_panel(control_x, panel_y, panel_width)
    
    def _draw_enhanced_3tier_control_panel(self, control_x: int, panel_y: int, panel_width: int) -> None:
        """🚀 v1.2.5: 3段構成拡張コントロールパネル描画"""
        
        # Tier 1: パネル名表示
        title_text = self.font.render("🚀 Execution Control v1.2.5", True, self.colors['text'])
        self.screen.blit(title_text, (control_x + 10, panel_y + 5))
        
        # Tier 2: 実行制御ボタン（既存）
        button_y = panel_y + 28
        button_x_start = control_x + 10
        
        # 5つの実行制御ボタン
        step_rect = self._draw_button(button_x_start, button_y, "Step", 'step')
        continue_rect = self._draw_button(button_x_start + (self.button_width + self.button_margin) * 1, 
                                        button_y, "Continue", 'continue')
        pause_rect = self._draw_button(button_x_start + (self.button_width + self.button_margin) * 2, 
                                     button_y, "Pause", 'pause')
        reset_rect = self._draw_button(button_x_start + (self.button_width + self.button_margin) * 3, 
                                     button_y, "Reset", 'reset')
        exit_rect = self._draw_button(button_x_start + (self.button_width + self.button_margin) * 4, 
                                    button_y, "Exit", 'exit')
        
        # 基本ボタン矩形記録
        self.button_rects = {
            'step': step_rect,
            'continue': continue_rect,  
            'pause': pause_rect,
            'reset': reset_rect,
            'exit': exit_rect
        }
        
        # Tier 3: 7段階速度制御ボタン
        speed_y = panel_y + 55
        self._draw_7stage_speed_control_buttons(control_x, speed_y, panel_width)
        
        # 超高速警告表示
        if self.current_speed_multiplier in [10, 50]:
            self._render_ultra_speed_warning(control_x, panel_y, panel_width)
        
        # ボタン登録（初回のみ）
        self._register_buttons_once_7stage(step_rect, continue_rect, pause_rect, reset_rect, exit_rect)
    
    def _draw_7stage_speed_control_buttons(self, control_x: int, speed_y: int, panel_width: int) -> None:
        """🚀 v1.2.5: 7段階速度制御ボタン群描画（横一列配置）"""
        
        # 速度ラベル
        speed_label = self.small_font.render("Speed Control:", True, self.colors['text'])
        self.screen.blit(speed_label, (control_x + 10, speed_y))
        
        # 横一列レイアウト設定
        all_speeds = [1, 2, 3, 4, 5, 10, 50]
        buttons_y = speed_y + 15
        
        # ボタン幅とマージンを調整（7個のボタンがパネル幅に収まるよう）
        available_width = panel_width - 200  # ラベルとmarginを考慮
        total_button_width = available_width // 7
        button_width = min(total_button_width - 3, 35)  # 最大35px、間隔3px
        button_margin = 3
        
        buttons_x_start = control_x + 10
        
        # 横一列に7個のボタンを配置
        for i, multiplier in enumerate(all_speeds):
            button_x = buttons_x_start + i * (button_width + button_margin)
            
            # ボタン描画
            rect = pygame.Rect(button_x, buttons_y, button_width, self.speed_button_height)
            
            # ボタン色選択
            if multiplier == self.current_speed_multiplier:
                button_color = self.button_colors['speed_selected']
                text_color = self.button_colors['button_text_dark']
            elif multiplier in [10, 50]:
                button_color = self.button_colors['speed_ultra']
                text_color = self.button_colors['button_text']
            else:
                button_color = self.button_colors['speed_standard']
                text_color = self.button_colors['button_text']
            
            # ボタン描画
            pygame.draw.rect(self.screen, button_color, rect)
            pygame.draw.rect(self.screen, self.colors['text'], rect, 1)  # ボーダー
            
            # テキスト描画（小さめフォント）
            text_surface = self.small_font.render(f"x{multiplier}", True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            
            # ボタン矩形を登録
            self.speed_button_rects[f'speed_{multiplier}'] = rect
        
        # 現在の速度表示（下部）
        current_speed_text = f"Current: x{self.current_speed_multiplier}"
        if self.current_speed_multiplier in [10, 50]:
            current_speed_text += " ⚡"  # 超高速インディケーター
        
        speed_info_surface = self.small_font.render(current_speed_text, True, self.colors['text'])
        speed_info_x = control_x + panel_width - speed_info_surface.get_width() - 10
        self.screen.blit(speed_info_surface, (speed_info_x, speed_y + 40))
    
    def _draw_speed_button(self, x: int, y: int, text: str, multiplier: int) -> pygame.Rect:
        """🚀 v1.2.5: 速度制御ボタン描画"""
        rect = pygame.Rect(x, y, self.speed_button_width, self.speed_button_height)
        
        # ボタン色選択
        if multiplier == self.current_speed_multiplier:
            # 選択中速度
            button_color = self.button_colors['speed_selected']
            text_color = self.button_colors['button_text_dark']
        elif multiplier in [10, 50]:
            # 超高速
            button_color = self.button_colors['speed_ultra']
            text_color = self.button_colors['button_text']
        else:
            # 標準速度
            button_color = self.button_colors['speed_standard']
            text_color = self.button_colors['button_text']
        
        # ボタン描画
        pygame.draw.rect(self.screen, button_color, rect)
        pygame.draw.rect(self.screen, (128, 128, 128), rect, 1)
        
        # テキスト描画
        text_surface = self.small_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return rect
    
    def _render_ultra_speed_warning(self, control_x: int, panel_y: int, panel_width: int) -> None:
        """🚀 v1.2.5: 超高速実行警告表示"""
        warning_text = f"⚠️ Ultra-Speed Mode (x{self.current_speed_multiplier})"
        warning_surface = self.small_font.render(warning_text, True, (255, 100, 0))  # オレンジ色
        warning_x = control_x + panel_width - warning_surface.get_width() - 10
        warning_y = panel_y + 8
        self.screen.blit(warning_surface, (warning_x, warning_y))
    
    def _register_buttons_once(self, step_rect, continue_rect, pause_rect, reset_rect, exit_rect):
        """ボタンをEventProcessingEngineに一度だけ登録"""
        if not self._buttons_registered:
            self.event_processing_engine.register_button(
                'step', step_rect, 
                lambda: self._execute_control_action('step'),
                EventPriority.HIGH
            )
            self.event_processing_engine.register_button(
                'continue', continue_rect,
                lambda: self._execute_control_action('continue'),
                EventPriority.HIGH
            )
            self.event_processing_engine.register_button(
                'pause', pause_rect,
                lambda: self._execute_control_action('pause'),
                EventPriority.HIGH
            )
            self.event_processing_engine.register_button(
                'reset', reset_rect,
                lambda: self._execute_control_action('reset'),
                EventPriority.HIGH
            )
            self.event_processing_engine.register_button(
                'exit', exit_rect,
                lambda: self._execute_control_action('exit'),
                EventPriority.CRITICAL
            )
            self._buttons_registered = True
            print("🔧 EventProcessingEngineボタン登録完了")
    
    def _register_buttons_once_7stage(self, step_rect, continue_rect, pause_rect, reset_rect, exit_rect):
        """🚀 v1.2.5: 7段階速度制御対応ボタン登録"""
        # 基本実行制御ボタン登録
        self._register_buttons_once(step_rect, continue_rect, pause_rect, reset_rect, exit_rect)
        
        # 7段階速度制御ボタン登録（1回のみ）
        if hasattr(self, 'speed_button_rects') and not hasattr(self, '_7stage_buttons_registered'):
            for speed_key, speed_rect in self.speed_button_rects.items():
                # speed_1, speed_2, ... から倍率を抽出
                multiplier = int(speed_key.split('_')[1])
                self.event_processing_engine.register_button(
                    speed_key, speed_rect,
                    lambda m=multiplier: self._handle_7stage_speed_button_click(m),
                    EventPriority.MEDIUM
                )
            self._7stage_buttons_registered = True
            print(f"🚀 7段階速度制御ボタン登録完了: {len(self.speed_button_rects)}個")
    
    def _handle_7stage_speed_button_click(self, multiplier: int) -> bool:
        """🚀 v1.2.5: 7段階速度ボタンクリック処理"""
        try:
            if not self._7stage_speed_manager:
                print("⚠️ 7段階速度制御システムが初期化されていません")
                print(f"   _7stage_speed_manager = {getattr(self, '_7stage_speed_manager', 'NOT_SET')}")
                print(f"   _ultra_speed_controller = {getattr(self, '_ultra_speed_controller', 'NOT_SET')}")
                return False
            
            # 速度変更実行
            success = self._7stage_speed_manager.apply_speed_change_realtime(multiplier)
            
            if success:
                # UI状態更新
                old_multiplier = self.current_speed_multiplier
                self.current_speed_multiplier = multiplier
                
                # 🚀 重要: ExecutionControllerのsleep_intervalを直接更新（統一化）
                try:
                    new_sleep_interval = self._7stage_speed_manager.calculate_sleep_interval(multiplier)
                    execution_controller = self._7stage_speed_manager.execution_controller
                    execution_controller.state.sleep_interval = new_sleep_interval
                    
                    print(f"✅ 速度変更成功: x{old_multiplier} → x{multiplier}")
                    print(f"   ExecutionController.sleep_interval = {new_sleep_interval}秒")
                    
                except Exception as update_e:
                    print(f"   ExecutionController更新エラー: {update_e}")
                
                # 超高速モード処理
                if multiplier in [10, 50]:
                    self._handle_ultra_high_speed_mode_activation(multiplier)
                
                return True
            else:
                print(f"❌ 速度変更失敗: x{multiplier}")
                return False
                
        except Exception as e:
            print(f"❌ 7段階速度ボタンクリックエラー: {e}")
            return False
    
    def _handle_ultra_high_speed_mode_activation(self, multiplier: int) -> None:
        """🚀 v1.2.5: 超高速モード有効化処理"""
        if not self._ultra_speed_controller:
            print("⚠️ UltraHighSpeedController未初期化")
            return
        
        target_interval = 0.02 if multiplier == 50 else 0.1  # x50=0.02s, x10=0.1s
        
        success = self._ultra_speed_controller.enable_ultra_high_speed_mode(target_interval)
        if success:
            self.speed_warning_display = True
            print(f"🏃‍♂️ 超高速モード有効化: x{multiplier}")
        else:
            print(f"❌ 超高速モード有効化失敗: x{multiplier}")
    
    def update_7stage_speed_display(self) -> None:
        """🚀 v1.2.5: 7段階速度表示更新"""
        if self._7stage_speed_manager:
            self.current_speed_multiplier = self._7stage_speed_manager.get_current_speed_multiplier()
            
            # 超高速警告フラグ更新
            self.speed_warning_display = self.current_speed_multiplier in [10, 50]
        
        # ボタン領域は既に上記で設定済み（exit含む5つのボタン）
        
    
    def _draw_button(self, x: int, y: int, text: str, button_type: str) -> pygame.Rect:
        """ボタンを描画"""
        rect = pygame.Rect(x, y, self.button_width, self.button_height)
        
        # ボタンの状態に応じた色選択
        if self.execution_controller:
            # 実際の状態に応じてボタン色を変更（簡略版）
            button_color = self.button_colors.get(button_type, self.button_colors['disabled'])
        else:
            button_color = self.button_colors['disabled']
        
        # ボタン描画
        pygame.draw.rect(self.screen, button_color, rect)
        pygame.draw.rect(self.screen, (128, 128, 128), rect, 2)
        
        # テキスト描画
        text_surface = self.small_font.render(text, True, self.button_colors['button_text'])
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return rect
    
    def _handle_control_events(self, event) -> bool:
        """実行制御イベントを処理
        
        Returns:
            bool: イベントが処理された場合True
        """
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        
        if not hasattr(self, 'button_rects') or not self.execution_controller:
            return False
        
        mouse_pos = event.pos
        
        # ボタンクリック判定
        for button_name, rect in self.button_rects.items():
            if rect.collidepoint(mouse_pos):
                print(f"✅ {button_name}ボタンがクリックされました")
                self._execute_control_action(button_name)
                return True
        return False
    
    def _execute_control_action(self, action: str) -> None:
        """🆕 v1.2.1: 実行制御アクションを実行（新規コンポーネント対応）"""
        if not self.execution_controller:
            print("❌ ExecutionController が初期化されていません")
            return
        
        start_time = datetime.now()
        
        try:
            if action == 'step':
                print("🔍 GUI: Step button clicked")
                # 🆕 v1.2.1: 強化されたstep_execution()を使用
                step_result = self.execution_controller.step_execution()
                if step_result and step_result.success:
                    print(f"✅ ステップ実行成功 ({step_result.execution_time_ms:.1f}ms)")
                else:
                    error_msg = step_result.error_message if step_result else "step_result is None"
                    print(f"❌ ステップ実行失敗: {error_msg}")
                    # Reset後の状態を詳細確認
                    if hasattr(self.execution_controller, 'state'):
                        print(f"🔍 ExecutionController状態: mode={self.execution_controller.state.mode}")
                    if hasattr(self, '_global_api') and hasattr(self._global_api, 'game_manager'):
                        gm_state = "initialized" if self._global_api.game_manager else "None"
                        print(f"🔍 GameManager状態: {gm_state}")
                    
            elif action == 'continue':
                print("▶️ GUI: Continue button clicked")
                self.execution_controller.continuous_execution()
                
            elif action == 'pause':
                print("⏸️ GUI: Pause button clicked")
                # 🆕 v1.2.1: PauseController統合の一時停止
                self.execution_controller.pause_execution()
                
            elif action == 'reset':
                print("🔄 GUI: Reset button clicked")
                # 🆕 v1.2.1: ResetManager統合の完全リセット
                self._handle_enhanced_reset_request()
                
            elif action == 'exit':
                print("🚪 GUI: Exit button clicked")
                self._handle_exit_request()
                
            # NFR-001.1: 50ms以内のボタン応答時間検証
            response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            if response_time_ms > 50.0:
                print(f"⚠️ ボタン応答時間要件違反: {response_time_ms:.2f}ms > 50ms")
                
        except Exception as e:
            print(f"❌ 実行制御エラー: {e}")
            # 🆕 v1.2.1: エラー発生時の安全状態復帰
            if hasattr(self.execution_controller, '_safe_state_recovery'):
                self.execution_controller._safe_state_recovery()
    
    def _handle_reset_request(self) -> None:
        """Reset要求を処理（ゲーム初期状態リセット）"""
        print("🔄 ゲームを初期状態にリセットします")
        
        # ExecutionControllerをリセット
        if self.execution_controller:
            self.execution_controller.reset()
        
        # APIレイヤーでゲーム状態をリセット
        try:
            from engine.api import _global_api
            if _global_api and _global_api.game_manager:
                # ゲームマネージャーのリセット（再初期化）
                if hasattr(_global_api.game_manager, 'reset_game'):
                    _global_api.game_manager.reset_game()
                
                # セッションログもリセット
                if hasattr(_global_api, 'session_log_manager') and _global_api.session_log_manager:
                    _global_api.session_log_manager.reset_session()
                    
            print("✅ ゲーム初期状態リセット完了")
        except Exception as e:
            print(f"⚠️ リセット処理エラー: {e}")
    
    def _handle_enhanced_reset_request(self) -> None:
        """🆕 v1.2.1: 強化されたリセット要求処理（ResetManager統合）"""
        start_time = datetime.now()
        print("🔄 完全システムリセットを実行します")
        
        try:
            # ExecutionControllerの完全リセット機能を使用
            if self.execution_controller and hasattr(self.execution_controller, 'full_system_reset'):
                reset_result = self.execution_controller.full_system_reset()
                
                if reset_result.success:
                    print("✅ 完全システムリセット成功")
                    print(f"📊 リセット対象: {', '.join(reset_result.components_reset)}")
                else:
                    print("⚠️ 完全システムリセット部分的失敗")
                    for error in reset_result.errors:
                        print(f"❌ {error}")
            else:
                # フォールバック：従来のリセット処理
                print("⚠️ 新しいリセット機能が利用できません - 従来の方式を使用")
                self._handle_reset_request()
            
            # NFR-001.3: 200ms以内のリセット完了時間検証
            reset_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            if reset_time_ms > 200.0:
                print(f"⚠️ リセット時間要件違反: {reset_time_ms:.2f}ms > 200ms")
            else:
                print(f"✅ リセット時間: {reset_time_ms:.2f}ms (要件内)")
                
        except Exception as e:
            print(f"❌ 強化リセット処理エラー: {e}")
            # 緊急フォールバック
            try:
                self._handle_reset_request()
                print("🔄 緊急フォールバックリセット完了")
            except Exception as fallback_error:
                print(f"🚨 緊急フォールバックも失敗: {fallback_error}")
    
    def _handle_exit_request(self) -> None:
        """Exit要求を処理"""
        print("🏁 プログラム終了を開始します")
        
        # ExecutionControllerがまだ完了していない場合のみ完了状態に設定
        from engine import ExecutionMode
        if self.execution_controller and self.execution_controller.state.mode != ExecutionMode.COMPLETED:
            self.execution_controller.mark_solve_complete()
        
        # pygameのQUITイベントを生成してメインループを終了
        try:
            import pygame
            import threading
            # メインスレッドチェック（NSInternalInconsistencyException回避）
            if threading.current_thread() is not threading.main_thread():
                print("⚠️ バックグラウンドスレッドからのイベント送信をスキップ")
                return
                
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
            print("✅ 正常終了イベント送信完了")
        except Exception as e:
            print(f"⚠️ 終了イベント送信エラー: {e}")
    
    def _draw_enemy_vision(self, game_state: GameState, start_x: int, start_y: int) -> None:
        """敵の視野範囲を描画"""
        for enemy in game_state.enemies:
            if not enemy.is_alive():
                continue
            
            # 敵の視野範囲セルを取得（壁による遮蔽を考慮）
            vision_cells = enemy.get_vision_cells(game_state.board)
            
            # 視野の色を決定（警戒状態かどうかで変更）
            vision_color = self.colors['vision_alerted'] if enemy.alerted else self.colors['vision_normal']
            
            # 各視野セルを半透明で描画
            for vision_pos in vision_cells:
                # 画面範囲内かチェック
                if 0 <= vision_pos.x < self.width and 0 <= vision_pos.y < self.height:
                    # 壁や移動禁止セルは視野描画をスキップ
                    if self._is_vision_blocked(vision_pos, game_state):
                        continue
                    
                    cell_x = start_x + vision_pos.x * self.cell_size
                    cell_y = start_y + vision_pos.y * self.cell_size
                    
                    # 半透明サーフェスを作成
                    vision_surface = pygame.Surface((self.cell_size, self.cell_size))
                    vision_surface.set_alpha(80)  # 透明度設定（0-255、低いほど透明）
                    vision_surface.fill(vision_color)
                    
                    # サーフェスを描画
                    self.screen.blit(vision_surface, (cell_x, cell_y))
                    
                    # 警戒状態の場合は枠線を追加
                    if enemy.alerted:
                        alert_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                        pygame.draw.rect(self.screen, (200, 0, 0), alert_rect, 3)  # 濃い赤の太い枠線
    
    def _is_vision_blocked(self, pos: Position, game_state: GameState) -> bool:
        """視野が遮られるセルかチェック（壁など）"""
        # 壁は視野を遮る
        if pos in game_state.board.walls:
            return True
        
        # 移動禁止セルも視野を遮る
        if pos in game_state.board.forbidden_cells:
            return True
        
        return False
    
    def _get_enemy_mode_display(self, enemy) -> str:
        """敵モード表示名取得 - v1.2.8特殊条件付きステージ"""
        from . import EnemyMode
        
        mode_names = {
            EnemyMode.CALM: "Calm",
            EnemyMode.RAGE: "Rage",
            EnemyMode.TRANSITIONING: "Trans",
            EnemyMode.HUNTING: "Hunt"
        }
        
        return mode_names.get(enemy.enemy_mode, "Unknown")
    
    def _draw_area_attack_range(self, game_state: GameState, start_x: int, start_y: int) -> None:
        """範囲攻撃範囲視覚化 - v1.2.8特殊条件付きステージ"""
        from .enemy_system import LargeEnemySystem
        from . import EnemyMode
        
        # 仮の大型敵システム作成（実際の実装では外部から渡される）
        large_enemy_system = LargeEnemySystem()
        
        for i, enemy in enumerate(game_state.enemies):
            if not enemy.is_alive():
                continue
            
            # Stage11専用範囲攻撃描画
            if hasattr(enemy, 'stage11_area_attack_active') and enemy.stage11_area_attack_active:
                if hasattr(enemy, 'stage11_attack_range'):
                    # Stage11専用範囲攻撃描画
                    for attack_pos in enemy.stage11_attack_range:
                        # 画面範囲内かチェック
                        if (0 <= attack_pos.x < self.width and 
                            0 <= attack_pos.y < self.height):
                            # 攻撃範囲セルを描画（黄色でハイライト）
                            cell_rect = pygame.Rect(
                                start_x + attack_pos.x * self.cell_size,
                                start_y + attack_pos.y * self.cell_size,
                                self.cell_size,
                                self.cell_size
                            )
                            
                            # 範囲攻撃色（透明度付き）
                            range_surface = pygame.Surface((self.cell_size, self.cell_size))
                            range_surface.set_alpha(180)  # 透明度設定
                            range_surface.fill(self.colors['area_attack_range'])
                            self.screen.blit(range_surface, cell_rect)
                            
                            # 範囲攻撃境界線
                            pygame.draw.rect(self.screen, (255, 100, 0), cell_rect, 2)
                            
            # 怒りモードの大型敵のみ範囲攻撃表示
            elif (hasattr(enemy, 'enemy_mode') and 
                enemy.enemy_mode == EnemyMode.RAGE and 
                hasattr(enemy, 'enemy_type')):
                
                from . import EnemyType
                if enemy.enemy_type in [EnemyType.LARGE_2X2, EnemyType.LARGE_3X3]:
                    # 大型敵システムに一時登録して範囲取得
                    enemy_id = f"temp_{i}"
                    large_enemy_system.large_enemies[enemy_id] = enemy
                    
                    attack_range = large_enemy_system.get_area_attack_range(enemy_id)
                    
                    # 範囲攻撃セルを描画
                    for attack_pos in attack_range:
                        if 0 <= attack_pos.x < self.width and 0 <= attack_pos.y < self.height:
                            cell_x = start_x + attack_pos.x * self.cell_size
                            cell_y = start_y + attack_pos.y * self.cell_size
                            
                            # 半透明の黄色オーバーレイ
                            range_surface = pygame.Surface((self.cell_size, self.cell_size))
                            range_surface.set_alpha(100)
                            range_surface.fill(self.colors['area_attack_range'])
                            self.screen.blit(range_surface, (cell_x, cell_y))
                            
                            # 範囲攻撃枠線
                            range_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                            pygame.draw.rect(self.screen, (255, 165, 0), range_rect, 2)

    def cleanup(self) -> None:
        """リソースをクリーンアップ"""
        print("🎮 GUIレンダラー終了")
        pygame.quit()


class RendererFactory:
    """レンダラーファクトリー"""
    
    @staticmethod
    def create_renderer(renderer_type: str) -> Renderer:
        """指定されたタイプのレンダラーを作成"""
        if renderer_type.lower() == "cui":
            return CuiRenderer()
        elif renderer_type.lower() == "gui":
            if PYGAME_AVAILABLE:
                return GuiRenderer()
            else:
                print("⚠️ pygame が利用できません。CUIレンダラーを使用します。")
                return CuiRenderer()
        else:
            raise ValueError(f"未対応のレンダラータイプ: {renderer_type}")


# エクスポート用
__all__ = ["Renderer", "CuiRenderer", "GuiRenderer", "RendererFactory"]