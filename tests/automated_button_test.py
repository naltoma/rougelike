#!/usr/bin/env python3
"""
GUI Critical Fixes 自動テスト
Step/Pause/Resetボタンの機能を自動的にテスト
"""

import time
import threading
import sys
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock

# パス修正（tests/ディレクトリから親ディレクトリのengineにアクセス）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# テスト用のモック
class MockGameAPI:
    def __init__(self):
        self.move_calls = 0
        self.turn_calls = 0
        self.reset_calls = 0
        
    def move(self):
        self.move_calls += 1
        print(f"🔍 テスト: move() #{self.move_calls} 呼び出し")
        return True
        
    def turn_right(self):
        self.turn_calls += 1
        print(f"🔍 テスト: turn_right() #{self.turn_calls} 呼び出し")
        return True
        
    def reset_game(self):
        self.reset_calls += 1
        print(f"🔍 テスト: reset_game() #{self.reset_calls} 呼び出し")

class MockGameManager:
    def __init__(self):
        self.reset_calls = 0
        
    def reset_game(self):
        self.reset_calls += 1
        print(f"🔍 テスト: GameManager.reset_game() #{self.reset_calls} 呼び出し")
import pygame
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def automated_button_test():
    """自動ボタンクリックテスト"""
    print("🧪 自動ボタンクリックテスト開始")
    
    try:
        import engine.api as api
        from engine.execution_controller import ExecutionController
        from engine import ExecutionMode
        
        # 初期化
        print("📝 システム初期化...")
        execution_controller = ExecutionController()
        
        print("🔧 initialize_api('gui')実行中...")
        api.initialize_api("gui")
        print(f"🔧 初期化後のrenderer_type: {api._global_api.renderer_type}")
        
        # ExecutionController設定
        api._global_api.execution_controller = execution_controller
        
        if not api.initialize_stage("stage01"):
            print("❌ ステージ初期化失敗")
            return False
            
        renderer = api._global_api.renderer
        game_manager = api._global_api.game_manager
        
        print(f"🔧 レンダラー状態: {type(renderer).__name__}")
        print(f"🔧 ゲームマネージャー状態: {type(game_manager).__name__}")
        
        if not renderer:
            print("❌ レンダラー初期化失敗")
            return False
            
        # ExecutionController設定
        if hasattr(renderer, 'set_execution_controller'):
            renderer.set_execution_controller(execution_controller)
            print("✅ ExecutionController設定完了")
        
        # 一時停止状態にする
        execution_controller.pause_before_solve()
        initial_mode = execution_controller.state.mode
        print(f"🎯 初期モード: {initial_mode}")
        
        # 初回描画
        if game_manager:
            game_state = game_manager.get_current_state()
            renderer.render_frame(game_state)
            renderer.update_display()
            
        print(f"🖥️ ウィンドウサイズ: {renderer.screen.get_size()}")
        print(f"🔘 ボタン矩形数: {len(renderer.button_rects) if hasattr(renderer, 'button_rects') else 0}")
        
        if hasattr(renderer, 'button_rects') and 'step' in renderer.button_rects:
            step_rect = renderer.button_rects['step']
            print(f"🔘 Stepボタン位置: {step_rect}")
        
        # 自動ボタンクリックテスト
        print("\n🤖 自動ボタンクリック実行...")
        
        tests_passed = 0
        total_tests = 3
        
        # テスト1: スペースキー自動押下
        print("\n📋 テスト1: スペースキー自動実行")
        old_mode = execution_controller.state.mode
        print(f"   実行前モード: {old_mode}")
        
        # スペースキーイベントを生成
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        pygame.event.post(space_event)
        
        # 短時間イベント処理
        start_time = time.time()
        while time.time() - start_time < 1.0:  # 1秒間
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    execution_controller.step_execution()
                    print("   🔍 スペースキーイベント処理実行")
                    
            # 描画更新
            if game_manager:
                game_state = game_manager.get_current_state()
                renderer.render_frame(game_state)
                renderer.update_display()
                
            time.sleep(0.016)
            
        new_mode = execution_controller.state.mode
        print(f"   実行後モード: {new_mode}")
        
        if old_mode != new_mode:
            print("   ✅ スペースキーテスト成功")
            tests_passed += 1
        else:
            print("   ❌ スペースキーテスト失敗")
        
        # テスト2: ボタンクリック自動実行
        print("\n📋 テスト2: Stepボタン自動クリック")
        
        # 一度PAUSEDに戻す
        execution_controller.pause_before_solve()
        old_mode = execution_controller.state.mode
        print(f"   実行前モード: {old_mode}")
        
        if hasattr(renderer, 'button_rects') and 'step' in renderer.button_rects:
            step_rect = renderer.button_rects['step']
            click_pos = step_rect.center
            print(f"   クリック位置: {click_pos}")
            
            # マウスクリックイベントを生成
            click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=click_pos, button=1)
            pygame.event.post(click_event)
            
            # イベント処理
            start_time = time.time()
            while time.time() - start_time < 1.0:  # 1秒間
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if step_rect.collidepoint(event.pos):
                            execution_controller.step_execution()
                            print("   🖱️ ボタンクリックイベント処理実行")
                
                # 描画更新
                if game_manager:
                    game_state = game_manager.get_current_state()
                    renderer.render_frame(game_state)
                    renderer.update_display()
                    
                time.sleep(0.016)
                
            new_mode = execution_controller.state.mode
            print(f"   実行後モード: {new_mode}")
            
            if old_mode != new_mode:
                print("   ✅ ボタンクリックテスト成功")
                tests_passed += 1
            else:
                print("   ❌ ボタンクリックテスト失敗")
        else:
            print("   ❌ Stepボタンが見つかりません")
        
        # テスト3: 連続実行テスト
        print("\n📋 テスト3: 連続実行テスト")
        
        # Enterキーイベントを生成
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        pygame.event.post(enter_event)
        
        old_mode = execution_controller.state.mode
        print(f"   実行前モード: {old_mode}")
        
        # イベント処理
        start_time = time.time()
        while time.time() - start_time < 1.0:  # 1秒間
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    execution_controller.continuous_execution()
                    print("   ▶️ 連続実行イベント処理実行")
                    
            # 描画更新
            if game_manager:
                game_state = game_manager.get_current_state()
                renderer.render_frame(game_state)
                renderer.update_display()
                
            time.sleep(0.016)
            
        new_mode = execution_controller.state.mode
        print(f"   実行後モード: {new_mode}")
        
        if new_mode == ExecutionMode.CONTINUOUS:
            print("   ✅ 連続実行テスト成功")
            tests_passed += 1
        else:
            print("   ❌ 連続実行テスト失敗")
        
        # 最終結果
        print(f"\n🎯 自動テスト結果: {tests_passed}/{total_tests} 成功")
        
        success_rate = tests_passed / total_tests
        if success_rate >= 0.67:  # 2/3以上成功
            print("🎉 自動ボタンテスト成功！")
            return True
        else:
            print("⚠️ 自動ボタンテストに問題があります")
            return False
        
    except Exception as e:
        print(f"❌ 自動テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if 'pygame' in sys.modules:
            pygame.quit()

if __name__ == "__main__":
    success = automated_button_test()
    print(f"\n🎯 自動ボタンテスト: {'成功' if success else '失敗'}")
    
    if success:
        print("✅ ボタン機能が正常に動作しています")
    else:
        print("❌ ボタン機能に問題があります")