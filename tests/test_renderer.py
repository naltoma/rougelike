#!/usr/bin/env python3
"""
レンダラーのテスト
"""

import sys
import io
from contextlib import redirect_stdout
sys.path.append('..')

from engine import (
    Position, Direction, Character, Enemy, Item, Board, GameState,
    ItemType, EnemyType, GameStatus
)
from engine.renderer import CuiRenderer, RendererFactory


def create_test_game_state():
    """テスト用のゲーム状態を作成"""
    # プレイヤー
    player = Character(Position(1, 1), Direction.EAST, hp=80, attack_power=15)
    
    # 敵
    enemy = Enemy(Position(3, 2), Direction.SOUTH, hp=30, enemy_type=EnemyType.NORMAL)
    
    # アイテム
    item = Item(Position(2, 3), ItemType.WEAPON, "剣", {"attack": 5})
    
    # ボード
    board = Board(
        width=5,
        height=4,
        walls=[Position(2, 1), Position(4, 2)],
        forbidden_cells=[Position(0, 3)]
    )
    
    return GameState(
        player=player,
        enemies=[enemy],
        items=[item],
        board=board,
        turn_count=5,
        max_turns=20,
        status=GameStatus.PLAYING,
        goal_position=Position(4, 3)
    )


def test_cui_renderer_initialization():
    """CUIレンダラー初期化テスト"""
    print("🖼️ CUIレンダラー初期化テスト...")
    
    renderer = CuiRenderer()
    
    # 初期化前の状態
    assert renderer.width == 0
    assert renderer.height == 0
    
    # 初期化実行
    with redirect_stdout(io.StringIO()) as f:
        renderer.initialize(5, 4)
    
    # 初期化後の状態確認
    assert renderer.width == 5
    assert renderer.height == 4
    assert len(renderer.current_frame) == 4  # height
    assert len(renderer.current_frame[0]) == 5  # width
    
    # 出力確認
    output = f.getvalue()
    assert "CUIレンダラー初期化完了" in output
    
    print("✅ 初期化正常")


def test_frame_rendering():
    """フレーム描画テスト"""
    print("🎨 フレーム描画テスト...")
    
    renderer = CuiRenderer()
    renderer.initialize(5, 4)
    game_state = create_test_game_state()
    
    # フレーム描画
    renderer.render_frame(game_state)
    
    # フレーム内容確認
    frame = renderer.current_frame
    
    # プレイヤー位置確認 (1, 1)
    assert frame[1][1] == renderer.symbol_map['player']
    
    # 敵位置確認 (3, 2)
    assert frame[2][3] == renderer.symbol_map['enemy']
    
    # アイテム位置確認 (2, 3)
    assert frame[3][2] == renderer.symbol_map['item']
    
    # ゴール位置確認 (4, 3)
    assert frame[3][4] == renderer.symbol_map['goal']
    
    # 壁位置確認
    assert frame[1][2] == renderer.symbol_map['wall']  # (2, 1)
    assert frame[2][4] == renderer.symbol_map['wall']  # (4, 2)
    
    # 移動禁止マス確認 (0, 3)
    assert frame[3][0] == renderer.symbol_map['forbidden']
    
    print("✅ フレーム描画正常")


def test_display_output():
    """ディスプレイ出力テスト"""
    print("📺 ディスプレイ出力テスト...")
    
    renderer = CuiRenderer()
    renderer.initialize(3, 3)
    
    # 簡単なゲーム状態を作成
    player = Character(Position(1, 1), Direction.NORTH)
    board = Board(3, 3, [Position(0, 0)], [])
    simple_state = GameState(
        player=player,
        enemies=[],
        items=[],
        board=board,
        goal_position=Position(2, 2)
    )
    
    renderer.render_frame(simple_state)
    
    # 出力をキャプチャ
    with redirect_stdout(io.StringIO()) as f:
        renderer.update_display()
    
    output = f.getvalue()
    
    # 出力内容確認
    assert "| # . . |" in output  # 壁がある行
    assert "| . P . |" in output  # プレイヤーがいる行
    assert "| . . G |" in output  # ゴールがある行
    assert "=" in output          # 境界線
    
    print("✅ ディスプレイ出力正常")


def test_game_info_rendering():
    """ゲーム情報表示テスト"""
    print("ℹ️ ゲーム情報表示テスト...")
    
    renderer = CuiRenderer()
    game_state = create_test_game_state()
    
    with redirect_stdout(io.StringIO()) as f:
        renderer.render_game_info(game_state)
    
    output = f.getvalue()
    
    # 必要な情報が含まれているかチェック
    assert "ターン: 5/20" in output
    assert "位置: (1, 1)" in output
    assert "向き: E" in output
    assert "HP: 80/100" in output
    assert "攻撃力: 15" in output
    assert "状態: playing" in output
    assert "ゴールまでの距離:" in output
    
    print("✅ ゲーム情報表示正常")


def test_legend_rendering():
    """凡例表示テスト"""
    print("📋 凡例表示テスト...")
    
    renderer = CuiRenderer()
    
    with redirect_stdout(io.StringIO()) as f:
        renderer.render_legend()
    
    output = f.getvalue()
    
    # 凡例の各要素が含まれているかチェック
    assert "凡例:" in output
    assert "P = プレイヤー" in output
    assert "G = ゴール" in output
    assert "# = 壁" in output
    assert "E = 敵" in output
    assert "I = アイテム" in output
    assert "X = 移動禁止" in output
    assert ". = 空きマス" in output
    
    print("✅ 凡例表示正常")


def test_debug_mode():
    """デバッグモードテスト"""
    print("🔧 デバッグモードテスト...")
    
    renderer = CuiRenderer()
    renderer.initialize(3, 3)
    
    # デバッグモード有効化
    with redirect_stdout(io.StringIO()) as f:
        renderer.set_debug_mode(True)
    
    output = f.getvalue()
    assert "デバッグモード: ON" in output
    
    # デバッグモードでのプレイヤー表示
    player = Character(Position(1, 1), Direction.NORTH)
    board = Board(3, 3, [], [])
    debug_state = GameState(
        player=player,
        enemies=[],
        items=[],
        board=board
    )
    
    renderer.render_frame(debug_state)
    
    # プレイヤーが方向記号で表示されているかチェック
    assert renderer.current_frame[1][1] == '↑'  # Direction.NORTH
    
    # デバッグモード無効化
    with redirect_stdout(io.StringIO()) as f:
        renderer.set_debug_mode(False)
    
    output = f.getvalue()
    assert "デバッグモード: OFF" in output
    
    # 通常モードでのプレイヤー表示
    renderer.render_frame(debug_state)
    assert renderer.current_frame[1][1] == 'P'  # 通常の'P'
    
    print("✅ デバッグモード正常")


def test_game_result_rendering():
    """ゲーム結果表示テスト"""
    print("🏁 ゲーム結果表示テスト...")
    
    renderer = CuiRenderer()
    
    # 勝利状態のテスト
    win_state = create_test_game_state()
    win_state.status = GameStatus.WON
    
    with redirect_stdout(io.StringIO()) as f:
        renderer.render_game_result(win_state)
    
    output = f.getvalue()
    assert "ゲーム終了！" in output
    assert "🎉 ゲームクリア！" in output
    assert "使用ターン: 5/20" in output
    assert "効率性:" in output
    
    # 失敗状態のテスト
    fail_state = create_test_game_state()
    fail_state.status = GameStatus.FAILED
    
    with redirect_stdout(io.StringIO()) as f:
        renderer.render_game_result(fail_state)
    
    output = f.getvalue()
    assert "💀 ゲーム失敗" in output
    
    print("✅ ゲーム結果表示正常")


def test_action_history_rendering():
    """アクション履歴表示テスト"""
    print("📜 アクション履歴表示テスト...")
    
    renderer = CuiRenderer()
    
    # アクション履歴を作成
    actions = [
        "左に90度回転",
        "右に90度回転", 
        "正面方向に1マス移動",
        "正面1マスを攻撃",
        "足元のアイテムを取得"
    ]
    
    with redirect_stdout(io.StringIO()) as f:
        renderer.render_action_history(actions, limit=3)
    
    output = f.getvalue()
    
    # 最新3件が表示されているかチェック
    assert "最近のアクション:" in output
    assert "1. 正面方向に1マス移動" in output  # 最新3件の1番目
    assert "2. 正面1マスを攻撃" in output      # 最新3件の2番目
    assert "3. 足元のアイテムを取得" in output  # 最新3件の3番目
    assert "... (他 2 件)" in output
    
    print("✅ アクション履歴表示正常")


def test_complete_view_rendering():
    """完全ビュー表示テスト"""
    print("🖼️ 完全ビュー表示テスト...")
    
    renderer = CuiRenderer()
    renderer.initialize(5, 4)
    game_state = create_test_game_state()
    
    with redirect_stdout(io.StringIO()) as f:
        renderer.render_complete_view(game_state, show_legend=True)
    
    output = f.getvalue()
    
    # 各要素が含まれているかチェック
    assert "|" in output                 # フレーム境界
    assert "ターン: 5/20" in output      # ゲーム情報
    assert "凡例:" in output             # 凡例
    assert "P = プレイヤー" in output    # 凡例内容
    
    print("✅ 完全ビュー表示正常")


def test_renderer_factory():
    """レンダラーファクトリーテスト"""
    print("🏭 レンダラーファクトリーテスト...")
    
    # CUIレンダラー作成
    cui_renderer = RendererFactory.create_renderer("cui")
    assert isinstance(cui_renderer, CuiRenderer)
    print("✅ CUIレンダラー作成成功")
    
    # GUIレンダラー作成（未実装のため警告が出る）
    with redirect_stdout(io.StringIO()) as f:
        gui_renderer = RendererFactory.create_renderer("gui")
    
    output = f.getvalue()
    assert "GUIレンダラーは未実装" in output
    assert isinstance(gui_renderer, CuiRenderer)  # フォールバック
    print("✅ GUIレンダラーフォールバック確認")
    
    # 無効なタイプ
    try:
        RendererFactory.create_renderer("invalid")
        assert False, "例外が発生すべき"
    except ValueError as e:
        assert "未対応のレンダラータイプ" in str(e)
        print("✅ 無効タイプエラー処理正常")


def test_large_enemy_rendering():
    """大型敵レンダリングテスト"""
    print("🐲 大型敵レンダリングテスト...")
    
    renderer = CuiRenderer()
    renderer.initialize(5, 5)
    
    # 大型敵（2x2）を作成
    large_enemy = Enemy(
        Position(2, 2), 
        Direction.NORTH, 
        enemy_type=EnemyType.LARGE_2X2
    )
    
    player = Character(Position(0, 0), Direction.EAST)
    board = Board(5, 5, [], [])
    
    state = GameState(
        player=player,
        enemies=[large_enemy],
        items=[],
        board=board
    )
    
    renderer.render_frame(state)
    
    # 大型敵が占有する4つの座標に'E'が表示されているかチェック
    occupied_positions = large_enemy.get_occupied_positions()
    for pos in occupied_positions:
        assert renderer.current_frame[pos.y][pos.x] == 'E'
    
    print("✅ 大型敵レンダリング正常")


def test_integration():
    """統合テスト"""
    print("🔗 レンダラー統合テスト...")
    
    # 複雑なゲーム状況を作成
    renderer = CuiRenderer()
    renderer.initialize(6, 6)
    
    # 複数の敵、アイテム、壁がある状況
    player = Character(Position(0, 0), Direction.SOUTH)
    
    enemies = [
        Enemy(Position(2, 2), Direction.NORTH),
        Enemy(Position(4, 4), Direction.WEST, enemy_type=EnemyType.LARGE_2X2)
    ]
    
    items = [
        Item(Position(1, 3), ItemType.WEAPON, "剣", {"attack": 5}),
        Item(Position(3, 1), ItemType.POTION, "薬", {"heal": 20})
    ]
    
    board = Board(
        width=6,
        height=6,
        walls=[Position(2, 0), Position(2, 1), Position(3, 3)],
        forbidden_cells=[Position(5, 0)]
    )
    
    complex_state = GameState(
        player=player,
        enemies=enemies,
        items=items,
        board=board,
        turn_count=15,
        max_turns=50,
        status=GameStatus.PLAYING,
        goal_position=Position(5, 5)
    )
    
    # 統合レンダリング
    with redirect_stdout(io.StringIO()) as f:
        renderer.render_complete_view(complex_state)
    
    output = f.getvalue()
    
    # 各要素が正しく表示されているかチェック
    assert "P" in output  # プレイヤー
    assert "E" in output  # 敵
    assert "I" in output  # アイテム
    assert "#" in output  # 壁
    assert "G" in output  # ゴール
    assert "X" in output  # 移動禁止
    assert "ターン: 15/50" in output
    
    print("✅ 統合テスト正常")


def main():
    """メイン実行"""
    print("🧪 レンダラーテスト開始\n")
    
    try:
        test_cui_renderer_initialization()
        test_frame_rendering()
        test_display_output()
        test_game_info_rendering()
        test_legend_rendering()
        test_debug_mode()
        test_game_result_rendering()
        test_action_history_rendering()
        test_complete_view_rendering()
        test_renderer_factory()
        test_large_enemy_rendering()
        test_integration()
        
        print("\n🎉 全てのレンダラーテストが完了！")
        print("✅ CUIレンダラーの実装")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()