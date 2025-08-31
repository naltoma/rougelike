#!/usr/bin/env python3
"""
進歩ログ系統と品質メトリクス拡充システム

セッションログ、品質保証、進捗管理を統合した包括的な学習分析システム
Google Sheets連携の準備も含む
"""

import json
import hashlib
import inspect
import ast
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import statistics


class AnalysisLevel(Enum):
    """分析レベル"""
    BASIC = "basic"           # 基本分析
    DETAILED = "detailed"     # 詳細分析
    COMPREHENSIVE = "comprehensive"  # 包括的分析


class CodeComplexity(Enum):
    """コード複雑度レベル"""
    SIMPLE = "simple"         # 単純
    MODERATE = "moderate"     # 中程度
    COMPLEX = "complex"       # 複雑
    VERY_COMPLEX = "very_complex"  # 非常に複雑


@dataclass
class CodeAnalysisResult:
    """コード分析結果"""
    # 基本メトリクス
    total_lines: int = 0
    logical_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    
    # 複雑度メトリクス
    cyclomatic_complexity: int = 1
    cognitive_complexity: int = 0
    nesting_depth: int = 0
    
    # 構造メトリクス
    function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    
    # コード品質指標
    code_hash: str = ""
    duplication_ratio: float = 0.0
    maintainability_index: float = 100.0
    
    # API使用パターン
    api_calls: List[str] = field(default_factory=list)
    api_diversity_score: float = 0.0
    api_usage_patterns: Dict[str, int] = field(default_factory=dict)
    
    @property
    def complexity_level(self) -> CodeComplexity:
        """複雑度レベルを判定"""
        if self.cyclomatic_complexity <= 5:
            return CodeComplexity.SIMPLE
        elif self.cyclomatic_complexity <= 10:
            return CodeComplexity.MODERATE
        elif self.cyclomatic_complexity <= 20:
            return CodeComplexity.COMPLEX
        else:
            return CodeComplexity.VERY_COMPLEX
    
    @property
    def code_quality_score(self) -> float:
        """コード品質スコア (0-1)"""
        factors = []
        
        # 保守性指標
        maintainability_score = min(1.0, self.maintainability_index / 100.0)
        factors.append(maintainability_score * 0.3)
        
        # 複雑度スコア（低いほど良い）
        complexity_score = max(0.0, 1.0 - (self.cyclomatic_complexity - 1) / 20.0)
        factors.append(complexity_score * 0.25)
        
        # API多様性スコア
        factors.append(self.api_diversity_score * 0.2)
        
        # コメント率（適度な値が良い）
        comment_ratio = self.comment_lines / max(1, self.total_lines)
        optimal_comment_score = 1.0 - abs(comment_ratio - 0.15) / 0.15
        factors.append(max(0.0, optimal_comment_score) * 0.15)
        
        # 重複率（低いほど良い）
        duplication_score = max(0.0, 1.0 - self.duplication_ratio)
        factors.append(duplication_score * 0.1)
        
        return sum(factors)


@dataclass
class LearningProgressMetrics:
    """学習進捗メトリクス"""
    # セッション基本情報
    session_id: str = ""
    student_id: str = ""
    stage_id: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # パフォーマンス指標
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    hint_requests: int = 0
    
    # 時間関連メトリクス
    session_duration: timedelta = field(default_factory=lambda: timedelta())
    average_response_time: float = 0.0
    total_think_time: float = 0.0
    
    # 学習行動指標
    error_recovery_rate: float = 0.0
    consistency_score: float = 0.0
    exploration_breadth: float = 0.0
    learning_momentum: float = 0.0
    
    # 協力・提出情報
    collaborators: List[str] = field(default_factory=list)
    late_submission: bool = False
    submission_date: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_attempts == 0:
            return 0.0
        return self.successful_attempts / self.total_attempts
    
    @property
    def efficiency_score(self) -> float:
        """効率性スコア"""
        factors = []
        
        # 成功率
        factors.append(self.success_rate * 0.4)
        
        # 応答時間（適度な速さが良い）
        if self.average_response_time > 0:
            optimal_time = 3.0  # 理想的な応答時間（秒）
            time_score = max(0.0, 1.0 - abs(self.average_response_time - optimal_time) / optimal_time)
            factors.append(time_score * 0.3)
        
        # エラー回復率
        factors.append(self.error_recovery_rate * 0.2)
        
        # 一貫性
        factors.append(self.consistency_score * 0.1)
        
        return sum(factors) / len(factors) if factors else 0.0


@dataclass
class ComprehensiveReport:
    """包括的レポート"""
    # メタデータ
    report_id: str = ""
    generated_at: datetime = field(default_factory=datetime.now)
    analysis_level: AnalysisLevel = AnalysisLevel.BASIC
    
    # 分析結果
    code_analysis: CodeAnalysisResult = field(default_factory=CodeAnalysisResult)
    learning_metrics: LearningProgressMetrics = field(default_factory=LearningProgressMetrics)
    
    # 統合評価
    overall_score: float = 0.0
    learning_grade: str = "C"
    
    # フィードバック
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_sheets_format(self) -> Dict[str, Any]:
        """Google Sheets用のフォーマットに変換"""
        return {
            # 基本情報
            "学生ID": self.learning_metrics.student_id,
            "ステージID": self.learning_metrics.stage_id,
            "セッションID": self.learning_metrics.session_id,
            "提出日時": self.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "遅延提出": "はい" if self.learning_metrics.late_submission else "いいえ",
            "協力者": ", ".join(self.learning_metrics.collaborators) if self.learning_metrics.collaborators else "",
            
            # コードメトリクス
            "総行数": self.code_analysis.total_lines,
            "論理行数": self.code_analysis.logical_lines,
            "関数数": self.code_analysis.function_count,
            "複雑度": self.code_analysis.cyclomatic_complexity,
            "コードハッシュ": self.code_analysis.code_hash[:12],
            
            # 学習メトリクス
            "試行回数": self.learning_metrics.total_attempts,
            "成功率": f"{self.learning_metrics.success_rate:.1%}",
            "セッション時間(分)": int(self.learning_metrics.session_duration.total_seconds() / 60),
            "平均応答時間(秒)": round(self.learning_metrics.average_response_time, 1),
            "ヒント使用回数": self.learning_metrics.hint_requests,
            
            # 評価
            "総合スコア": f"{self.overall_score:.1%}",
            "学習評価": self.learning_grade,
            "コード品質": f"{self.code_analysis.code_quality_score:.1%}",
            "効率性スコア": f"{self.learning_metrics.efficiency_score:.1%}",
            
            # フィードバック（最初の3つまで）
            "強み1": self.strengths[0] if len(self.strengths) > 0 else "",
            "強み2": self.strengths[1] if len(self.strengths) > 1 else "",
            "強み3": self.strengths[2] if len(self.strengths) > 2 else "",
            "改善点1": self.improvements[0] if len(self.improvements) > 0 else "",
            "改善点2": self.improvements[1] if len(self.improvements) > 1 else "",
            "改善点3": self.improvements[2] if len(self.improvements) > 2 else "",
        }


class CodeAnalyzer:
    """高度なコード分析器"""
    
    def __init__(self):
        self.api_functions = {
            "move", "turn_left", "turn_right", "attack", "pickup", "see",
            "can_undo", "undo", "is_game_finished", "get_game_result"
        }
    
    def analyze_code(self, code_text: str, api_history: List[str] = None) -> CodeAnalysisResult:
        """包括的なコード分析"""
        result = CodeAnalysisResult()
        
        if not code_text:
            return result
        
        # 基本行数カウント
        lines = code_text.split('\n')
        result.total_lines = len(lines)
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result.blank_lines += 1
            elif stripped.startswith('#'):
                result.comment_lines += 1
            else:
                result.logical_lines += 1
        
        # AST解析
        try:
            tree = ast.parse(code_text)
            self._analyze_ast(tree, result)
        except SyntaxError:
            pass  # 構文エラーがある場合はスキップ
        
        # API使用パターン分析
        if api_history:
            result.api_calls = api_history
            self._analyze_api_usage(api_history, result)
        else:
            self._extract_api_calls_from_code(code_text, result)
        
        # コードハッシュ生成
        result.code_hash = hashlib.md5(code_text.encode('utf-8')).hexdigest()
        
        # 重複率計算
        result.duplication_ratio = self._calculate_duplication_ratio(lines)
        
        # 保守性指標計算
        result.maintainability_index = self._calculate_maintainability_index(result)
        
        return result
    
    def _analyze_ast(self, tree: ast.AST, result: CodeAnalysisResult) -> None:
        """AST解析による詳細メトリクス計算"""
        for node in ast.walk(tree):
            # 関数・クラス数カウント
            if isinstance(node, ast.FunctionDef):
                result.function_count += 1
            elif isinstance(node, ast.ClassDef):
                result.class_count += 1
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                result.import_count += 1
            
            # 循環的複雑度計算
            elif isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                result.cyclomatic_complexity += 1
            elif isinstance(node, ast.BoolOp):
                result.cyclomatic_complexity += len(node.values) - 1
        
        # ネスト深度計算
        result.nesting_depth = self._calculate_nesting_depth(tree)
        
        # 認知的複雑度計算
        result.cognitive_complexity = self._calculate_cognitive_complexity(tree)
    
    def _analyze_api_usage(self, api_history: List[str], result: CodeAnalysisResult) -> None:
        """API使用パターン分析"""
        if not api_history:
            return
        
        # API使用頻度
        for api_call in api_history:
            result.api_usage_patterns[api_call] = result.api_usage_patterns.get(api_call, 0) + 1
        
        # API多様性スコア
        unique_apis = set(api_history)
        result.api_diversity_score = min(1.0, len(unique_apis) / len(self.api_functions))
    
    def _extract_api_calls_from_code(self, code_text: str, result: CodeAnalysisResult) -> None:
        """コードからAPI呼び出しを抽出"""
        for api_func in self.api_functions:
            pattern = rf'\b{api_func}\s*\('
            matches = re.findall(pattern, code_text)
            if matches:
                result.api_calls.extend([api_func] * len(matches))
                result.api_usage_patterns[api_func] = len(matches)
        
        # API多様性スコア
        unique_apis = set(result.api_calls)
        result.api_diversity_score = min(1.0, len(unique_apis) / len(self.api_functions))
    
    def _calculate_nesting_depth(self, tree: ast.AST) -> int:
        """ネスト深度を計算"""
        max_depth = 0
        
        def visit_node(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                for child in ast.iter_child_nodes(node):
                    visit_node(child, current_depth + 1)
            else:
                for child in ast.iter_child_nodes(node):
                    visit_node(child, current_depth)
        
        visit_node(tree)
        return max_depth
    
    def _calculate_cognitive_complexity(self, tree: ast.AST) -> int:
        """認知的複雑度を計算"""
        complexity = 0
        
        def visit_node(node, nesting_level=0):
            nonlocal complexity
            
            if isinstance(node, ast.If):
                complexity += 1 + nesting_level
            elif isinstance(node, (ast.While, ast.For)):
                complexity += 1 + nesting_level
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1 + nesting_level
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            
            # 再帰的に子ノードを処理
            new_nesting = nesting_level + (1 if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try)) else 0)
            for child in ast.iter_child_nodes(node):
                visit_node(child, new_nesting)
        
        visit_node(tree)
        return complexity
    
    def _calculate_duplication_ratio(self, lines: List[str]) -> float:
        """重複コード率を計算"""
        if len(lines) < 2:
            return 0.0
        
        # 意味のある行のみを対象
        meaningful_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        
        if len(meaningful_lines) < 2:
            return 0.0
        
        # 重複行を検出
        line_counts = {}
        for line in meaningful_lines:
            if len(line) > 5:  # 短すぎる行は除外
                line_counts[line] = line_counts.get(line, 0) + 1
        
        duplicates = sum(count - 1 for count in line_counts.values() if count > 1)
        return duplicates / len(meaningful_lines) if meaningful_lines else 0.0
    
    def _calculate_maintainability_index(self, result: CodeAnalysisResult) -> float:
        """保守性指標を計算（簡略版）"""
        # Microsoft 保守性指標の簡略版
        halstead_volume = max(1, result.logical_lines * 2)  # 簡略化
        cyclomatic = max(1, result.cyclomatic_complexity)
        lines_of_code = max(1, result.logical_lines)
        
        # 簡略版の保守性指標計算
        maintainability = (171 - 5.2 * (halstead_volume ** 0.23) - 
                          0.23 * cyclomatic - 16.2 * (lines_of_code ** 0.5))
        
        return max(0.0, min(100.0, maintainability))


class ProgressAnalyzer:
    """進歩分析器"""
    
    def __init__(self, data_dir: str = "data/progress"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.code_analyzer = CodeAnalyzer()
    
    def analyze_session(self, student_id: str, stage_id: str, session_id: str,
                       code_text: str, session_log: List[Dict[str, Any]],
                       api_history: List[str] = None,
                       collaborators: List[str] = None,
                       submission_date: datetime = None) -> ComprehensiveReport:
        """セッション包括分析"""
        
        # 基本情報設定
        report = ComprehensiveReport()
        report.report_id = f"{student_id}_{stage_id}_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # コード分析
        report.code_analysis = self.code_analyzer.analyze_code(code_text, api_history)
        
        # 学習メトリクス計算
        report.learning_metrics = self._calculate_learning_metrics(
            student_id, stage_id, session_id, session_log, collaborators, submission_date
        )
        
        # 総合評価
        report.overall_score = self._calculate_overall_score(
            report.code_analysis, report.learning_metrics
        )
        
        # 学習評価グレード
        report.learning_grade = self._calculate_learning_grade(report.overall_score)
        
        # フィードバック生成
        report.strengths = self._identify_strengths(report.code_analysis, report.learning_metrics)
        report.improvements = self._identify_improvements(report.code_analysis, report.learning_metrics)
        report.recommendations = self._generate_recommendations(report.code_analysis, report.learning_metrics)
        
        return report
    
    def _calculate_learning_metrics(self, student_id: str, stage_id: str, session_id: str,
                                  session_log: List[Dict[str, Any]], 
                                  collaborators: List[str] = None,
                                  submission_date: datetime = None) -> LearningProgressMetrics:
        """学習メトリクス計算"""
        metrics = LearningProgressMetrics(
            student_id=student_id,
            stage_id=stage_id,
            session_id=session_id,
            collaborators=collaborators or [],
            submission_date=submission_date
        )
        
        if not session_log:
            return metrics
        
        # 時間範囲計算
        timestamps = []
        response_times = []
        last_timestamp = None
        
        success_count = 0
        failure_count = 0
        error_recoveries = 0
        consecutive_errors = 0
        
        for entry in session_log:
            try:
                timestamp = datetime.fromisoformat(entry.get('timestamp', ''))
                timestamps.append(timestamp)
                
                # 応答時間計算
                if last_timestamp:
                    response_time = (timestamp - last_timestamp).total_seconds()
                    if 0.1 <= response_time <= 60:  # 合理的な範囲のみ
                        response_times.append(response_time)
                
                # イベント処理
                event_type = entry.get('event_type', '')
                if event_type == 'action_executed':
                    success = entry.get('data', {}).get('success', False)
                    if success:
                        success_count += 1
                        if consecutive_errors > 0:
                            error_recoveries += 1
                            consecutive_errors = 0
                    else:
                        failure_count += 1
                        consecutive_errors += 1
                
                elif event_type == 'hint_used':
                    metrics.hint_requests += 1
                
                last_timestamp = timestamp
                
            except (ValueError, KeyError):
                continue
        
        # メトリクス設定
        if timestamps:
            metrics.start_time = min(timestamps)
            metrics.end_time = max(timestamps)
            metrics.session_duration = metrics.end_time - metrics.start_time
        
        metrics.total_attempts = success_count + failure_count
        metrics.successful_attempts = success_count
        metrics.failed_attempts = failure_count
        
        if response_times:
            metrics.average_response_time = statistics.mean(response_times)
            metrics.total_think_time = sum(response_times)
        
        # エラー回復率
        if failure_count > 0:
            metrics.error_recovery_rate = error_recoveries / failure_count
        
        # 一貫性スコア（成功率の安定性）
        if metrics.total_attempts >= 10:
            # 時系列での成功率変動を計算
            window_size = 5
            success_rates = []
            
            actions = [entry for entry in session_log if entry.get('event_type') == 'action_executed']
            for i in range(len(actions) - window_size + 1):
                window = actions[i:i + window_size]
                successes = sum(1 for action in window if action.get('data', {}).get('success', False))
                success_rates.append(successes / window_size)
            
            if success_rates:
                metrics.consistency_score = 1.0 - (statistics.stdev(success_rates) if len(success_rates) > 1 else 0.0)
        
        # 遅延提出判定
        if submission_date and metrics.start_time:
            expected_date = metrics.start_time.date()
            actual_date = submission_date.date()
            metrics.late_submission = actual_date > expected_date
        
        return metrics
    
    def _calculate_overall_score(self, code_analysis: CodeAnalysisResult, 
                               learning_metrics: LearningProgressMetrics) -> float:
        """総合スコア計算"""
        weights = {
            'code_quality': 0.35,
            'learning_efficiency': 0.30,
            'success_rate': 0.20,
            'consistency': 0.10,
            'exploration': 0.05
        }
        
        scores = {
            'code_quality': code_analysis.code_quality_score,
            'learning_efficiency': learning_metrics.efficiency_score,
            'success_rate': learning_metrics.success_rate,
            'consistency': learning_metrics.consistency_score,
            'exploration': learning_metrics.exploration_breadth
        }
        
        # 重み付き平均
        total_score = sum(weights[key] * scores[key] for key in weights.keys())
        
        # 遅延提出や協力者の影響
        if learning_metrics.late_submission:
            total_score *= 0.9
        
        if learning_metrics.collaborators:
            total_score *= 0.95  # 協力者がいる場合はわずかな減点
        
        return min(1.0, max(0.0, total_score))
    
    def _calculate_learning_grade(self, overall_score: float) -> str:
        """学習評価グレード計算"""
        if overall_score >= 0.9:
            return "A+"
        elif overall_score >= 0.8:
            return "A"
        elif overall_score >= 0.7:
            return "B"
        elif overall_score >= 0.6:
            return "C"
        elif overall_score >= 0.5:
            return "D"
        else:
            return "F"
    
    def _identify_strengths(self, code_analysis: CodeAnalysisResult,
                          learning_metrics: LearningProgressMetrics) -> List[str]:
        """強みを特定"""
        strengths = []
        
        # コード品質の強み
        if code_analysis.code_quality_score >= 0.8:
            strengths.append("高品質なコードを書けています")
        
        if code_analysis.api_diversity_score >= 0.7:
            strengths.append("多様なAPIを効果的に活用しています")
        
        if code_analysis.complexity_level in [CodeComplexity.SIMPLE, CodeComplexity.MODERATE]:
            strengths.append("適切な複雑度でコードを構成しています")
        
        # 学習行動の強み
        if learning_metrics.success_rate >= 0.8:
            strengths.append("高い成功率を維持しています")
        
        if learning_metrics.consistency_score >= 0.8:
            strengths.append("安定したパフォーマンスを示しています")
        
        if learning_metrics.error_recovery_rate >= 0.7:
            strengths.append("エラーから素早く回復できています")
        
        if learning_metrics.average_response_time <= 5.0:
            strengths.append("適切な思考時間で効率的に取り組んでいます")
        
        return strengths
    
    def _identify_improvements(self, code_analysis: CodeAnalysisResult,
                             learning_metrics: LearningProgressMetrics) -> List[str]:
        """改善点を特定"""
        improvements = []
        
        # コード品質の改善点
        if code_analysis.code_quality_score < 0.5:
            improvements.append("コードの構造と可読性を改善しましょう")
        
        if code_analysis.complexity_level == CodeComplexity.VERY_COMPLEX:
            improvements.append("コードをより単純に分割することを検討しましょう")
        
        if code_analysis.api_diversity_score < 0.3:
            improvements.append("より多くのAPIを試してみましょう")
        
        if code_analysis.duplication_ratio > 0.3:
            improvements.append("重複コードを関数化して整理しましょう")
        
        # 学習行動の改善点
        if learning_metrics.success_rate < 0.5:
            improvements.append("基本的なアプローチを見直しましょう")
        
        if learning_metrics.error_recovery_rate < 0.3:
            improvements.append("エラー後の対処方法を改善しましょう")
        
        if learning_metrics.consistency_score < 0.5:
            improvements.append("一貫した解法パターンを身につけましょう")
        
        if learning_metrics.hint_requests > 5:
            improvements.append("自力での問題解決能力を向上させましょう")
        
        return improvements
    
    def _generate_recommendations(self, code_analysis: CodeAnalysisResult,
                                learning_metrics: LearningProgressMetrics) -> List[str]:
        """推奨事項生成"""
        recommendations = []
        
        # コード品質基準の推奨
        if code_analysis.comment_lines == 0:
            recommendations.append("コメントを追加して、コードの意図を明確にしましょう")
        
        if code_analysis.function_count == 0:
            recommendations.append("処理を関数に分割して、再利用性を高めましょう")
        
        # 学習効率向上の推奨
        if learning_metrics.average_response_time > 10.0:
            recommendations.append("もう少し迅速に判断して、学習リズムを向上させましょう")
        
        if learning_metrics.exploration_breadth < 0.5:
            recommendations.append("異なるアプローチを試して、学習の幅を広げましょう")
        
        # 段階別推奨
        if learning_metrics.success_rate >= 0.8 and code_analysis.complexity_level == CodeComplexity.SIMPLE:
            recommendations.append("基本をマスターしました。より高度な問題に挑戦してみましょう")
        
        elif learning_metrics.success_rate < 0.5:
            recommendations.append("基本的なパターンを反復練習して、確実性を高めましょう")
        
        return recommendations
    
    def save_report(self, report: ComprehensiveReport) -> Path:
        """レポートを保存"""
        filename = f"{report.report_id}.json"
        filepath = self.data_dir / filename
        
        # レポートをシリアライズ
        report_data = asdict(report)
        
        # datetime オブジェクトを文字列に変換
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, timedelta):
                return obj.total_seconds()
            return obj
        
        # 再帰的にdatetimeとEnumを変換
        def deep_convert(data):
            if isinstance(data, dict):
                return {k: deep_convert(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [deep_convert(item) for item in data]
            elif isinstance(data, Enum):
                return data.value
            else:
                return convert_datetime(data)
        
        report_data = deep_convert(report_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_report(self, report_id: str) -> Optional[ComprehensiveReport]:
        """レポートを読み込み"""
        filepath = self.data_dir / f"{report_id}.json"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 簡略版の復元（必要に応じて詳細化）
            # 実際の実装では、すべてのフィールドを正確に復元する必要があります
            return ComprehensiveReport(
                report_id=data.get('report_id', ''),
                overall_score=data.get('overall_score', 0.0),
                learning_grade=data.get('learning_grade', 'C')
            )
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"レポート読み込みエラー: {e}")
            return None
    
    def get_student_history(self, student_id: str) -> List[ComprehensiveReport]:
        """学生の履歴レポート取得"""
        reports = []
        pattern = f"{student_id}_*.json"
        
        for filepath in self.data_dir.glob(pattern):
            report_id = filepath.stem
            report = self.load_report(report_id)
            if report:
                reports.append(report)
        
        # 時刻順にソート
        reports.sort(key=lambda r: r.generated_at)
        return reports


# グローバルインスタンス
_progress_analyzer = ProgressAnalyzer()


def analyze_student_progress(student_id: str, stage_id: str, session_id: str,
                           code_text: str, session_log: List[Dict[str, Any]],
                           api_history: List[str] = None,
                           collaborators: List[str] = None,
                           submission_date: datetime = None) -> ComprehensiveReport:
    """学生進捗包括分析（グローバル関数）"""
    return _progress_analyzer.analyze_session(
        student_id, stage_id, session_id, code_text, session_log,
        api_history, collaborators, submission_date
    )


def save_progress_report(report: ComprehensiveReport) -> str:
    """進捗レポート保存（グローバル関数）"""
    filepath = _progress_analyzer.save_report(report)
    return str(filepath)


def get_student_learning_history(student_id: str) -> List[Dict[str, Any]]:
    """学生学習履歴取得（グローバル関数）"""
    reports = _progress_analyzer.get_student_history(student_id)
    return [asdict(report) for report in reports]


def analyze_code_complexity(code_text: str) -> Dict[str, Any]:
    """コード複雑度分析（グローバル関数）"""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_code(code_text)
    
    return {
        "complexity_level": result.complexity_level.value,
        "cyclomatic_complexity": result.cyclomatic_complexity,
        "cognitive_complexity": result.cognitive_complexity,
        "maintainability_index": result.maintainability_index,
        "code_quality_score": result.code_quality_score,
        "api_diversity_score": result.api_diversity_score
    }


# エクスポート用
__all__ = [
    "AnalysisLevel", "CodeComplexity", "CodeAnalysisResult", "LearningProgressMetrics",
    "ComprehensiveReport", "CodeAnalyzer", "ProgressAnalyzer",
    "analyze_student_progress", "save_progress_report", "get_student_learning_history",
    "analyze_code_complexity"
]