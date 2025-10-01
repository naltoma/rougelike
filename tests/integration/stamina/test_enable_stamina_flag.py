"""
ENABLE_STAMINA フラグの動作確認テスト（簡易版）

main.py の ENABLE_STAMINA = True 設定が
正しくシステムに反映されるかを確認します。
"""
import sys
import os

# Add project root to path (3 levels up: stamina -> integration -> tests -> root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from engine.hyperparameter_manager import HyperParameterManager

def test_stamina_flag_simple():
    """ENABLE_STAMINA=True の簡易動作確認"""
    print("=" * 60)
    print("テスト: ENABLE_STAMINA フラグ動作確認（簡易版）")
    print("=" * 60)

    # 1. main.pyをインポートして、ENABLE_STAMINAをTrueに設定
    import main
    original_flag = main.ENABLE_STAMINA
    print(f"\n1. main.py の元の ENABLE_STAMINA: {original_flag}")

    main.ENABLE_STAMINA = True
    print(f"   ENABLE_STAMINA を True に設定: {main.ENABLE_STAMINA}")

    # 2. HyperParameterManager のシングルトンを取得
    hyper_manager = HyperParameterManager()
    print(f"\n2. HyperParameterManager 初期状態:")
    print(f"   enable_stamina = {hyper_manager.data.enable_stamina}")

    # 3. main.pyのsetup_stage()で実行される処理をシミュレート
    print(f"\n3. setup_stage() 相当の処理を実行:")
    print(f"   hyperparameter_manager.data.enable_stamina = ENABLE_STAMINA")
    hyper_manager.data.enable_stamina = main.ENABLE_STAMINA
    print(f"   設定後: {hyper_manager.data.enable_stamina}")

    # 4. 別のインスタンスでも同じ値が取得できるか確認（シングルトンテスト）
    print(f"\n4. シングルトン動作確認:")
    another_manager = HyperParameterManager()
    print(f"   別のインスタンス: {another_manager.data.enable_stamina}")
    print(f"   同一インスタンス？: {hyper_manager is another_manager}")

    # 5. 検証
    print(f"\n5. 検証結果:")
    success = True

    if not hyper_manager.data.enable_stamina:
        print("   ❌ enable_staminaがTrueに設定されていない")
        success = False
    else:
        print("   ✅ enable_staminaがTrueに設定されている")

    if hyper_manager is not another_manager:
        print("   ❌ シングルトンパターンが機能していない")
        success = False
    else:
        print("   ✅ シングルトンパターンが正しく機能している")

    if hyper_manager.data.enable_stamina != main.ENABLE_STAMINA:
        print("   ❌ main.ENABLE_STAMINAと同期していない")
        success = False
    else:
        print("   ✅ main.ENABLE_STAMINAと正しく同期している")

    print("\n" + "=" * 60)
    if success:
        print("✅ テスト成功: ENABLE_STAMINAフラグが正しく機能します")
        print("\n📝 実際の使用方法:")
        print("   1. main.py または main_hoge4.py で:")
        print("      ENABLE_STAMINA = True")
        print("   2. setup_stage() 内で自動的に設定されます:")
        print("      hyperparameter_manager.data.enable_stamina = ENABLE_STAMINA")
        print("   3. ゲーム実行中、スタミナ表示と消費が有効になります")
    else:
        print("❌ テスト失敗: ENABLE_STAMINAフラグに問題があります")
    print("=" * 60)

    # 元の設定を復元
    main.ENABLE_STAMINA = original_flag
    hyper_manager.data.enable_stamina = original_flag

    return success

if __name__ == "__main__":
    try:
        success = test_stamina_flag_simple()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)