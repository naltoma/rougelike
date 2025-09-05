"""
セッションログ条件制御システム
ConditionalSessionLogger - 初回確認モードに応じたセッションログ制御
"""

from typing import Optional, Dict, Any
import logging
from .session_log_manager import SessionLogManager

logger = logging.getLogger(__name__)


class ConditionalSessionLogger:
    """セッションログ条件制御クラス
    
    SessionLogManagerと統合し、初回確認モードの状態に応じて
    セッションログの生成・除外を制御する。
    """
    
    def __init__(self, session_log_manager: SessionLogManager):
        """初期化
        
        Args:
            session_log_manager: 既存のセッションログマネージャー
        """
        self.session_log_manager = session_log_manager
        self._confirmation_mode = False  # 内部キャッシュ
        logger.debug("ConditionalSessionLogger初期化完了")
    
    def should_log_session(self, confirmation_mode: bool) -> bool:
        """ログ生成条件判定機能
        
        Args:
            confirmation_mode: True=実行モード, False=確認モード
        
        Returns:
            bool: True=ログ生成, False=ログ除外
        """
        # 確認モード(False)時はログを生成しない
        # 実行モード(True)時は通常通りログを生成
        self._confirmation_mode = confirmation_mode
        
        should_log = confirmation_mode  # True=実行モード時のみログ生成
        
        if should_log:
            logger.debug("実行モード: セッションログ生成を実行")
        else:
            logger.debug("確認モード: セッションログ生成を除外")
        
        return should_log
    
    def conditional_log_start(self, confirmation_mode: bool, **kwargs) -> Optional[Any]:
        """条件付きセッション開始ログ機能
        
        Args:
            confirmation_mode: True=実行モード, False=確認モード
            **kwargs: セッション開始に必要な追加データ
        
        Returns:
            Optional[Any]: ログ開始結果（確認モード時はNone）
        """
        if not self.should_log_session(confirmation_mode):
            logger.info("確認モード: セッション開始ログを除外")
            return None
        
        try:
            # 実行モード時は通常通りログを開始
            additional_data = kwargs.copy()
            additional_data["mode"] = "execution"
            additional_data["confirmation_disabled"] = True
            
            self.session_log_manager.log_session_start(additional_data)
            logger.info("実行モード: セッション開始ログ記録完了")
            
            return {"status": "logged", "mode": "execution"}
            
        except Exception as e:
            logger.error(f"条件付きセッション開始ログ記録中にエラー: {e}")
            return None
    
    def conditional_log_end(self, confirmation_mode: bool, **kwargs) -> Optional[Any]:
        """条件付きセッション終了ログ機能
        
        Args:
            confirmation_mode: True=実行モード, False=確認モード
            **kwargs: セッション終了に必要な追加データ
        
        Returns:
            Optional[Any]: ログ終了結果（確認モード時はNone）
        """
        if not self.should_log_session(confirmation_mode):
            logger.info("確認モード: セッション終了ログを除外")
            return None
        
        try:
            # 実行モード時は通常通りログを終了
            execution_summary = kwargs.copy()
            execution_summary["mode"] = "execution"
            execution_summary["confirmation_disabled"] = True
            
            self.session_log_manager.log_session_complete(execution_summary)
            logger.info("実行モード: セッション終了ログ記録完了")
            
            return {"status": "logged", "mode": "execution"}
            
        except Exception as e:
            logger.error(f"条件付きセッション終了ログ記録中にエラー: {e}")
            return None
    
    def conditional_log_event(self, confirmation_mode: bool, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """条件付きイベントログ機能
        
        Args:
            confirmation_mode: True=実行モード, False=確認モード
            event_type: イベントタイプ
            event_data: イベントデータ
        
        Returns:
            Optional[Any]: ログ結果（確認モード時はNone）
        """
        if not self.should_log_session(confirmation_mode):
            logger.debug(f"確認モード: イベントログを除外 ({event_type})")
            return None
        
        try:
            # 実行モード時は通常通りイベントログを記録
            if self.session_log_manager.session_logger:
                enhanced_data = event_data.copy() if event_data else {}
                enhanced_data["mode"] = "execution"
                enhanced_data["confirmation_disabled"] = True
                
                self.session_log_manager.session_logger.log_event(event_type, enhanced_data)
                logger.debug(f"実行モード: イベントログ記録完了 ({event_type})")
                
                return {"status": "logged", "event_type": event_type}
            else:
                logger.warning("SessionLoggerが初期化されていません")
                return None
                
        except Exception as e:
            logger.error(f"条件付きイベントログ記録中にエラー: {e}")
            return None
    
    def get_current_mode_status(self) -> Dict[str, Any]:
        """現在のモード状態の取得
        
        Returns:
            Dict[str, Any]: モード状態情報
        """
        return {
            "confirmation_mode": self._confirmation_mode,
            "logging_enabled": self.should_log_session(self._confirmation_mode),
            "mode_description": "実行モード" if self._confirmation_mode else "確認モード",
            "log_behavior": "生成" if self.should_log_session(self._confirmation_mode) else "除外"
        }
    
    def is_logging_active(self) -> bool:
        """現在のモードでログが有効かどうか確認
        
        Returns:
            bool: True=ログ有効, False=ログ無効
        """
        return self.should_log_session(self._confirmation_mode)
    
    def enable_debug_logging(self, stage_id: str, student_id: str = "DEBUG_USER") -> bool:
        """デバッグ用の強制ログ有効化
        
        Args:
            stage_id: ステージID
            student_id: 学生ID（デフォルト: DEBUG_USER）
        
        Returns:
            bool: 有効化成功フラグ
        """
        try:
            # 確認モードを無視してログを強制有効化
            result = self.session_log_manager.enable_default_logging(
                student_id=student_id,
                stage_id=stage_id,
                force_enable=True
            )
            
            if result.success:
                logger.info(f"デバッグモード: ログ強制有効化完了 ({stage_id})")
                return True
            else:
                logger.error(f"デバッグモード: ログ強制有効化失敗 - {result.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"デバッグログ有効化中にエラー: {e}")
            return False
    
    def get_log_exclusion_summary(self) -> Dict[str, Any]:
        """ログ除外機能のサマリー情報
        
        Returns:
            Dict[str, Any]: ログ除外状況のサマリー
        """
        try:
            current_status = self.get_current_mode_status()
            session_logger_active = (
                self.session_log_manager.session_logger is not None and
                self.session_log_manager.is_logging_enabled()
            )
            
            return {
                "confirmation_mode": current_status["confirmation_mode"],
                "logging_will_be_excluded": not current_status["logging_enabled"],
                "session_logger_initialized": session_logger_active,
                "exclusion_reason": "確認モードのため学習データ記録を除外" if not current_status["logging_enabled"] else None,
                "recommendation": (
                    "実行モードに切り替えるとセッションログが記録されます" 
                    if not current_status["logging_enabled"] 
                    else "現在実行モードでセッションログが記録されています"
                )
            }
            
        except Exception as e:
            logger.error(f"ログ除外サマリー取得中にエラー: {e}")
            return {
                "confirmation_mode": self._confirmation_mode,
                "logging_will_be_excluded": True,
                "session_logger_initialized": False,
                "exclusion_reason": f"エラーのため状態確認不可: {e}",
                "recommendation": "システム管理者にお問い合わせください"
            }
    
    def simulate_execution_mode_logging(self, stage_id: str, student_id: str = "SIMULATION_USER") -> Dict[str, Any]:
        """実行モードでのログ動作をシミュレート
        
        Args:
            stage_id: ステージID
            student_id: 学生ID
        
        Returns:
            Dict[str, Any]: シミュレーション結果
        """
        try:
            # 実行モード（True）でのログ動作をテスト
            simulation_mode = True
            
            # ログ生成条件をチェック
            would_log = self.should_log_session(simulation_mode)
            
            if would_log:
                # 実際にはログを生成せず、生成される内容を予測
                log_prediction = {
                    "session_would_start": True,
                    "events_would_be_recorded": True,
                    "action_count_would_be_tracked": True,
                    "session_would_complete": True,
                    "file_would_be_created": f"data/sessions/{stage_id}/[timestamp]_{student_id}.json"
                }
            else:
                log_prediction = {
                    "session_would_start": False,
                    "events_would_be_recorded": False,
                    "action_count_would_be_tracked": False,
                    "session_would_complete": False,
                    "file_would_be_created": None
                }
            
            return {
                "simulation_mode": "execution",
                "would_generate_logs": would_log,
                "predicted_behavior": log_prediction,
                "recommendation": "実行モードに切り替えてセッションログを生成してください" if would_log else "確認モードではログは生成されません"
            }
            
        except Exception as e:
            logger.error(f"実行モードシミュレーション中にエラー: {e}")
            return {
                "simulation_mode": "execution",
                "would_generate_logs": False,
                "predicted_behavior": {},
                "error": str(e),
                "recommendation": "システム管理者にお問い合わせください"
            }
    
    def get_session_log_manager(self) -> SessionLogManager:
        """SessionLogManagerインスタンスの取得
        
        Returns:
            SessionLogManager: 内部で使用しているSessionLogManagerインスタンス
        """
        return self.session_log_manager