"""
ハイパーパラメータ管理システム
HyperParameterManager - ステージID、学生ID、ログ設定の管理
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class HyperParametersData:
    """ハイパーパラメータデータ"""
    stage_id: str = "stage01"
    student_id: Optional[str] = None
    log_enabled: bool = True
    
    # v1.2.4新機能: 初回確認モード関連フィールド
    initial_confirmation_mode: bool = False  # False=確認モード, True=実行モード
    stage_intro_displayed: Dict[str, bool] = field(default_factory=dict)
    
    def __post_init__(self):
        """バリデーション"""
        if not self.stage_id:
            raise ValueError("ステージIDは必須です")
        if self.student_id is not None and not self.student_id:
            raise ValueError("学生IDが空文字です")
        
        # v1.2.4: 初回確認モード関連フィールドのバリデーション
        if not isinstance(self.initial_confirmation_mode, bool):
            raise ValueError("initial_confirmation_modeはbool型である必要があります")
        if not isinstance(self.stage_intro_displayed, dict):
            raise ValueError("stage_intro_displayedはdict型である必要があります")

class HyperParameterError(Exception):
    """ハイパーパラメータ関連のエラー"""
    pass

class HyperParameterManager:
    """ハイパーパラメータ管理クラス"""
    
    def __init__(self):
        self.data = HyperParametersData()
    
    def validate(self) -> bool:
        """ハイパーパラメータの検証"""
        try:
            if self.data.student_id is None:
                raise HyperParameterError(
                    "❌ 学生IDが設定されていません。\n"
                    "💡 main.py内のハイパーパラメータ設定セクションで学生IDを設定してください。\n"
                    "例: student_id = '123456A'"
                )
            
            # 学生IDの形式チェック（6桁数字 + 英大文字1桁）
            if len(self.data.student_id) != 7:
                raise HyperParameterError(
                    f"❌ 学生ID '{self.data.student_id}' の形式が正しくありません。\n"
                    "💡 正しい形式: 6桁数字 + 英大文字1桁（例: 123456A）"
                )
            
            # 数字部分のチェック
            if not self.data.student_id[:6].isdigit():
                raise HyperParameterError(
                    f"❌ 学生ID '{self.data.student_id}' の最初6桁は数字である必要があります。\n"
                    "💡 正しい形式: 6桁数字 + 英大文字1桁（例: 123456A）"
                )
            
            # 英字部分のチェック
            if not self.data.student_id[6].isupper():
                raise HyperParameterError(
                    f"❌ 学生ID '{self.data.student_id}' の最後1桁は英大文字である必要があります。\n"
                    "💡 正しい形式: 6桁数字 + 英大文字1桁（例: 123456A）"
                )
            
            logger.info(f"✅ ハイパーパラメータ検証成功: stage_id={self.data.stage_id}, student_id={self.data.student_id}")
            return True
            
        except HyperParameterError:
            raise
        except Exception as e:
            raise HyperParameterError(f"ハイパーパラメータ検証中にエラーが発生しました: {e}")
    
    def load_from_config(self, config_module: Any) -> None:
        """config.pyから設定を読み込み"""
        try:
            if hasattr(config_module, 'STUDENT_ID'):
                self.data.student_id = config_module.STUDENT_ID
            
            if hasattr(config_module, 'DEFAULT_STAGE'):
                self.data.stage_id = config_module.DEFAULT_STAGE
            
            if hasattr(config_module, 'ENABLE_LOGGING'):
                self.data.log_enabled = config_module.ENABLE_LOGGING
                
            logger.debug(f"設定ファイルから読み込み完了: {self.data}")
            
        except Exception as e:
            logger.warning(f"設定ファイル読み込み中にエラー: {e}")
            raise HyperParameterError(f"設定ファイルの読み込みに失敗しました: {e}")
    
    def save_to_config(self, config_path: Path) -> None:
        """設定をファイルに保存（将来拡張用）"""
        try:
            # 現在は実装しない（既存のconfig.pyの構造を維持）
            logger.debug("設定保存は現在未実装です")
        except Exception as e:
            raise HyperParameterError(f"設定ファイルの保存に失敗しました: {e}")
    
    def set_stage_id(self, stage_id: str) -> None:
        """ステージIDの設定"""
        if not stage_id:
            raise HyperParameterError("ステージIDは必須です")
        self.data.stage_id = stage_id
        logger.debug(f"ステージID設定: {stage_id}")
    
    def set_student_id(self, student_id: Optional[str]) -> None:
        """学生IDの設定"""
        self.data.student_id = student_id
        logger.debug(f"学生ID設定: {student_id}")
    
    def set_logging_enabled(self, enabled: bool) -> None:
        """ログ機能の有効/無効設定"""
        self.data.log_enabled = enabled
        logger.debug(f"ログ機能設定: {enabled}")
    
    def get_stage_id(self) -> str:
        """ステージIDの取得"""
        return self.data.stage_id
    
    def get_student_id(self) -> Optional[str]:
        """学生IDの取得"""
        return self.data.student_id
    
    def is_logging_enabled(self) -> bool:
        """ログ機能の有効性確認"""
        return self.data.log_enabled
    
    def get_summary(self) -> dict:
        """ハイパーパラメータサマリーの取得"""
        return {
            "stage_id": self.data.stage_id,
            "student_id": self.data.student_id,
            "log_enabled": self.data.log_enabled,
            "validation_status": "未検証"
        }