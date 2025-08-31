"""
教育的エラー処理システム
Educational Error Handling System for Programming Beginners
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import traceback
import re
from pathlib import Path
import json

from . import GameState, Position, Direction


class ErrorCategory(Enum):
    """エラーカテゴリー"""
    LOGIC_ERROR = "logic_error"              # 論理エラー
    SYNTAX_ERROR = "syntax_error"            # 構文エラー
    RUNTIME_ERROR = "runtime_error"          # 実行時エラー
    API_USAGE_ERROR = "api_usage_error"      # API使用エラー
    GAME_RULE_ERROR = "game_rule_error"      # ゲームルールエラー
    PERFORMANCE_ERROR = "performance_error"  # パフォーマンスエラー
    INPUT_ERROR = "input_error"              # 入力エラー
    SYSTEM_ERROR = "system_error"            # システムエラー


class ErrorSeverity(Enum):
    """エラー深刻度"""
    INFO = "info"          # 情報（注意喚起）
    WARNING = "warning"    # 警告（改善推奨）
    ERROR = "error"        # エラー（修正必要）
    CRITICAL = "critical"  # 重大エラー（プログラム停止）


@dataclass
class ErrorSolution:
    """エラー解決策"""
    title: str                    # 解決策のタイトル
    description: str              # 詳細説明
    code_example: str = ""        # サンプルコード
    difficulty: str = "beginner"  # 難易度（beginner/intermediate/advanced）
    priority: int = 1             # 優先度（1が最高）
    
    def __str__(self) -> str:
        result = f"💡 {self.title}\n   {self.description}"
        if self.code_example:
            result += f"\n   例: {self.code_example}"
        return result


@dataclass
class EducationalError:
    """教育的エラー情報"""
    original_error: Exception
    category: ErrorCategory
    severity: ErrorSeverity
    japanese_message: str
    english_message: str
    context: str = ""
    solutions: List[ErrorSolution] = None
    related_concepts: List[str] = None
    learning_objectives: List[str] = None
    
    def __post_init__(self):
        if self.solutions is None:
            self.solutions = []
        if self.related_concepts is None:
            self.related_concepts = []
        if self.learning_objectives is None:
            self.learning_objectives = []
    
    def get_formatted_message(self, language: str = "japanese") -> str:
        """フォーマットされたエラーメッセージを取得"""
        if language == "english":
            return self.english_message
        return self.japanese_message
    
    def get_severity_icon(self) -> str:
        """深刻度に応じたアイコンを取得"""
        icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨"
        }
        return icons.get(self.severity, "❓")
    
    @property
    def title(self) -> str:
        """エラータイトルを取得"""
        return f"{type(self.original_error).__name__}: {self.japanese_message}"
    
    @property
    def explanation(self) -> str:
        """エラー説明を取得"""
        return self.context or "詳細な説明が利用できません"
    
    @property
    def solution(self) -> str:
        """主要な解決方法を取得"""
        if self.solutions and len(self.solutions) > 0:
            return self.solutions[0].description
        return ""
    
    @property
    def example_code(self) -> str:
        """例コードを取得"""
        if self.solutions and len(self.solutions) > 0:
            return self.solutions[0].example_code or ""
        return ""
    
    @property
    def hints(self) -> List[str]:
        """ヒントリストを取得"""
        hints = []
        for solution in self.solutions:
            if solution.description:
                hints.append(solution.description)
        return hints


class ErrorAnalyzer:
    """エラー分析器"""
    
    def __init__(self):
        self.error_patterns = self._load_error_patterns()
        self.context_analyzers = self._setup_context_analyzers()
        
    def _load_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """エラーパターンを読み込み"""
        return {
            # API使用エラー
            "APIUsageError": {
                "category": ErrorCategory.API_USAGE_ERROR,
                "severity": ErrorSeverity.ERROR,
                "patterns": {
                    r"このステージでは.*APIは使用できません": {
                        "japanese": "🚫 API制限エラー: このステージでは使用できないAPIを呼び出しました。",
                        "english": "API Restriction Error: You called an API that is not allowed in this stage.",
                        "solutions": [
                            ErrorSolution(
                                "利用可能なAPIを確認する",
                                "ステージ初期化時に表示される利用可能APIリストを確認してください。",
                                "initialize_stage('stage01')  # 利用可能APIが表示されます"
                            ),
                            ErrorSolution(
                                "ステージに適した戦略を考える", 
                                "制限されたAPIの中で目標を達成する方法を考えてみましょう。"
                            )
                        ],
                        "concepts": ["API制限", "ステージ設計", "制約プログラミング"],
                        "objectives": ["APIの適切な使用方法を理解する", "制約下での問題解決能力を養う"]
                    }
                }
            },
            
            # 移動エラー
            "MovementError": {
                "category": ErrorCategory.GAME_RULE_ERROR,
                "severity": ErrorSeverity.WARNING,
                "patterns": {
                    r"壁にぶつかりました": {
                        "japanese": "🧱 移動エラー: 壁があるため移動できません。",
                        "english": "Movement Error: Cannot move because there is a wall.",
                        "solutions": [
                            ErrorSolution(
                                "事前に周囲を確認する",
                                "move()の前にsee()で周囲の状況を確認しましょう。",
                                "info = see()\nif info['surroundings']['front'] != 'wall':\n    move()"
                            ),
                            ErrorSolution(
                                "別の方向を探す",
                                "壁がある場合は回転して別の方向を試してみましょう。",
                                "turn_left()  # または turn_right()"
                            )
                        ],
                        "concepts": ["衝突判定", "事前チェック", "条件分岐"],
                        "objectives": ["安全な移動プログラムを書けるようになる", "エラー回避の重要性を理解する"]
                    },
                    r"移動禁止マスです": {
                        "japanese": "🚫 移動エラー: そのマスは移動禁止区域です。",
                        "english": "Movement Error: That cell is a forbidden area.",
                        "solutions": [
                            ErrorSolution(
                                "別の経路を探す",
                                "移動禁止マスを避けて、別の経路でゴールを目指しましょう。",
                                "# 迂回ルートを考える\nturn_left()\nmove()\nturn_right()"
                            )
                        ],
                        "concepts": ["経路探索", "障害物回避"],
                        "objectives": ["複数の解決策を考える能力を養う"]
                    }
                }
            },
            
            # Python一般エラー
            "NameError": {
                "category": ErrorCategory.SYNTAX_ERROR,
                "severity": ErrorSeverity.ERROR,
                "patterns": {
                    r"name '(.*)' is not defined": {
                        "japanese": "📝 変数/関数未定義エラー: '{1}'が定義されていません。",
                        "english": "Name Error: '{1}' is not defined.",
                        "solutions": [
                            ErrorSolution(
                                "スペルを確認する",
                                "関数名や変数名のスペル（綴り）を確認してください。",
                                "move()  # ✓ 正しい\nmov()   # ✗ スペルミス"
                            ),
                            ErrorSolution(
                                "インポートを確認する", 
                                "必要な関数をインポートしているか確認してください。",
                                "from engine.api import move, turn_left, turn_right"
                            ),
                            ErrorSolution(
                                "関数が存在するか確認する",
                                "使おうとしている関数名が正しいかドキュメントで確認しましょう。"
                            )
                        ],
                        "concepts": ["変数スコープ", "関数定義", "インポート"],
                        "objectives": ["Pythonの基本構文を理解する", "デバッグスキルを身につける"]
                    }
                }
            },
            
            # インデントエラー
            "IndentationError": {
                "category": ErrorCategory.SYNTAX_ERROR,
                "severity": ErrorSeverity.ERROR,
                "patterns": {
                    r"expected an indented block": {
                        "japanese": "🎯 インデントエラー: ここにはインデントされたコードブロックが必要です。",
                        "english": "Indentation Error: Expected an indented block here.",
                        "solutions": [
                            ErrorSolution(
                                "適切にインデントする",
                                "if文やfor文の後は、内容を4スペースまたは1タブでインデントしてください。",
                                "if condition:\n    move()  # 4スペースのインデント\n    turn_right()"
                            ),
                            ErrorSolution(
                                "空のブロックにはpassを使う",
                                "何も実行しない場合はpassキーワードを使用してください。",
                                "if condition:\n    pass  # 何もしない"
                            )
                        ],
                        "concepts": ["インデント", "コードブロック", "Python構文"],
                        "objectives": ["Pythonのインデントルールを理解する"]
                    }
                }
            },
            
            # 無限ループ
            "InfiniteLoopError": {
                "category": ErrorCategory.LOGIC_ERROR,
                "severity": ErrorSeverity.WARNING,
                "patterns": {
                    r"最大ターン数に達しました": {
                        "japanese": "🔄 ループエラー: 最大ターン数に達しました。無限ループの可能性があります。",
                        "english": "Loop Error: Maximum turns reached. Possible infinite loop.",
                        "solutions": [
                            ErrorSolution(
                                "ゴール条件を確認する",
                                "ゴールに到達する条件を正しく設定しているか確認してください。",
                                "while not is_game_finished():\n    # ゴールに向かう処理"
                            ),
                            ErrorSolution(
                                "ループ脱出条件を追加する",
                                "ループが永続的に続かないよう、適切な終了条件を設けましょう。",
                                "max_attempts = 100\nfor i in range(max_attempts):\n    if is_game_finished():\n        break"
                            ),
                            ErrorSolution(
                                "デバッグ出力を追加する",
                                "ループ中で現在位置を出力して、進歩しているか確認しましょう。",
                                "info = see()\nprint(f\"現在位置: {info['player']['position']}\")"
                            )
                        ],
                        "concepts": ["ループ制御", "終了条件", "デバッグ"],
                        "objectives": ["効率的なアルゴリズムを設計する能力を養う", "デバッグ技術を習得する"]
                    }
                }
            }
        }
    
    def _setup_context_analyzers(self) -> Dict[str, Callable]:
        """コンテキスト分析器を設定"""
        return {
            "game_state": self._analyze_game_context,
            "code_location": self._analyze_code_location,
            "recent_actions": self._analyze_recent_actions,
            "learning_stage": self._analyze_learning_stage
        }
    
    def analyze_error(self, error: Exception, context: Dict[str, Any] = None) -> EducationalError:
        """エラーを分析して教育的エラー情報を生成"""
        context = context or {}
        
        # エラータイプとメッセージを取得
        error_type = type(error).__name__
        error_message = str(error)
        
        # パターンマッチング
        educational_info = self._match_error_pattern(error_type, error_message)
        
        # コンテキスト分析
        context_info = self._analyze_context(context)
        
        # EducationalError オブジェクトを構築
        educational_error = EducationalError(
            original_error=error,
            category=educational_info.get("category", ErrorCategory.RUNTIME_ERROR),
            severity=educational_info.get("severity", ErrorSeverity.ERROR),
            japanese_message=educational_info.get("japanese", f"エラーが発生しました: {error_message}"),
            english_message=educational_info.get("english", f"An error occurred: {error_message}"),
            context=context_info.get("summary", ""),
            solutions=educational_info.get("solutions", []),
            related_concepts=educational_info.get("concepts", []),
            learning_objectives=educational_info.get("objectives", [])
        )
        
        # コンテキストに基づく解決策の追加
        self._add_contextual_solutions(educational_error, context)
        
        return educational_error
    
    def _match_error_pattern(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """エラーパターンにマッチング"""
        if error_type in self.error_patterns:
            patterns = self.error_patterns[error_type]["patterns"]
            
            for pattern, info in patterns.items():
                match = re.search(pattern, error_message)
                if match:
                    # マッチしたグループを使ってメッセージを動的生成
                    result = info.copy()
                    if match.groups():
                        try:
                            result["japanese"] = result["japanese"].format(*match.groups())
                            result["english"] = result["english"].format(*match.groups())
                        except (IndexError, KeyError):
                            # フォーマットに失敗した場合はそのまま使用
                            pass
                    return result
        
        # デフォルトパターン
        return {
            "category": ErrorCategory.RUNTIME_ERROR,
            "severity": ErrorSeverity.ERROR,
            "japanese": f"🐛 {error_type}: {error_message}",
            "english": f"🐛 {error_type}: {error_message}",
            "solutions": [
                ErrorSolution(
                    "エラーメッセージを読む",
                    "エラーメッセージをよく読んで、何が問題なのかを理解しましょう。"
                ),
                ErrorSolution(
                    "先生に質問する",
                    "分からない場合は、遠慮せずに先生に質問してください。"
                )
            ]
        }
    
    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """コンテキストを分析"""
        analysis_result = {
            "summary": "",
            "suggestions": []
        }
        
        for analyzer_name, analyzer_func in self.context_analyzers.items():
            try:
                result = analyzer_func(context)
                if result:
                    analysis_result[analyzer_name] = result
            except Exception as e:
                # 分析エラーは無視（メインエラー処理を妨げない）
                pass
        
        return analysis_result
    
    def _analyze_game_context(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """ゲーム状態のコンテキスト分析"""
        game_state = context.get("game_state")
        if not game_state:
            return None
        
        analysis = {}
        
        # プレイヤー位置分析
        player_pos = game_state.player.position
        analysis["player_position"] = f"({player_pos.x}, {player_pos.y})"
        
        # ゴールとの距離
        if game_state.goal_position:
            distance = int(player_pos.distance_to(game_state.goal_position))
            analysis["distance_to_goal"] = distance
            
            if distance == 1:
                analysis["suggestion"] = "ゴールまであと1マス！もう一度移動を試してみましょう。"
            elif distance > 10:
                analysis["suggestion"] = "ゴールまで遠いです。効率的な経路を考えてみましょう。"
        
        # ターン数分析
        turn_ratio = game_state.turn_count / game_state.max_turns
        if turn_ratio > 0.8:
            analysis["turn_warning"] = "残りターン数が少なくなっています。効率的な移動を心がけましょう。"
        
        return analysis
    
    def _analyze_code_location(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """コード位置の分析"""
        # スタックトレースから実行位置を特定
        traceback_info = context.get("traceback")
        if traceback_info:
            # 学生のコードファイルを特定
            for frame in traceback_info:
                if "solve" in frame.get("function", "") or "main.py" in frame.get("filename", ""):
                    return {
                        "file": frame.get("filename", ""),
                        "line": frame.get("lineno", 0),
                        "function": frame.get("function", ""),
                        "suggestion": "エラーが発生した行を確認して、コードを見直してみましょう。"
                    }
        
        return None
    
    def _analyze_recent_actions(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """最近のアクション履歴分析"""
        recent_actions = context.get("recent_actions", [])
        if not recent_actions:
            return None
        
        analysis = {"actions": recent_actions[-5:]}  # 最新5アクション
        
        # パターン分析
        if len(recent_actions) >= 3:
            last_three = [action.get("api", "") for action in recent_actions[-3:]]
            
            # 同じアクションの繰り返し検出
            if len(set(last_three)) == 1:
                analysis["pattern"] = "same_action_repeated"
                analysis["suggestion"] = "同じアクションを繰り返しています。別のアプローチを試してみましょう。"
            
            # 無駄な回転検出
            if last_three == ["turn_right", "turn_right", "turn_right"]:
                analysis["pattern"] = "inefficient_turning"
                analysis["suggestion"] = "右に3回回転するより、turn_left()を1回使う方が効率的です。"
        
        return analysis
    
    def _analyze_learning_stage(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """学習段階の分析"""
        stage_id = context.get("stage_id", "")
        student_progress = context.get("student_progress")
        
        analysis = {"stage": stage_id}
        
        # ステージ別アドバイス
        if stage_id == "stage01":
            analysis["stage_advice"] = "基本移動の練習ステージです。move()とturn_right()を使ってゴールを目指しましょう。"
        elif stage_id == "stage02":
            analysis["stage_advice"] = "迷路ステージです。右手法（右手を壁に付けて歩く）を試してみましょう。"
        elif stage_id == "stage03":
            analysis["stage_advice"] = "障害物回避ステージです。see()で周囲を確認してから行動しましょう。"
        
        # 進捗に基づくアドバイス
        if student_progress:
            attempts = student_progress.get("total_attempts", 0)
            success_rate = student_progress.get("success_rate", 0)
            
            if attempts > 10 and success_rate < 0.3:
                analysis["progress_advice"] = "成功率が低めです。基本的なアルゴリズムを復習してみましょう。"
            elif attempts > 5 and success_rate > 0.8:
                analysis["progress_advice"] = "順調に進歩しています！より効率的な解法に挑戦してみましょう。"
        
        return analysis
    
    def _add_contextual_solutions(self, educational_error: EducationalError, context: Dict[str, Any]) -> None:
        """コンテキストに基づく追加解決策"""
        game_state = context.get("game_state")
        stage_id = context.get("stage_id", "")
        
        # ゲーム状態に基づく解決策
        if game_state and educational_error.category == ErrorCategory.GAME_RULE_ERROR:
            player_pos = game_state.player.position
            
            # 端に近い場合の警告
            if player_pos.x == 0 or player_pos.y == 0:
                educational_error.solutions.append(
                    ErrorSolution(
                        "境界付近での注意",
                        "ゲームフィールドの端にいます。壁や境界に注意して移動しましょう。",
                        "# 移動前に安全確認\ninfo = see()\nif info['surroundings']['front'] == 'empty':\n    move()"
                    )
                )
        
        # ステージ固有の解決策
        if stage_id == "stage02" and "move" in str(educational_error.original_error):
            educational_error.solutions.append(
                ErrorSolution(
                    "迷路攻略のヒント",
                    "迷路では右手法が有効です。常に右側の壁に手を付けて歩くイメージです。",
                    "# 右手法の基本形\nwhile not is_game_finished():\n    if see()['surroundings']['right'] != 'wall':\n        turn_right()\n        move()\n    elif see()['surroundings']['front'] != 'wall':\n        move()\n    else:\n        turn_left()"
                )
            )


class ErrorHandler:
    """教育的エラーハンドラー"""
    
    def __init__(self, language: str = "japanese", detailed_mode: bool = True):
        self.language = language
        self.detailed_mode = detailed_mode
        self.analyzer = ErrorAnalyzer()
        self.error_history: List[EducationalError] = []
        
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> EducationalError:
        """エラーを処理して教育的フィードバックを提供"""
        # エラー分析
        educational_error = self.analyzer.analyze_error(error, context)
        
        # エラー履歴に追加
        self.error_history.append(educational_error)
        
        # エラー表示
        self._display_error(educational_error)
        
        return educational_error
    
    def _display_error(self, educational_error: EducationalError) -> None:
        """エラーを表示"""
        icon = educational_error.get_severity_icon()
        message = educational_error.get_formatted_message(self.language)
        
        print(f"\n{icon} {message}")
        
        # 詳細モードの場合は追加情報を表示
        if self.detailed_mode:
            self._display_detailed_info(educational_error)
    
    def _display_detailed_info(self, educational_error: EducationalError) -> None:
        """詳細情報を表示"""
        # コンテキスト情報
        if educational_error.context:
            print(f"🔍 状況: {educational_error.context}")
        
        # 解決策表示
        if educational_error.solutions:
            print("\n📚 解決策:")
            for i, solution in enumerate(educational_error.solutions[:3], 1):  # 最大3つ表示
                print(f"{i}. {solution}")
        
        # 関連概念
        if educational_error.related_concepts:
            concepts = ", ".join(educational_error.related_concepts)
            print(f"\n🎓 関連概念: {concepts}")
        
        # 学習目標
        if educational_error.learning_objectives:
            print("\n🎯 学習目標:")
            for objective in educational_error.learning_objectives[:2]:  # 最大2つ表示
                print(f"   • {objective}")
        
        print()  # 改行
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計を取得"""
        if not self.error_history:
            return {"total_errors": 0}
        
        # カテゴリ別集計
        category_counts = {}
        for error in self.error_history:
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # 深刻度別集計
        severity_counts = {}
        for error in self.error_history:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # 最頻出エラー
        error_types = [type(error.original_error).__name__ for error in self.error_history]
        most_common_error = max(set(error_types), key=error_types.count) if error_types else None
        
        return {
            "total_errors": len(self.error_history),
            "categories": category_counts,
            "severities": severity_counts,
            "most_common_error": most_common_error,
            "recent_errors": len([e for e in self.error_history[-10:]])  # 最新10エラー
        }
    
    def generate_learning_report(self) -> str:
        """学習レポートを生成"""
        stats = self.get_error_statistics()
        
        if stats["total_errors"] == 0:
            return "🎉 エラーは発生していません。順調に進んでいます！"
        
        report = f"📊 エラー学習レポート\n"
        report += f"=" * 30 + "\n"
        report += f"総エラー数: {stats['total_errors']}\n"
        
        # カテゴリ別分析
        if stats["categories"]:
            report += f"\n📋 エラーカテゴリ別:\n"
            for category, count in stats["categories"].items():
                percentage = count / stats["total_errors"] * 100
                report += f"  • {category}: {count}回 ({percentage:.1f}%)\n"
        
        # 改善提案
        report += f"\n💡 改善提案:\n"
        if stats.get("most_common_error"):
            report += f"  • '{stats['most_common_error']}'が最も多く発生しています\n"
            report += f"  • このエラーの解決方法を重点的に学習しましょう\n"
        
        if stats["categories"].get("syntax_error", 0) > 0:
            report += f"  • 構文エラーが発生しています。Python基本構文を復習しましょう\n"
        
        if stats["categories"].get("logic_error", 0) > 0:
            report += f"  • 論理エラーが多めです。アルゴリズムの設計を見直してみましょう\n"
        
        return report
    
    def get_personalized_hints(self, current_context: Dict[str, Any] = None) -> List[str]:
        """個人化されたヒントを取得"""
        hints = []
        stats = self.get_error_statistics()
        
        # エラー履歴に基づくヒント
        if stats["categories"].get("api_usage_error", 0) > 2:
            hints.append("💡 APIの使用方法を確認しましょう。各ステージで利用可能なAPIが異なります。")
        
        if stats["categories"].get("game_rule_error", 0) > 3:
            hints.append("💡 事前確認を心がけましょう。see()で周囲を確認してから行動すると安全です。")
        
        # 最近のエラーパターンに基づくヒント
        recent_errors = self.error_history[-5:] if len(self.error_history) >= 5 else self.error_history
        
        if len(recent_errors) >= 3:
            recent_categories = [e.category for e in recent_errors]
            if recent_categories.count(ErrorCategory.GAME_RULE_ERROR) >= 2:
                hints.append("💡 同じタイプのエラーが続いています。アプローチを変えてみましょう。")
        
        # デフォルトヒント
        if not hints:
            hints.append("💡 エラーを恐れず、チャレンジしてみましょう。エラーから学ぶことが大切です。")
        
        return hints[:3]  # 最大3つまで
    
    def check_common_patterns(self, call_history: List[Dict[str, Any]]) -> List[str]:
        """一般的なミステイクパターンをチェック"""
        mistakes = []
        
        if not call_history:
            return mistakes
        
        # 連続した同じ失敗
        consecutive_failures = 1
        last_failure = None
        
        for call in call_history[-10:]:  # 直近10回をチェック
            if "失敗" in call.get("message", "") or "エラー" in call.get("message", ""):
                if last_failure == call.get("api"):
                    consecutive_failures += 1
                else:
                    consecutive_failures = 1
                    last_failure = call.get("api")
                
                if consecutive_failures >= 3:
                    mistakes.append(f"同じアクション（{last_failure}）で連続して失敗しています。別のアプローチを試してみましょう。")
                    break
        
        # 壁に向かって連続移動
        wall_moves = 0
        for call in call_history[-5:]:
            if call.get("api") == "move" and "壁" in call.get("message", ""):
                wall_moves += 1
            else:
                wall_moves = 0
                
            if wall_moves >= 2:
                mistakes.append("壁に向かって移動し続けています。turn_right()やturn_left()で向きを変えてみましょう。")
                break
        
        # see()を使わずに行動し続ける
        recent_actions = [call.get("api") for call in call_history[-7:]]
        if "see" not in recent_actions and len(recent_actions) >= 5:
            action_count = len([a for a in recent_actions if a in ["move", "attack", "pickup"]])
            if action_count >= 4:
                mistakes.append("周囲を確認せずに行動し続けています。see()で状況確認することをお勧めします。")
        
        # 同じ場所でループしている可能性
        move_count = sum(1 for call in call_history[-8:] if call.get("api") == "move")
        turn_count = sum(1 for call in call_history[-8:] if call.get("api") in ["turn_left", "turn_right"])
        
        if move_count >= 4 and turn_count >= 4 and len(call_history) >= 8:
            mistakes.append("同じ場所を回っている可能性があります。迷路では右手法や左手法を試してみましょう。")
        
        return mistakes
    
    def get_error_pattern(self, error_type: str) -> Optional[str]:
        """特定のエラータイプのパターンを取得"""
        patterns = {
            "NameError": "変数名や関数名のスペルミスが原因の可能性があります。",
            "SyntaxError": "構文エラーです。括弧の対応やインデントを確認してください。",
            "TypeError": "データ型が期待されるものと異なります。",
            "AttributeError": "オブジェクトが持たない属性やメソッドを使用しようとしています。",
            "IndexError": "リストや文字列の範囲外にアクセスしようとしています。",
            "APIUsageError": "このステージで使用できないAPIを呼び出しています。"
        }
        return patterns.get(error_type)
    
    def show_help(self, error_category: str = None) -> None:
        """エラーヘルプを表示"""
        if error_category is None:
            print("🆘 エラーヘルプ")
            print("=" * 40)
            print("💡 よくあるエラーとその対処法:")
            print("  • NameError: 変数・関数名のスペルミス")
            print("  • SyntaxError: 括弧の対応、インデントの問題")  
            print("  • APIUsageError: 利用不可能なAPIの使用")
            print("  • 壁への衝突: see()で事前確認")
            print("  • 同じエラーの繰り返し: アプローチを変更")
            print("\n📚 基本的なデバッグ手順:")
            print("  1. エラーメッセージをよく読む")
            print("  2. see()で現在の状況を確認")
            print("  3. 小さなステップで問題を分割")
            print("  4. 先生やサンプルコードを参考にする")
        else:
            pattern = self.get_error_pattern(error_category)
            if pattern:
                print(f"🆘 {error_category}について:")
                print(f"💡 {pattern}")
            else:
                print(f"❌ '{error_category}'についてのヘルプが見つかりませんでした")


# グローバルエラーハンドラー
_global_error_handler = ErrorHandler()


def set_error_language(language: str) -> None:
    """エラー表示言語を設定"""
    global _global_error_handler
    _global_error_handler.language = language
    print(f"エラー表示言語を{language}に設定しました")


def set_detailed_error_mode(enabled: bool) -> None:
    """詳細エラーモードを設定"""
    global _global_error_handler
    _global_error_handler.detailed_mode = enabled
    mode_str = "詳細" if enabled else "簡易"
    print(f"エラー表示モードを{mode_str}に設定しました")


def handle_educational_error(error: Exception, context: Dict[str, Any] = None) -> EducationalError:
    """教育的エラーを処理（グローバル関数）"""
    return _global_error_handler.handle_error(error, context)


def get_error_statistics() -> Dict[str, Any]:
    """エラー統計を取得（グローバル関数）"""
    return _global_error_handler.get_error_statistics()


def generate_error_learning_report() -> str:
    """エラー学習レポートを生成（グローバル関数）"""
    return _global_error_handler.generate_learning_report()


def get_personalized_error_hints(context: Dict[str, Any] = None) -> List[str]:
    """個人化されたエラーヒントを取得（グローバル関数）"""
    return _global_error_handler.get_personalized_hints(context)


# エクスポート用
__all__ = [
    "ErrorCategory", "ErrorSeverity", "ErrorSolution", "EducationalError",
    "ErrorAnalyzer", "ErrorHandler",
    "set_error_language", "set_detailed_error_mode", 
    "handle_educational_error", "get_error_statistics", 
    "generate_error_learning_report", "get_personalized_error_hints"
]