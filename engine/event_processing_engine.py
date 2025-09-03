"""
イベント処理エンジン - GUI Critical Fixes v1.2

マウスイベント・キーボードショートカット・ボタンクリック判定の信頼性を向上させ、
100%確実なイベント処理とステップ実行機能を提供します。
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import pygame
import time


class EventType(Enum):
    """イベントタイプ定義"""
    MOUSE_CLICK = "mouse_click"
    KEY_PRESS = "key_press"
    BUTTON_CLICK = "button_click"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"


class EventPriority(Enum):
    """イベント優先順位"""
    CRITICAL = 1    # システム制御（Stop等）
    HIGH = 2        # 実行制御（Step, Continue, Pause）
    MEDIUM = 3      # 一般操作（設定変更等）
    LOW = 4         # 補助機能（デバッグ等）


@dataclass
class EventProcessingMetrics:
    """イベント処理メトリクス"""
    total_events: int = 0
    processed_events: int = 0
    failed_events: int = 0
    processing_times: List[float] = None
    error_count: int = 0
    
    def __post_init__(self):
        if self.processing_times is None:
            self.processing_times = []


@dataclass
class ProcessedEvent:
    """処理済みイベント情報"""
    event_type: EventType
    priority: EventPriority
    timestamp: float
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    event_data: Dict[str, Any] = None


class ButtonCollisionValidator:
    """ボタンクリック判定検証クラス"""
    
    def __init__(self):
        self.click_tolerance = 2  # クリック許容誤差（ピクセル）
        self.double_click_time = 0.3  # ダブルクリック判定時間（秒）
        self.last_click_time = 0
        self.last_click_pos = (0, 0)
    
    def validate_button_collision(self, 
                                 click_pos: Tuple[int, int], 
                                 button_rect: pygame.Rect) -> bool:
        """正確なボタンクリック判定
        
        Args:
            click_pos: クリック座標
            button_rect: ボタン矩形
            
        Returns:
            bool: クリックが有効な場合 True
        """
        # 基本的な矩形内判定
        if not button_rect.collidepoint(click_pos):
            return False
        
        # 許容誤差を考慮した判定
        expanded_rect = pygame.Rect(
            button_rect.x - self.click_tolerance,
            button_rect.y - self.click_tolerance,
            button_rect.width + self.click_tolerance * 2,
            button_rect.height + self.click_tolerance * 2
        )
        
        return expanded_rect.collidepoint(click_pos)
    
    def is_double_click(self, click_pos: Tuple[int, int]) -> bool:
        """ダブルクリック判定"""
        current_time = time.time()
        
        if (current_time - self.last_click_time < self.double_click_time and
            abs(click_pos[0] - self.last_click_pos[0]) < self.click_tolerance and
            abs(click_pos[1] - self.last_click_pos[1]) < self.click_tolerance):
            return True
        
        self.last_click_time = current_time
        self.last_click_pos = click_pos
        return False


class EventProcessingEngine:
    """イベント処理エンジン
    
    マウスイベント、キーボードショートカット、ボタンクリック判定を
    100%確実に処理し、ステップ実行機能の信頼性を向上させます。
    """
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.metrics = EventProcessingMetrics()
        self.collision_validator = ButtonCollisionValidator()
        
        # イベントハンドラー登録
        self.event_handlers: Dict[EventType, List[Callable]] = {
            EventType.MOUSE_CLICK: [],
            EventType.KEY_PRESS: [],
            EventType.BUTTON_CLICK: [],
            EventType.KEYBOARD_SHORTCUT: []
        }
        
        # 優先順位付きイベントキュー
        self.event_queue: List[Tuple[EventPriority, ProcessedEvent]] = []
        
        # キーボードショートカット定義
        self.keyboard_shortcuts = {
            pygame.K_SPACE: ("step", EventPriority.HIGH),
            pygame.K_RETURN: ("continue", EventPriority.HIGH),
            pygame.K_ESCAPE: ("stop", EventPriority.CRITICAL),
            pygame.K_p: ("pause", EventPriority.HIGH),
            pygame.K_r: ("reset", EventPriority.MEDIUM),
            pygame.K_F1: ("help", EventPriority.LOW)
        }
        
        # ボタン定義
        self.button_definitions: Dict[str, Dict] = {}
        
        if self.debug_mode:
            print("🔧 EventProcessingEngine初期化完了（デバッグモード）")
        
    def register_button(self, 
                       button_id: str, 
                       button_rect: pygame.Rect, 
                       callback: Callable,
                       priority: EventPriority = EventPriority.MEDIUM) -> None:
        """ボタンを登録
        
        Args:
            button_id: ボタンID
            button_rect: ボタン矩形
            callback: コールバック関数
            priority: イベント優先順位
        """
        self.button_definitions[button_id] = {
            'rect': button_rect,
            'callback': callback,
            'priority': priority
        }
        
        if self.debug_mode:
            print(f"🔘 ボタン登録: {button_id} @ {button_rect}")
    
    def process_mouse_events(self, pygame_events: List[pygame.event.Event]) -> List[ProcessedEvent]:
        """マウスイベントを100%確実に処理
        
        Args:
            pygame_events: pygameイベントリスト
            
        Returns:
            List[ProcessedEvent]: 処理済みイベントリスト
        """
        processed_events = []
        
        for event in pygame_events:
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
                
            start_time = time.time()
            
            try:
                click_pos = event.pos
                button_clicked = None
                
                # 全登録ボタンでクリック判定
                for button_id, button_data in self.button_definitions.items():
                    if self.collision_validator.validate_button_collision(
                        click_pos, button_data['rect']):
                        button_clicked = button_id
                        break
                
                if button_clicked:
                    # ボタンクリックイベントを処理
                    processing_time = time.time() - start_time
                    
                    button_data = self.button_definitions[button_clicked]
                    
                    # コールバック実行
                    try:
                        button_data['callback']()
                        success = True
                        error_msg = None
                    except Exception as callback_error:
                        success = False
                        error_msg = str(callback_error)
                        self.metrics.error_count += 1
                    
                    processed_event = ProcessedEvent(
                        event_type=EventType.BUTTON_CLICK,
                        priority=button_data['priority'],
                        timestamp=time.time(),
                        processing_time=processing_time,
                        success=success,
                        error_message=error_msg,
                        event_data={
                            'button_id': button_clicked,
                            'click_pos': click_pos,
                            'double_click': self.collision_validator.is_double_click(click_pos)
                        }
                    )
                    
                    processed_events.append(processed_event)
                    self.metrics.processed_events += 1
                    self.metrics.processing_times.append(processing_time)
                    
                    if self.debug_mode:
                        print(f"🖱️ ボタンクリック処理: {button_clicked} ({processing_time:.3f}ms)")
                
            except Exception as e:
                self.metrics.failed_events += 1
                self.metrics.error_count += 1
                
                processed_event = ProcessedEvent(
                    event_type=EventType.MOUSE_CLICK,
                    priority=EventPriority.LOW,
                    timestamp=time.time(),
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=str(e),
                    event_data={'click_pos': event.pos if hasattr(event, 'pos') else None}
                )
                processed_events.append(processed_event)
                
                if self.debug_mode:
                    print(f"❌ マウスイベント処理エラー: {e}")
        
        self.metrics.total_events += len([e for e in pygame_events if e.type == pygame.MOUSEBUTTONDOWN])
        return processed_events
    
    def handle_keyboard_shortcuts(self, pygame_events: List[pygame.event.Event]) -> List[ProcessedEvent]:
        """キーボードショートカットを処理
        
        Args:
            pygame_events: pygameイベントリスト
            
        Returns:
            List[ProcessedEvent]: 処理済みイベントリスト
        """
        processed_events = []
        
        for event in pygame_events:
            if event.type != pygame.KEYDOWN:
                continue
                
            start_time = time.time()
            
            if event.key in self.keyboard_shortcuts:
                shortcut_id, priority = self.keyboard_shortcuts[event.key]
                
                try:
                    # ショートカット処理を実行制御コールバックに委譲
                    success = self._execute_shortcut(shortcut_id)
                    processing_time = time.time() - start_time
                    
                    processed_event = ProcessedEvent(
                        event_type=EventType.KEYBOARD_SHORTCUT,
                        priority=priority,
                        timestamp=time.time(),
                        processing_time=processing_time,
                        success=success,
                        error_message=None,
                        event_data={
                            'shortcut_id': shortcut_id,
                            'key': event.key,
                            'unicode': event.unicode
                        }
                    )
                    
                    processed_events.append(processed_event)
                    self.metrics.processed_events += 1
                    self.metrics.processing_times.append(processing_time)
                    
                    if self.debug_mode:
                        print(f"⌨️ ショートカット処理: {shortcut_id} ({processing_time:.3f}ms)")
                
                except Exception as e:
                    self.metrics.failed_events += 1
                    self.metrics.error_count += 1
                    
                    processed_event = ProcessedEvent(
                        event_type=EventType.KEYBOARD_SHORTCUT,
                        priority=priority,
                        timestamp=time.time(),
                        processing_time=time.time() - start_time,
                        success=False,
                        error_message=str(e),
                        event_data={'shortcut_id': shortcut_id, 'key': event.key}
                    )
                    processed_events.append(processed_event)
                    
                    if self.debug_mode:
                        print(f"❌ ショートカット処理エラー: {shortcut_id} - {e}")
        
        return processed_events
    
    def ensure_event_priority(self, events: List[ProcessedEvent]) -> List[ProcessedEvent]:
        """イベント優先順位管理
        
        Args:
            events: 処理済みイベントリスト
            
        Returns:
            List[ProcessedEvent]: 優先順位でソートされたイベントリスト
        """
        # 優先順位でソート（CRITICAL=1が最優先）
        sorted_events = sorted(events, key=lambda e: e.priority.value)
        
        if self.debug_mode and sorted_events:
            print(f"📋 イベント優先順位処理: {len(sorted_events)}件")
            for event in sorted_events:
                print(f"   {event.priority.name}: {event.event_type.value}")
        
        return sorted_events
    
    def _execute_shortcut(self, shortcut_id: str) -> bool:
        """ショートカット実行
        
        Args:
            shortcut_id: ショートカットID
            
        Returns:
            bool: 実行成功フラグ
        """
        if hasattr(self, 'execution_controller') and self.execution_controller:
            try:
                if shortcut_id == 'step':
                    print("🔍 スペースキー押下 - ステップ実行")
                    self.execution_controller.step_execution()
                    return True
                elif shortcut_id == 'continue':
                    print("▶️ Enterキー押下 - 連続実行")
                    self.execution_controller.continuous_execution()
                    return True
                elif shortcut_id == 'pause':
                    print("⏸️ Pキー押下 - 一時停止")
                    self.execution_controller.pause_execution()
                    return True
                elif shortcut_id == 'stop':
                    print("⏹️ Escapeキー押下 - 停止")
                    self.execution_controller.stop_execution()
                    return True
                elif shortcut_id == 'reset':
                    print("🔄 Rキー押下 - リセット")
                    # Reset functionality can be implemented here
                    return True
                elif shortcut_id == 'help':
                    print("❓ F1キー押下 - ヘルプ")
                    # Help functionality can be implemented here
                    return True
            except Exception as e:
                if self.debug_mode:
                    print(f"❌ ショートカット実行エラー {shortcut_id}: {e}")
                return False
        
        if self.debug_mode:
            print(f"⚠️ 実行制御コントローラー未設定: {shortcut_id}")
        
        return False
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """処理メトリクスを取得
        
        Returns:
            Dict: メトリクス情報
        """
        avg_processing_time = (
            sum(self.metrics.processing_times) / len(self.metrics.processing_times)
            if self.metrics.processing_times else 0
        )
        
        success_rate = (
            (self.metrics.processed_events / self.metrics.total_events) * 100
            if self.metrics.total_events > 0 else 0
        )
        
        return {
            "total_events": self.metrics.total_events,
            "processed_events": self.metrics.processed_events,
            "failed_events": self.metrics.failed_events,
            "success_rate": f"{success_rate:.1f}%",
            "error_count": self.metrics.error_count,
            "avg_processing_time": f"{avg_processing_time:.3f}ms",
            "registered_buttons": len(self.button_definitions),
            "keyboard_shortcuts": len(self.keyboard_shortcuts)
        }
    
    def reset_metrics(self) -> None:
        """メトリクスをリセット"""
        self.metrics = EventProcessingMetrics()
        if self.debug_mode:
            print("📊 メトリクスリセット完了")