"""
SolutionPath Data Model

A*アルゴリズムが生成するプレイヤー行動シーケンスのデータモデル。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import hashlib


@dataclass
class SolutionPath:
    """解法例データモデル"""
    stage_file: str
    action_sequence: List[str]
    expected_success: bool
    actual_success: bool
    total_steps: int
    failure_step: Optional[int] = None
    generation_timestamp: datetime = field(default_factory=datetime.now)
    execution_timestamp: Optional[datetime] = None

    def __post_init__(self):
        """バリデーション"""
        if not self.stage_file:
            raise ValueError("stage_file cannot be empty")

        if not self.action_sequence:
            raise ValueError("action_sequence cannot be empty")

        if self.total_steps != len(self.action_sequence):
            raise ValueError("total_steps must equal length of action_sequence")

        if self.total_steps <= 0:
            raise ValueError("total_steps must be positive")

        # アクション検証
        valid_actions = {"move", "turn_left", "turn_right", "attack", "pickup", "wait", "dispose"}
        invalid_actions = [action for action in self.action_sequence if action not in valid_actions]
        if invalid_actions:
            raise ValueError(f"Invalid actions found: {invalid_actions}")

        # failure_step検証
        if self.failure_step is not None:
            if self.failure_step < 0 or self.failure_step >= self.total_steps:
                raise ValueError("failure_step must be within valid step range")

            if self.actual_success:
                raise ValueError("Cannot have failure_step when actual_success is True")

    @property
    def solution_id(self) -> str:
        """解法例の一意識別子"""
        content = f"{self.stage_file}:{','.join(self.action_sequence)}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    @property
    def success_rate(self) -> float:
        """成功率（予測 vs 実際）"""
        if self.expected_success and self.actual_success:
            return 1.0
        elif not self.expected_success and not self.actual_success:
            return 1.0
        else:
            return 0.0

    @property
    def is_validated(self) -> bool:
        """検証済みかどうか"""
        return self.execution_timestamp is not None

    def get_action_at_step(self, step: int) -> str:
        """指定ステップのアクションを取得"""
        if step < 0 or step >= len(self.action_sequence):
            raise IndexError(f"Step {step} out of range")
        return self.action_sequence[step]

    def get_actions_up_to_failure(self) -> List[str]:
        """失敗ポイントまでのアクションを取得"""
        if self.failure_step is None:
            return self.action_sequence.copy()
        return self.action_sequence[:self.failure_step + 1]

    def get_remaining_actions(self, from_step: int) -> List[str]:
        """指定ステップ以降のアクションを取得"""
        if from_step < 0 or from_step >= len(self.action_sequence):
            return []
        return self.action_sequence[from_step:]

    def mark_execution_complete(self, success: bool, failure_step: Optional[int] = None) -> None:
        """実行完了をマーク"""
        self.actual_success = success
        self.failure_step = failure_step
        self.execution_timestamp = datetime.now()

        # バリデーション
        if failure_step is not None and success:
            raise ValueError("Cannot have failure_step when marking as successful")

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "solution_id": self.solution_id,
            "stage_file": self.stage_file,
            "action_sequence": self.action_sequence,
            "expected_success": self.expected_success,
            "actual_success": self.actual_success,
            "total_steps": self.total_steps,
            "failure_step": self.failure_step,
            "generation_timestamp": self.generation_timestamp.isoformat(),
            "execution_timestamp": self.execution_timestamp.isoformat() if self.execution_timestamp else None,
            "success_rate": self.success_rate,
            "is_validated": self.is_validated
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SolutionPath':
        """辞書から作成"""
        generation_timestamp = datetime.fromisoformat(data["generation_timestamp"])
        execution_timestamp = None
        if data.get("execution_timestamp"):
            execution_timestamp = datetime.fromisoformat(data["execution_timestamp"])

        return cls(
            stage_file=data["stage_file"],
            action_sequence=data["action_sequence"],
            expected_success=data["expected_success"],
            actual_success=data["actual_success"],
            total_steps=data["total_steps"],
            failure_step=data.get("failure_step"),
            generation_timestamp=generation_timestamp,
            execution_timestamp=execution_timestamp
        )

    @classmethod
    def create_from_actions(cls, stage_file: str, actions: List[str], expected_success: bool = True) -> 'SolutionPath':
        """アクション列から解法例を作成"""
        return cls(
            stage_file=stage_file,
            action_sequence=actions,
            expected_success=expected_success,
            actual_success=False,  # 未実行
            total_steps=len(actions)
        )

    def __str__(self) -> str:
        """文字列表現"""
        status = "✓" if self.actual_success else "✗" if self.is_validated else "?"
        return f"Solution {self.solution_id} [{status}]: {len(self.action_sequence)} steps for {self.stage_file}"

    def __repr__(self) -> str:
        """デバッグ表現"""
        return (f"SolutionPath(id={self.solution_id}, stage={self.stage_file}, "
                f"steps={self.total_steps}, expected={self.expected_success}, "
                f"actual={self.actual_success}, validated={self.is_validated})")


def analyze_solution_patterns(solutions: List[SolutionPath]) -> dict:
    """解法例パターン分析"""
    if not solutions:
        return {"total": 0}

    total = len(solutions)
    validated = sum(1 for s in solutions if s.is_validated)
    successful = sum(1 for s in solutions if s.actual_success)
    avg_steps = sum(s.total_steps for s in solutions) / total

    # アクションパターン分析
    action_counts = {}
    for solution in solutions:
        for action in solution.action_sequence:
            action_counts[action] = action_counts.get(action, 0) + 1

    most_common_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)

    return {
        "total": total,
        "validated": validated,
        "successful": successful,
        "success_rate": successful / validated if validated > 0 else 0,
        "avg_steps": avg_steps,
        "most_common_actions": most_common_actions[:5],
        "validation_rate": validated / total
    }