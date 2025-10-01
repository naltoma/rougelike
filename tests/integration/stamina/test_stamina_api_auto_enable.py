"""
ENABLE_STAMINA = True 時の get_stamina() 自動有効化テスト

ステージYAMLにget_staminaが記載されていなくても、
ENABLE_STAMINA = True の場合は自動的に利用可能になることを確認します。
"""
import sys
import os

# Add project root to path (3 levels up: stamina -> integration -> tests -> root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

def test_get_stamina_auto_enable():
    """get_stamina() 自動有効化の確認"""
    print("=" * 60)
    print("テスト: ENABLE_STAMINA=True で get_stamina() 自動有効化")
    print("=" * 60)

    # 1. ENABLE_STAMINAをTrueに設定
    import main
    main.ENABLE_STAMINA = True
    print(f"\n1. ENABLE_STAMINA = {main.ENABLE_STAMINA}")

    # 2. HyperParameterManagerを設定
    from engine.hyperparameter_manager import HyperParameterManager
    hyper_manager = HyperParameterManager()
    hyper_manager.data.enable_stamina = main.ENABLE_STAMINA
    print(f"   hyper_manager.data.enable_stamina = {hyper_manager.data.enable_stamina}")

    # 3. APIレイヤー初期化
    from engine.api import initialize_api, initialize_stage, get_stamina
    initialize_api("cui")
    print(f"\n2. APIレイヤー初期化完了")

    # 4. ステージ初期化（stage01はallowed_apisにget_staminaが含まれていない）
    print(f"\n3. ステージ初期化: stage01")
    initialize_stage("stage01")

    # 5. allowed_apisを確認
    from engine.api import _global_api
    print(f"\n4. allowed_apis確認:")
    print(f"   {_global_api.allowed_apis}")

    # 6. get_stamina() を呼び出してみる
    print(f"\n5. get_stamina() 呼び出しテスト:")
    try:
        stamina = get_stamina()
        print(f"   ✅ get_stamina() 成功: {stamina}")
        success = True
    except Exception as e:
        print(f"   ❌ get_stamina() 失敗: {e}")
        success = False

    # 7. 検証
    print(f"\n6. 検証結果:")
    if "get_stamina" not in _global_api.allowed_apis:
        print("   ❌ get_stamina が allowed_apis に含まれていない")
        success = False
    else:
        print("   ✅ get_stamina が allowed_apis に自動追加されている")

    if not success:
        print("   ❌ get_stamina() の呼び出しに失敗")
    else:
        print("   ✅ get_stamina() の呼び出しに成功")

    print("\n" + "=" * 60)
    if success:
        print("✅ テスト成功: ENABLE_STAMINA=True で get_stamina() が自動有効化されます")
        print("\n📝 確認事項:")
        print("   • ENABLE_STAMINA = True の設定")
        print("   • ステージYAMLに記載がなくても get_stamina が利用可能")
        print("   • allowed_apis に自動追加される")
    else:
        print("❌ テスト失敗: get_stamina() の自動有効化に問題があります")
    print("=" * 60)

    return success

if __name__ == "__main__":
    try:
        success = test_get_stamina_auto_enable()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)