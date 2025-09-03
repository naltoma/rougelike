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
        
        # 実行制御UIの設定（v1.1新機能）
        self.control_panel_height = 55  # パネル高さを1行分に調整（85→55）
        self.button_width = 55  # ボタン幅を+5px増加（50→55）
        self.button_height = 22 # ボタン高さ
        self.button_margin = 6  # ボタン間隔
        
        # ボタンの色定義
        self.button_colors = {
            'step': (100, 180, 100),        # 緑（ステップ実行）
            'continue': (100, 150, 255),    # 青（連続実行）
            'pause': (255, 150, 100),       # オレンジ（一時停止）
            'stop': (255, 100, 100),        # 赤（停止）
            'speed': (200, 200, 100),       # 黄（速度調整）
            'disabled': (150, 150, 150),    # グレー（無効）
            'button_text': (255, 255, 255), # 白（ボタンテキスト）
        }
        
        # 実行制御コールバック
        self.execution_controller = None
        self.button_rects = {}  # ボタン矩形管理
        
        # レイアウト制約管理（v1.2新機能）
        self.layout_constraint_manager = LayoutConstraintManager()
        
        # イベント処理エンジン（v1.2新機能）
        self.event_processing_engine = EventProcessingEngine(debug_mode=False)
        
        # ボタン登録フラグ
        self._buttons_registered = False
        
        print("🎮 GUIレンダラー初期化完了（実行制御UI・レイアウト制約管理・イベント処理エンジン対応）")
    
    def initialize(self, width: int, height: int) -> None:
        """GUIレンダラーを初期化"""
        self.width = width
        self.height = height
        
        # 画面サイズ計算
        game_area_width = self.width * self.cell_size
        game_area_height = self.height * self.cell_size
        
        # 情報パネル・コントロールパネルの720px幅を考慮した画面サイズ計算
        info_control_width = 720  # 情報パネルとコントロールパネルの幅
        screen_width = max(game_area_width + self.sidebar_width + self.margin * 3, info_control_width + self.sidebar_width + self.margin * 3)
        screen_height = game_area_height + self.info_height + self.control_panel_height + self.margin * 4
        
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
        
        # 実行制御パネルの描画（v1.1新機能）
        self._draw_control_panel()
        
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
        
        # プレイヤーの向きを矢印で表示
        self._draw_player_direction(game_state.player, start_x, start_y)
    
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
        
        # 敵チェック
        for enemy in game_state.enemies:
            if pos in enemy.get_occupied_positions():
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
    
    def _draw_sidebar(self, game_state: GameState) -> None:
        """サイドバーを描画（左側に配置）"""
        sidebar_x = self.margin  # 左側に配置
        sidebar_y = self.margin + self.control_panel_height + self.margin  # ゲームエリアと同じY座標
        
        # ステージ情報を左上に表示
        stage_info_text = "Stage: stage01"  # ステージファイル名
        stage_info_surface = self.small_font.render(stage_info_text, True, self.colors['text'])
        self.screen.blit(stage_info_surface, (self.margin, self.margin + 5))
        
        # サイドバー背景（十分に高く - 全ての要素が収まるように）
        # 最小高さを計算: プレイヤー情報 + ゲーム情報 + 凡例
        min_sidebar_height = 60 + 130 + 200 + 30  # ヘッダー + プレイヤー情報 + ゲーム情報 + 凡例（拡大） + 30px拡張
        calculated_height = self.height * self.cell_size + self.info_height + self.control_panel_height
        sidebar_height = max(calculated_height, min_sidebar_height)
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
        
        # ゲーム情報
        self._draw_text("Game Info", sidebar_x + 10, y_offset, self.font)
        y_offset += 30
        
        game_info = [
            f"Turn: {game_state.turn_count}/{game_state.max_turns}",
            f"Status: {game_state.status.value}",
        ]
        
        if game_state.goal_position:
            player_pos = game_state.player.position
            goal_pos = game_state.goal_position
            distance = int(player_pos.distance_to(goal_pos))
            game_info.append(f"Goal Dist: {distance}")
        
        for info in game_info:
            self._draw_text(info, sidebar_x + 20, y_offset, self.small_font)
            y_offset += 20
        
        y_offset += 20
        
        # 凡例
        self._draw_text("Legend", sidebar_x + 10, y_offset, self.font)
        y_offset += 30
        
        legend_items = [
            ("■", self.colors['player'], "Player"),
            ("■", self.colors['goal'], "Goal"),
            ("■", self.colors['wall'], "Wall"),
            ("■", self.colors['enemy'], "Enemy"),
            ("■", self.colors['item'], "Item"),
            ("■", self.colors['forbidden'], "Blocked"),
            ("■", self.colors['empty'], "Empty"),
        ]
        
        for symbol, color, description in legend_items:
            # カラーボックスを描画
            color_rect = pygame.Rect(sidebar_x + 20, y_offset + 2, 12, 12)
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
        """実行制御パネルを描画"""
        if not self.screen:
            return
        
        # パネル領域の計算（400px幅に調整、上部に配置）
        panel_y = self.margin  # 上部に配置
        panel_width = 400  # 情報パネルと同じ400px幅
        
        # パネル背景（サイドバーの右側に配置）
        control_x = self.margin + self.sidebar_width + self.margin  # サイドバーの右側
        panel_rect = pygame.Rect(control_x, panel_y, panel_width, self.control_panel_height)
        pygame.draw.rect(self.screen, (230, 230, 230), panel_rect)
        pygame.draw.rect(self.screen, (180, 180, 180), panel_rect, 2)
        
        # タイトル
        title_text = self.font.render("Execution Control", True, self.colors['text'])
        self.screen.blit(title_text, (control_x + 10, panel_y + 5))
        
        # ボタン配置（1行レイアウト、横一列配置）
        button_y = panel_y + 25  # 1行のみ
        button_x_start = control_x + 10
        
        # 5つのボタンを横一列に配置
        step_rect = self._draw_button(button_x_start, button_y, "Step", 'step')
        continue_rect = self._draw_button(button_x_start + (self.button_width + self.button_margin) * 1, 
                                        button_y, "Continue", 'continue')
        pause_rect = self._draw_button(button_x_start + (self.button_width + self.button_margin) * 2, 
                                     button_y, "Pause", 'pause')
        reset_rect = self._draw_button(button_x_start + (self.button_width + self.button_margin) * 3, 
                                     button_y, "Reset", 'reset')
        exit_rect = self._draw_button(button_x_start + (self.button_width + self.button_margin) * 4, 
                                    button_y, "Exit", 'exit')
        
        # ボタン矩形を記録（クリック判定用）
        self.button_rects = {
            'step': step_rect,
            'continue': continue_rect,
            'pause': pause_rect,
            'reset': reset_rect,
            'exit': exit_rect
        }
        
        # ボタン登録は初回のみ実行（EventProcessingEngine）
        self._register_buttons_once(step_rect, continue_rect, pause_rect, reset_rect, exit_rect)
        
        # 速度調整表示
        speed_text = "Speed: 1x"
        if self.execution_controller:
            current_speed = getattr(self.execution_controller.state, 'sleep_interval', 1.0)
            if current_speed >= 1.0:
                speed_text = "Speed: 1x"
            elif current_speed >= 0.5:
                speed_text = "Speed: 2x"
            elif current_speed >= 0.25:
                speed_text = "Speed: 4x"
            elif current_speed >= 0.125:
                speed_text = "Speed: 8x"
            else:
                speed_text = "Speed: 16x"
        
        # Speed表示をExitボタンの右側に配置
        speed_surface = self.small_font.render(speed_text, True, self.colors['text'])
        speed_x = button_x_start + (self.button_width + self.button_margin) * 5  # Exitボタンの右側
        speed_y = button_y + 2  # ボタンと同じ高さ
        
        # パネル内に収まる場合のみ表示
        if speed_x + speed_surface.get_width() <= panel_rect.right - 5:
            self.screen.blit(speed_surface, (speed_x, speed_y))
    
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
                    print("❌ ステップ実行失敗")
                    
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
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
            print("✅ 正常終了イベント送信完了")
        except Exception as e:
            print(f"⚠️ 終了イベント送信エラー: {e}")
    
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