#!/usr/bin/env python3
"""
StageDescriptionRendererの単体テスト
v1.2.4新機能: ステージ説明表示システムのテスト
"""

import pytest
from unittest.mock import Mock, patch
from engine.stage_loader import StageLoader, StageValidationError
from engine.stage_description_renderer import StageDescriptionRenderer
from engine import Stage, Position, Direction


class TestStageDescriptionRenderer:
    """StageDescriptionRendererクラスの基本動作テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.stage_loader = Mock(spec=StageLoader)
        self.renderer = StageDescriptionRenderer(self.stage_loader)
    
    def test_initialization(self):
        """初期化テスト"""
        assert isinstance(self.renderer.stage_loader, Mock)
        assert self.renderer.max_width == 80
    
    def test_display_stage_conditions_invalid_stage_id(self):
        """無効なステージIDでのエラーテスト"""
        with pytest.raises(ValueError, match="stage_idは必須です"):
            self.renderer.display_stage_conditions("")
        
        with pytest.raises(ValueError, match="stage_idは必須です"):
            self.renderer.display_stage_conditions(None)


class TestStageDescriptionWithValidStage:
    """有効なステージデータでの説明表示テスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.stage_loader = Mock(spec=StageLoader)
        self.renderer = StageDescriptionRenderer(self.stage_loader)
        
        # モックステージオブジェクトの作成
        self.mock_stage = Mock()
        self.mock_stage.id = "stage01"
        self.mock_stage.title = "基本移動ステージ"
        self.mock_stage.description = "基本的な移動操作を学ぶステージです。turn_leftとturn_right、moveを使ってゴールを目指しましょう。"
        self.mock_stage.board_size = (5, 5)
        self.mock_stage.player_start = Position(0, 0)
        self.mock_stage.goal_position = Position(4, 4)
        self.mock_stage.allowed_apis = ["turn_left", "turn_right", "move", "see"]
        self.mock_stage.constraints = {"max_turns": 20}
        self.mock_stage.enemies = []
        self.mock_stage.items = []
    
    def test_yaml_description_exists_case(self):
        """YAML description項目が存在する場合の表示テスト"""
        # StageLoaderのモック設定
        self.stage_loader.load_stage.return_value = self.mock_stage
        
        # ステージ説明表示の実行
        result = self.renderer.display_stage_conditions("stage01")
        
        # 基本的な内容の確認
        assert "ステージ情報: 基本移動ステージ (stage01)" in result
        assert "基本的な移動操作を学ぶステージです" in result
        assert "サイズ: 5 x 5" in result
        assert "スタート位置: (0, 0)" in result
        assert "ゴール位置: (4, 4)" in result
        assert "最大ターン数: 20" in result
        assert "使用可能なAPI: turn_left, turn_right, move, see" in result
        
        # ヘッダーとフッターの確認
        assert "📚 ステージ情報:" in result
        assert "🎯 ボード情報:" in result
        assert "⚡ 制約条件:" in result
        assert "🏆 クリア条件:" in result
        assert "💡 ヒント:" in result
        
        # StageLoaderが正しく呼ばれたことを確認
        self.stage_loader.load_stage.assert_called_once_with("stage01")
    
    def test_stage_with_enemies_and_items(self):
        """敵とアイテムが存在するステージの表示テスト"""
        # 敵とアイテムを含むステージの設定
        self.mock_stage.enemies = [
            {"position": [2, 2], "type": "normal"},
            {"position": [3, 1], "type": "large_2x2"}
        ]
        self.mock_stage.items = [
            {"position": [1, 1], "name": "鍵", "type": "key"},
            {"position": [2, 3], "name": "剣", "type": "weapon"}
        ]
        
        self.stage_loader.load_stage.return_value = self.mock_stage
        
        result = self.renderer.display_stage_conditions("stage01")
        
        # 敵情報の確認
        assert "⚔️ 敵情報:" in result
        assert "敵1: normal at (2, 2)" in result
        assert "敵2: large_2x2 at (3, 1)" in result
        
        # アイテム情報の確認
        assert "🎁 アイテム情報:" in result
        assert "鍵 (key) at (1, 1)" in result
        assert "剣 (weapon) at (2, 3)" in result
    
    def test_long_description_wrapping(self):
        """長い説明文の折り返し機能テスト"""
        # 非常に長い説明文を設定
        long_description = "これは" + "非常に" * 30 + "長い説明文です。"
        self.mock_stage.description = long_description
        
        self.stage_loader.load_stage.return_value = self.mock_stage
        
        result = self.renderer.display_stage_conditions("stage01")
        
        # 説明文の主要部分が含まれていることを確認（完全な一致ではなく、部分的な確認）
        assert "これは非常に" in result
        assert "長い説明文です。" in result
        
        # 行が適切に分割されていることを確認（厳密なチェックは難しいので基本的な確認のみ）
        lines = result.split('\n')
        description_section = False
        for line in lines:
            if "📖 ステージ説明:" in line:
                description_section = True
            elif description_section and line.strip() and not line.startswith('   '):
                # 説明セクションの終了
                break
            elif description_section and line.strip():
                # 説明文の行は80文字を大幅に超えないことを確認
                assert len(line) <= 85  # インデントを考慮してゆるい制限


class TestStageDescriptionFallback:
    """フォールバック機能のテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.stage_loader = Mock(spec=StageLoader)
        self.renderer = StageDescriptionRenderer(self.stage_loader)
    
    def test_description_not_exists_fallback(self):
        """description項目が存在しない場合のフォールバック表示テスト"""
        # FileNotFoundErrorを発生させる
        self.stage_loader.load_stage.side_effect = FileNotFoundError("ステージファイルが見つかりません")
        
        result = self.renderer.display_fallback_message("stage01")
        
        # フォールバック表示の内容確認
        assert "📚 ステージ情報: stage01" in result
        assert "⚠️ ステージ説明を読み込めませんでした" in result
        assert "このステージは基本的なローグライク学習ステージです" in result
        assert "利用可能なAPI: turn_left(), turn_right(), move(), see()" in result
        assert "1. プレイヤーをゴール位置まで移動させる" in result
        assert "💡 学習のヒント:" in result
    
    def test_stage_loading_error_fallback(self):
        """ステージ読み込みエラー時のフォールバック動作テスト"""
        # StageValidationErrorを発生させる
        self.stage_loader.load_stage.side_effect = StageValidationError("バリデーションエラー")
        
        result = self.renderer.display_stage_conditions("stage01")
        
        # フォールバック表示になることを確認
        assert "📚 ステージ情報: stage01" in result
        assert "⚠️ ステージ説明を読み込めませんでした" in result
    
    def test_general_exception_fallback(self):
        """一般的な例外発生時のフォールバック動作テスト"""
        # 一般的な例外を発生させる
        self.stage_loader.load_stage.side_effect = Exception("予期しないエラー")
        
        result = self.renderer.display_stage_conditions("stage01")
        
        # フォールバック表示になることを確認
        assert "📚 ステージ情報: stage01" in result
        assert "⚠️ ステージ説明を読み込めませんでした" in result


class TestStageDescriptionReadability:
    """説明文の可読性向上機能のテスト"""
    
    def setup_method(self):
        """各テスト前のセットアップ"""
        self.stage_loader = Mock(spec=StageLoader)
        self.renderer = StageDescriptionRenderer(self.stage_loader)
    
    def test_text_wrapping_function(self):
        """テキスト折り返し機能の単体テスト"""
        # 短いテキスト
        short_text = "短いテキスト"
        result = self.renderer._wrap_text(short_text, 20)
        assert result == ["短いテキスト"]
        
        # 長いテキスト
        long_text = "これは非常に長いテキストで、指定された幅を超えるため折り返しが必要です"
        result = self.renderer._wrap_text(long_text, 20)
        assert len(result) > 1
        for line in result:
            assert len(line) <= 20
        
        # 空のテキスト
        empty_text = ""
        result = self.renderer._wrap_text(empty_text, 20)
        assert result == [""]
        
        # Noneテキスト
        result = self.renderer._wrap_text(None, 20)
        assert result == [""]
    
    def test_format_consistency(self):
        """フォーマット一貫性のテスト"""
        mock_stage = Mock()
        mock_stage.id = "test01"
        mock_stage.title = "テストステージ"
        mock_stage.description = "テスト用の説明"
        mock_stage.board_size = (3, 3)
        mock_stage.player_start = Position(0, 0)
        mock_stage.goal_position = Position(2, 2)
        mock_stage.allowed_apis = ["move"]
        mock_stage.constraints = {"max_turns": 10}
        mock_stage.enemies = []
        mock_stage.items = []
        
        result = self.renderer.format_description_text(mock_stage)
        
        # セクションの順序確認
        sections = [
            "📚 ステージ情報:",
            "📖 ステージ説明:",
            "🎯 ボード情報:",
            "⚡ 制約条件:",
            "🏆 クリア条件:",
            "💡 ヒント:"
        ]
        
        last_index = -1
        for section in sections:
            current_index = result.find(section)
            assert current_index > last_index, f"セクション '{section}' の順序が正しくありません"
            last_index = current_index


class TestStageLoaderIntegration:
    """StageLoaderとの統合動作テスト"""
    
    def test_stage_loader_integration_with_real_stage(self):
        """実際のStageLoaderとの統合動作テスト"""
        # 実際のStageLoaderを使用
        stage_loader = StageLoader("stages")
        renderer = StageDescriptionRenderer(stage_loader)
        
        # stage01が存在することを前提とした統合テスト
        try:
            result = renderer.display_stage_conditions("stage01")
            
            # 基本的な構造が含まれていることを確認
            assert "📚 ステージ情報:" in result
            assert "stage01" in result
            assert "📖 ステージ説明:" in result
            assert "🎯 ボード情報:" in result
            assert "⚡ 制約条件:" in result
            
        except FileNotFoundError:
            # stage01.ymlが存在しない場合はフォールバックが動作することを確認
            result = renderer.display_stage_conditions("stage01")
            assert "⚠️ ステージ説明を読み込めませんでした" in result
    
    def test_get_stage_summary_success(self):
        """ステージサマリー取得の成功ケース"""
        stage_loader = Mock(spec=StageLoader)
        renderer = StageDescriptionRenderer(stage_loader)
        
        mock_stage = Mock()
        mock_stage.id = "stage01"
        mock_stage.title = "基本移動ステージ"
        mock_stage.description = "基本的な移動操作を学ぶステージです"
        mock_stage.board_size = (5, 5)
        mock_stage.allowed_apis = ["move", "turn_left", "turn_right"]
        mock_stage.constraints = {"max_turns": 20}
        mock_stage.enemies = []
        mock_stage.items = []
        
        stage_loader.load_stage.return_value = mock_stage
        
        summary = renderer.get_stage_summary("stage01")
        
        assert summary["stage_id"] == "stage01"
        assert summary["title"] == "基本移動ステージ"
        assert summary["board_size"] == (5, 5)
        assert summary["max_turns"] == 20
        assert summary["allowed_apis"] == ["move", "turn_left", "turn_right"]
        assert summary["has_enemies"] is False
        assert summary["has_items"] is False
        assert summary["status"] == "loaded"
    
    def test_get_stage_summary_error(self):
        """ステージサマリー取得のエラーケース"""
        stage_loader = Mock(spec=StageLoader)
        renderer = StageDescriptionRenderer(stage_loader)
        
        stage_loader.load_stage.side_effect = Exception("読み込みエラー")
        
        summary = renderer.get_stage_summary("stage01")
        
        assert summary["stage_id"] == "stage01"
        assert summary["title"] == "ステージstage01"
        assert summary["description"] == "説明を読み込めませんでした"
        assert summary["board_size"] == (0, 0)
        assert summary["max_turns"] == 100
        assert summary["allowed_apis"] == ["turn_left", "turn_right", "move"]
        assert summary["has_enemies"] is False
        assert summary["has_items"] is False
        assert summary["status"] == "error"