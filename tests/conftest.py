#!/usr/bin/env python3
"""
pytest設定ファイル
テスト全体で共有するfixture定義とカスタムマーカー設定
"""

import pytest
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def pytest_configure(config):
    """pytest設定の初期化"""
    config.addinivalue_line("markers", "slow: テスト実行に時間がかかるもの")
    config.addinivalue_line("markers", "integration: 統合テスト")
    config.addinivalue_line("markers", "unit: 単体テスト")
    config.addinivalue_line("markers", "gui: GUI機能（pygame）が必要なテスト")
    config.addinivalue_line("markers", "sheets: Google Sheets連携が必要なテスト")
    config.addinivalue_line("markers", "api: API機能のテスト")
    config.addinivalue_line("markers", "core: コアエンジン機能のテスト")

@pytest.fixture(scope="session")
def project_root_path():
    """プロジェクトルートパスを返すfixture"""
    return project_root

@pytest.fixture(scope="session")
def test_data_dir():
    """テストデータディレクトリパスを返すfixture"""
    return project_root / "tests" / "test_data"

@pytest.fixture(scope="function")
def temp_test_dir(tmp_path):
    """一時的なテストディレクトリを作成するfixture"""
    return tmp_path

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """テスト後のクリーンアップfixture"""
    yield
    # テスト後のクリーンアップ処理
    test_files = [
        "test_student_data.json",
        "test_session.log", 
        "test_progress.json"
    ]
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                pass

@pytest.fixture
def mock_pygame_available():
    """pygameが利用可能かどうかをモックするfixture"""
    try:
        import pygame
        return True
    except ImportError:
        return False

def pytest_runtest_setup(item):
    """テスト実行前の設定"""
    # GUI関連のテストでpygameが利用できない場合はスキップ
    if item.get_closest_marker("gui"):
        try:
            import pygame
        except ImportError:
            pytest.skip("pygame is not available")

def pytest_collection_modifyitems(config, items):
    """テストアイテムの修正"""
    # 各テストファイルに自動的にマーカーを付与
    for item in items:
        # ファイル名によるマーカー自動付与
        file_path = str(item.fspath)
        
        if "gui" in file_path or "renderer" in file_path:
            item.add_marker(pytest.mark.gui)
        elif "sheets" in file_path:
            item.add_marker(pytest.mark.sheets)
        elif "integration" in file_path or "comprehensive" in file_path:
            item.add_marker(pytest.mark.integration)
        elif "api" in file_path:
            item.add_marker(pytest.mark.api)
        else:
            item.add_marker(pytest.mark.unit)

def pytest_report_header(config):
    """テストレポートヘッダーのカスタマイズ"""
    return [
        "🧪 Python初学者向けローグライクフレームワーク - pytest実行",
        f"📂 テストディレクトリ: {project_root}/tests",
        f"🐍 Python: {sys.version.split()[0]}"
    ]