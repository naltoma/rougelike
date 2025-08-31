"""
レンダラー基盤とCUI/GUI実装
Rendererベースクラス、テキスト表示機能、pygame GUI機能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import sys
from . import GameState, Position, Direction, GameStatus

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
        
        # UI設定
        self.sidebar_width = 250
        self.info_height = 100
        self.margin = 10
        
        # アニメーション用
        self.animation_duration = 200  # ミリ秒
        self.last_update = 0
        
        # 描画オプション
        self.show_grid = True
        self.show_coordinates = False
        self.debug_mode = False
        
        print("🎮 GUIレンダラー初期化完了")
    
    def initialize(self, width: int, height: int) -> None:
        """GUIレンダラーを初期化"""
        self.width = width
        self.height = height
        
        # 画面サイズ計算
        game_area_width = self.width * self.cell_size
        game_area_height = self.height * self.cell_size
        
        screen_width = game_area_width + self.sidebar_width + self.margin * 3
        screen_height = game_area_height + self.info_height + self.margin * 3
        
        # pygame 画面初期化
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Python初学者向けローグライク - GUI版")
        
        # フォント初期化
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        print(f"📺 GUI画面初期化: {screen_width}x{screen_height}")
    
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
        
        # イベント処理
        self._handle_events()
    
    def _draw_game_area(self, game_state: GameState) -> None:
        """ゲームエリアを描画"""
        start_x = self.margin
        start_y = self.margin
        
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
        """サイドバーを描画"""
        sidebar_x = self.width * self.cell_size + self.margin * 2
        sidebar_y = self.margin
        
        # サイドバー背景
        sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, 
                                 self.sidebar_width, 
                                 self.height * self.cell_size)
        pygame.draw.rect(self.screen, self.colors['text_bg'], sidebar_rect)
        pygame.draw.rect(self.screen, self.colors['grid'], sidebar_rect, 2)
        
        # プレイヤー情報
        y_offset = sidebar_y + 10
        self._draw_text("🎮 プレイヤー情報", sidebar_x + 10, y_offset, self.font)
        y_offset += 30
        
        player_info = [
            f"位置: ({game_state.player.position.x}, {game_state.player.position.y})",
            f"向き: {game_state.player.direction.value}",
            f"HP: {game_state.player.hp}/{game_state.player.max_hp}",
            f"攻撃力: {game_state.player.attack_power}"
        ]
        
        for info in player_info:
            self._draw_text(info, sidebar_x + 20, y_offset, self.small_font)
            y_offset += 20
        
        y_offset += 20
        
        # ゲーム情報
        self._draw_text("🎯 ゲーム情報", sidebar_x + 10, y_offset, self.font)
        y_offset += 30
        
        game_info = [
            f"ターン: {game_state.turn_count}/{game_state.max_turns}",
            f"状態: {game_state.status.value}",
        ]
        
        if game_state.goal_position:
            player_pos = game_state.player.position
            goal_pos = game_state.goal_position
            distance = int(player_pos.distance_to(goal_pos))
            game_info.append(f"ゴール距離: {distance}")
        
        for info in game_info:
            self._draw_text(info, sidebar_x + 20, y_offset, self.small_font)
            y_offset += 20
        
        y_offset += 20
        
        # 凡例
        self._draw_text("📋 凡例", sidebar_x + 10, y_offset, self.font)
        y_offset += 30
        
        legend_items = [
            ("■", self.colors['player'], "プレイヤー"),
            ("■", self.colors['goal'], "ゴール"),
            ("■", self.colors['wall'], "壁"),
            ("■", self.colors['enemy'], "敵"),
            ("■", self.colors['item'], "アイテム"),
            ("■", self.colors['forbidden'], "移動禁止"),
            ("■", self.colors['empty'], "空きマス"),
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
        """下部情報エリアを描画"""
        info_y = self.height * self.cell_size + self.margin * 2
        info_rect = pygame.Rect(self.margin, info_y, 
                              self.width * self.cell_size, 
                              self.info_height)
        
        pygame.draw.rect(self.screen, self.colors['text_bg'], info_rect)
        pygame.draw.rect(self.screen, self.colors['grid'], info_rect, 2)
        
        # ステータスメッセージ
        status_text = self._get_status_message(game_state)
        self._draw_text(status_text, info_rect.x + 10, info_rect.y + 10, self.font)
        
        # 操作ヒント
        hint_text = "操作: 矢印キー=移動, R=右回転, L=左回転, ESC=終了"
        self._draw_text(hint_text, info_rect.x + 10, info_rect.y + 40, self.small_font)
        
        # デバッグ情報（デバッグモード時）
        if self.debug_mode:
            debug_text = f"FPS: {self.clock.get_fps():.1f}"
            self._draw_text(debug_text, info_rect.x + 10, info_rect.y + 65, self.small_font)
    
    def _get_status_message(self, game_state: GameState) -> str:
        """状態に応じたメッセージを取得"""
        if game_state.status == GameStatus.WON:
            return "🎉 ゲームクリア！おめでとうございます！"
        elif game_state.status == GameStatus.FAILED:
            return "💀 ゲーム失敗。もう一度挑戦してみましょう。"
        elif game_state.status == GameStatus.TIMEOUT:
            return "⏰ 時間切れです。効率的な移動を心がけましょう。"
        elif game_state.status == GameStatus.ERROR:
            return "❌ エラーが発生しました。"
        else:
            remaining_turns = game_state.max_turns - game_state.turn_count
            return f"🎮 プレイ中... 残りターン: {remaining_turns}"
    
    def _draw_text(self, text: str, x: int, y: int, font: pygame.font.Font, color: Tuple[int, int, int] = None) -> None:
        """テキストを描画"""
        if color is None:
            color = self.colors['text']
        
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def _handle_events(self) -> None:
        """pygame イベントを処理"""
        for event in pygame.event.get():
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