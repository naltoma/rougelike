"""
Configuration settings for the Rogue-like Educational Framework
"""
import os
from pathlib import Path

# プロジェクトルートディレクトリ
ROOT_DIR = Path(__file__).parent

# ディレクトリ設定
STAGES_DIR = ROOT_DIR / "stages"
LOGS_DIR = ROOT_DIR / "logs"
ASSETS_DIR = ROOT_DIR / "assets"
TESTS_DIR = ROOT_DIR / "tests"

# 学生設定（学生が編集する部分）
STUDENT_ID = os.getenv("STUDENT_ID", "000000A")  # 6桁数字+英大文字1桁
PERFORMED_DATE = os.getenv("PERFORMED_DATE", "")  # YYYY-MM-DD形式
COLLABORATORS = os.getenv("COLLABORATORS", "")  # カンマ区切り学籍番号

# ゲーム設定
DEFAULT_MAX_TURNS = 100
DEFAULT_CELL_SIZE = 40  # pygameセルサイズ
DEFAULT_GRID_SIZE = (5, 5)  # デフォルトグリッドサイズ

# ログ設定
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Google Sheets設定（教員が設定）
GOOGLE_SHEETS_URL = os.getenv("GOOGLE_SHEETS_URL", "")
UPLOAD_RATE_LIMIT = 6  # 1分あたり最大6件

# ファイルサイズ制限
MAX_CODE_LINES = 300
MAX_CODE_SIZE_KB = 32

# 遅延提出判定時刻（日本時間）
DEADLINE_HOUR = 11
DEADLINE_MINUTE = 50