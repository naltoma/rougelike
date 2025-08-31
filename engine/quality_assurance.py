#!/usr/bin/env python3
"""
学習メトリクスと品質保証システム

学習効果の測定、コード品質の評価、システムの信頼性確保を行う
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import statistics
import re


class CodeQuality(Enum):
    """コード品質レベル"""
    POOR = "poor"           # 改善が必要
    FAIR = "fair"           # まずまず
    GOOD = "good"           # 良い
    EXCELLENT = "excellent" # 優秀


class LearningEfficiency(Enum):
    """学習効率レベル"""
    STRUGGLING = "struggling"   # 苦戦中
    LEARNING = "learning"       # 学習中
    PROGRESSING = "progressing" # 順調
    MASTERING = "mastering"     # 習得中


@dataclass
class CodeMetrics:
    """コードメトリクス"""
    lines_of_code: int = 0
    complexity_score: float = 0.0
    readability_score: float = 0.0
    efficiency_score: float = 0.0
    error_density: float = 0.0
    
    # 詳細メトリクス
    cyclomatic_complexity: int = 0
    duplicate_code_ratio: float = 0.0
    api_usage_diversity: int = 0
    comments_ratio: float = 0.0
    
    @property
    def overall_quality(self) -> CodeQuality:
        """全体的なコード品質を評価"""
        scores = [
            self.readability_score,
            self.efficiency_score,
            1.0 - self.error_density,  # エラー密度は低いほど良い
            min(1.0, self.api_usage_diversity / 5.0)  # API使用多様性
        ]
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 0.9:
            return CodeQuality.EXCELLENT
        elif avg_score >= 0.7:
            return CodeQuality.GOOD
        elif avg_score >= 0.5:
            return CodeQuality.FAIR
        else:
            return CodeQuality.POOR


@dataclass
class LearningMetrics:
    """学習メトリクス"""
    session_duration: timedelta = field(default_factory=lambda: timedelta())
    total_attempts: int = 0
    successful_attempts: int = 0
    error_count: int = 0
    hint_usage_count: int = 0
    
    # 学習行動メトリクス
    average_response_time: float = 0.0
    consistency_score: float = 0.0
    improvement_rate: float = 0.0
    exploration_score: float = 0.0
    
    # 時系列データ
    attempt_timestamps: List[datetime] = field(default_factory=list)
    success_pattern: List[bool] = field(default_factory=list)
    response_times: List[float] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_attempts == 0:
            return 0.0
        return self.successful_attempts / self.total_attempts
    
    @property
    def error_rate(self) -> float:
        """エラー率"""
        if self.total_attempts == 0:
            return 0.0
        return self.error_count / self.total_attempts
    
    @property
    def learning_efficiency(self) -> LearningEfficiency:
        """学習効率を評価"""
        success_rate = self.success_rate
        improvement = self.improvement_rate
        consistency = self.consistency_score
        
        # 総合スコア計算
        efficiency_score = (success_rate * 0.4 + 
                           improvement * 0.3 + 
                           consistency * 0.3)
        
        if efficiency_score >= 0.8:
            return LearningEfficiency.MASTERING
        elif efficiency_score >= 0.6:
            return LearningEfficiency.PROGRESSING
        elif efficiency_score >= 0.4:
            return LearningEfficiency.LEARNING
        else:
            return LearningEfficiency.STRUGGLING
    
    def add_attempt(self, success: bool, response_time: float = 0.0) -> None:
        """試行記録を追加"""
        self.total_attempts += 1
        if success:
            self.successful_attempts += 1
        
        self.attempt_timestamps.append(datetime.now())
        self.success_pattern.append(success)
        if response_time > 0:
            self.response_times.append(response_time)
        
        self._update_derived_metrics()
    
    def _update_derived_metrics(self) -> None:
        """派生メトリクスを更新"""
        if self.response_times:
            self.average_response_time = statistics.mean(self.response_times)
        
        # 改善率計算（最近の成功率と初期の成功率を比較）
        if len(self.success_pattern) >= 10:
            recent_success = sum(self.success_pattern[-5:]) / 5
            initial_success = sum(self.success_pattern[:5]) / 5
            self.improvement_rate = max(0.0, recent_success - initial_success)
        
        # 一貫性スコア（成功パターンの安定性）
        if len(self.success_pattern) >= 5:
            recent_patterns = self.success_pattern[-10:]
            if recent_patterns:
                variance = statistics.variance([1 if x else 0 for x in recent_patterns])
                self.consistency_score = max(0.0, 1.0 - variance)


@dataclass
class QualityReport:
    """品質レポート"""
    student_id: str
    session_id: str
    timestamp: datetime
    code_metrics: CodeMetrics
    learning_metrics: LearningMetrics
    
    # 統合評価
    overall_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    
    def generate_summary(self) -> str:
        """サマリーレポート生成"""
        return f"""
📊 学習品質レポート
==================
学生ID: {self.student_id}
セッション: {self.session_id}
評価時刻: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

📈 学習メトリクス:
  成功率: {self.learning_metrics.success_rate:.1%}
  学習効率: {self.learning_metrics.learning_efficiency.value}
  改善率: {self.learning_metrics.improvement_rate:.1%}
  平均応答時間: {self.learning_metrics.average_response_time:.1f}秒

💻 コード品質:
  全体品質: {self.code_metrics.overall_quality.value}
  可読性: {self.code_metrics.readability_score:.1%}
  効率性: {self.code_metrics.efficiency_score:.1%}
  エラー密度: {self.code_metrics.error_density:.3f}

🏆 総合スコア: {self.overall_score:.1%}

💡 推奨事項:
{chr(10).join(f"  • {rec}" for rec in self.recommendations)}

🎉 達成項目:
{chr(10).join(f"  • {ach}" for ach in self.achievements)}
"""


class CodeAnalyzer:
    """コード分析器"""
    
    def __init__(self):
        self.api_patterns = {
            "move", "turn_left", "turn_right", "attack", "pickup", "see",
            "can_undo", "undo", "is_game_finished", "get_game_result"
        }
    
    def analyze_code_quality(self, code_text: str, api_calls: List[str]) -> CodeMetrics:
        """コード品質を分析"""
        metrics = CodeMetrics()
        
        if not code_text:
            return metrics
        
        lines = code_text.split('\n')
        metrics.lines_of_code = len([line for line in lines if line.strip()])
        
        # 基本メトリクス計算
        metrics.cyclomatic_complexity = self._calculate_complexity(code_text)
        metrics.readability_score = self._calculate_readability(code_text)
        metrics.efficiency_score = self._calculate_efficiency(code_text, api_calls)
        metrics.api_usage_diversity = len(set(api_calls))
        metrics.comments_ratio = self._calculate_comments_ratio(code_text)
        metrics.duplicate_code_ratio = self._calculate_duplication(code_text)
        
        return metrics
    
    def _calculate_complexity(self, code: str) -> int:
        """循環的複雑度を計算"""
        complexity = 1  # 基本パス
        
        # 制御構造をカウント
        patterns = [
            r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bwhile\b', r'\bfor\b',
            r'\btry\b', r'\bexcept\b',
            r'\band\b', r'\borg\b'
        ]
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, code))
        
        return complexity
    
    def _calculate_readability(self, code: str) -> float:
        """コードの可読性を計算"""
        if not code.strip():
            return 0.0
        
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        if not lines:
            return 0.0
        
        # 可読性要素を評価
        score_factors = []
        
        # 適切な長さの行（短すぎず長すぎない）
        good_length_lines = sum(1 for line in lines if 10 <= len(line) <= 80)
        score_factors.append(good_length_lines / len(lines))
        
        # インデントの一貫性
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        if indents:
            indent_consistency = 1.0 - (statistics.stdev(indents) / 10.0 if len(indents) > 1 else 0.0)
            score_factors.append(max(0.0, min(1.0, indent_consistency)))
        
        # 空行の使用（適切な分割）
        empty_lines = len([line for line in code.split('\n') if not line.strip()])
        empty_ratio = empty_lines / len(code.split('\n'))
        score_factors.append(min(1.0, empty_ratio * 5))  # 適度な空行は良い
        
        return sum(score_factors) / len(score_factors) if score_factors else 0.0
    
    def _calculate_efficiency(self, code: str, api_calls: List[str]) -> float:
        """効率性を計算"""
        if not api_calls:
            return 0.0
        
        efficiency_factors = []
        
        # API呼び出しの重複チェック
        unique_calls = set(api_calls)
        if len(api_calls) > 0:
            diversity_ratio = len(unique_calls) / len(api_calls)
            efficiency_factors.append(diversity_ratio)
        
        # see()の適切な使用
        see_calls = api_calls.count('see')
        action_calls = len([call for call in api_calls 
                           if call in ['move', 'attack', 'pickup']])
        
        if action_calls > 0:
            see_ratio = see_calls / action_calls
            # 適度なsee()使用が望ましい（0.2-0.5が理想）
            optimal_see_score = 1.0 - abs(see_ratio - 0.35) / 0.35
            efficiency_factors.append(max(0.0, optimal_see_score))
        
        # ループの検出と評価
        loop_patterns = len(re.findall(r'\b(for|while)\b', code))
        if loop_patterns > 0:
            efficiency_factors.append(0.8)  # ループ使用は効率的
        
        return sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0.0
    
    def _calculate_comments_ratio(self, code: str) -> float:
        """コメント率を計算"""
        lines = code.split('\n')
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        
        if code_lines == 0:
            return 0.0
        
        return comment_lines / (code_lines + comment_lines)
    
    def _calculate_duplication(self, code: str) -> float:
        """重複コード率を計算"""
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        if len(lines) < 2:
            return 0.0
        
        duplicates = 0
        for i, line in enumerate(lines):
            for j, other_line in enumerate(lines[i+1:], i+1):
                if line == other_line and len(line) > 5:  # 短いライン以外
                    duplicates += 1
        
        return duplicates / len(lines) if lines else 0.0


class LearningAnalyzer:
    """学習分析器"""
    
    def analyze_learning_pattern(self, session_data: List[Dict[str, Any]]) -> LearningMetrics:
        """学習パターンを分析"""
        metrics = LearningMetrics()
        
        if not session_data:
            return metrics
        
        # セッション継続時間
        if len(session_data) > 1:
            start_time = datetime.fromisoformat(session_data[0]['timestamp'])
            end_time = datetime.fromisoformat(session_data[-1]['timestamp'])
            metrics.session_duration = end_time - start_time
        
        # 各イベントを処理
        response_times = []
        last_timestamp = None
        
        for event in session_data:
            event_time = datetime.fromisoformat(event['timestamp'])
            event_type = event.get('event_type', '')
            
            if event_type == 'action_executed':
                success = event.get('data', {}).get('success', False)
                
                # 応答時間計算
                if last_timestamp:
                    response_time = (event_time - last_timestamp).total_seconds()
                    response_times.append(response_time)
                    metrics.add_attempt(success, response_time)
                else:
                    metrics.add_attempt(success)
            
            elif event_type == 'error_occurred':
                metrics.error_count += 1
            
            elif event_type == 'hint_used':
                metrics.hint_usage_count += 1
            
            last_timestamp = event_time
        
        # 探索スコア計算（異なるAPIの使用度合い）
        api_variety = set()
        for event in session_data:
            if event.get('event_type') == 'action_executed':
                api = event.get('data', {}).get('action', '')
                if api:
                    api_variety.add(api)
        
        metrics.exploration_score = min(1.0, len(api_variety) / 6.0)  # 6種類のAPIを想定
        
        return metrics


class QualityAssuranceManager:
    """品質保証マネージャー"""
    
    def __init__(self, report_dir: str = "data/quality_reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.code_analyzer = CodeAnalyzer()
        self.learning_analyzer = LearningAnalyzer()
        
        # 品質基準
        self.quality_thresholds = {
            "min_success_rate": 0.3,
            "min_code_quality": CodeQuality.FAIR,
            "max_error_density": 0.5,
            "min_improvement_rate": 0.1
        }
    
    def generate_quality_report(self, student_id: str, session_id: str, 
                              code_text: str, api_calls: List[str],
                              session_data: List[Dict[str, Any]]) -> QualityReport:
        """品質レポートを生成"""
        
        # コード分析
        code_metrics = self.code_analyzer.analyze_code_quality(code_text, api_calls)
        
        # 学習分析
        learning_metrics = self.learning_analyzer.analyze_learning_pattern(session_data)
        
        # レポート作成
        report = QualityReport(
            student_id=student_id,
            session_id=session_id,
            timestamp=datetime.now(),
            code_metrics=code_metrics,
            learning_metrics=learning_metrics
        )
        
        # 総合スコア計算
        report.overall_score = self._calculate_overall_score(code_metrics, learning_metrics)
        
        # 推奨事項生成
        report.recommendations = self._generate_recommendations(code_metrics, learning_metrics)
        
        # 達成項目生成
        report.achievements = self._generate_achievements(code_metrics, learning_metrics)
        
        return report
    
    def _calculate_overall_score(self, code_metrics: CodeMetrics, 
                               learning_metrics: LearningMetrics) -> float:
        """総合スコアを計算"""
        # 重み付き平均でスコア計算
        weights = {
            'success_rate': 0.25,
            'code_quality': 0.25,
            'learning_efficiency': 0.20,
            'improvement': 0.15,
            'consistency': 0.15
        }
        
        # 各要素のスコア（0-1）
        success_score = learning_metrics.success_rate
        
        code_quality_scores = {
            CodeQuality.POOR: 0.25,
            CodeQuality.FAIR: 0.5,
            CodeQuality.GOOD: 0.75,
            CodeQuality.EXCELLENT: 1.0
        }
        code_score = code_quality_scores.get(code_metrics.overall_quality, 0.5)
        
        efficiency_scores = {
            LearningEfficiency.STRUGGLING: 0.25,
            LearningEfficiency.LEARNING: 0.5,
            LearningEfficiency.PROGRESSING: 0.75,
            LearningEfficiency.MASTERING: 1.0
        }
        efficiency_score = efficiency_scores.get(learning_metrics.learning_efficiency, 0.5)
        
        improvement_score = min(1.0, learning_metrics.improvement_rate * 2)
        consistency_score = learning_metrics.consistency_score
        
        overall_score = (
            weights['success_rate'] * success_score +
            weights['code_quality'] * code_score +
            weights['learning_efficiency'] * efficiency_score +
            weights['improvement'] * improvement_score +
            weights['consistency'] * consistency_score
        )
        
        return overall_score
    
    def _generate_recommendations(self, code_metrics: CodeMetrics, 
                                learning_metrics: LearningMetrics) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        # コード品質に基づく推奨
        if code_metrics.overall_quality == CodeQuality.POOR:
            recommendations.append("コードの構造を見直し、より読みやすい書き方を心がけましょう")
        
        if code_metrics.readability_score < 0.5:
            recommendations.append("適切なインデントとコメントを使って、コードを読みやすくしましょう")
        
        if code_metrics.api_usage_diversity < 3:
            recommendations.append("様々なAPIを試して、機能の幅を広げましょう")
        
        if code_metrics.efficiency_score < 0.5:
            recommendations.append("see()で状況確認してから行動する習慣を身につけましょう")
        
        # 学習メトリクスに基づく推奨
        if learning_metrics.success_rate < 0.3:
            recommendations.append("基本的なアルゴリズムを復習し、段階的に取り組みましょう")
        
        if learning_metrics.error_rate > 0.5:
            recommendations.append("エラーメッセージを注意深く読み、原因を理解しましょう")
        
        if learning_metrics.improvement_rate < 0.1:
            recommendations.append("新しいアプローチを試し、学習方法を変えてみましょう")
        
        if learning_metrics.consistency_score < 0.5:
            recommendations.append("安定した解法を身につけるまで、基本を繰り返し練習しましょう")
        
        # 探索スコアに基づく推奨
        if learning_metrics.exploration_score < 0.3:
            recommendations.append("他の機能も積極的に試して、システムを探索してみましょう")
        
        return recommendations
    
    def _generate_achievements(self, code_metrics: CodeMetrics,
                             learning_metrics: LearningMetrics) -> List[str]:
        """達成項目を生成"""
        achievements = []
        
        # 学習メトリクス達成
        if learning_metrics.success_rate >= 0.8:
            achievements.append("高い成功率を達成しました！")
        
        if learning_metrics.improvement_rate >= 0.3:
            achievements.append("顕著な改善を示しています！")
        
        if learning_metrics.consistency_score >= 0.8:
            achievements.append("安定したパフォーマンスを維持しています！")
        
        if learning_metrics.learning_efficiency == LearningEfficiency.MASTERING:
            achievements.append("習得段階に到達しました！")
        
        # コード品質達成
        if code_metrics.overall_quality == CodeQuality.EXCELLENT:
            achievements.append("優秀なコード品質を達成しました！")
        
        if code_metrics.readability_score >= 0.8:
            achievements.append("読みやすいコードを書けています！")
        
        if code_metrics.efficiency_score >= 0.8:
            achievements.append("効率的なプログラムを作成しました！")
        
        if code_metrics.api_usage_diversity >= 5:
            achievements.append("様々な機能を活用しています！")
        
        # 特別な達成
        if learning_metrics.error_rate < 0.1:
            achievements.append("エラーの少ない優秀な実装です！")
        
        if learning_metrics.exploration_score >= 0.8:
            achievements.append("積極的な探索姿勢を示しています！")
        
        return achievements
    
    def save_report(self, report: QualityReport) -> Path:
        """レポートをファイルに保存"""
        filename = f"{report.student_id}_{report.session_id}_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.report_dir / filename
        
        # レポートをシリアライズ
        report_data = {
            "student_id": report.student_id,
            "session_id": report.session_id,
            "timestamp": report.timestamp.isoformat(),
            "overall_score": report.overall_score,
            "code_metrics": {
                "lines_of_code": report.code_metrics.lines_of_code,
                "complexity_score": report.code_metrics.complexity_score,
                "readability_score": report.code_metrics.readability_score,
                "efficiency_score": report.code_metrics.efficiency_score,
                "error_density": report.code_metrics.error_density,
                "overall_quality": report.code_metrics.overall_quality.value
            },
            "learning_metrics": {
                "session_duration_seconds": report.learning_metrics.session_duration.total_seconds(),
                "total_attempts": report.learning_metrics.total_attempts,
                "successful_attempts": report.learning_metrics.successful_attempts,
                "success_rate": report.learning_metrics.success_rate,
                "error_count": report.learning_metrics.error_count,
                "learning_efficiency": report.learning_metrics.learning_efficiency.value,
                "improvement_rate": report.learning_metrics.improvement_rate,
                "consistency_score": report.learning_metrics.consistency_score
            },
            "recommendations": report.recommendations,
            "achievements": report.achievements
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_report(self, filepath: Path) -> Optional[QualityReport]:
        """レポートをファイルから読み込み"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # データ復元（簡略版）
            code_metrics = CodeMetrics(
                lines_of_code=data["code_metrics"]["lines_of_code"],
                readability_score=data["code_metrics"]["readability_score"],
                efficiency_score=data["code_metrics"]["efficiency_score"],
                error_density=data["code_metrics"]["error_density"]
            )
            
            learning_metrics = LearningMetrics(
                session_duration=timedelta(seconds=data["learning_metrics"]["session_duration_seconds"]),
                total_attempts=data["learning_metrics"]["total_attempts"],
                successful_attempts=data["learning_metrics"]["successful_attempts"],
                error_count=data["learning_metrics"]["error_count"]
            )
            
            report = QualityReport(
                student_id=data["student_id"],
                session_id=data["session_id"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                code_metrics=code_metrics,
                learning_metrics=learning_metrics,
                overall_score=data["overall_score"],
                recommendations=data["recommendations"],
                achievements=data["achievements"]
            )
            
            return report
            
        except Exception as e:
            print(f"レポート読み込みエラー: {e}")
            return None
    
    def get_student_reports(self, student_id: str) -> List[QualityReport]:
        """学生の全レポートを取得"""
        reports = []
        pattern = f"{student_id}_*.json"
        
        for filepath in self.report_dir.glob(pattern):
            report = self.load_report(filepath)
            if report:
                reports.append(report)
        
        # 時刻順にソート
        reports.sort(key=lambda r: r.timestamp)
        return reports
    
    def generate_progress_summary(self, student_id: str) -> Dict[str, Any]:
        """進捗サマリーを生成"""
        reports = self.get_student_reports(student_id)
        
        if not reports:
            return {"error": "レポートが見つかりません"}
        
        # 統計計算
        scores = [r.overall_score for r in reports]
        success_rates = [r.learning_metrics.success_rate for r in reports]
        
        summary = {
            "student_id": student_id,
            "total_sessions": len(reports),
            "date_range": {
                "start": reports[0].timestamp.isoformat(),
                "end": reports[-1].timestamp.isoformat()
            },
            "overall_progress": {
                "average_score": statistics.mean(scores),
                "latest_score": scores[-1],
                "score_trend": scores[-1] - scores[0] if len(scores) > 1 else 0,
                "highest_score": max(scores),
                "consistency": 1.0 - statistics.stdev(scores) if len(scores) > 1 else 1.0
            },
            "learning_statistics": {
                "average_success_rate": statistics.mean(success_rates),
                "latest_success_rate": success_rates[-1],
                "improvement_trend": success_rates[-1] - success_rates[0] if len(success_rates) > 1 else 0
            },
            "achievements_summary": {
                "total_achievements": sum(len(r.achievements) for r in reports),
                "unique_achievements": len(set().union(*[r.achievements for r in reports])),
                "recent_achievements": reports[-1].achievements if reports else []
            }
        }
        
        return summary


# グローバルインスタンス
_quality_manager = QualityAssuranceManager()


def generate_quality_report(student_id: str, session_id: str, code_text: str, 
                          api_calls: List[str], session_data: List[Dict[str, Any]]) -> QualityReport:
    """品質レポートを生成（グローバル関数）"""
    return _quality_manager.generate_quality_report(student_id, session_id, code_text, api_calls, session_data)


def save_quality_report(report: QualityReport) -> str:
    """品質レポートを保存（グローバル関数）"""
    filepath = _quality_manager.save_report(report)
    return str(filepath)


def get_student_progress_summary(student_id: str) -> Dict[str, Any]:
    """学生の進捗サマリーを取得（グローバル関数）"""
    return _quality_manager.generate_progress_summary(student_id)


def analyze_code_quality(code_text: str, api_calls: List[str]) -> Dict[str, Any]:
    """コード品質を分析（グローバル関数）"""
    analyzer = CodeAnalyzer()
    metrics = analyzer.analyze_code_quality(code_text, api_calls)
    
    return {
        "overall_quality": metrics.overall_quality.value,
        "readability_score": metrics.readability_score,
        "efficiency_score": metrics.efficiency_score,
        "api_usage_diversity": metrics.api_usage_diversity,
        "lines_of_code": metrics.lines_of_code,
        "error_density": metrics.error_density
    }


# エクスポート用
__all__ = [
    "CodeQuality", "LearningEfficiency", "CodeMetrics", "LearningMetrics",
    "QualityReport", "CodeAnalyzer", "LearningAnalyzer", "QualityAssuranceManager",
    "generate_quality_report", "save_quality_report", "get_student_progress_summary",
    "analyze_code_quality"
]