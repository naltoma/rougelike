#!/usr/bin/env python3
"""
複数学生テストデータアップロード
Multiple Students Test Data Upload

指定されたWebhook URLとステージIDに対して、N人分のテストログを生成・アップロードします。
"""

import json
import requests
import argparse
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

# テスト用学生IDリスト（実際の学生IDパターンに準拠）
STUDENT_IDS = [
    "123456A", "123456B", "123456C", "123456D", "123456E",
    "234567A", "234567B", "234567C", "234567D", "234567E",
    "345678A", "345678B", "345678C", "345678D", "345678E",
    "456789A", "456789B", "456789C", "456789D", "456789E",
    "567890A", "567890B", "567890C", "567890D", "567890E"
]

# サンプル解法コード
SAMPLE_CODES = [
    '''def solve():
    """Stage01 基本解法"""
    from engine.api import turn_right, move
    
    # 東を向いて移動
    turn_right()
    for _ in range(4):
        move()
    
    # 南を向いて移動  
    turn_right()
    for _ in range(4):
        move()''',
    
    '''def solve():
    """Stage01 コンパクト解法"""
    from engine.api import turn_right, move
    
    turn_right()
    move(); move(); move(); move()
    turn_right() 
    move(); move(); move(); move()''',
    
    '''def solve():
    """Stage01 ループ解法"""
    from engine.api import turn_right, move
    
    for direction in range(2):
        turn_right()
        for step in range(4):
            move()''',
    
    '''def solve():
    """Stage01 詳細解法（コメント多め）"""
    from engine.api import turn_right, move, see
    
    print("ゲーム開始")
    
    # まず東を向く
    turn_right()  # 右に90度回転
    print("東を向きました")
    
    # 4歩東に進む
    for i in range(4):
        move()  # 1マス前進
        print(f"東に{i+1}歩目")
    
    # 次に南を向く
    turn_right()  # さらに右に90度回転
    print("南を向きました")
    
    # 4歩南に進む
    for i in range(4):
        move()  # 1マス前進  
        print(f"南に{i+1}歩目")
    
    print("ゲーム完了")''',
    
    '''def solve():
    """Stage01 失敗例（途中で終了）"""
    from engine.api import turn_right, move
    
    # 東に少し移動して終了
    turn_right()
    move()
    move()
    # ここで諦めた...'''
]


def generate_test_log_data(student_id: str, stage_id: str, success_rate: float = 0.7) -> Dict[str, Any]:
    """
    テスト用ログデータを生成
    
    Args:
        student_id: 学生ID
        stage_id: ステージID  
        success_rate: 成功率（0.0-1.0）
        
    Returns:
        ログデータ辞書
    """
    # 成功/失敗をランダムに決定
    completed_successfully = random.random() < success_rate
    
    # 成功の場合は多めのアクション数、失敗の場合は少なめ
    if completed_successfully:
        action_count = random.randint(8, 15)
        code_lines = random.randint(20, 40)
        solve_code = random.choice(SAMPLE_CODES[:4])  # 成功コードから選択
    else:
        action_count = random.randint(0, 5)
        code_lines = random.randint(5, 15) 
        solve_code = SAMPLE_CODES[4]  # 失敗コード（途中終了）
    
    # ランダムな過去時刻を生成（過去24時間以内）
    hours_ago = random.randint(1, 24)
    minutes_ago = random.randint(0, 59)
    end_time = datetime.now() - timedelta(hours=hours_ago, minutes=minutes_ago)
    
    return {
        'student_id': student_id,
        'stage_id': stage_id,
        'end_time': end_time.isoformat(),
        'solve_code': solve_code,
        'completed_successfully': completed_successfully,
        'action_count': action_count,
        'code_lines': code_lines
    }


def send_webhook_request(webhook_url: str, data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Webhook リクエスト送信
    
    Args:
        webhook_url: WebhookエンドポイントURL
        data: 送信データ
        
    Returns:
        (成功フラグ, レスポンスメッセージ)
    """
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Multiple-Students-Test-v1.0'
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "成功"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        return False, "タイムアウト"
    except requests.exceptions.ConnectionError:
        return False, "接続エラー"
    except Exception as e:
        return False, f"送信エラー: {e}"


def main():
    parser = argparse.ArgumentParser(description='複数学生テストデータアップロード')
    parser.add_argument('webhook_url', help='Webhook エンドポイント URL')
    parser.add_argument('stage_id', help='ステージID (例: stage01)')
    parser.add_argument('-n', '--count', type=int, default=5, 
                       help='生成する学生数 (デフォルト: 5)')
    parser.add_argument('--success-rate', type=float, default=0.7,
                       help='成功率 0.0-1.0 (デフォルト: 0.7)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='詳細ログを表示')
    
    args = parser.parse_args()
    
    if args.count > len(STUDENT_IDS):
        print(f"エラー: 最大{len(STUDENT_IDS)}人まで指定可能です")
        return 1
    
    if not (0.0 <= args.success_rate <= 1.0):
        print("エラー: success-rateは0.0-1.0の範囲で指定してください")
        return 1
    
    print(f"📊 複数学生テストデータアップロード")
    print(f"   WebhookURL: {args.webhook_url}")
    print(f"   ステージID: {args.stage_id}")
    print(f"   学生数: {args.count}人")
    print(f"   成功率: {args.success_rate*100:.0f}%")
    print()
    
    # テスト用学生IDを選択
    selected_students = STUDENT_IDS[:args.count]
    
    success_count = 0
    failed_count = 0
    
    print("🚀 アップロード開始...")
    
    for i, student_id in enumerate(selected_students, 1):
        print(f"[{i:2d}/{args.count}] {student_id}: ", end="", flush=True)
        
        # テストデータ生成
        test_data = generate_test_log_data(student_id, args.stage_id, args.success_rate)
        
        if args.verbose:
            print(f"\n  データ: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        # Webhook送信
        success, message = send_webhook_request(args.webhook_url, test_data)
        
        if success:
            success_count += 1
            completion_status = "✅" if test_data['completed_successfully'] else "❌"
            print(f"{completion_status} 成功 (アクション数: {test_data['action_count']}, "
                  f"コード行数: {test_data['code_lines']})")
        else:
            failed_count += 1
            print(f"❌ 失敗: {message}")
    
    print()
    print(f"📋 結果サマリー:")
    print(f"   アップロード成功: {success_count}人")
    print(f"   アップロード失敗: {failed_count}人")
    print(f"   成功率: {success_count/args.count*100:.1f}%")
    
    if success_count > 0:
        print()
        print(f"✅ Google Sheetsで「ローグライク演習_セッションログ_{args.stage_id}」を確認してください")
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    exit(main())