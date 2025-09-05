"""
初回確認モード例外クラス
v1.2.4新機能: 初回確認モード関連のエラーハンドリング
"""

from typing import Optional, List


class InitialConfirmationModeError(Exception):
    """初回確認モード関連エラー（基底クラス）"""
    
    def __init__(self, message: str, stage_id: Optional[str] = None, student_id: Optional[str] = None):
        super().__init__(message)
        self.stage_id = stage_id
        self.student_id = student_id
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        return [
            "フラグマネージャーの設定を確認してください",
            "ハイパーパラメータマネージャーが正しく初期化されているか確認してください",
            "ステージIDと学生IDが正しく設定されているか確認してください"
        ]


class ConfirmationModeStateError(InitialConfirmationModeError):
    """確認モード状態エラー"""
    
    def __init__(self, message: str, current_state: Optional[bool] = None, expected_state: Optional[bool] = None):
        super().__init__(message)
        self.current_state = current_state
        self.expected_state = expected_state
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "confirmation_flag_manager.set_confirmation_mode() でモードを設定してください",
            "ハイパーパラメータの initial_confirmation_mode 設定を確認してください"
        ]
        
        if self.current_state is not None and self.expected_state is not None:
            expected_mode = "実行モード" if self.expected_state else "確認モード"
            suggestions.append(f"期待されるモード: {expected_mode}")
        
        return suggestions


class StageIntroDisplayError(InitialConfirmationModeError):
    """ステージ説明表示エラー"""
    
    def __init__(self, message: str, stage_id: Optional[str] = None, render_error: Optional[str] = None):
        super().__init__(message, stage_id=stage_id)
        self.render_error = render_error
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "ステージファイル（YAML）が存在し、正しい形式かを確認してください",
            "StageLoaderが正しく初期化されているか確認してください",
            "フォールバック表示を使用して続行することも可能です"
        ]
        
        if self.stage_id:
            suggestions.append(f"対象ステージ: {self.stage_id}")
        
        if self.render_error:
            suggestions.append(f"レンダリングエラー: {self.render_error}")
        
        return suggestions


class SessionLogExclusionError(InitialConfirmationModeError):
    """セッションログ除外処理エラー"""
    
    def __init__(self, message: str, confirmation_mode: Optional[bool] = None, log_operation: Optional[str] = None):
        super().__init__(message)
        self.confirmation_mode = confirmation_mode
        self.log_operation = log_operation
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "ConditionalSessionLoggerが正しく初期化されているか確認してください",
            "SessionLogManagerとの統合が正常に動作しているか確認してください",
            "ログ除外が意図的な動作かを確認してください"
        ]
        
        if self.confirmation_mode is not None:
            mode_desc = "実行モード" if self.confirmation_mode else "確認モード"
            suggestions.append(f"現在のモード: {mode_desc}")
        
        if self.log_operation:
            suggestions.append(f"失敗した操作: {self.log_operation}")
        
        return suggestions


class InitialExecutionDetectionError(InitialConfirmationModeError):
    """初回実行判定エラー"""
    
    def __init__(self, message: str, stage_id: Optional[str] = None, detection_data: Optional[dict] = None):
        super().__init__(message, stage_id=stage_id)
        self.detection_data = detection_data or {}
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "ステージ説明表示履歴データが破損している可能性があります",
            "confirmation_flag_manager.reset_stage_intro_history() でリセットを試してください",
            "ハイパーパラメータマネージャーのデータ整合性を確認してください"
        ]
        
        if self.stage_id:
            suggestions.append(f"問題のステージ: {self.stage_id}")
        
        if self.detection_data:
            suggestions.append(f"判定データ: {self.detection_data}")
        
        return suggestions


def format_error_message(error: InitialConfirmationModeError, include_suggestions: bool = True) -> str:
    """初回確認モードエラーメッセージのフォーマット
    
    Args:
        error: 初回確認モードエラーインスタンス
        include_suggestions: 回復提案を含めるかどうか
    
    Returns:
        str: フォーマット済みエラーメッセージ
    """
    lines = []
    
    # エラータイプとメッセージ
    error_type = error.__class__.__name__
    lines.append(f"❌ {error_type}: {str(error)}")
    
    # コンテキスト情報
    if hasattr(error, 'stage_id') and error.stage_id:
        lines.append(f"   ステージ: {error.stage_id}")
    
    if hasattr(error, 'student_id') and error.student_id:
        lines.append(f"   学生ID: {error.student_id}")
    
    # 特定のエラー情報
    if isinstance(error, ConfirmationModeStateError):
        if error.current_state is not None:
            current_desc = "実行モード" if error.current_state else "確認モード"
            lines.append(f"   現在の状態: {current_desc}")
        if error.expected_state is not None:
            expected_desc = "実行モード" if error.expected_state else "確認モード"
            lines.append(f"   期待する状態: {expected_desc}")
    
    elif isinstance(error, StageIntroDisplayError):
        if error.render_error:
            lines.append(f"   レンダリングエラー: {error.render_error}")
    
    elif isinstance(error, SessionLogExclusionError):
        if error.confirmation_mode is not None:
            mode_desc = "実行モード" if error.confirmation_mode else "確認モード"
            lines.append(f"   確認モード状態: {mode_desc}")
        if error.log_operation:
            lines.append(f"   失敗した操作: {error.log_operation}")
    
    elif isinstance(error, InitialExecutionDetectionError):
        if error.detection_data:
            lines.append(f"   判定データ: {error.detection_data}")
    
    # 回復提案
    if include_suggestions:
        suggestions = error.get_recovery_suggestions()
        if suggestions:
            lines.append("\n💡 回復方法:")
            for suggestion in suggestions:
                lines.append(f"   • {suggestion}")
    
    return "\n".join(lines)


# エクスポート用
__all__ = [
    "InitialConfirmationModeError",
    "ConfirmationModeStateError", 
    "StageIntroDisplayError",
    "SessionLogExclusionError",
    "InitialExecutionDetectionError",
    "format_error_message"
]