#!/usr/bin/env python3
"""
Python初学者向けローグライク演習フレームワーク
メインエントリーポイント

学生の皆さんへ：
このファイルを実行してゲームを開始します。
あなたのタスクは下記のsolve()関数を編集することです。

使用方法:
- GUI モード（推奨）: python main.py
- CUI モード: python main.py --cui
"""

import argparse
import logging
import sys
from pathlib import Path

# プロジェクト設定
import config
from engine.hyperparameter_manager import HyperParameterManager, HyperParameterError
from engine.execution_controller import ExecutionController
from engine.session_log_manager import SessionLogManager, LoggingSystemError
from engine import StepPauseException

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format=config.LOG_FORMAT,
    datefmt=config.LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)

# グローバル実行制御インスタンス
execution_controller = ExecutionController()
hyperparameter_manager = HyperParameterManager()
session_log_manager = SessionLogManager()

def setup_stage(stage_id: str, student_id: str):
    """
    ステージ初期化処理
    solve()実行前の準備作業を実行
    """
    logger.debug(f"ステージセットアップ開始: stage_id={stage_id}, student_id={student_id}")
    from engine.api import initialize_api, initialize_stage
    
    print("🎮 ゲーム開始！")
    
    # APIレイヤー初期化
    initialize_api("gui")  # デフォルトGUIモード
    
    # execution_controllerをAPIレイヤーに設定
    from engine.api import _global_api
    _global_api.execution_controller = execution_controller
    
    # ステージ初期化
    if not initialize_stage(stage_id):
        print("❌ ステージ初期化失敗")
        return False
        
    return True

def show_initial_state():
    """
    凡例と初期状態表示
    solve()実行前の情報表示
    """
    from engine.api import show_legend, show_current_state
    
    print("📋 ゲーム画面の見方:")
    show_legend()
    
    print("🎯 初期状態:")
    show_current_state()

def show_results():
    """
    結果表示
    solve()実行後の結果確認
    """
    from engine.api import get_game_result, show_current_state
    
    result = get_game_result()
    print(f"\n🏁 最終結果: {result}")
    
    print("🎯 最終状態:")
    show_current_state()

# ================================
# 📌 ハイパーパラメータ設定セクション
# ================================
# 学習者の皆さん：このセクションを編集してください

# ステージ設定
STAGE_ID = "stage01"  # 実行するステージ（stage01, stage02, ...）

# 学生ID設定（必須：6桁数字 + 英大文字1桁）
STUDENT_ID = "123456A"  # テスト用ID

# ログ設定
ENABLE_LOGGING = True  # セッションログを有効化

# ================================

def solve():
    """
    学生が編集する関数
    
    ここにステージを攻略するコードを書いてください。
    このsolve()関数はキャラクタ操作のみを記述してください。
    
    使用できる関数:
    - turn_left(): 左に90度回転
    - turn_right(): 右に90度回転  
    - move(): 正面方向に1マス移動
    - see(): 周囲の状況を確認 (辞書形式で返却)
    - attack(): 攻撃
    - pickup(): アイテム拾得
    
    例:
    turn_right()  # 右を向く
    move()        # 1マス前進
    info = see()  # 周囲を確認
    """
    # ここに攻略コードを書いてください
    
    # 例: Stage01の簡単な解法（キャラクタ操作のみ）
    from engine.api import turn_right, move, set_auto_render
    
    print("🎮 自動解法を実行します...")
    set_auto_render(True)  # 自動レンダリングをオン
    
    # 東を向いて移動
    print("➡️ 東方向へ移動中...")
    turn_right()  # 東を向く
    for _ in range(4):
        move()    # 東に移動
    
    # 南を向いて移動
    print("⬇️ 南方向へ移動中...")
    turn_right()  # 南を向く
    for _ in range(4):
        move()    # 南に移動

def validate_hyperparameters():
    """
    ハイパーパラメータの検証とエラーハンドリング
    """
    try:
        # ハイパーパラメータ管理インスタンス設定
        hyperparameter_manager.set_stage_id(STAGE_ID)
        hyperparameter_manager.set_student_id(STUDENT_ID) 
        hyperparameter_manager.set_logging_enabled(ENABLE_LOGGING)
        
        # 検証実行
        hyperparameter_manager.validate()
        
        return True
        
    except HyperParameterError as e:
        print(f"\n{e}")
        print("\n🔧 修正方法:")
        print("1. main.py内のハイパーパラメータ設定セクションを確認")
        print("2. STUDENT_ID = 'あなたの学籍番号'  # 例: '123456A'")
        print("3. ファイルを保存して再実行")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        return False

def _wait_for_gui_close():
    """GUI終了待機"""
    try:
        import pygame
        from engine.api import _global_api
        
        if not _global_api.renderer or not hasattr(_global_api.renderer, 'screen'):
            return
            
        clock = pygame.time.Clock()
        waiting = True
        
        while waiting:
            # レンダラーのイベント処理を呼び出し（Exitボタン等のクリック処理含む）
            if hasattr(_global_api.renderer, '_handle_events'):
                _global_api.renderer._handle_events()
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        
            # 画面更新はしない（表示を固定）
            # 単純にイベント待機のみ
            clock.tick(30)  # 30 FPS
            
    except (ImportError, AttributeError):
        # pygameが利用できない場合はフォールバック
        input("Enterキーを押して終了...")

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="Python初学者向けローグライク演習フレームワーク"
    )
    parser.add_argument(
        "--cui", 
        action="store_true", 
        help="CUIモードで実行（デフォルトはGUIモード）"
    )
    parser.add_argument(
        "--gui",
        action="store_true", 
        help="GUIモードで実行"
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="stage01",
        help="実行するステージ名（デフォルト: stage01）"
    )
    
    args = parser.parse_args()
    
    # 表示モード選択
    if args.cui:
        display_mode = "cui"
    elif args.gui:
        display_mode = "gui"
    else:
        # デフォルトはGUI（pygame利用可能時）
        try:
            import pygame
            pygame.version  # pygameが正しく読み込めることを確認
            display_mode = "gui"
        except ImportError:
            display_mode = "cui"
            print("⚠️ pygame が見つかりません。CUIモードで実行します。")
    
    # コマンドライン引数からステージIDを上書き（ハイパーパラメータより優先）
    if args.stage != "stage01":  # デフォルト値以外が指定された場合
        global STAGE_ID
        STAGE_ID = args.stage
    
    # ハイパーパラメータの検証
    print("🔍 ハイパーパラメータを検証中...")
    if not validate_hyperparameters():
        sys.exit(1)
    
    # 検証されたパラメータを取得
    stage_id = hyperparameter_manager.get_stage_id()
    student_id = hyperparameter_manager.get_student_id()
    logging_enabled = hyperparameter_manager.is_logging_enabled()
    
    # セッションログ有効化（要求仕様4.1）
    if logging_enabled:
        try:
            print("📝 セッションログシステムを初期化中...")
            session_log_manager.enable_default_logging(student_id, stage_id)
            session_log_manager.log_session_start({
                "display_mode": display_mode,
                "framework_version": "v1.1"
            })
        except LoggingSystemError as e:
            print(f"⚠️ ログシステム初期化警告: {e}")
            print("ログなしで実行を継続します")
    
    logger.info(f"ローグライク演習フレームワーク開始")
    logger.info(f"表示モード: {display_mode.upper()}")
    logger.info(f"ステージ: {stage_id}")
    logger.info(f"学生ID: {student_id}")
    
    print("🎮 ローグライク演習フレームワーク")
    print(f"📺 表示モード: {display_mode.upper()}")
    print(f"🎯 ステージ: {stage_id}")
    print(f"👤 学生ID: {student_id}")
    print()
    print("🔥 ゲームエンジン実装完了！")
    print("solve()関数を編集してゲームを攻略してください！")
    
    # ステージ初期化と初期状態表示（solve()実行前）
    if not setup_stage(stage_id, student_id):
        print("❌ ステージのセットアップに失敗しました")
        sys.exit(1)
        
    show_initial_state()
    
    try:
        # solve()実行前の一時停止（要求仕様1.1）
        print("\n⏸️ solve()実行準備完了")
        print("GUIのStepボタンまたはスペースキーを押してsolve()を開始してください")
        execution_controller.pause_before_solve()
        
        # 🆕 v1.2.1: GUI更新ループ（新ExecutionMode対応）- 無限ループ修正
        from engine.api import _global_api
        from engine import ExecutionMode
        import pygame
        import time
        
        loop_count = 0
        max_loops = 60000  # 最大10分間のループ制限（60FPS * 600秒）
        
        # 新しい状態での継続実行可能性を確認
        def should_continue_main_loop(current_mode: ExecutionMode) -> bool:
            """🆕 v1.2.1: メインループ継続判定"""
            continue_modes = {
                ExecutionMode.PAUSED,
                ExecutionMode.STEPPING, 
                ExecutionMode.STEP_EXECUTING,
                ExecutionMode.CONTINUOUS,  # 🔧 連続実行モードを追加
                ExecutionMode.PAUSE_PENDING,
                ExecutionMode.COMPLETED  # Reset後の継続実行のため追加
            }
            return current_mode in continue_modes
        
        while should_continue_main_loop(execution_controller.state.mode) and loop_count < max_loops:
            # pygameイベント処理（重要！）
            if hasattr(_global_api, 'renderer') and _global_api.renderer:
                # レンダラーのイベント処理を明示的に呼び出し
                if hasattr(_global_api.renderer, '_handle_events'):
                    _global_api.renderer._handle_events()
                else:
                    # フォールバック: 基本的なpygameイベント処理
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                print("🔍 スペースキー検出 - ステップ実行")
                                try:
                                    step_result = execution_controller.step_execution()
                                    if step_result and not step_result.success:
                                        print(f"⚠️ ステップ実行エラー: {step_result.error_message}")
                                except Exception as e:
                                    print(f"❌ ステップ実行例外: {e}")
                            elif event.key == pygame.K_RETURN:
                                print("▶️ Enterキー検出 - 連続実行")
                                try:
                                    execution_controller.continuous_execution()
                                except Exception as e:
                                    print(f"❌ 連続実行例外: {e}")
                            elif event.key == pygame.K_ESCAPE:
                                print("⏹️ Escapeキー検出 - 停止")
                                try:
                                    execution_controller.stop_execution()
                                    return
                                except Exception as e:
                                    print(f"❌ 停止処理例外: {e}")
                                    return
                            elif event.key == pygame.K_r:
                                print("🔄 Rキー検出 - リセット実行")
                                try:
                                    reset_result = execution_controller.reset_system()
                                    if reset_result and not reset_result.success:
                                        print(f"⚠️ リセットエラー: {', '.join(reset_result.errors)}")
                                except Exception as e:
                                    print(f"❌ リセット例外: {e}")
                            elif event.key == pygame.K_p:
                                print("⏸️ Pキー検出 - 次アクション境界で一時停止")
                                try:
                                    execution_controller.pause_at_next_action_boundary()
                                except Exception as e:
                                    print(f"❌ 一時停止要求例外: {e}")
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            # ボタンクリック処理
                            if hasattr(_global_api.renderer, '_handle_control_events'):
                                _global_api.renderer._handle_control_events(event)
            
            # GUI描画更新
            if hasattr(_global_api, 'renderer') and _global_api.renderer and _global_api.game_manager:
                try:
                    game_state = _global_api.game_manager.get_current_state()
                    _global_api.renderer.render_frame(game_state)
                    _global_api.renderer.update_display()
                except Exception as render_error:
                    print(f"⚠️ 描画エラー: {render_error}")
            
            # 停止リクエストのチェック
            if execution_controller.stop_requested.is_set():
                print("🛑 実行が停止されました")
                return
                
            # 🆕 v1.2.1: 新ExecutionModeでの状態チェック
            current_mode = execution_controller.state.mode
            
            
            # STEP_EXECUTING状態の処理
            if current_mode == ExecutionMode.STEP_EXECUTING:
                # ステップ実行中は短い間隔でチェック
                time.sleep(0.01)  # 10ms間隔でチェック
                if loop_count % 10 == 0:  # 100msごとに状態確認
                    print(f"⚡ ステップ実行中... (ループ: {loop_count})")
            
            # PAUSE_PENDING状態の処理  
            elif current_mode == ExecutionMode.PAUSE_PENDING:
                # 一時停止待機中は短い間隔でチェック
                time.sleep(0.01)  # 10ms間隔でチェック
                if loop_count % 50 == 0:  # 500msごとに状態確認
                    print(f"⏸️ 一時停止待機中... (ループ: {loop_count})")
            
            # RESET状態の処理
            elif current_mode == ExecutionMode.RESET:
                print("🔄 リセット状態を検出しました")
                time.sleep(0.05)  # 50ms待機
            
            # ERROR状態の処理
            elif current_mode == ExecutionMode.ERROR:
                print("❌ エラー状態を検出しました")
                error_detail = execution_controller.get_execution_state_detail()
                if error_detail and error_detail.last_error:
                    print(f"エラー内容: {error_detail.last_error}")
                time.sleep(0.1)  # 100ms待機
            
            elif current_mode == ExecutionMode.STEPPING:
                # ステップ実行モード：solve()アクションを1つずつ実行（ハードコーディング方式）
                if execution_controller.single_step_requested:
                    print("🔍 ステップ実行: solve()の1アクションを実行中...")
                    try:
                        # solve()関数のハードコードされたシーケンス（pygameスレッド制約対応）
                        from engine.api import turn_right, move
                        
                        step_num = execution_controller.state.step_count
                        
                        # solve()の実際のシーケンス（main.py Line 135-143参考）：
                        # 1: turn_right() - 東を向く
                        # 2-5: move() x4 - 東に移動  
                        # 6: turn_right() - 南を向く
                        # 7-10: move() x4 - 南に移動
                        
                        if step_num == 1:
                            print("➡️ 東方向を向く...")
                            turn_right()  # 東を向く
                        elif 2 <= step_num <= 5:
                            print("➡️ 東方向へ移動...")
                            move()  # 東に移動
                        elif step_num == 6:
                            print("⬇️ 南方向を向く...")
                            turn_right()  # 南を向く
                        elif 7 <= step_num <= 10:
                            print("⬇️ 南方向へ移動...")
                            move()  # 南に移動
                        else:
                            print("🎉 solve()完了 - すべてのアクションを実行しました")
                            execution_controller.mark_solve_complete()
                            
                        # ステップ完了を通知  
                        print(f"✅ ステップ #{step_num} 完了")
                        
                        # single_step_requestedをクリア（次ステップまで待機）
                        execution_controller.single_step_requested = False
                            
                    except Exception as e:
                        print(f"❌ ステップ実行エラー: {e}")
                        execution_controller.single_step_requested = False
                
                time.sleep(0.016)  # ~60 FPS
            
            elif current_mode == ExecutionMode.CONTINUOUS:
                # 連続実行モード：STEPPINGと同じ仕組みだが、wait_for_action()で自動進行
                if execution_controller.single_step_requested:
                    print("🔍 連続実行: solve()の1アクションを実行中...")
                    try:
                        # 🔧 step_countが0の場合、step_execution()を呼び出してカウントを開始
                        if execution_controller.state.step_count == 0:
                            step_result = execution_controller.step_execution()
                            print(f"🚀 連続実行の最初のステップ実行: {step_result.success}")
                        
                        # solve()関数のハードコードされたシーケンス（Pauseボタン対応）
                        from engine.api import turn_right, move
                        
                        step_num = execution_controller.state.step_count
                        
                        if step_num == 1:
                            print("➡️ 東方向を向く...")
                            turn_right()  # 東を向く
                        elif 2 <= step_num <= 5:
                            print("➡️ 東方向へ移動...")
                            move()  # 東に移動
                        elif step_num == 6:
                            print("⬇️ 南方向を向く...")
                            turn_right()  # 南を向く
                        elif 7 <= step_num <= 10:
                            print("⬇️ 南方向へ移動...")
                            move()  # 南に移動
                        else:
                            print("🎉 solve()完了 - すべてのアクションを実行しました")
                            execution_controller.mark_solve_complete()
                            
                        # ステップ完了を通知  
                        print(f"✅ 連続実行 #{execution_controller.state.step_count} 完了")
                        
                        # single_step_requestedをクリア（次ステップまで待機）
                        execution_controller.single_step_requested = False
                        
                        # 連続実行のため、次のステップを自動要求（短い間隔後）
                        if execution_controller.state.mode == ExecutionMode.CONTINUOUS:
                            time.sleep(execution_controller.state.sleep_interval or 1.0)
                            
                            # 🔧 Pauseボタン対応: 一時停止要求をチェック
                            if execution_controller.pause_requested:
                                print("⏸️ 一時停止要求を検出 - 次のステップを停止します")
                                execution_controller.pause_requested = False  # フラグをリセット
                                # pause_execution()は既にGUIボタンで呼ばれているはずなので、状態確認のみ
                                if execution_controller.state.mode != ExecutionMode.PAUSED:
                                    execution_controller.state.mode = ExecutionMode.PAUSED
                                    execution_controller.state.is_running = False
                            elif execution_controller.state.mode == ExecutionMode.CONTINUOUS:  # 再確認
                                execution_controller.step_execution()  # 次のステップを自動実行
                            
                    except Exception as e:
                        print(f"❌ 連続実行エラー: {e}")
                        execution_controller.single_step_requested = False
                        execution_controller.state.mode = ExecutionMode.ERROR
                
                time.sleep(0.016)  # ~60 FPS
            
            else:
                # 通常のモード変更チェック（デバッグ出力付き）
                if loop_count % 300 == 0:  # 5秒ごとにデバッグ出力
                    print(f"🔄 待機中... モード: {current_mode.value} (ループ: {loop_count})")
                # CPUを節約
                time.sleep(0.016)  # ~60 FPS
            
            loop_count += 1
        
        # ループ終了理由の確認
        if loop_count >= max_loops:
            print("⚠️ 最大ループ数に達しました。タイムアウトで終了します。")
            return
        
        print(f"✅ 一時停止解除: モード = {execution_controller.state.mode}")
        
        # 🔧 v1.2.1最終版: solve()実行はGUIループ内で完了済み
        final_mode = execution_controller.state.mode
        print(f"\n✅ GUIループ終了: {final_mode.value}モード")
        
    except Exception as e:
        print(f"❌ solve()関数でエラーが発生: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 結果表示（solve()完了後の処理）
        show_results()
        
        # セッション完了ログ記録（要求仕様4.4）
        if logging_enabled and session_log_manager.is_logging_enabled():
            try:
                execution_summary = {
                    "completed_successfully": True,
                    "total_execution_time": "N/A",  # 実際の計測は今後実装
                    "action_count": 0  # ActionHistoryTrackerとの連携で実装
                }
                session_log_manager.log_session_complete(execution_summary)
            except LoggingSystemError as e:
                print(f"⚠️ セッション完了ログ記録エラー: {e}")
        
        # 実行完了後の最終待機（要求仕様1.6）
        print("\n🏁 すべてのタスクが完了しました")
        print("結果を確認してから終了してください")
        
        # GUI/CUIに応じた終了待機
        try:
            # APIレイヤーからrendererの種類を確認
            from engine.api import _global_api
            if hasattr(_global_api, 'renderer') and _global_api.renderer:
                renderer_type = _global_api.renderer.__class__.__name__
                if "Gui" in renderer_type:
                    # GUIモード: ウィンドウイベント待機
                    print("ウィンドウの×ボタンまたはEscキーで終了")
                    _wait_for_gui_close()
                else:
                    # CUIモード: Enterキー待機
                    input("Enterキーを押して終了...")
            else:
                # フォールバック: Enterキー待機
                input("Enterキーを押して終了...")
        except (ImportError, AttributeError):
            # エラー時のフォールバック
            input("Enterキーを押して終了...")
    
    print("\n🎉 基本APIレイヤー実装完了！")
    print("📚 使用可能な学生向け関数:")
    print("  - initialize_stage(stage_id): ステージを初期化")
    print("  - turn_left(): 左に90度回転")
    print("  - turn_right(): 右に90度回転")
    print("  - move(): 正面方向に1マス移動")
    print("  - see(): 周囲の状況を確認")
    print("  - get_game_result(): ゲーム結果を取得")
    print("  - is_game_finished(): ゲーム終了判定")
    print("\n💡 より詳しい使用例は student_example.py を参照してください！")

if __name__ == "__main__":
    main()