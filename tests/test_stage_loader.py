#!/usr/bin/env python3
"""
StageLoaderクラスのテスト
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.append('..')

from engine.stage_loader import StageLoader, StageValidationError
from engine import Position, Direction, Stage


def test_load_basic_stage():
    """基本ステージ読み込みテスト"""
    print("📂 基本ステージ読み込みテスト...")
    
    loader = StageLoader("stages")
    
    # Stage01の読み込み
    stage = loader.load_stage("stage01")
    
    assert stage.id == "stage01"
    assert stage.title == "基本移動ステージ"
    assert stage.board_size == (5, 5)
    assert stage.player_start == Position(0, 0)
    assert stage.player_direction == Direction.NORTH
    assert stage.goal_position == Position(4, 4)
    assert len(stage.walls) == 1  # グリッドに1つの壁がある
    assert Position(2, 2) in stage.walls
    assert stage.allowed_apis == ["turn_left", "turn_right", "move", "see"]
    assert stage.constraints["max_turns"] == 20
    
    print("✅ Stage01読み込み成功")
    
    # Stage02の読み込み
    stage2 = loader.load_stage("stage02")
    
    assert stage2.id == "stage02"
    assert stage2.board_size == (7, 5)
    assert stage2.player_start == Position(1, 1)
    assert stage2.player_direction == Direction.EAST
    assert stage2.goal_position == Position(5, 3)
    assert len(stage2.walls) > 5  # 迷路なので壁が多い
    
    print("✅ Stage02読み込み成功")
    
    # Stage03の読み込み（移動禁止マス含む）
    stage3 = loader.load_stage("stage03")
    
    assert stage3.id == "stage03"
    assert stage3.board_size == (6, 6)
    assert len(stage3.forbidden_cells) == 1  # Xマークが1つ
    assert Position(2, 2) in stage3.forbidden_cells
    
    print("✅ Stage03読み込み成功")


def test_stage_validation():
    """ステージバリデーションテスト"""
    print("✅ ステージバリデーションテスト...")
    
    # テンポラリディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    loader = StageLoader(temp_dir)
    
    try:
        # 正常なステージデータ
        valid_stage = {
            "id": "test_stage",
            "title": "テストステージ",
            "description": "テスト用",
            "board": {
                "size": [3, 3],
                "grid": ["...", "...", "..."]
            },
            "player": {
                "start": [0, 0],
                "direction": "N"
            },
            "goal": {
                "position": [2, 2]
            }
        }
        
        # 正常データの検証（エラーなし）
        loader.validate_stage(valid_stage, "test_stage")
        print("✅ 正常データ検証成功")
        
        # 必須フィールド不足のテスト
        invalid_stage = valid_stage.copy()
        del invalid_stage["board"]
        
        try:
            loader.validate_stage(invalid_stage, "test_stage")
            assert False, "バリデーションエラーが発生すべき"
        except StageValidationError as e:
            assert "必須フィールドが不足" in str(e)
            print("✅ 必須フィールド不足検出")
        
        # 不正なボードサイズのテスト
        invalid_size = valid_stage.copy()
        invalid_size["board"] = invalid_size["board"].copy()
        invalid_size["board"]["size"] = [0, 5]  # 無効なサイズ
        
        try:
            loader.validate_stage(invalid_size, "test_stage")
            assert False, "バリデーションエラーが発生すべき"
        except StageValidationError as e:
            assert "1以上である必要があります" in str(e)
            print("✅ 無効サイズ検出")
        
        # グリッドサイズ不整合のテスト
        invalid_grid = valid_stage.copy()
        invalid_grid["board"] = invalid_grid["board"].copy()
        invalid_grid["board"]["grid"] = ["...", ".."]  # 行数不足（3行期待のところ2行）
        
        try:
            loader.validate_stage(invalid_grid, "test_stage")
            assert False, "バリデーションエラーが発生すべき"
        except StageValidationError as e:
            assert "一致しません" in str(e)
            print("✅ グリッドサイズ不整合検出")
        
        # 無効な方向のテスト
        invalid_direction = valid_stage.copy()
        invalid_direction["player"] = invalid_direction["player"].copy()
        invalid_direction["player"]["direction"] = "X"  # 無効な方向
        
        try:
            loader.validate_stage(invalid_direction, "test_stage")
            assert False, "バリデーションエラーが発生すべき"
        except StageValidationError as e:
            assert "N/E/S/W" in str(e)
            print("✅ 無効方向検出")
            
    finally:
        # テンポラリディレクトリをクリーンアップ
        shutil.rmtree(temp_dir)


def test_available_stages():
    """利用可能ステージ一覧テスト"""
    print("📋 利用可能ステージ一覧テスト...")
    
    loader = StageLoader("stages")
    available = loader.get_available_stages()
    
    assert "stage01" in available
    assert "stage02" in available
    assert "stage03" in available
    assert len(available) >= 3
    
    print(f"✅ 利用可能ステージ: {sorted(available)}")


def test_enemy_validation():
    """敵データバリデーションテスト"""
    print("👹 敵データバリデーションテスト...")
    
    loader = StageLoader()
    
    # 正常な敵データ
    valid_enemies = [
        {
            "position": [1, 1],
            "type": "normal",
            "direction": "S",
            "hp": 30
        },
        {
            "position": [3, 3],
            "type": "large_2x2",
            "direction": "W",
            "hp": 50
        }
    ]
    
    # バリデーション実行（エラーなし）
    loader._validate_enemies(valid_enemies)
    print("✅ 正常な敵データ検証成功")
    
    # 無効な敵タイプのテスト
    invalid_enemies = [
        {
            "position": [1, 1],
            "type": "invalid_type",  # 無効なタイプ
            "direction": "S"
        }
    ]
    
    try:
        loader._validate_enemies(invalid_enemies)
        assert False, "バリデーションエラーが発生すべき"
    except StageValidationError as e:
        assert "invalid_type" in str(e)
        print("✅ 無効敵タイプ検出")


def test_item_validation():
    """アイテムデータバリデーションテスト"""
    print("🎒 アイテムデータバリデーションテスト...")
    
    loader = StageLoader()
    
    # 正常なアイテムデータ
    valid_items = [
        {
            "position": [2, 3],
            "type": "weapon",
            "name": "剣",
            "effect": {"attack": 5}
        },
        {
            "position": [4, 1],
            "type": "potion",
            "name": "回復薬",
            "effect": {"heal": 20}
        }
    ]
    
    # バリデーション実行（エラーなし）
    loader._validate_items(valid_items)
    print("✅ 正常なアイテムデータ検証成功")
    
    # 無効なアイテムタイプのテスト
    invalid_items = [
        {
            "position": [2, 3],
            "type": "invalid_item",  # 無効なタイプ
            "name": "謎のアイテム"
        }
    ]
    
    try:
        loader._validate_items(invalid_items)
        assert False, "バリデーションエラーが発生すべき"
    except StageValidationError as e:
        assert "invalid_item" in str(e)
        print("✅ 無効アイテムタイプ検出")


def test_template_creation():
    """ステージテンプレート作成テスト"""
    print("📝 ステージテンプレート作成テスト...")
    
    # テンポラリディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    loader = StageLoader(temp_dir)
    
    try:
        # テンプレート作成
        template_path = loader.create_stage_template("test_template")
        
        assert Path(template_path).exists()
        print(f"✅ テンプレート作成成功: {template_path}")
        
        # 作成されたテンプレートを読み込んでテスト
        stage = loader.load_stage("test_template")
        assert stage.id == "test_template"
        assert stage.board_size == (5, 5)
        assert len(stage.allowed_apis) == 3
        
        print("✅ 作成されたテンプレート読み込み成功")
        
    finally:
        # テンポラリディレクトリをクリーンアップ
        shutil.rmtree(temp_dir)


def test_file_not_found():
    """ファイル未発見エラーテスト"""
    print("🔍 ファイル未発見エラーテスト...")
    
    loader = StageLoader("stages")
    
    try:
        stage = loader.load_stage("non_existent_stage")
        assert False, "FileNotFoundErrorが発生すべき"
    except FileNotFoundError as e:
        assert "ステージファイルが見つかりません" in str(e)
        print("✅ ファイル未発見エラー検出")


def test_constraints_validation():
    """制約データバリデーションテスト"""
    print("⚖️ 制約データバリデーションテスト...")
    
    loader = StageLoader()
    
    # 正常な制約データ
    valid_constraints = {
        "max_turns": 50,
        "allowed_apis": ["turn_left", "turn_right", "move", "attack"]
    }
    
    # バリデーション実行（エラーなし）
    loader._validate_constraints(valid_constraints)
    print("✅ 正常な制約データ検証成功")
    
    # 無効なmax_turnsのテスト
    invalid_constraints = {
        "max_turns": 0  # 無効な値
    }
    
    try:
        loader._validate_constraints(invalid_constraints)
        assert False, "バリデーションエラーが発生すべき"
    except StageValidationError as e:
        assert "正の整数である必要があります" in str(e)
        print("✅ 無効max_turns検出")
    
    # 無効なAPIのテスト
    invalid_api_constraints = {
        "allowed_apis": ["turn_left", "invalid_api"]
    }
    
    try:
        loader._validate_constraints(invalid_api_constraints)
        assert False, "バリデーションエラーが発生すべき"
    except StageValidationError as e:
        assert "無効なAPI" in str(e)
        print("✅ 無効API検出")


def test_integration():
    """統合テスト"""
    print("🔗 統合テスト...")
    
    loader = StageLoader("stages")
    
    # 全ての利用可能ステージを順次読み込み
    available_stages = loader.get_available_stages()
    
    for stage_id in available_stages:
        try:
            stage = loader.load_stage(stage_id)
            
            # 基本的な整合性チェック
            assert stage.id == stage_id
            assert isinstance(stage.player_start, Position)
            assert isinstance(stage.player_direction, Direction)
            assert isinstance(stage.board_size, tuple)
            assert len(stage.board_size) == 2
            assert stage.board_size[0] > 0 and stage.board_size[1] > 0
            
            print(f"✅ {stage_id}: {stage.title}")
            
        except Exception as e:
            print(f"❌ {stage_id}でエラー: {e}")
            raise
    
    print("✅ 全ステージ統合テスト成功")


def main():
    """メイン実行"""
    print("🧪 StageLoaderテスト開始\n")
    
    try:
        test_load_basic_stage()
        test_stage_validation()
        test_available_stages()
        test_enemy_validation()
        test_item_validation()
        test_template_creation()
        test_file_not_found()
        test_constraints_validation()
        test_integration()
        
        print("\n🎉 全てのStageLoaderテストが完了！")
        print("✅ タスク6完了: YAMLステージローダーの実装")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()