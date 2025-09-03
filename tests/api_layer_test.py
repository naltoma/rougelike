#!/usr/bin/env python3
"""
APILayer初期化詳細テスト
"""

import sys
import os

# パス修正（tests/ディレクトリから親ディレクトリのengineにアクセス）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_layer_init():
    """APILayer初期化テスト"""
    print("🧪 APILayer初期化テスト")
    
    try:
        from engine.api import APILayer
        
        # GUI モードで初期化
        print("\n📋 GUI モードでAPILayer作成...")
        api = APILayer("gui")
        print(f"✅ APILayer作成完了: renderer_type = {api.renderer_type}")
        
        # 初期レンダラー状態
        print(f"🔧 初期レンダラー: {api.renderer}")
        print(f"🔧 StageLoader: {api.stage_loader}")
        
        return api
        
    except Exception as e:
        print(f"❌ APILayer初期化エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_initialize_stage(api):
    """initialize_stage テスト"""
    print("\n🧪 initialize_stage テスト")
    
    try:
        print("📋 stage01 初期化中...")
        success = api.initialize_stage("stage01")
        
        print(f"🎯 初期化結果: {success}")
        print(f"🔧 初期化後レンダラー: {api.renderer}")
        print(f"🔧 レンダラータイプ: {type(api.renderer).__name__ if api.renderer else 'None'}")
        print(f"🔧 GameManager: {api.game_manager}")
        
        # レンダラーが正しく作成されているかチェック
        if api.renderer:
            print("✅ レンダラー正常作成")
            if hasattr(api.renderer, 'screen'):
                print(f"🖥️ pygame screen: {api.renderer.screen}")
            if hasattr(api.renderer, 'width'):
                print(f"📐 レンダラーサイズ: {api.renderer.width}x{api.renderer.height}")
        else:
            print("❌ レンダラーが None です")
            
        return success
        
    except Exception as e:
        print(f"❌ initialize_stage エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_global_api():
    """グローバルAPI初期化テスト"""
    print("\n🧪 グローバルAPI初期化テスト")
    
    try:
        from engine.api import initialize_api, _global_api
        
        print("📋 initialize_api('gui') 実行中...")
        initialize_api("gui")
        
        print(f"✅ グローバルAPI初期化完了")
        print(f"🔧 renderer_type = {_global_api.renderer_type}")
        print(f"🔧 renderer = {_global_api.renderer}")
        
        return _global_api
        
    except Exception as e:
        print(f"❌ グローバルAPI初期化エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_global_initialize_stage():
    """グローバル initialize_stage テスト"""
    print("\n🧪 グローバル initialize_stage テスト")
    
    try:
        from engine.api import initialize_stage, _global_api
        
        print("📋 グローバル initialize_stage('stage01') 実行中...")
        success = initialize_stage("stage01")
        
        print(f"🎯 初期化結果: {success}")
        print(f"🔧 グローバルAPI renderer: {_global_api.renderer}")
        print(f"🔧 レンダラータイプ: {type(_global_api.renderer).__name__ if _global_api.renderer else 'None'}")
        
        return success
        
    except Exception as e:
        print(f"❌ グローバル initialize_stage エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 APILayer 詳細テスト開始")
    
    # 個別APILayerテスト
    api = test_api_layer_init()
    if api:
        stage_ok = test_initialize_stage(api)
    else:
        stage_ok = False
        
    # グローバルAPIテスト
    global_api = test_global_api()
    if global_api:
        global_stage_ok = test_global_initialize_stage()
    else:
        global_stage_ok = False
        
    print(f"\n🎯 最終結果:")
    print(f"   個別API作成: {'✅' if api else '❌'}")
    print(f"   個別Stage初期化: {'✅' if stage_ok else '❌'}")
    print(f"   グローバルAPI作成: {'✅' if global_api else '❌'}")
    print(f"   グローバルStage初期化: {'✅' if global_stage_ok else '❌'}")
    
    if api and stage_ok and global_api and global_stage_ok:
        print("🎉 全ての API Layer テストが成功しました")
    else:
        print("⚠️ API Layer に問題があります")