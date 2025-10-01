"""
T027: 既存13ステージ動作確認
各ステージが正常にロードされ、基本的なアクションが実行できることを確認
"""
import sys
import os

# Add project root to path (3 levels up: stamina -> integration -> tests -> root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from engine.api import initialize_api, initialize_stage, move, turn_left
from engine.hyperparameter_manager import HyperParameterManager

def test_all_stages():
    """既存13ステージの動作確認"""
    # スタミナ無効化（デフォルト動作）
    hyper_manager = HyperParameterManager()
    hyper_manager.data.enable_stamina = False

    # API初期化
    initialize_api(renderer_type="cui", enable_progression=False, enable_session_logging=False)

    stage_ids = [f"stage{str(i).zfill(2)}" for i in range(1, 14)]

    print("=" * 60)
    print("既存13ステージ動作確認（ENABLE_STAMINA=False）")
    print("=" * 60)

    results = []

    for stage_id in stage_ids:
        try:
            # ステージ初期化
            initialize_stage(stage_id)

            # 基本的なアクション実行
            turn_left()
            turn_left()
            move()

            results.append((stage_id, "✅ OK"))
            print(f"{stage_id}: ✅ OK - 正常にロード・アクション実行")

        except Exception as e:
            results.append((stage_id, f"❌ ERROR: {str(e)[:50]}"))
            print(f"{stage_id}: ❌ ERROR - {str(e)[:100]}")

    print("=" * 60)
    print("結果サマリー")
    print("=" * 60)

    success_count = sum(1 for _, result in results if result.startswith("✅"))
    total_count = len(results)

    for stage_id, result in results:
        print(f"{stage_id}: {result}")

    print("=" * 60)
    print(f"合格: {success_count}/{total_count} ステージ")
    print("=" * 60)

    if success_count == total_count:
        print("✅ 全ステージが正常動作（後方互換性確認完了）")
    else:
        print(f"⚠️  {total_count - success_count}個のステージでエラー")

    return success_count == total_count


if __name__ == "__main__":
    success = test_all_stages()
    exit(0 if success else 1)