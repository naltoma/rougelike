#!/usr/bin/env python3
"""
高度な教育フィードバックシステム

学習パターン分析、個別化されたヒント生成、無限ループ検出、
段階的指導支援を提供する包括的な教育支援システム
"""

import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics
from collections import defaultdict, deque


class FeedbackType(Enum):
    """フィードバックタイプ"""
    HINT = "hint"                    # ヒント
    SUGGESTION = "suggestion"        # 提案
    WARNING = "warning"              # 警告
    ENCOURAGEMENT = "encouragement"  # 励まし
    CORRECTION = "correction"        # 修正指導


class LearningStage(Enum):
    """学習段階"""
    BEGINNER = "beginner"        # 初心者
    INTERMEDIATE = "intermediate"  # 中級者
    ADVANCED = "advanced"        # 上級者
    EXPERT = "expert"            # 熟練者


class PatternType(Enum):
    """行動パターンタイプ"""
    INFINITE_LOOP = "infinite_loop"          # 無限ループ
    WALL_COLLISION = "wall_collision"        # 壁への衝突
    INEFFICIENT_PATH = "inefficient_path"    # 非効率な経路
    RANDOM_MOVEMENT = "random_movement"      # ランダムな移動
    STUCK_BEHAVIOR = "stuck_behavior"        # 行き詰まり行動
    OPTIMAL_SOLUTION = "optimal_solution"    # 最適解


@dataclass
class FeedbackMessage:
    """フィードバックメッセージ"""
    type: FeedbackType
    title: str
    message: str
    priority: int = 1  # 1(高) - 5(低)
    stage_specific: bool = False
    code_example: Optional[str] = None
    learning_objective: Optional[str] = None
    
    def format_message(self, student_name: str = "学習者") -> str:
        """個人化されたメッセージを生成"""
        icons = {
            FeedbackType.HINT: "💡",
            FeedbackType.SUGGESTION: "💭",
            FeedbackType.WARNING: "⚠️",
            FeedbackType.ENCOURAGEMENT: "🌟",
            FeedbackType.CORRECTION: "🔧"
        }
        
        icon = icons.get(self.type, "📝")
        formatted = f"{icon} {self.title}\n{self.message}"
        
        if self.code_example:
            formatted += f"\n\n📝 例:\n{self.code_example}"
        
        if self.learning_objective:
            formatted += f"\n\n🎯 学習目標: {self.learning_objective}"
        
        return formatted


@dataclass
class LearningPattern:
    """学習パターン"""
    pattern_type: PatternType
    confidence: float  # 0.0 - 1.0
    frequency: int
    last_occurrence: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_problematic(self) -> bool:
        """問題のあるパターンかどうか"""
        return self.pattern_type in [
            PatternType.INFINITE_LOOP,
            PatternType.WALL_COLLISION,
            PatternType.STUCK_BEHAVIOR
        ]


@dataclass
class StudentProfile:
    """学生プロファイル"""
    student_id: str
    learning_stage: LearningStage = LearningStage.BEGINNER
    preferred_feedback_style: str = "detailed"  # detailed, concise, visual
    
    # 学習特性
    error_tolerance: float = 0.5
    exploration_tendency: float = 0.5
    help_seeking_frequency: float = 0.3
    
    # 学習履歴
    completed_stages: Set[str] = field(default_factory=set)
    common_mistakes: List[str] = field(default_factory=list)
    strength_areas: List[str] = field(default_factory=list)
    
    # 時間的特性
    average_session_duration: timedelta = field(default_factory=lambda: timedelta(minutes=20))
    preferred_hint_timing: float = 30.0  # 秒
    
    def update_from_session(self, session_data: Dict[str, Any]) -> None:
        """セッションデータから更新"""
        success_rate = session_data.get('success_rate', 0.5)
        
        # 学習段階の更新
        if success_rate >= 0.9:
            if self.learning_stage == LearningStage.BEGINNER:
                self.learning_stage = LearningStage.INTERMEDIATE
            elif self.learning_stage == LearningStage.INTERMEDIATE:
                self.learning_stage = LearningStage.ADVANCED
        elif success_rate < 0.3:
            if self.learning_stage != LearningStage.BEGINNER:
                self.learning_stage = LearningStage.BEGINNER
        
        # 特性の更新
        self.error_tolerance = min(1.0, max(0.0, success_rate))
        
        hint_usage = session_data.get('hint_usage', 0)
        total_actions = session_data.get('total_actions', 1)
        self.help_seeking_frequency = min(1.0, hint_usage / total_actions)


class InfiniteLoopDetector:
    """無限ループ検出器"""
    
    def __init__(self, max_history: int = 20, detection_threshold: int = 8):
        self.max_history = max_history
        self.detection_threshold = detection_threshold
        self.action_history: deque = deque(maxlen=max_history)
        self.position_history: deque = deque(maxlen=max_history)
        self.pattern_cache: Dict[str, int] = {}
    
    def add_action(self, action: str, position: Optional[Tuple[int, int]] = None,
                   timestamp: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """アクションを追加し、無限ループをチェック"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.action_history.append({
            'action': action,
            'position': position,
            'timestamp': timestamp
        })
        
        if position:
            self.position_history.append(position)
        
        # パターン検出
        return self._detect_patterns()
    
    def _detect_patterns(self) -> Optional[Dict[str, Any]]:
        """パターン検出"""
        if len(self.action_history) < self.detection_threshold:
            return None
        
        # アクションシーケンスパターンの検出
        action_sequence = [entry['action'] for entry in list(self.action_history)[-self.detection_threshold:]]
        
        # 循環パターンをチェック
        for cycle_length in range(2, self.detection_threshold // 2):
            if self._check_cycle(action_sequence, cycle_length):
                return {
                    'type': 'action_cycle',
                    'cycle_length': cycle_length,
                    'pattern': action_sequence[-cycle_length:],
                    'confidence': 0.9
                }
        
        # 位置の循環パターンをチェック
        if len(self.position_history) >= self.detection_threshold:
            position_cycle = self._detect_position_cycle()
            if position_cycle:
                return position_cycle
        
        # 時間ベースのパターンをチェック
        return self._detect_time_based_patterns()
    
    def _check_cycle(self, sequence: List[str], cycle_length: int) -> bool:
        """指定された長さの循環パターンをチェック"""
        if len(sequence) < cycle_length * 3:
            return False
        
        pattern = sequence[-cycle_length:]
        
        # パターンが少なくとも3回繰り返されているかチェック
        repetitions = 0
        for i in range(len(sequence) - cycle_length, -1, -cycle_length):
            if i >= 0 and sequence[i:i + cycle_length] == pattern:
                repetitions += 1
            else:
                break
        
        return repetitions >= 3
    
    def _detect_position_cycle(self) -> Optional[Dict[str, Any]]:
        """位置の循環パターンを検出"""
        if len(set(self.position_history)) <= 3:
            recent_positions = list(self.position_history)[-8:]
            unique_positions = len(set(recent_positions))
            
            if unique_positions <= 3:
                return {
                    'type': 'position_cycle',
                    'positions': list(set(recent_positions)),
                    'confidence': 0.8
                }
        
        return None
    
    def _detect_time_based_patterns(self) -> Optional[Dict[str, Any]]:
        """時間ベースのパターンを検出"""
        if len(self.action_history) < 10:
            return None
        
        recent_actions = list(self.action_history)[-10:]
        time_intervals = []
        
        for i in range(1, len(recent_actions)):
            prev_time = recent_actions[i-1]['timestamp']
            curr_time = recent_actions[i]['timestamp']
            interval = (curr_time - prev_time).total_seconds()
            time_intervals.append(interval)
        
        # 非常に短い間隔での連続アクション（可能な無限ループ）
        if len(time_intervals) >= 5:
            avg_interval = statistics.mean(time_intervals)
            if avg_interval < 0.5:  # 0.5秒未満の平均間隔
                return {
                    'type': 'rapid_execution',
                    'average_interval': avg_interval,
                    'confidence': 0.7
                }
        
        return None
    
    def reset(self) -> None:
        """検出器をリセット"""
        self.action_history.clear()
        self.position_history.clear()
        self.pattern_cache.clear()


class LearningPatternAnalyzer:
    """学習パターン分析器"""
    
    def __init__(self):
        self.detected_patterns: List[LearningPattern] = []
        self.loop_detector = InfiniteLoopDetector()
    
    def analyze_session(self, api_history: List[Dict[str, Any]], 
                       game_states: List[Dict[str, Any]] = None) -> List[LearningPattern]:
        """セッション分析"""
        patterns = []
        
        # 無限ループ検出
        loop_patterns = self._detect_infinite_loops(api_history)
        patterns.extend(loop_patterns)
        
        # 移動効率の分析
        efficiency_patterns = self._analyze_movement_efficiency(api_history, game_states)
        patterns.extend(efficiency_patterns)
        
        # 壁衝突パターンの分析
        collision_patterns = self._analyze_collision_patterns(api_history)
        patterns.extend(collision_patterns)
        
        # 最適解パターンの検出
        optimal_patterns = self._detect_optimal_patterns(api_history, game_states)
        patterns.extend(optimal_patterns)
        
        self.detected_patterns = patterns
        return patterns
    
    def _detect_infinite_loops(self, api_history: List[Dict[str, Any]]) -> List[LearningPattern]:
        """無限ループの検出"""
        patterns = []
        
        for entry in api_history:
            action = entry.get('api', '')
            position = entry.get('position')
            timestamp = entry.get('timestamp')
            
            if timestamp and isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            loop_info = self.loop_detector.add_action(action, position, timestamp)
            
            if loop_info:
                pattern = LearningPattern(
                    pattern_type=PatternType.INFINITE_LOOP,
                    confidence=loop_info['confidence'],
                    frequency=1,
                    last_occurrence=timestamp or datetime.now(),
                    context=loop_info
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_movement_efficiency(self, api_history: List[Dict[str, Any]], 
                                   game_states: List[Dict[str, Any]] = None) -> List[LearningPattern]:
        """移動効率の分析"""
        patterns = []
        
        if not api_history:
            return patterns
        
        move_actions = [entry for entry in api_history if entry.get('api') == 'move']
        total_moves = len(move_actions)
        
        if total_moves == 0:
            return patterns
        
        # 成功した移動の割合
        successful_moves = len([entry for entry in move_actions if entry.get('success', False)])
        success_rate = successful_moves / total_moves if total_moves > 0 else 0
        
        # 非効率な経路の検出
        if success_rate < 0.5 and total_moves >= 10:
            pattern = LearningPattern(
                pattern_type=PatternType.INEFFICIENT_PATH,
                confidence=1.0 - success_rate,
                frequency=total_moves - successful_moves,
                last_occurrence=datetime.now(),
                context={'success_rate': success_rate, 'total_moves': total_moves}
            )
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_collision_patterns(self, api_history: List[Dict[str, Any]]) -> List[LearningPattern]:
        """壁衝突パターンの分析"""
        patterns = []
        
        consecutive_failures = 0
        max_consecutive = 0
        failure_count = 0
        
        for entry in api_history:
            if entry.get('api') == 'move':
                success = entry.get('success', False)
                if not success and '壁' in entry.get('message', ''):
                    consecutive_failures += 1
                    failure_count += 1
                    max_consecutive = max(max_consecutive, consecutive_failures)
                else:
                    consecutive_failures = 0
        
        # 連続した壁への衝突
        if max_consecutive >= 3:
            pattern = LearningPattern(
                pattern_type=PatternType.WALL_COLLISION,
                confidence=min(1.0, max_consecutive / 5.0),
                frequency=failure_count,
                last_occurrence=datetime.now(),
                context={'max_consecutive': max_consecutive, 'total_failures': failure_count}
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_optimal_patterns(self, api_history: List[Dict[str, Any]], 
                               game_states: List[Dict[str, Any]] = None) -> List[LearningPattern]:
        """最適解パターンの検出"""
        patterns = []
        
        if not api_history:
            return patterns
        
        # 高い成功率とsee()の適切な使用
        see_count = len([entry for entry in api_history if entry.get('api') == 'see'])
        action_count = len([entry for entry in api_history if entry.get('api') in ['move', 'turn_left', 'turn_right']])
        
        if action_count > 0:
            see_ratio = see_count / action_count
            success_rate = len([e for e in api_history if e.get('success', False)]) / len(api_history)
            
            # 適切なsee使用と高い成功率
            if see_ratio >= 0.3 and success_rate >= 0.8:
                pattern = LearningPattern(
                    pattern_type=PatternType.OPTIMAL_SOLUTION,
                    confidence=min(success_rate, see_ratio * 2),
                    frequency=1,
                    last_occurrence=datetime.now(),
                    context={'see_ratio': see_ratio, 'success_rate': success_rate}
                )
                patterns.append(pattern)
        
        return patterns


class EducationalFeedbackGenerator:
    """教育フィードバック生成器"""
    
    def __init__(self):
        self.pattern_analyzer = LearningPatternAnalyzer()
        self.student_profiles: Dict[str, StudentProfile] = {}
        
        # ステージ別のヒントテンプレート
        self.stage_hints = {
            'stage01': {
                'basic': "基本移動: move()で前進、turn_right()で右回転できます",
                'stuck': "壁にぶつかったら turn_right() で向きを変えてみましょう",
                'exploration': "see() で周囲を確認してから行動すると安全です"
            },
            'stage02': {
                'basic': "迷路では右手法が有効です: 右手を壁に付けて歩くイメージ",
                'stuck': "同じ場所を回っている場合は、アルゴリズムを見直しましょう",
                'loop': "無限ループに注意! 適切な終了条件を設定してください"
            },
            'stage03': {
                'basic': "複雑な迷路では計画的な探索が重要です",
                'optimization': "効率的な経路を見つけるため、複数の戦略を試してみましょう",
                'advanced': "右手法以外のアルゴリズムも挑戦してみましょう"
            }
        }
    
    def get_or_create_profile(self, student_id: str) -> StudentProfile:
        """学生プロファイルを取得または作成"""
        if student_id not in self.student_profiles:
            self.student_profiles[student_id] = StudentProfile(student_id=student_id)
        return self.student_profiles[student_id]
    
    def generate_feedback(self, student_id: str, stage_id: str,
                         api_history: List[Dict[str, Any]],
                         game_states: List[Dict[str, Any]] = None,
                         current_situation: Dict[str, Any] = None) -> List[FeedbackMessage]:
        """フィードバック生成"""
        profile = self.get_or_create_profile(student_id)
        feedback_messages = []
        
        # 学習パターンを分析
        patterns = self.pattern_analyzer.analyze_session(api_history, game_states)
        
        # パターンベースのフィードバック
        pattern_feedback = self._generate_pattern_feedback(patterns, profile, stage_id)
        feedback_messages.extend(pattern_feedback)
        
        # 進捗ベースのフィードバック
        progress_feedback = self._generate_progress_feedback(api_history, profile, stage_id)
        feedback_messages.extend(progress_feedback)
        
        # 状況に応じた即座のフィードバック
        if current_situation:
            immediate_feedback = self._generate_immediate_feedback(current_situation, profile, stage_id)
            feedback_messages.extend(immediate_feedback)
        
        # 励ましのフィードバック
        encouragement = self._generate_encouragement(api_history, profile)
        feedback_messages.extend(encouragement)
        
        # 優先度でソート
        feedback_messages.sort(key=lambda x: x.priority)
        
        return feedback_messages[:3]  # 最大3つのフィードバック
    
    def _generate_pattern_feedback(self, patterns: List[LearningPattern],
                                 profile: StudentProfile, stage_id: str) -> List[FeedbackMessage]:
        """パターンベースのフィードバック生成"""
        messages = []
        
        for pattern in patterns:
            if pattern.pattern_type == PatternType.INFINITE_LOOP:
                messages.append(FeedbackMessage(
                    type=FeedbackType.WARNING,
                    title="無限ループの可能性",
                    message="同じアクションを繰り返しています。終了条件を確認してください。",
                    priority=1,
                    code_example="while not is_game_finished():\n    # ここに適切な処理を書く\n    if get_game_result() == 'timeout':\n        break",
                    learning_objective="適切なループ制御を学ぶ"
                ))
            
            elif pattern.pattern_type == PatternType.WALL_COLLISION:
                stage_hint = self.stage_hints.get(stage_id, {}).get('stuck', 
                    "壁にぶつかったら向きを変えてみましょう")
                messages.append(FeedbackMessage(
                    type=FeedbackType.HINT,
                    title="壁への衝突が多発",
                    message=f"{stage_hint}",
                    priority=2,
                    stage_specific=True,
                    learning_objective="障害物回避の戦略を学ぶ"
                ))
            
            elif pattern.pattern_type == PatternType.INEFFICIENT_PATH:
                messages.append(FeedbackMessage(
                    type=FeedbackType.SUGGESTION,
                    title="移動効率の改善",
                    message="see()で周囲を確認してから移動すると効率が向上します。",
                    priority=3,
                    code_example="info = see()\nif info['surroundings']['front'] == 'empty':\n    move()\nelse:\n    turn_right()",
                    learning_objective="計画的な行動の重要性を学ぶ"
                ))
            
            elif pattern.pattern_type == PatternType.OPTIMAL_SOLUTION:
                messages.append(FeedbackMessage(
                    type=FeedbackType.ENCOURAGEMENT,
                    title="素晴らしい問題解決!",
                    message="効率的なアプローチを使って問題を解決しています。この調子で続けましょう！",
                    priority=4,
                    learning_objective="効率的な問題解決手法の確立"
                ))
        
        return messages
    
    def _generate_progress_feedback(self, api_history: List[Dict[str, Any]],
                                  profile: StudentProfile, stage_id: str) -> List[FeedbackMessage]:
        """進捗ベースのフィードバック生成"""
        messages = []
        
        if not api_history:
            return messages
        
        # API使用の多様性をチェック
        used_apis = set(entry.get('api', '') for entry in api_history)
        available_apis = {'move', 'turn_left', 'turn_right', 'see', 'attack', 'pickup'}
        
        if 'see' not in used_apis and len(api_history) > 5:
            messages.append(FeedbackMessage(
                type=FeedbackType.HINT,
                title="周囲確認の活用",
                message="see()を使って周囲の状況を確認してみましょう。より安全に進めます。",
                priority=2,
                stage_specific=True,
                learning_objective="情報収集の重要性を学ぶ"
            ))
        
        # 学習段階に応じたフィードバック
        if profile.learning_stage == LearningStage.BEGINNER:
            basic_hint = self.stage_hints.get(stage_id, {}).get('basic', 
                "基本的な移動コマンドから始めましょう")
            messages.append(FeedbackMessage(
                type=FeedbackType.HINT,
                title="基本操作の確認",
                message=basic_hint,
                priority=3,
                stage_specific=True,
                learning_objective="基本操作の習得"
            ))
        
        return messages
    
    def _generate_immediate_feedback(self, situation: Dict[str, Any],
                                   profile: StudentProfile, stage_id: str) -> List[FeedbackMessage]:
        """即座のフィードバック生成"""
        messages = []
        
        error_type = situation.get('error_type')
        last_action = situation.get('last_action')
        
        if error_type == 'wall_collision':
            messages.append(FeedbackMessage(
                type=FeedbackType.CORRECTION,
                title="壁に衝突しました",
                message="進路が壁で塞がれています。turn_right()またはturn_left()で向きを変えましょう。",
                priority=1,
                learning_objective="障害物の回避方法を学ぶ"
            ))
        
        elif error_type == 'api_usage_error':
            messages.append(FeedbackMessage(
                type=FeedbackType.CORRECTION,
                title="API使用エラー",
                message="このステージでは使用できないAPIです。利用可能なAPIを確認してください。",
                priority=1,
                learning_objective="ステージの制約を理解する"
            ))
        
        return messages
    
    def _generate_encouragement(self, api_history: List[Dict[str, Any]],
                              profile: StudentProfile) -> List[FeedbackMessage]:
        """励ましのフィードバック生成"""
        messages = []
        
        if not api_history:
            return messages
        
        success_count = len([entry for entry in api_history if entry.get('success', False)])
        total_count = len(api_history)
        
        if total_count >= 5:
            success_rate = success_count / total_count
            
            if success_rate >= 0.8:
                messages.append(FeedbackMessage(
                    type=FeedbackType.ENCOURAGEMENT,
                    title="順調な進歩!",
                    message="高い成功率を維持しています。この調子で頑張りましょう！",
                    priority=5,
                    learning_objective="自信を持って学習を続ける"
                ))
            elif 0.3 <= success_rate < 0.6:
                messages.append(FeedbackMessage(
                    type=FeedbackType.ENCOURAGEMENT,
                    title="着実な学習",
                    message="試行錯誤を通じて学習しています。失敗から学ぶことが大切です。",
                    priority=5,
                    learning_objective="失敗を恐れずに挑戦する"
                ))
        
        return messages
    
    def update_student_profile(self, student_id: str, session_data: Dict[str, Any]) -> None:
        """学生プロファイルを更新"""
        profile = self.get_or_create_profile(student_id)
        profile.update_from_session(session_data)


class AdaptiveHintSystem:
    """適応的ヒントシステム"""
    
    def __init__(self):
        self.feedback_generator = EducationalFeedbackGenerator()
        self.hint_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def should_provide_hint(self, student_id: str, time_since_last_action: float,
                           consecutive_failures: int, api_history: List[Dict[str, Any]]) -> bool:
        """ヒントを提供すべきかを判定"""
        profile = self.feedback_generator.get_or_create_profile(student_id)
        
        # 基本的な条件
        if consecutive_failures >= 3:
            return True
        
        # 時間ベースの条件
        if time_since_last_action > profile.preferred_hint_timing:
            return True
        
        # 学習段階による調整
        if profile.learning_stage == LearningStage.BEGINNER and consecutive_failures >= 2:
            return True
        
        # 無限ループの検出
        if len(api_history) >= 10:
            recent_actions = [entry.get('api', '') for entry in api_history[-8:]]
            if len(set(recent_actions)) <= 2:  # 2種類以下のAPIしか使っていない
                return True
        
        return False
    
    def provide_contextual_hint(self, student_id: str, stage_id: str,
                              current_situation: Dict[str, Any],
                              api_history: List[Dict[str, Any]]) -> Optional[FeedbackMessage]:
        """文脈に応じたヒントを提供"""
        feedback_list = self.feedback_generator.generate_feedback(
            student_id, stage_id, api_history, current_situation=current_situation
        )
        
        # 最も優先度の高いヒントまたは提案を選択
        for feedback in feedback_list:
            if feedback.type in [FeedbackType.HINT, FeedbackType.SUGGESTION]:
                # ヒント履歴に記録
                self.hint_history[student_id].append({
                    'timestamp': datetime.now().isoformat(),
                    'stage_id': stage_id,
                    'hint': feedback.message
                })
                return feedback
        
        return None
    
    def get_hint_effectiveness(self, student_id: str) -> Dict[str, float]:
        """ヒントの効果を評価"""
        hints = self.hint_history.get(student_id, [])
        if len(hints) < 2:
            return {'effectiveness': 0.5, 'frequency': 0.0}
        
        # ヒントの頻度
        total_hints = len(hints)
        
        # 最近のヒント効果（簡略版）
        effectiveness = 0.7  # デフォルト値
        
        return {
            'effectiveness': effectiveness,
            'frequency': total_hints,
            'recent_hints': hints[-3:]  # 最近の3つ
        }


# グローバルインスタンス
_feedback_generator = EducationalFeedbackGenerator()
_adaptive_hint_system = AdaptiveHintSystem()


def generate_educational_feedback(student_id: str, stage_id: str,
                                api_history: List[Dict[str, Any]],
                                current_situation: Dict[str, Any] = None) -> List[FeedbackMessage]:
    """教育フィードバック生成（グローバル関数）"""
    return _feedback_generator.generate_feedback(student_id, stage_id, api_history, 
                                               current_situation=current_situation)


def should_provide_hint(student_id: str, time_since_last_action: float,
                       consecutive_failures: int, api_history: List[Dict[str, Any]]) -> bool:
    """ヒント提供判定（グローバル関数）"""
    return _adaptive_hint_system.should_provide_hint(student_id, time_since_last_action,
                                                    consecutive_failures, api_history)


def get_contextual_hint(student_id: str, stage_id: str,
                       current_situation: Dict[str, Any],
                       api_history: List[Dict[str, Any]]) -> Optional[str]:
    """文脈ヒント取得（グローバル関数）"""
    hint_message = _adaptive_hint_system.provide_contextual_hint(
        student_id, stage_id, current_situation, api_history
    )
    return hint_message.format_message() if hint_message else None


def detect_infinite_loop(api_history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """無限ループ検出（グローバル関数）"""
    detector = InfiniteLoopDetector()
    
    for entry in api_history:
        action = entry.get('api', '')
        position = entry.get('position')
        timestamp = entry.get('timestamp')
        
        if timestamp and isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        result = detector.add_action(action, position, timestamp)
        if result:
            return result
    
    return None


def update_student_learning_profile(student_id: str, session_data: Dict[str, Any]) -> None:
    """学生学習プロファイル更新（グローバル関数）"""
    _feedback_generator.update_student_profile(student_id, session_data)


# エクスポート用
__all__ = [
    "FeedbackType", "LearningStage", "PatternType", "FeedbackMessage",
    "LearningPattern", "StudentProfile", "InfiniteLoopDetector",
    "LearningPatternAnalyzer", "EducationalFeedbackGenerator", "AdaptiveHintSystem",
    "generate_educational_feedback", "should_provide_hint", "get_contextual_hint",
    "detect_infinite_loop", "update_student_learning_profile"
]