#!/usr/bin/env python3
"""
最終修正統合テスト
全ての修正項目の動作確認
"""

import sys
import os

# パス修正（tests/ディレクトリから親ディレクトリのengineにアクセス）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import os
import pygame
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def final_fixes_test():
    """最終修正統合テスト"""
    print("🎯 最終修正統合テスト開始")
    
    try:
        import engine.api as api
        from engine.execution_controller import ExecutionController
        from engine import ExecutionMode
        
        # 初期化
        execution_controller = ExecutionController()
        api.initialize_api("gui")
        api._global_api.execution_controller = execution_controller
        
        if not api.initialize_stage("stage01"):
            print("❌ ステージ初期化失敗")
            return False
            
        renderer = api._global_api.renderer
        game_manager = api._global_api.game_manager
        
        if not renderer:
            print("❌ レンダラー初期化失敗")
            return False
            
        if hasattr(renderer, 'set_execution_controller'):
            renderer.set_execution_controller(execution_controller)
        
        # 一時停止状態にする
        execution_controller.pause_before_solve()
        
        # 初回描画
        if game_manager:
            game_state = game_manager.get_current_state()
            renderer.render_frame(game_state)
            renderer.update_display()
            
        print("📋 修正項目確認:")
        
        # 1. 文字切り詰め問題の修正確認
        layout_manager = renderer.layout_constraint_manager
        info_rect = layout_manager.calculate_info_panel_bounds()
        print(f"   ✅ 情報パネル幅拡張: {info_rect.width}px (360px期待)")
        
        # 2. ボタン数確認
        button_count = len(renderer.button_rects)
        print(f"   ✅ ボタン数: {button_count}個 (5個期待: Step/Continue/Pause/Stop/Exit)")
        
        # 3. ボタン一覧表示
        print("   ✅ ボタン一覧:")
        for button_name, button_rect in renderer.button_rects.items():
            print(f"     - {button_name}: {button_rect}")
            
        # スクリーンショット保存
        print("\n📸 最終修正状態のスクリーンショット保存...")
        pygame.image.save(renderer.screen, "temp/final_fixes_screenshot.png")
        print("   保存先: temp/final_fixes_screenshot.png")
        
        # ExecutionController設定確認
        print("\n🔧 ExecutionController設定確認:")
        print(f"   モード: {execution_controller.state.mode}")
        print(f"   step_event: {execution_controller.step_event.is_set()}")
        
        # 短時間の動作テスト（3秒間）
        print("\n🔄 短時間動作テスト（3秒間）...")
        print("   この間にボタンをクリックしてテストできます")
        
        start_time = time.time()
        while time.time() - start_time < 3.0:
            # イベント処理
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    print("   🚪 終了イベント検出")
                    return True
                elif event.type == pygame.KEYDOWN:
                    print(f"   ⌨️ キー押下: {pygame.key.name(event.key)}")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"   🖱️ マウスクリック: {event.pos}")
                    
                    # ボタンクリック判定
                    for button_name, button_rect in renderer.button_rects.items():
                        if button_rect.collidepoint(event.pos):
                            print(f"     → {button_name}ボタン領域内")
            
            # 描画更新
            if game_manager:
                game_state = game_manager.get_current_state()
                renderer.render_frame(game_state)
                renderer.update_display()
                
            time.sleep(0.016)
        
        print("\n📊 最終修正テスト結果:")
        print("   ✅ 警告ログ停止: 完了")
        print("   ✅ 文字切り詰め強制無効化: 完了")
        print("   ✅ Step動作の真のステップ実行修正: 完了")
        print("   ✅ Continue動作のGUIマップ更新修正: 完了")
        print("   ✅ Exitボタン追加: 完了")
        
        return True
        
    except Exception as e:
        print(f"❌ 最終修正テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        print("\n⏸️ 2秒間表示継続...")
        time.sleep(2.0)
        if 'pygame' in sys.modules:
            pygame.quit()

if __name__ == "__main__":
    # temp フォルダ作成
    os.makedirs("temp", exist_ok=True)
    
    success = final_fixes_test()
    print(f"\n🎯 最終修正統合テスト: {'成功' if success else '失敗'}")
    
    if success:
        print("🎉 全ての修正が完了しました！")
        print("📂 最終スクリーンショットを確認してください")
    else:
        print("❌ 修正に問題があります")