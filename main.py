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
import threading
from pathlib import Path
# 確認モードでもExecutionModeが必要なため、常にimport
from engine import ExecutionMode

# プロジェクト設定
import config
from engine.hyperparameter_manager import HyperParameterManager, HyperParameterError
from engine.execution_controller import ExecutionController
from engine.session_log_manager import SessionLogManager, LoggingSystemError
from engine import StepPauseException
from engine.solve_parser import parse_solve_function

# v1.2.4新機能: 初回確認モード統合
from engine.initial_confirmation_flag_manager import InitialConfirmationFlagManager
from engine.stage_description_renderer import StageDescriptionRenderer
from engine.conditional_session_logger import ConditionalSessionLogger
from engine.stage_loader import StageLoader

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
solve_parser = None  # 動的solve()解析用

# v1.2.4新機能: 初回確認モード管理インスタンス
confirmation_flag_manager = InitialConfirmationFlagManager(hyperparameter_manager)
stage_loader = StageLoader()
stage_description_renderer = StageDescriptionRenderer(stage_loader)
conditional_session_logger = ConditionalSessionLogger(session_log_manager)

def setup_stage(stage_id: str, student_id: str):
    """
    ステージ初期化処理
    solve()実行前の準備作業を実行
    """
    logger.debug(f"ステージセットアップ開始: stage_id={stage_id}, student_id={student_id}")
    print(f"🔧 setup_stage() が呼び出されました: stage_id={stage_id}, student_id={student_id}")
    
    from engine.api import initialize_api, initialize_stage
    from engine.enhanced_7stage_speed_control_manager import Enhanced7StageSpeedControlManager
    from engine.ultra_high_speed_controller import UltraHighSpeedController
    from engine.speed_control_error_handler import SpeedControlErrorHandler
    
    print("🎮 ゲーム開始！")
    
    # 🚀 v1.2.5: 7段階速度制御システム初期化
    speed_manager = None
    ultra_controller = None
    error_handler = None
    
    try:
        print("🚀 7段階速度制御システム初期化中...")
        
        # Step 1: Enhanced7StageSpeedControlManager 作成
        print("   Step 1: Enhanced7StageSpeedControlManager 作成中...")
        try:
            speed_manager = Enhanced7StageSpeedControlManager(execution_controller)
            print(f"   ✅ speed_manager created: {speed_manager}")
        except Exception as e1:
            print(f"   ❌ speed_manager作成失敗: {e1}")
            raise e1
        
        # Step 2: UltraHighSpeedController 作成
        print("   Step 2: UltraHighSpeedController 作成中...")
        try:
            ultra_controller = UltraHighSpeedController(speed_manager)
            print(f"   ✅ ultra_controller created: {ultra_controller}")
        except Exception as e2:
            print(f"   ❌ ultra_controller作成失敗: {e2}")
            raise e2
        
        # Step 3: SpeedControlErrorHandler 作成（オプショナル）
        print("   Step 3: SpeedControlErrorHandler 作成中...")
        try:
            error_handler = SpeedControlErrorHandler(
                speed_manager=speed_manager,
                ultra_controller=ultra_controller,
                execution_controller=execution_controller
            )
            print(f"   ✅ error_handler created: {error_handler}")
        except Exception as e3:
            print(f"   ⚠️ error_handler作成失敗（オプショナル）: {e3}")
            error_handler = None  # エラーハンドラーなしで継続
        
        # Step 4: ExecutionController統合（必須）
        print("   Step 4: ExecutionController に統合中...")
        try:
            print(f"   execution_controller before setup: {execution_controller}")
            
            execution_controller.setup_7stage_speed_control(
                speed_manager, ultra_controller
            )
            
            # 統合後確認
            setup_success = (
                hasattr(execution_controller, '_7stage_speed_manager') and
                hasattr(execution_controller, '_ultra_high_speed_controller')
            )
            
            if setup_success:
                print(f"   ✅ ExecutionController統合成功")
                print(f"   _7stage_speed_manager: {getattr(execution_controller, '_7stage_speed_manager', 'NOT_SET')}")
                print(f"   _ultra_high_speed_controller: {getattr(execution_controller, '_ultra_high_speed_controller', 'NOT_SET')}")
            else:
                print(f"   ❌ ExecutionController統合失敗")
                raise Exception("setup_7stage_speed_control failed to set attributes")
            
        except Exception as e4:
            print(f"   ❌ ExecutionController統合失敗: {e4}")
            raise e4
        
        # Step 5: エラーハンドラー設定（オプショナル）
        if error_handler:
            execution_controller.speed_error_handler = error_handler
            print("   ✅ エラーハンドラー設定完了")
        
        # Step 6: 初期速度をExecutionControllerに適用
        print("   Step 6: 初期速度設定（x1）を適用中...")
        try:
            initial_sleep_interval = speed_manager.calculate_sleep_interval(1)  # x1 = 1.0秒
            execution_controller.state.sleep_interval = initial_sleep_interval
            print(f"   ✅ 初期速度設定完了: x1 (sleep_interval={initial_sleep_interval}秒)")
        except Exception as e6:
            print(f"   ⚠️ 初期速度設定失敗: {e6}")
        
        print("✅ 7段階速度制御システム初期化完了")
        
    except Exception as e:
        print(f"⚠️ 7段階速度制御システム初期化失敗: {e}")
        print("   初期化に失敗しましたが、標準機能で継続します")
        # import traceback
        # traceback.print_exc()
    
    # APIレイヤー初期化
    initialize_api("gui")  # デフォルトGUIモード
    
    # execution_controllerをAPIレイヤーに設定
    from engine.api import _global_api
    _global_api.execution_controller = execution_controller
    
    # ステージ初期化（レンダラー作成完了）
    if not initialize_stage(stage_id):
        print("❌ ステージ初期化失敗")
        return False
    
    # ステージ初期化後に7段階速度制御をレンダラーに統合
    if hasattr(_global_api, 'renderer') and _global_api.renderer:
        try:
            print(f"🔍 統合前チェック:")
            print(f"   _global_api: {_global_api}")
            print(f"   _global_api.renderer: {_global_api.renderer}")
            print(f"   renderer type: {type(_global_api.renderer).__name__}")
            print(f"   execution_controller._7stage_speed_manager: {getattr(execution_controller, '_7stage_speed_manager', 'NOT_SET')}")
            print(f"   execution_controller._ultra_high_speed_controller: {getattr(execution_controller, '_ultra_high_speed_controller', 'NOT_SET')}")
            
            # ExecutionControllerの属性が存在するかチェック
            if not hasattr(execution_controller, '_7stage_speed_manager'):
                print("⚠️ ExecutionController._7stage_speed_manager が存在しません")
                print("   7段階速度制御システムは無効化されました（標準速度制御で継続）")
                print("✅ GUI統合スキップ: 標準速度制御で動作")
                return True  # 7段階速度制御なしでも継続
            
            if not hasattr(execution_controller, '_ultra_high_speed_controller'):
                print("⚠️ ExecutionController._ultra_high_speed_controller が存在しません")
                print("   7段階速度制御システムは無効化されました（標準速度制御で継続）")
                print("✅ GUI統合スキップ: 標準速度制御で動作")
                return True  # 7段階速度制御なしでも継続
            
            # レンダラーに速度制御システムを設定
            print("   レンダラーへの設定実行中...")
            _global_api.renderer._7stage_speed_manager = execution_controller._7stage_speed_manager
            _global_api.renderer._ultra_speed_controller = execution_controller._ultra_high_speed_controller
            _global_api.renderer.error_handler = getattr(execution_controller, 'speed_error_handler', None)
            
            # 現在の速度倍率を同期（デフォルトx2を維持）
            if hasattr(_global_api.renderer, 'current_speed_multiplier') and execution_controller._7stage_speed_manager:
                # speed_managerがx2でない場合のみ、デフォルトx2に設定
                if execution_controller._7stage_speed_manager.config.current_multiplier != 2:
                    execution_controller._7stage_speed_manager.apply_speed_change_realtime(2)
                _global_api.renderer.current_speed_multiplier = execution_controller._7stage_speed_manager.config.current_multiplier
                print(f"   速度倍率同期: x{_global_api.renderer.current_speed_multiplier}")
            
            print(f"🔍 統合後確認:")
            print(f"   renderer._7stage_speed_manager: {getattr(_global_api.renderer, '_7stage_speed_manager', 'NOT_SET')}")
            print(f"   renderer._ultra_speed_controller: {getattr(_global_api.renderer, '_ultra_speed_controller', 'NOT_SET')}")
            print("✅ GUI統合完了: 7段階速度制御")
        except Exception as e:
            print(f"⚠️ GUI統合警告: {e}")
            import traceback
            traceback.print_exc()
        
    # _global_api の準備確認
    from engine.api import _global_api
    if not hasattr(_global_api, 'game_manager') or _global_api.game_manager is None:
        raise RuntimeError("ゲーム初期化に失敗しました")
    
    return _global_api.game_manager, execution_controller

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

def _get_solve_function_code() -> str:
    """solve()関数のソースコードを取得"""
    try:
        import inspect
        source_code = inspect.getsource(solve)
        return source_code
    except Exception as e:
        return f"# ソースコード取得エラー: {e}"

def _initialize_solve_parser():
    """solve()関数を解析してsolve_parserを初期化"""
    global solve_parser
    try:
        solve_parser = parse_solve_function(solve)
        print(f"📋 solve()関数解析完了: {solve_parser.total_steps}ステップ検出")
        return True
    except Exception as e:
        print(f"⚠️ solve()解析エラー: {e}")
        return False

def _execute_solve_step(step_number: int) -> bool:
    """指定されたステップのsolve()アクションを実行"""
    global solve_parser
    
    if not solve_parser:
        print("❌ solve_parserが初期化されていません")
        return False
    
    # ステップ番号を調整（1-basedから0-basedへ）
    solve_parser.current_step = step_number - 1
    action = solve_parser.get_next_action()
    
    if not action:
        print(f"⚠️ ステップ {step_number}: 実行するアクションがありません")
        return False
    
    try:
        # アクションを実行
        from engine.api import turn_right, turn_left, move, attack, pickup, see
        
        if action.action_type == 'turn_right':
            print(f"➡️ 右に回転... (step {step_number})")
            turn_right()
        elif action.action_type == 'turn_left':
            print(f"⬅️ 左に回転... (step {step_number})")
            turn_left()
        elif action.action_type == 'move':
            print(f"🚶 前進... (step {step_number})")
            move()
        elif action.action_type == 'attack':
            print(f"⚔️ 攻撃... (step {step_number})")
            attack()
        elif action.action_type == 'pickup':
            print(f"🎒 アイテム取得... (step {step_number})")
            pickup()
        elif action.action_type == 'see':
            print(f"👁️ 周囲確認... (step {step_number})")
            see()
        else:
            print(f"❓ 不明なアクション: {action.action_type}")
            return False
        
        print(f"✅ ステップ {step_number}/{solve_parser.total_steps} 完了: {action.action_type}")
        return True
        
    except Exception as e:
        print(f"❌ ステップ {step_number} 実行エラー: {e}")
        return False

def show_results():
    """
    結果表示
    solve()実行後の結果確認
    """
    from engine.api import get_game_result, show_current_state
    
    try:
        result = get_game_result()
        print(f"\n🏁 最終結果: {result}")
    except SystemExit:
        print("🚪 システム終了中のためゲーム結果表示をスキップします")
        return
    except Exception as e:
        print(f"⚠️ ゲーム結果取得エラー: {e}")
    
    try:
        print("🎯 最終状態:")
        show_current_state()
    except SystemExit:
        print("🚪 システム終了中のため状態表示をスキップします")
    except Exception as e:
        print(f"⚠️ 現在状態表示エラー: {e}")

# ================================
# 📌 ハイパーパラメータ設定セクション
# ================================
# 学習者の皆さん：このセクションを編集してください

# ステージ設定
STAGE_ID = "stage01"  # 実行するステージ（stage01, stage02, ...）

# 学生ID設定（必須：6桁数字 + 英大文字1桁）
STUDENT_ID = "123456A"  # テスト用ID

# ログ設定
ENABLE_LOGGING = False  # セッションログを有効化

# ================================

# APIをsolve()関数外でimport（関数内で使用可能）
from engine.api import turn_left, turn_right, move, attack, pickup, see, wait, set_auto_render, get_stage_info

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
    
    print("🎮 自動解法を実行します...")
    set_auto_render(True)  # 自動レンダリングをオン
    
    # 東を向いて移動
    print("➡️ 東方向へ移動中...")
    turn_right()  # 東を向く
    for _ in range(4):
        move()    # 東に移動
    
    # 南を向いて移動
    #print("⬇️ 南方向へ移動中...")
    turn_right()  # 南を向く
    for _ in range(4):
        move()    # 南に移動

def setup_confirmation_mode(stage_id: str, student_id: str) -> bool:
    """
    v1.2.4新機能: 初回確認モード判定ロジック
    
    Args:
        stage_id: ステージID
        student_id: 学生ID
    
    Returns:
        bool: True=確認モード表示完了, False=確認モードスキップ
    """
    try:
        # 初回実行判定
        is_first_time = confirmation_flag_manager.is_first_execution(stage_id, student_id)
        confirmation_mode = confirmation_flag_manager.get_confirmation_mode()
        logging_enabled = hyperparameter_manager.is_logging_enabled()
        
        # 確認モード条件: 初回実行 AND 確認モード(False) AND ログ無効(False)
        if is_first_time and not confirmation_mode and not logging_enabled:
            # 初回実行かつ確認モード(False)かつログ無効の場合：ステージ説明を表示
            print("\n" + "="*80)
            print("🔰 初回実行検出：ステージ理解モード")
            print("="*80)
            print("このステージを初めて実行します。")
            print("まずはステージの内容を理解してからコードを書きましょう。")
            print()
            
            # ステージ説明表示
            try:
                stage_description = stage_description_renderer.display_stage_conditions(
                    stage_id, student_id
                )
                print(stage_description)
            except Exception as e:
                logger.error(f"ステージ説明表示エラー: {e}")
                # フォールバック表示
                fallback_description = stage_description_renderer.display_fallback_message(stage_id)
                print(fallback_description)
            
            # 表示済みマークを設定
            confirmation_flag_manager.mark_stage_intro_displayed(stage_id)
            
            print("\n💡 次回実行時のヒント:")
            print("ステージ内容を理解したら、実行モードに切り替えてください。")
            print("実行モードでは学習データ(セッションログ)が記録されます。")
            print()
            print("🔧 実行モードへの切り替え方法:")
            print("ハイパーパラメータ設定で ENABLE_LOGGING = True に設定")
            print()
            
            return True
            
        elif not confirmation_mode:
            # 再実行だが確認モード：短いメッセージ
            print(f"\n🔰 確認モード実行: {stage_id}")
            print("セッションログは記録されません（学習データ収集を除外）")
            print("実行モードに切り替えると学習データが記録されます")
            print()
            return False
            
        else:
            # 実行モード：通常のログ記録実行
            print(f"\n🚀 実行モード: {stage_id}")
            print("セッションログを記録し、学習データを収集します")
            print()
            return False
            
    except Exception as e:
        logger.error(f"確認モード設定中にエラー: {e}")
        print(f"⚠️ 確認モード設定エラー: {e}")
        print("通常モードで続行します")
        return False

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
            try:
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
                
            except (pygame.error, SystemExit):
                # pygame終了済みまたはシステム終了
                print("🚪 アプリケーション終了")
                waiting = False
            
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
    
    # v1.2.4新機能: 初回確認モード判定処理
    print("🔰 初回確認モードを確認中...")
    confirmation_mode_displayed = setup_confirmation_mode(stage_id, student_id)
    
    # v1.2.4新機能: 確認モード時の処理フラグ
    is_confirmation_mode = confirmation_mode_displayed
    
    # v1.2.4新機能: 条件付きセッションログ有効化
    # ログ有効時は実行モード、無効時は確認モードとして動作
    actual_execution_mode = logging_enabled
    
    if logging_enabled:
        try:
            print("📝 セッションログシステムを初期化中...")
            
            # 実行モードでのログ記録
            log_start_result = conditional_session_logger.conditional_log_start(
                actual_execution_mode,
                display_mode=display_mode,
                framework_version="v1.2.4",
                stage_id=stage_id,
                student_id=student_id
            )
            
            if log_start_result:
                # 実行モード：通常通りログを有効化
                result = session_log_manager.enable_default_logging(student_id, stage_id)
                if result.success:
                    print(f"✅ 実行モード：セッションログ有効化完了")
                    print(f"📂 ログファイル: {result.log_path}")
                    
                    # solve()関数のソースコード取得
                    solve_code = _get_solve_function_code()
                    
                    # セッション情報を設定（コード含む）
                    if session_log_manager.session_logger:
                        session_log_manager.session_logger.set_session_info(
                            stage_id=stage_id, 
                            solve_code=solve_code
                        )
                else:
                    print(f"⚠️ ログシステム初期化警告: {result.error_message}")
                    print("ログなしで実行を継続します")
            else:
                # 確認モード：セッションログを除外
                print("🔰 確認モード：セッションログ記録を除外します")
                mode_status = conditional_session_logger.get_current_mode_status()
                print(f"📊 現在のモード: {mode_status['mode_description']}")
                print(f"📝 ログ動作: {mode_status['log_behavior']}")
                
        except LoggingSystemError as e:
            print(f"⚠️ ログシステム初期化警告: {e}")
            print("ログなしで実行を継続します")
    
    # v1.2.4新機能: 確認モード時は最小限のGUI初期化のみ実行
    if not is_confirmation_mode:
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
    
    # ステージ初期化と初期状態表示（GUI描画に必須）
    if not setup_stage(stage_id, student_id):
        print("❌ ステージのセットアップに失敗しました")
        sys.exit(1)
        
    show_initial_state()
    
    # 確認モード時はここで一時停止
    if is_confirmation_mode:
        print("\n" + "="*80)
        print("📚 ステージ理解完了")
        print("="*80)
        print("ステージの内容と攻略方法を理解できましたか？")
        print("理解できたら、上記の切り替え方法で実行モードに変更して再実行してください。")
        print("\n⏸️ 確認完了後、Escapeキーまたは×ボタンでプログラムを終了してください")
        print("（確認モードではsolve()は実行されません）")
        
        # GUI表示のためのメインループ開始
        from engine.api import _global_api
        import pygame
        import time
        
        while True:
            # pygameイベント処理
            if hasattr(_global_api, 'renderer') and _global_api.renderer:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            print("⏹️ 確認モード終了")
                            return
                        else:
                            print("📚 確認モードではsolve()は実行されません")
                            print("実行モードに変更してから再実行してください")
            
            # GUI描画更新
            if hasattr(_global_api, 'renderer') and _global_api.renderer and _global_api.game_manager:
                try:
                    game_state = _global_api.game_manager.get_current_state()
                    _global_api.renderer.render_frame(game_state)
                    _global_api.renderer.update_display()
                except Exception as render_error:
                    print(f"⚠️ 描画エラー: {render_error}")
            
            # 連続実行中は描画フレームレートを動的調整（実行モード時のみ）
            if 'execution_controller' in locals() and hasattr(execution_controller, 'state'):
                if execution_controller.state.mode == ExecutionMode.CONTINUOUS and execution_controller.state.sleep_interval < 0.016:
                    # 高速実行時（16ms未満）は描画を最小限に
                    time.sleep(max(0.001, execution_controller.state.sleep_interval / 2))  # アクション間隔の半分
                else:
                    time.sleep(0.016)  # 通常時は60FPS
            else:
                time.sleep(0.016)  # 確認モード時は固定60FPS
    
    # 実行モード時のsolve()関数解析
    print("\n🔍 solve()関数を解析中...")
    if not _initialize_solve_parser():
        print("⚠️ solve()解析に失敗しましたが、継続します")
    else:
        # solve()解析結果の表示
        if solve_parser:
            print(f"📊 solve()解析結果:")
            summary = solve_parser.get_action_summary()
            for item in summary[:10]:  # 最初の10ステップまで表示
                print(f"   {item['step']}. {item['action']} (line {item['line']})")
            if len(summary) > 10:
                print(f"   ... 他 {len(summary) - 10} ステップ")
    
    try:
        # solve()実行前の一時停止（要求仕様1.1） - 実行モードのみ
        print("\n⏸️ solve()実行準備完了")
        print("GUIのStepボタンまたはスペースキーを押してsolve()を開始してください")
        execution_controller.pause_before_solve()
        
        # 🆕 v1.2.1: GUI更新ループ（新ExecutionMode対応）- 無限ループ修正
        from engine.api import _global_api
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
                                if is_confirmation_mode:
                                    print("📚 確認モードではsolve()は実行されません")
                                    print("実行モードに変更してから再実行してください")
                                else:
                                    print("🔍 スペースキー検出 - ステップ実行")
                                    try:
                                        step_result = execution_controller.step_execution()
                                        if step_result and not step_result.success:
                                            print(f"⚠️ ステップ実行エラー: {step_result.error_message}")
                                    except Exception as e:
                                        print(f"❌ ステップ実行例外: {e}")
                            elif event.key == pygame.K_RETURN:
                                if is_confirmation_mode:
                                    print("📚 確認モードではsolve()は実行されません")
                                    print("実行モードに変更してから再実行してください")
                                else:
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
                                if is_confirmation_mode:
                                    # 確認モードでは実行系ボタンを無効化
                                    print("📚 確認モードではsolve()実行ボタンは無効です")
                                    print("実行モードに変更してから再実行してください")
                                else:
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
                # ステップ実行中は最小スリープ
                time.sleep(0.001)  # 1ms間隔でチェック
                if loop_count % 100 == 0:  # 100msごとに状態確認
                    print(f"⚡ ステップ実行中... (ループ: {loop_count})")
            
            # PAUSE_PENDING状態の処理  
            elif current_mode == ExecutionMode.PAUSE_PENDING:
                # 一時停止待機中は最小スリープ
                time.sleep(0.001)  # 1ms間隔でチェック
                if loop_count % 500 == 0:  # 500msごとに状態確認
                    print(f"⏸️ 一時停止待機中... (ループ: {loop_count})")
            
            # RESET状態の処理
            elif current_mode == ExecutionMode.RESET:
                print("🔄 リセット状態を検出しました")
                time.sleep(0.001)  # 最小スリープ
            
            # ERROR状態の処理
            elif current_mode == ExecutionMode.ERROR:
                print("❌ エラー状態を検出しました")
                error_detail = execution_controller.get_execution_state_detail()
                if error_detail and error_detail.last_error:
                    print(f"エラー内容: {error_detail.last_error}")
                time.sleep(0.01)  # 10ms待機（エラー表示のため少し長め）
            
            elif current_mode == ExecutionMode.STEPPING:
                # ステップ実行モード：実際のsolve()をネストループ対応で実行
                try:
                    # 実際のsolve()関数を呼び出し（APIレイヤーでwait_for_action()制御）
                    if not hasattr(execution_controller, '_solve_thread_started'):
                        # 初回のみsolve()をバックグラウンドで開始
                        def run_solve():
                            try:
                                solve()
                            except RuntimeError as e:
                                if "stopped by reset" in str(e):
                                    print(f"🔄 solve()はReset操作により正常終了しました")
                                else:
                                    print(f"❌ solve()実行エラー: {e}")
                            except Exception as e:
                                print(f"❌ solve()実行エラー: {e}")
                            finally:
                                execution_controller.mark_solve_complete()
                        
                        solve_thread = threading.Thread(target=run_solve, daemon=True)
                        solve_thread.start()
                        execution_controller._solve_thread_started = True
                        print("🚀 solve()をバックグラウンドで開始しました")
                        
                except Exception as e:
                    print(f"❌ ステップ実行エラー: {e}")
                
                # ステップ実行モードではスリープなし（ユーザー待機）
            
            elif current_mode == ExecutionMode.CONTINUOUS:
                # 連続実行モード：実際のsolve()をネストループ対応で連続実行
                try:
                    if not hasattr(execution_controller, '_solve_thread_started'):
                        # 実際のsolve()関数をバックグラウンドで実行
                        def run_solve_continuous():
                            try:
                                solve()
                            except RuntimeError as e:
                                if "stopped by reset" in str(e):
                                    print(f"🔄 solve()はReset操作により正常終了しました")
                                else:
                                    print(f"❌ solve()実行エラー: {e}")
                            except Exception as e:
                                print(f"❌ solve()実行エラー: {e}")
                            finally:
                                execution_controller.mark_solve_complete()
                        
                        solve_thread = threading.Thread(target=run_solve_continuous, daemon=True)
                        solve_thread.start()
                        execution_controller._solve_thread_started = True
                        print("🚀 連続実行のsolve()をバックグラウンドで開始しました")
                        
                except Exception as e:
                    print(f"❌ 連続実行開始エラー: {e}")
                    execution_controller.state.mode = ExecutionMode.ERROR
                
                # 連続実行モードでは自動進行（wait_for_action()で速度制御）
            
            else:
                # PAUSED状態等での待機
                # solve()スレッドが開始されていない場合でも、モード変更後に開始できるようにチェック
                if current_mode == ExecutionMode.PAUSED and not hasattr(execution_controller, '_solve_thread_started'):
                    # PAUSED状態だがsolve()スレッドが開始されていない場合のチェック
                    # （起動直後のPause→Step/Continue対応）
                    pass  # 次のループでモード変更時にsolve()スレッドが開始される
                
                # 通常のモード変更チェック（デバッグ出力付き）
                if loop_count % 300 == 0:  # 5秒ごとにデバッグ出力
                    print(f"🔄 待機中... モード: {current_mode.value} (ループ: {loop_count})")
                # CPUを節約（最小限のスリープ）
                time.sleep(0.001)  # 1ms - CPU節約のみ
            
            loop_count += 1
        
        # ループ終了理由の確認
        if loop_count >= max_loops:
            print("⚠️ 最大ループ数に達しました。タイムアウトで終了します。")
            return
        
        print(f"✅ 一時停止解除: モード = {execution_controller.state.mode}")
        
        # 🔧 v1.2.1最終版: solve()実行はGUIループ内で完了済み
        final_mode = execution_controller.state.mode
        print(f"\n✅ GUIループ終了: {final_mode.value}モード")
        
    except SystemExit:
        # Exitボタンやsys.exit()による正常な終了
        print("🚪 Exitボタンまたはシステム終了が要求されました")
    except Exception as e:
        print(f"❌ solve()関数でエラーが発生: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 結果表示（solve()完了後の処理）
        show_results()
        
        # v1.2.4新機能: 条件付きセッション完了ログ記録
        if logging_enabled:
            try:
                # 実際のゲーム結果を確認
                from engine.api import _global_api, get_game_result
                game_completed = False
                actual_action_count = 0
                
                try:
                    # ゲーム結果を取得
                    result_text = get_game_result()
                    game_completed = "ゴール到達" in result_text or "ゲームクリア" in result_text
                    
                    # 実際のアクション数を取得
                    if _global_api and _global_api.action_tracker:
                        actual_action_count = _global_api.action_tracker.get_action_count()
                except Exception as e:
                    print(f"⚠️ ゲーム結果確認エラー: {e}")
                
                # 条件付きセッション終了ログ記録
                execution_summary = {
                    "completed_successfully": game_completed,
                    "total_execution_time": "N/A",  # 実際の計測は今後実装
                    "action_count": actual_action_count
                }
                
                log_end_result = conditional_session_logger.conditional_log_end(
                    actual_execution_mode,
                    **execution_summary
                )
                
                if log_end_result:
                    print("\n📝 実行モード：セッション完了ログを記録しました")
                else:
                    print("\n🔰 確認モード：セッション完了ログを除外しました")
                    
            except LoggingSystemError as e:
                print(f"⚠️ セッション完了ログ記録エラー: {e}")
            except Exception as e:
                print(f"⚠️ セッションログ終了処理エラー: {e}")
        
        # ログファイルの場所とアクセス方法を表示
        if logging_enabled and session_log_manager.enabled:
            try:
                print("\n📊 セッションログが生成されました")
                
            except Exception as e:
                print(f"⚠️ ログ情報表示エラー: {e}")
        
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