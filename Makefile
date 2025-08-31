# Python初学者向けローグライクフレームワーク - Makefile

.PHONY: help install test test-unit test-integration test-gui test-failed test-coverage clean lint format

# デフォルトターゲット
help:
	@echo "🧪 Python初学者向けローグライクフレームワーク - テスト管理"
	@echo ""
	@echo "利用可能なコマンド:"
	@echo "  make install          - 依存関係をインストール"
	@echo "  make test             - 全テストを実行"
	@echo "  make test-unit        - 単体テストのみ実行"
	@echo "  make test-integration - 統合テストのみ実行"
	@echo "  make test-gui         - GUIテスト以外を実行"
	@echo "  make test-failed      - 前回失敗したテストのみ実行"
	@echo "  make test-coverage    - カバレッジ付きテスト実行"
	@echo "  make test-verbose     - 詳細モードでテスト実行"
	@echo "  make clean            - テスト成果物をクリーンアップ"
	@echo "  make lint             - コード品質チェック"
	@echo "  make format           - コードフォーマット"

# 依存関係のインストール
install:
	@echo "📦 依存関係をインストール中..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ インストール完了"

# 全テスト実行
test:
	@echo "🧪 全テスト実行中..."
	python run_pytest.py

# 単体テストのみ
test-unit:
	@echo "🔬 単体テスト実行中..."
	python -m pytest -m unit -v

# 統合テストのみ
test-integration:
	@echo "🔗 統合テスト実行中..."
	python -m pytest -m integration -v

# GUIテスト以外
test-no-gui:
	@echo "🖥️  GUIテスト以外を実行中..."
	python -m pytest -m "not gui" -v

# 失敗したテストのみ再実行
test-failed:
	@echo "🔄 失敗したテストのみ再実行中..."
	python -m pytest --lf -v

# カバレッジ付きテスト
test-coverage:
	@echo "📊 カバレッジ付きテスト実行中..."
	python -m pytest --cov=engine --cov-report=html --cov-report=term -v

# 詳細モードテスト
test-verbose:
	@echo "📝 詳細モードテスト実行中..."
	python -m pytest -vvv --tb=long

# 特定のテストファイル実行（使用例: make test-file FILE=test_api.py）
test-file:
	@echo "📁 テストファイル $(FILE) を実行中..."
	python -m pytest tests/$(FILE) -v

# 特定のテスト関数実行（使用例: make test-function FUNC=test_move_command）
test-function:
	@echo "⚡ テスト関数 $(FUNC) を実行中..."
	python -m pytest -k $(FUNC) -v

# 並列テスト実行
test-parallel:
	@echo "🚀 並列テスト実行中..."
	python -m pytest -n auto -v

# ベンチマークテスト
test-benchmark:
	@echo "⏱️  ベンチマークテスト実行中..."
	python -m pytest --benchmark-only -v

# クリーンアップ
clean:
	@echo "🧹 テスト成果物をクリーンアップ中..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf pytest_report.json
	rm -rf *.log
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "✅ クリーンアップ完了"

# コード品質チェック（flake8が利用可能な場合）
lint:
	@echo "🔍 コード品質チェック中..."
	-python -m flake8 engine/ tests/ --max-line-length=120
	@echo "✅ コード品質チェック完了"

# コードフォーマット（blackが利用可能な場合）
format:
	@echo "✨ コードフォーマット中..."
	-python -m black engine/ tests/ --line-length=120
	@echo "✅ コードフォーマット完了"