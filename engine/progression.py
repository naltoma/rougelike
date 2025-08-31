"""
学習進捗管理システム
Progression Management for Educational Framework
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import threading
import time

from . import GameState, GameStatus, Position


class SkillLevel(Enum):
    """スキルレベル定義"""
    BEGINNER = "beginner"      # 初心者
    INTERMEDIATE = "intermediate"  # 中級者  
    ADVANCED = "advanced"      # 上級者
    EXPERT = "expert"          # エキスパート


class MetricType(Enum):
    """評価メトリックタイプ"""
    EFFICIENCY = "efficiency"        # 効率性（最小ターン数）
    ACCURACY = "accuracy"           # 正確性（エラー率）
    SPEED = "speed"                 # 速度（実行時間）
    PROBLEM_SOLVING = "problem_solving"  # 問題解決力
    ALGORITHM_QUALITY = "algorithm_quality"  # アルゴリズム品質


@dataclass
class StageAttempt:
    """ステージ挑戦記録"""
    stage_id: str
    attempt_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[GameStatus] = None
    turns_used: int = 0
    max_turns: int = 0
    actions_taken: List[str] = field(default_factory=list)
    errors_made: List[str] = field(default_factory=list)
    hints_used: int = 0
    success: bool = False
    
    @property
    def duration(self) -> Optional[timedelta]:
        """実行時間を取得"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def efficiency_score(self) -> float:
        """効率性スコア（0-1）"""
        if self.max_turns == 0:
            return 0.0
        return max(0.0, 1.0 - (self.turns_used / self.max_turns))
    
    @property
    def accuracy_score(self) -> float:
        """正確性スコア（0-1）"""
        total_actions = len(self.actions_taken)
        if total_actions == 0:
            return 1.0
        error_rate = len(self.errors_made) / total_actions
        return max(0.0, 1.0 - error_rate)


@dataclass
class SkillProgress:
    """スキル進捗"""
    skill_type: MetricType
    current_level: SkillLevel
    experience_points: float = 0.0
    level_progress: float = 0.0  # 現在レベル内の進捗（0-1）
    
    def add_experience(self, points: float) -> bool:
        """経験値を追加してレベルアップ判定"""
        self.experience_points += points
        
        # レベルアップ判定とレベル更新
        old_level = self.current_level
        self._update_level()
        
        return self.current_level != old_level
    
    def _update_level(self) -> None:
        """経験値に基づいてレベルを更新"""
        # レベル閾値定義
        level_thresholds = {
            SkillLevel.BEGINNER: 0,
            SkillLevel.INTERMEDIATE: 100,
            SkillLevel.ADVANCED: 300,
            SkillLevel.EXPERT: 600
        }
        
        # 現在のレベルを決定
        for level, threshold in reversed(list(level_thresholds.items())):
            if self.experience_points >= threshold:
                self.current_level = level
                
                # 次のレベルまでの進捗を計算
                current_threshold = threshold
                if level == SkillLevel.EXPERT:
                    # エキスパートは上限なし
                    self.level_progress = min(1.0, (self.experience_points - current_threshold) / 200)
                else:
                    # 次のレベルの閾値を取得
                    level_values = list(level_thresholds.values())
                    current_index = level_values.index(current_threshold)
                    if current_index < len(level_values) - 1:
                        next_threshold = level_values[current_index + 1]
                        progress_range = next_threshold - current_threshold
                        self.level_progress = (self.experience_points - current_threshold) / progress_range
                    else:
                        self.level_progress = 1.0
                break


@dataclass
class LearningMetrics:
    """学習メトリクス"""
    total_attempts: int = 0
    successful_attempts: int = 0
    total_play_time: timedelta = field(default_factory=lambda: timedelta())
    average_efficiency: float = 0.0
    average_accuracy: float = 0.0
    improvement_rate: float = 0.0  # 改善率
    consistency_score: float = 0.0  # 一貫性スコア
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_attempts == 0:
            return 0.0
        return self.successful_attempts / self.total_attempts
    
    def update_from_attempts(self, attempts: List[StageAttempt]) -> None:
        """挑戦記録からメトリクスを更新"""
        if not attempts:
            return
        
        self.total_attempts = len(attempts)
        self.successful_attempts = sum(1 for a in attempts if a.success)
        
        # 平均効率性
        efficiencies = [a.efficiency_score for a in attempts if a.success]
        self.average_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else 0.0
        
        # 平均正確性
        accuracies = [a.accuracy_score for a in attempts]
        self.average_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
        
        # 総プレイ時間
        durations = [a.duration for a in attempts if a.duration]
        self.total_play_time = sum(durations, timedelta()) if durations else timedelta()
        
        # 改善率（最初と最後の比較）
        if len(attempts) >= 2:
            first_success = next((a for a in attempts if a.success), None)
            last_success = next((a for a in reversed(attempts) if a.success), None)
            
            if first_success and last_success and first_success != last_success:
                first_score = (first_success.efficiency_score + first_success.accuracy_score) / 2
                last_score = (last_success.efficiency_score + last_success.accuracy_score) / 2
                self.improvement_rate = (last_score - first_score) / first_score if first_score > 0 else 0.0
        
        # 一貫性スコア（成功時のスコアの分散の逆数）
        if len(efficiencies) >= 2:
            efficiency_variance = sum((e - self.average_efficiency) ** 2 for e in efficiencies) / len(efficiencies)
            self.consistency_score = 1.0 / (1.0 + efficiency_variance)


@dataclass 
class StudentProgress:
    """学生の進捗データ"""
    student_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # ステージ別の挑戦記録
    stage_attempts: Dict[str, List[StageAttempt]] = field(default_factory=dict)
    
    # スキル進捗
    skills: Dict[MetricType, SkillProgress] = field(default_factory=dict)
    
    # 学習メトリクス（ステージ別）
    stage_metrics: Dict[str, LearningMetrics] = field(default_factory=dict)
    
    # 全体メトリクス
    overall_metrics: LearningMetrics = field(default_factory=LearningMetrics)
    
    def __post_init__(self):
        """初期化後処理"""
        # 全スキルタイプの初期化
        for metric_type in MetricType:
            if metric_type not in self.skills:
                self.skills[metric_type] = SkillProgress(
                    skill_type=metric_type,
                    current_level=SkillLevel.BEGINNER
                )
    
    def add_stage_attempt(self, attempt: StageAttempt) -> None:
        """ステージ挑戦を記録"""
        stage_id = attempt.stage_id
        
        # ステージ別記録を追加
        if stage_id not in self.stage_attempts:
            self.stage_attempts[stage_id] = []
        
        # 挑戦番号を設定
        attempt.attempt_number = len(self.stage_attempts[stage_id]) + 1
        self.stage_attempts[stage_id].append(attempt)
        
        # メトリクス更新
        self._update_stage_metrics(stage_id)
        self._update_overall_metrics()
        self._update_skills(attempt)
        
        self.last_updated = datetime.now()
    
    def _update_stage_metrics(self, stage_id: str) -> None:
        """ステージメトリクスを更新"""
        if stage_id not in self.stage_attempts:
            return
        
        if stage_id not in self.stage_metrics:
            self.stage_metrics[stage_id] = LearningMetrics()
        
        self.stage_metrics[stage_id].update_from_attempts(self.stage_attempts[stage_id])
    
    def _update_overall_metrics(self) -> None:
        """全体メトリクスを更新"""
        all_attempts = []
        for attempts in self.stage_attempts.values():
            all_attempts.extend(attempts)
        
        self.overall_metrics.update_from_attempts(all_attempts)
    
    def _update_skills(self, attempt: StageAttempt) -> None:
        """スキル経験値を更新"""
        if not attempt.success:
            return
        
        # 効率性経験値
        efficiency_xp = attempt.efficiency_score * 50
        self.skills[MetricType.EFFICIENCY].add_experience(efficiency_xp)
        
        # 正確性経験値
        accuracy_xp = attempt.accuracy_score * 40
        self.skills[MetricType.ACCURACY].add_experience(accuracy_xp)
        
        # 問題解決力経験値（成功時のベース経験値）
        problem_solving_xp = 30
        if attempt.hints_used == 0:
            problem_solving_xp += 20  # ヒントなしボーナス
        self.skills[MetricType.PROBLEM_SOLVING].add_experience(problem_solving_xp)
        
        # 速度経験値
        if attempt.duration:
            # 実行時間が短いほど高い経験値
            max_time_bonus = 60  # 最大60秒想定
            time_seconds = attempt.duration.total_seconds()
            speed_bonus = max(0, max_time_bonus - time_seconds) / max_time_bonus
            speed_xp = speed_bonus * 35
            self.skills[MetricType.SPEED].add_experience(speed_xp)
        
        # アルゴリズム品質経験値（効率性と正確性の組み合わせ）
        algorithm_xp = (attempt.efficiency_score + attempt.accuracy_score) / 2 * 45
        self.skills[MetricType.ALGORITHM_QUALITY].add_experience(algorithm_xp)
    
    def get_stage_progress_summary(self, stage_id: str) -> Optional[Dict[str, Any]]:
        """ステージ進捗サマリーを取得"""
        if stage_id not in self.stage_attempts:
            return None
        
        attempts = self.stage_attempts[stage_id]
        metrics = self.stage_metrics.get(stage_id)
        
        if not attempts or not metrics:
            return None
        
        latest_attempt = attempts[-1]
        best_attempt = max([a for a in attempts if a.success], 
                          key=lambda x: x.efficiency_score, default=None)
        
        return {
            "stage_id": stage_id,
            "total_attempts": len(attempts),
            "success_rate": metrics.success_rate,
            "latest_success": latest_attempt.success,
            "best_efficiency": best_attempt.efficiency_score if best_attempt else 0.0,
            "average_efficiency": metrics.average_efficiency,
            "improvement_rate": metrics.improvement_rate,
            "total_play_time": str(metrics.total_play_time),
            "skill_levels": {
                skill.skill_type.value: {
                    "level": skill.current_level.value,
                    "progress": skill.level_progress,
                    "xp": skill.experience_points
                } for skill in self.skills.values()
            }
        }
    
    def get_overall_summary(self) -> Dict[str, Any]:
        """全体進捗サマリーを取得"""
        return {
            "student_id": self.student_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "stages_attempted": len(self.stage_attempts),
            "total_attempts": self.overall_metrics.total_attempts,
            "overall_success_rate": self.overall_metrics.success_rate,
            "total_play_time": str(self.overall_metrics.total_play_time),
            "average_efficiency": self.overall_metrics.average_efficiency,
            "improvement_rate": self.overall_metrics.improvement_rate,
            "skills": {
                skill.skill_type.value: {
                    "level": skill.current_level.value,
                    "progress": skill.level_progress,
                    "xp": skill.experience_points
                } for skill in self.skills.values()
            },
            "stage_summaries": {
                stage_id: self.get_stage_progress_summary(stage_id)
                for stage_id in self.stage_attempts.keys()
            }
        }


class ProgressionManager:
    """進捗管理マネージャー"""
    
    def __init__(self, data_dir: str = "data/progression"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[StageAttempt] = None
        self.student_progress: Optional[StudentProgress] = None
        self._lock = threading.Lock()
        
        print(f"📊 進捗管理システム初期化: {self.data_dir}")
    
    def initialize_student(self, student_id: str) -> StudentProgress:
        """学生の進捗を初期化または読み込み"""
        with self._lock:
            # 既存データの読み込み
            progress_file = self.data_dir / f"{student_id}.json"
            
            if progress_file.exists():
                self.student_progress = self._load_progress(progress_file)
                print(f"📊 学生進捗を読み込み: {student_id}")
            else:
                self.student_progress = StudentProgress(student_id=student_id)
                print(f"📊 新しい学生進捗を作成: {student_id}")
            
            return self.student_progress
    
    def start_stage_attempt(self, student_id: str, stage_id: str) -> StageAttempt:
        """ステージ挑戦を開始"""
        if not self.student_progress or self.student_progress.student_id != student_id:
            self.initialize_student(student_id)
        
        with self._lock:
            self.current_session = StageAttempt(
                stage_id=stage_id,
                attempt_number=0,  # add_stage_attempt で設定される
                start_time=datetime.now()
            )
            
            print(f"🎯 ステージ挑戦開始: {stage_id}")
            return self.current_session
    
    def record_action(self, action: str) -> None:
        """アクションを記録"""
        if self.current_session:
            with self._lock:
                self.current_session.actions_taken.append(action)
    
    def record_error(self, error_message: str) -> None:
        """エラーを記録"""
        if self.current_session:
            with self._lock:
                self.current_session.errors_made.append(error_message)
    
    def use_hint(self) -> None:
        """ヒント使用を記録"""
        if self.current_session:
            with self._lock:
                self.current_session.hints_used += 1
    
    def end_stage_attempt(self, game_state: GameState) -> None:
        """ステージ挑戦を終了"""
        if not self.current_session or not self.student_progress:
            return
        
        with self._lock:
            # セッション情報を更新
            self.current_session.end_time = datetime.now()
            self.current_session.result = game_state.status
            self.current_session.turns_used = game_state.turn_count
            self.current_session.max_turns = game_state.max_turns
            self.current_session.success = (game_state.status == GameStatus.WON)
            
            # 学生進捗に追加
            self.student_progress.add_stage_attempt(self.current_session)
            
            # データを保存
            self._save_progress()
            
            print(f"🏁 ステージ挑戦終了: {self.current_session.stage_id} - {'成功' if self.current_session.success else '失敗'}")
            
            # レベルアップ通知
            self._check_level_ups()
            
            self.current_session = None
    
    def _check_level_ups(self) -> None:
        """レベルアップをチェックして通知"""
        if not self.student_progress:
            return
        
        for skill_type, skill in self.student_progress.skills.items():
            if skill.level_progress >= 1.0 and skill.current_level != SkillLevel.EXPERT:
                print(f"🎉 レベルアップ！ {skill_type.value}: {skill.current_level.value}")
    
    def get_progress_report(self, stage_id: Optional[str] = None) -> Dict[str, Any]:
        """進捗レポートを取得"""
        if not self.student_progress:
            return {}
        
        if stage_id:
            return self.student_progress.get_stage_progress_summary(stage_id) or {}
        else:
            return self.student_progress.get_overall_summary()
    
    def get_recommendations(self) -> List[str]:
        """学習推奨事項を取得"""
        if not self.student_progress:
            return []
        
        recommendations = []
        
        # スキルレベルに基づく推奨
        for skill_type, skill in self.student_progress.skills.items():
            if skill.current_level == SkillLevel.BEGINNER and skill.experience_points < 50:
                if skill_type == MetricType.EFFICIENCY:
                    recommendations.append("💡 より少ないターンでゴールを目指しましょう")
                elif skill_type == MetricType.ACCURACY:
                    recommendations.append("💡 エラーを減らすよう慎重に行動しましょう")
                elif skill_type == MetricType.PROBLEM_SOLVING:
                    recommendations.append("💡 ヒントに頼らず自力で解決してみましょう")
        
        # 成功率に基づく推奨
        if self.student_progress.overall_metrics.success_rate < 0.5:
            recommendations.append("💡 基本的なアルゴリズムを復習しましょう")
        
        # 改善率に基づく推奨
        if self.student_progress.overall_metrics.improvement_rate < 0.1:
            recommendations.append("💡 異なるアプローチを試してみましょう")
        
        return recommendations
    
    def _save_progress(self) -> None:
        """進捗データを保存"""
        if not self.student_progress:
            return
        
        progress_file = self.data_dir / f"{self.student_progress.student_id}.json"
        
        try:
            # JSONシリアライズ用にデータを変換
            data = self._serialize_progress(self.student_progress)
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ 進捗保存エラー: {e}")
    
    def _load_progress(self, progress_file: Path) -> StudentProgress:
        """進捗データを読み込み"""
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self._deserialize_progress(data)
            
        except Exception as e:
            print(f"❌ 進捗読み込みエラー: {e}")
            # エラー時は新しい進捗を作成
            student_id = progress_file.stem
            return StudentProgress(student_id=student_id)
    
    def _serialize_progress(self, progress: StudentProgress) -> Dict[str, Any]:
        """進捗データをJSONシリアライズ可能な形式に変換"""
        return {
            "student_id": progress.student_id,
            "created_at": progress.created_at.isoformat(),
            "last_updated": progress.last_updated.isoformat(),
            "stage_attempts": {
                stage_id: [self._serialize_attempt(attempt) for attempt in attempts]
                for stage_id, attempts in progress.stage_attempts.items()
            },
            "skills": {
                skill_type.value: {
                    "current_level": skill.current_level.value,
                    "experience_points": skill.experience_points,
                    "level_progress": skill.level_progress
                } for skill_type, skill in progress.skills.items()
            }
        }
    
    def _serialize_attempt(self, attempt: StageAttempt) -> Dict[str, Any]:
        """挑戦データをシリアライズ"""
        return {
            "stage_id": attempt.stage_id,
            "attempt_number": attempt.attempt_number,
            "start_time": attempt.start_time.isoformat(),
            "end_time": attempt.end_time.isoformat() if attempt.end_time else None,
            "result": attempt.result.value if attempt.result else None,
            "turns_used": attempt.turns_used,
            "max_turns": attempt.max_turns,
            "actions_taken": attempt.actions_taken,
            "errors_made": attempt.errors_made,
            "hints_used": attempt.hints_used,
            "success": attempt.success
        }
    
    def _deserialize_progress(self, data: Dict[str, Any]) -> StudentProgress:
        """JSON データから進捗データを復元"""
        progress = StudentProgress(
            student_id=data["student_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"])
        )
        
        # ステージ挑戦記録を復元
        for stage_id, attempts_data in data.get("stage_attempts", {}).items():
            attempts = [self._deserialize_attempt(attempt_data) for attempt_data in attempts_data]
            progress.stage_attempts[stage_id] = attempts
        
        # スキル情報を復元
        for skill_type_str, skill_data in data.get("skills", {}).items():
            try:
                skill_type = MetricType(skill_type_str)
                skill = SkillProgress(
                    skill_type=skill_type,
                    current_level=SkillLevel(skill_data["current_level"]),
                    experience_points=skill_data["experience_points"],
                    level_progress=skill_data["level_progress"]
                )
                progress.skills[skill_type] = skill
            except (ValueError, KeyError):
                # 無効なデータは無視
                continue
        
        # メトリクスを再計算
        progress._update_overall_metrics()
        for stage_id in progress.stage_attempts.keys():
            progress._update_stage_metrics(stage_id)
        
        return progress
    
    def _deserialize_attempt(self, data: Dict[str, Any]) -> StageAttempt:
        """JSON データから挑戦データを復元"""
        return StageAttempt(
            stage_id=data["stage_id"],
            attempt_number=data["attempt_number"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            result=GameStatus(data["result"]) if data.get("result") else None,
            turns_used=data.get("turns_used", 0),
            max_turns=data.get("max_turns", 0),
            actions_taken=data.get("actions_taken", []),
            errors_made=data.get("errors_made", []),
            hints_used=data.get("hints_used", 0),
            success=data.get("success", False)
        )


# エクスポート用
__all__ = [
    "SkillLevel", "MetricType", "StageAttempt", "SkillProgress", 
    "LearningMetrics", "StudentProgress", "ProgressionManager"
]