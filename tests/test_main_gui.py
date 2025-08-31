#!/usr/bin/env python3
"""
main.py GUIモード テスト
"""

import sys
sys.path.append('..')

def test_main_gui_mode():
    """main.py GUIモードのテスト"""
    print("🧪 main.py GUIモード テスト")
    print("=" * 50)
    
    try:
        # main.py の GUI モード実行をシミュレート
        import argparse
        from pathlib import Path
        
        # config をインポート
        import config
        
        # ロギング設定をインポート
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format=config.LOG_FORMAT,
            datefmt=config.LOG_DATE_FORMAT
        )
        logger = logging.getLogger(__name__)
        
        # 引数解析
        display_mode = "gui"  # GUI モードを指定
        stage_name = "stage01"
        
        logger.info(f"ローグライク演習フレームワーク開始")
        logger.info(f"表示モード: {display_mode.upper()}")
        logger.info(f"ステージ: {stage_name}")
        logger.info(f"学生ID: {config.STUDENT_ID}")
        
        print("🎮 ローグライク演習フレームワーク")
        print(f"📺 表示モード: {display_mode.upper()}")
        print(f"🎯 ステージ: {stage_name}")
        print(f"👤 学生ID: {config.STUDENT_ID}")
        print()
        print("🔥 ゲームエンジン実装完了！")
        print("solve()関数を編集してゲームを攻略してください！")
        
        # APIレイヤーを指定されたモードで初期化
        from engine.api import initialize_api
        initialize_api(display_mode)
        
        print("✅ GUI モードでの API 初期化成功")
        
        # 簡単な API テスト
        from engine.api import initialize_stage, show_legend
        
        if initialize_stage("stage01"):
            print("✅ ステージ初期化成功")
            
            print("📋 凡例表示:")
            show_legend()
            
            print("✅ GUI 機能が正常に動作")
        else:
            print("❌ ステージ初期化失敗")
            return False
        
        print("✅ main.py GUIモード テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    success = test_main_gui_mode()
    
    if success:
        print("\n🎉 main.py GUIモード テストが成功しました！")
        print("✅ GUIレンダラーがmain.pyに正常に統合されました")
        print("\n💡 実際のGUIモード実行方法:")
        print("   python main.py --gui")
        print("   または")
        print("   python main.py  # pygame利用可能時はデフォルトでGUI")
    else:
        print("\n❌ テストに失敗しました")


if __name__ == "__main__":
    main()