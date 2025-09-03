#!/usr/bin/env python3
"""
solve()関数の動的解析とステップ実行サポート
"""

import ast
import inspect
from typing import List, Dict, Any, Optional, Tuple

class SolveAction:
    """solve()関数内の1つのアクション"""
    def __init__(self, action_type: str, line_number: int, source_line: str):
        self.action_type = action_type  # turn_right, move, turn_left, attack, pickup, see
        self.line_number = line_number
        self.source_line = source_line.strip()
        
    def __repr__(self):
        return f"SolveAction({self.action_type}, line {self.line_number})"

class SolveParser:
    """solve()関数の解析とステップ実行管理"""
    
    # 認識するAPIアクション
    API_ACTIONS = {
        'turn_right', 'turn_left', 'move', 'attack', 'pickup', 'see'
    }
    
    def __init__(self):
        self.actions: List[SolveAction] = []
        self.current_step = 0
        self.total_steps = 0
        
    def parse_solve_function(self, solve_func) -> List[SolveAction]:
        """solve()関数のソースコードを解析してアクションリストを生成"""
        try:
            # ソースコードを取得
            source = inspect.getsource(solve_func)
            source_lines = source.split('\n')
            
            # インデントを正規化
            import textwrap
            source = textwrap.dedent(source)
            
            # ASTでパース
            tree = ast.parse(source)
            
            actions = []
            
            # AST走査でAPI呼び出しを探索
            self._process_ast_node(tree, source_lines, actions)
            
            # 重複除去（同じ行番号で同じアクションタイプは1つに統合）
            actions = self._deduplicate_actions(actions)
            
            # 行番号でソート
            actions.sort(key=lambda x: x.line_number)
            
            self.actions = actions
            self.total_steps = len(actions)
            self.current_step = 0
            
            return actions
            
        except Exception as e:
            print(f"⚠️ solve()関数の解析エラー: {e}")
            return []
    
    def _process_ast_node(self, node, source_lines: List[str], actions: List[SolveAction]):
        """ASTノードを再帰的に処理"""
        if isinstance(node, ast.FunctionDef):
            # 関数定義内の処理
            for child in node.body:
                self._process_ast_node(child, source_lines, actions)
        elif isinstance(node, ast.For):
            # forループの処理
            loop_actions = self._extract_actions_from_loop(node, source_lines)
            actions.extend(loop_actions)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            # 単純な関数呼び出し
            action = self._extract_action_from_call(node.value, source_lines)
            if action:
                actions.append(action)
        elif hasattr(node, 'body'):
            # その他のボディを持つノード（if, while等）
            for child in node.body:
                self._process_ast_node(child, source_lines, actions)
        elif hasattr(node, 'orelse'):
            # else節を持つノード
            for child in node.orelse:
                self._process_ast_node(child, source_lines, actions)
    
    def _deduplicate_actions(self, actions: List[SolveAction]) -> List[SolveAction]:
        """重複するアクションを除去（ループ展開は保持）"""
        # ループで展開されたアクションは保持し、単純な重複のみ除去
        seen = set()
        deduplicated = []
        
        for action in actions:
            # ループアクションかチェック
            is_loop_action = "ループ" in action.source_line
            
            if is_loop_action:
                # ループアクションはそのまま追加
                deduplicated.append(action)
            else:
                # 非ループアクションは重複除去
                key = (action.action_type, action.line_number)
                if key not in seen:
                    seen.add(key)
                    deduplicated.append(action)
        
        return deduplicated
    
    def _extract_action_from_call(self, node: ast.Call, source_lines: List[str]) -> Optional[SolveAction]:
        """AST Callノードからアクションを抽出"""
        try:
            # 関数名を取得
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            else:
                return None
            
            # APIアクションかチェック
            if func_name in self.API_ACTIONS:
                line_number = node.lineno
                # ソースラインを取得（1-indexed）
                if line_number <= len(source_lines):
                    source_line = source_lines[line_number - 1]
                    # コメントアウトされていないかチェック
                    if not source_line.strip().startswith('#'):
                        return SolveAction(func_name, line_number, source_line)
            
            return None
            
        except Exception:
            return None
    
    def _extract_actions_from_loop(self, node: ast.For, source_lines: List[str]) -> List[SolveAction]:
        """forループ内のアクションを展開"""
        actions = []
        
        try:
            # ループ回数を推定（簡単な場合のみ）
            iterations = self._estimate_loop_iterations(node)
            
            # ループ内のアクションを探索
            for body_node in node.body:
                if isinstance(body_node, ast.Expr) and isinstance(body_node.value, ast.Call):
                    action = self._extract_action_from_call(body_node.value, source_lines)
                    if action:
                        # ループ回数分複製
                        for i in range(iterations):
                            loop_action = SolveAction(
                                action.action_type,
                                action.line_number,
                                f"{action.source_line} # ループ {i+1}/{iterations}"
                            )
                            actions.append(loop_action)
            
        except Exception:
            pass
        
        return actions
    
    def _estimate_loop_iterations(self, node: ast.For) -> int:
        """ループ回数を推定（簡単なrange()の場合のみ）"""
        try:
            if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
                if node.iter.func.id == 'range':
                    if len(node.iter.args) == 1:
                        # range(n)
                        if isinstance(node.iter.args[0], ast.Constant):
                            return node.iter.args[0].value
                        elif isinstance(node.iter.args[0], ast.Num):  # Python 3.7以前
                            return node.iter.args[0].n
            elif isinstance(node.iter, ast.Name) and node.iter.id == '_':
                # for _ in range(n): の _ パターンをサポート
                return 4  # デフォルトで4を想定（後で改善予定）
            return 4  # デフォルトは4回（range(4)を想定）
        except Exception:
            return 4
    
    def get_next_action(self) -> Optional[SolveAction]:
        """次に実行するアクションを取得"""
        if self.current_step < len(self.actions):
            action = self.actions[self.current_step]
            self.current_step += 1
            return action
        return None
    
    def reset(self):
        """ステップカウンターをリセット"""
        self.current_step = 0
    
    def get_remaining_steps(self) -> int:
        """残りステップ数"""
        return max(0, len(self.actions) - self.current_step)
    
    def is_completed(self) -> bool:
        """全ステップ完了かチェック"""
        return self.current_step >= len(self.actions)
    
    def get_progress_info(self) -> Dict[str, Any]:
        """進捗情報を取得"""
        return {
            'current_step': self.current_step,
            'total_steps': len(self.actions),
            'remaining_steps': self.get_remaining_steps(),
            'completed': self.is_completed(),
            'progress_percent': (self.current_step / max(1, len(self.actions))) * 100
        }
    
    def get_action_summary(self) -> List[Dict[str, Any]]:
        """アクション一覧のサマリーを取得"""
        return [
            {
                'step': i + 1,
                'action': action.action_type,
                'line': action.line_number,
                'source': action.source_line,
                'executed': i < self.current_step
            }
            for i, action in enumerate(self.actions)
        ]

def parse_solve_function(solve_func) -> SolveParser:
    """solve()関数を解析してSolveParserを返す"""
    parser = SolveParser()
    parser.parse_solve_function(solve_func)
    return parser

# デバッグ用のテスト関数
def test_solve_parser():
    """SolveParserのテスト"""
    def sample_solve():
        from engine.api import turn_right, move
        
        print("🎮 自動解法を実行します...")
        
        # 東を向いて移動
        turn_right()  # 東を向く
        for _ in range(4):
            move()    # 東に移動
        
        # 南を向いて移動（コメントアウト）
        #turn_right()  # 南を向く  
        #for _ in range(4):
        #    move()    # 南に移動
    
    parser = parse_solve_function(sample_solve)
    
    print(f"📊 解析結果:")
    print(f"   総ステップ数: {parser.total_steps}")
    
    for action in parser.actions:
        print(f"   {action}")
    
    print(f"\n🔍 ステップ実行テスト:")
    while not parser.is_completed():
        action = parser.get_next_action()
        if action:
            print(f"   ステップ {parser.current_step}: {action.action_type} (line {action.line_number})")

if __name__ == "__main__":
    test_solve_parser()