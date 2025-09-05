"""
ステージ説明表示例外クラス
v1.2.4新機能: ステージ説明表示システムのエラーハンドリング
"""

from typing import Optional, List, Dict, Any
from pathlib import Path


class StageDescriptionError(Exception):
    """ステージ説明表示関連エラー（基底クラス）"""
    
    def __init__(self, message: str, stage_id: Optional[str] = None, file_path: Optional[Path] = None):
        super().__init__(message)
        self.stage_id = stage_id
        self.file_path = file_path
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        return [
            "ステージファイル（YAML）の存在と形式を確認してください",
            "StageLoaderが正しく初期化されているか確認してください",
            "フォールバック表示を使用して続行することも可能です"
        ]


class StageFileNotFoundError(StageDescriptionError):
    """ステージファイル未発見エラー"""
    
    def __init__(self, message: str, stage_id: str, expected_path: Optional[Path] = None):
        super().__init__(message, stage_id=stage_id, file_path=expected_path)
        self.expected_path = expected_path
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            f"ステージファイル '{self.stage_id}.yml' が存在するか確認してください",
            "stages/ ディレクトリにファイルが配置されているか確認してください",
            "ファイル名のスペルミス（大文字小文字含む）がないか確認してください"
        ]
        
        if self.expected_path:
            suggestions.append(f"期待されるパス: {self.expected_path}")
        
        return suggestions


class StageContentParsingError(StageDescriptionError):
    """ステージ内容解析エラー"""
    
    def __init__(self, message: str, stage_id: str, parsing_error: Optional[str] = None, line_number: Optional[int] = None):
        super().__init__(message, stage_id=stage_id)
        self.parsing_error = parsing_error
        self.line_number = line_number
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "YAMLファイルの構文が正しいか確認してください",
            "必須フィールド（id, title, description等）が存在するか確認してください",
            "インデントが正しく設定されているか確認してください"
        ]
        
        if self.parsing_error:
            suggestions.append(f"解析エラー詳細: {self.parsing_error}")
        
        if self.line_number:
            suggestions.append(f"エラー行番号: {self.line_number}")
        
        return suggestions


class StageDescriptionFormattingError(StageDescriptionError):
    """ステージ説明フォーマットエラー"""
    
    def __init__(self, message: str, stage_id: str, formatting_issue: Optional[str] = None, max_width: Optional[int] = None):
        super().__init__(message, stage_id=stage_id)
        self.formatting_issue = formatting_issue
        self.max_width = max_width
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "説明文の長さが制限を超えていないか確認してください",
            "特殊文字や改行文字が適切に処理されているか確認してください",
            "テキスト折り返し機能が正常に動作しているか確認してください"
        ]
        
        if self.max_width:
            suggestions.append(f"最大幅制限: {self.max_width}文字")
        
        if self.formatting_issue:
            suggestions.append(f"フォーマット問題: {self.formatting_issue}")
        
        return suggestions


class StageDescriptionRenderingError(StageDescriptionError):
    """ステージ説明レンダリングエラー"""
    
    def __init__(self, message: str, stage_id: str, template_section: Optional[str] = None, render_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, stage_id=stage_id)
        self.template_section = template_section
        self.render_data = render_data or {}
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "ステージデータが完全で有効な形式か確認してください",
            "レンダリングに必要な全フィールドが存在するか確認してください",
            "フォールバック表示機能を使用してください"
        ]
        
        if self.template_section:
            suggestions.append(f"問題のセクション: {self.template_section}")
        
        if self.render_data:
            missing_keys = []
            for key, value in self.render_data.items():
                if value is None or value == "":
                    missing_keys.append(key)
            if missing_keys:
                suggestions.append(f"不足しているデータ: {', '.join(missing_keys)}")
        
        return suggestions


class StageLoaderIntegrationError(StageDescriptionError):
    """StageLoader統合エラー"""
    
    def __init__(self, message: str, stage_id: str, loader_error: Optional[str] = None, stage_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, stage_id=stage_id)
        self.loader_error = loader_error
        self.stage_data = stage_data or {}
    
    def get_recovery_suggestions(self) -> List[str]:
        """回復方法の提案"""
        suggestions = [
            "StageLoaderが正しく初期化されているか確認してください",
            "ステージファイルがStageLoaderの要求する形式に準拠しているか確認してください",
            "StageLoaderのvalidation機能を実行して問題を特定してください"
        ]
        
        if self.loader_error:
            suggestions.append(f"ローダーエラー: {self.loader_error}")
        
        if self.stage_data:
            suggestions.append(f"取得されたデータ: {list(self.stage_data.keys())}")
        
        return suggestions


def format_stage_description_error(error: StageDescriptionError, include_suggestions: bool = True) -> str:
    """ステージ説明エラーメッセージのフォーマット
    
    Args:
        error: ステージ説明エラーインスタンス
        include_suggestions: 回復提案を含めるかどうか
    
    Returns:
        str: フォーマット済みエラーメッセージ
    """
    lines = []
    
    # エラータイプとメッセージ
    error_type = error.__class__.__name__
    lines.append(f"❌ {error_type}: {str(error)}")
    
    # 基本情報
    if error.stage_id:
        lines.append(f"   ステージ: {error.stage_id}")
    
    if error.file_path:
        lines.append(f"   ファイルパス: {error.file_path}")
    
    # 特定のエラー情報
    if isinstance(error, StageFileNotFoundError):
        if error.expected_path:
            lines.append(f"   期待されるパス: {error.expected_path}")
    
    elif isinstance(error, StageContentParsingError):
        if error.parsing_error:
            lines.append(f"   解析エラー: {error.parsing_error}")
        if error.line_number:
            lines.append(f"   行番号: {error.line_number}")
    
    elif isinstance(error, StageDescriptionFormattingError):
        if error.max_width:
            lines.append(f"   最大幅: {error.max_width}文字")
        if error.formatting_issue:
            lines.append(f"   フォーマット問題: {error.formatting_issue}")
    
    elif isinstance(error, StageDescriptionRenderingError):
        if error.template_section:
            lines.append(f"   問題のセクション: {error.template_section}")
        if error.render_data:
            lines.append(f"   レンダーデータ: {list(error.render_data.keys())}")
    
    elif isinstance(error, StageLoaderIntegrationError):
        if error.loader_error:
            lines.append(f"   ローダーエラー: {error.loader_error}")
        if error.stage_data:
            lines.append(f"   ステージデータ: {list(error.stage_data.keys())}")
    
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
    "StageDescriptionError",
    "StageFileNotFoundError",
    "StageContentParsingError", 
    "StageDescriptionFormattingError",
    "StageDescriptionRenderingError",
    "StageLoaderIntegrationError",
    "format_stage_description_error"
]