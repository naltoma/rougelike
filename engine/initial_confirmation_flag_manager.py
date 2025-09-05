"""
初回確認モードフラグ管理システム
InitialConfirmationFlagManager - 初回確認モード制御とハイパーパラメータ統合
"""

from typing import Optional
import logging
from .hyperparameter_manager import HyperParameterManager

logger = logging.getLogger(__name__)


class InitialConfirmationFlagManager:
    """初回確認モードフラグ管理クラス
    
    既存のHyperParameterManagerと統合し、初回確認モードの
    フラグ管理機能を提供する。
    """
    
    def __init__(self, hyperparameter_manager: HyperParameterManager):
        """初期化
        
        Args:
            hyperparameter_manager: 既存のハイパーパラメータマネージャー
        """
        self.hyperparameter_manager = hyperparameter_manager
        logger.debug("InitialConfirmationFlagManager初期化完了")
    
    def get_confirmation_mode(self) -> bool:
        """初回確認モードフラグの取得
        
        Returns:
            bool: True=実行モード, False=確認モード
        """
        return self.hyperparameter_manager.data.initial_confirmation_mode
    
    def set_confirmation_mode(self, enabled: bool) -> None:
        """初回確認モードフラグの設定
        
        Args:
            enabled: True=実行モード, False=確認モード
        """
        if not isinstance(enabled, bool):
            raise ValueError("confirmation_modeはbool型である必要があります")
        
        self.hyperparameter_manager.data.initial_confirmation_mode = enabled
        logger.info(f"初回確認モードフラグ更新: {'実行モード' if enabled else '確認モード'}")
    
    def is_first_execution(self, stage_id: str, student_id: Optional[str] = None) -> bool:
        """指定ステージの初回実行判定
        
        Args:
            stage_id: 判定対象のステージID
            student_id: 学生ID（オプション）
        
        Returns:
            bool: True=初回実行, False=再実行
        """
        if not stage_id:
            raise ValueError("stage_idは必須です")
        
        # ステージの説明表示履歴を確認
        stage_intro_displayed = self.hyperparameter_manager.data.stage_intro_displayed
        
        # 当該ステージの表示履歴がない場合は初回実行
        if stage_id not in stage_intro_displayed:
            logger.debug(f"初回実行判定: {stage_id} - 初回実行")
            return True
        
        # 表示履歴がある場合は再実行
        logger.debug(f"初回実行判定: {stage_id} - 再実行")
        return False
    
    def mark_stage_intro_displayed(self, stage_id: str) -> None:
        """ステージ説明表示済みマークの設定
        
        Args:
            stage_id: 表示済みとしてマークするステージID
        """
        if not stage_id:
            raise ValueError("stage_idは必須です")
        
        self.hyperparameter_manager.data.stage_intro_displayed[stage_id] = True
        logger.info(f"ステージ説明表示済みマーク設定: {stage_id}")
    
    def reset_stage_intro_history(self) -> None:
        """ステージ説明表示履歴のリセット
        
        開発・テスト用途での履歴クリア機能
        """
        self.hyperparameter_manager.data.stage_intro_displayed.clear()
        logger.info("ステージ説明表示履歴をリセットしました")
    
    def get_intro_displayed_stages(self) -> list[str]:
        """説明表示済みステージ一覧の取得
        
        Returns:
            list[str]: 説明表示済みのステージID一覧
        """
        return [
            stage_id for stage_id, displayed 
            in self.hyperparameter_manager.data.stage_intro_displayed.items() 
            if displayed
        ]