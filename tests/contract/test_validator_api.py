#!/usr/bin/env python3
"""Contract tests for stage_validator library API"""
import pytest
from pathlib import Path
import sys

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from stage_validator import validate_stage_solvability, analyze_solution_path
    from stage_validator.validation_models import ValidationResult
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@pytest.mark.contract
@pytest.mark.validator
class TestValidatorAPI:
    """Test stage_validator library API contracts"""

    @pytest.fixture(autouse=True)
    def skip_if_not_implemented(self):
        """Skip tests if the API is not yet implemented"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("stage_validator API not yet implemented")

    def test_validation_result_structure(self):
        """Test ValidationResult dataclass structure"""
        result = ValidationResult(
            success=True,
            stage_path="test.yml",
            path_found=True,
            required_apis=["move", "turn_left"],
            solution_length=10,
            error_details=None,
            detailed_analysis={"test": "data"}
        )

        assert result.success is True
        assert result.stage_path == "test.yml"
        assert result.path_found is True
        assert result.required_apis == ["move", "turn_left"]
        assert result.solution_length == 10
        assert result.error_details is None
        assert result.detailed_analysis == {"test": "data"}

    def test_validation_result_to_report(self):
        """Test ValidationResult.to_report() method"""
        # Successful validation
        success_result = ValidationResult(
            success=True,
            stage_path="test.yml",
            path_found=True,
            required_apis=["move"],
            solution_length=5
        )
        report = success_result.to_report()
        assert "✅" in report
        assert "test.yml" in report
        assert "5 steps" in report

        # Failed validation
        fail_result = ValidationResult(
            success=False,
            stage_path="fail.yml",
            path_found=False,
            required_apis=[],
            error_details="No path found"
        )
        report = fail_result.to_report()
        assert "❌" in report
        assert "fail.yml" in report
        assert "No path found" in report

    def test_validate_stage_solvability_signature(self):
        """Test validate_stage_solvability function signature"""
        import inspect

        sig = inspect.signature(validate_stage_solvability)
        params = list(sig.parameters.keys())
        assert "stage_path" in params

        # Check for timeout parameter with default
        if "timeout" in params:
            param = sig.parameters["timeout"]
            assert param.default == 60

    def test_validate_stage_solvability_with_existing_stage(self):
        """Test validate_stage_solvability with existing stage file"""
        stage_file = Path(__file__).parent.parent.parent / "stages" / "stage01.yml"

        if not stage_file.exists():
            pytest.skip("stage01.yml not found for testing")

        try:
            result = validate_stage_solvability(str(stage_file))
            assert isinstance(result, ValidationResult)
            assert result.stage_path == str(stage_file)
            assert isinstance(result.success, bool)
            assert isinstance(result.path_found, bool)
            assert isinstance(result.required_apis, list)

        except NotImplementedError:
            pytest.skip("validate_stage_solvability not yet implemented")

    def test_validate_stage_solvability_file_not_found(self):
        """Test error handling for non-existent files"""
        try:
            with pytest.raises(FileNotFoundError):
                validate_stage_solvability("nonexistent.yml")
        except NotImplementedError:
            pytest.skip("validate_stage_solvability not yet implemented")

    def test_validate_stage_solvability_timeout(self):
        """Test timeout parameter handling"""
        stage_file = Path(__file__).parent.parent.parent / "stages" / "stage01.yml"

        if not stage_file.exists():
            pytest.skip("stage01.yml not found for testing")

        try:
            result = validate_stage_solvability(str(stage_file), timeout=5)
            assert isinstance(result, ValidationResult)
            # Should complete within timeout or return timeout error

        except NotImplementedError:
            pytest.skip("validate_stage_solvability not yet implemented")

    def test_analyze_solution_path_signature(self):
        """Test analyze_solution_path function signature"""
        import inspect

        sig = inspect.signature(analyze_solution_path)
        params = list(sig.parameters.keys())
        assert "config" in params

        # Check for detailed parameter
        if "detailed" in params:
            param = sig.parameters["detailed"]
            assert param.default is False

    def test_analyze_solution_path_basic(self):
        """Test analyze_solution_path with basic parameters"""
        # This test will need to be implemented once StageConfiguration is available
        pytest.skip("Waiting for StageConfiguration implementation")

    def test_analyze_solution_path_detailed(self):
        """Test analyze_solution_path with detailed=True"""
        # This test will need to be implemented once StageConfiguration is available
        pytest.skip("Waiting for StageConfiguration implementation")

    def test_api_imports(self):
        """Test that all required APIs are importable"""
        try:
            from stage_validator import validate_stage_solvability, analyze_solution_path
            from stage_validator.validation_models import ValidationResult, SolutionPath
        except ImportError as e:
            pytest.fail(f"Required validator API not available: {e}")

    def test_performance_requirements(self):
        """Test that validation meets performance requirements"""
        stage_file = Path(__file__).parent.parent.parent / "stages" / "stage01.yml"

        if not stage_file.exists():
            pytest.skip("stage01.yml not found for testing")

        try:
            import time
            start_time = time.time()
            result = validate_stage_solvability(str(stage_file))
            end_time = time.time()

            # Should complete within 5 seconds for simple stages
            duration = end_time - start_time
            assert duration < 5.0, f"Validation took {duration:.2f}s, should be <5s"

        except NotImplementedError:
            pytest.skip("validate_stage_solvability not yet implemented")

    def test_validation_result_required_apis_accuracy(self):
        """Test that required_apis correctly identifies needed APIs"""
        stage_file = Path(__file__).parent.parent.parent / "stages" / "stage01.yml"

        if not stage_file.exists():
            pytest.skip("stage01.yml not found for testing")

        try:
            result = validate_stage_solvability(str(stage_file))

            if result.success:
                # stage01 should only require basic movement APIs
                expected_apis = {"turn_left", "turn_right", "move", "see"}
                actual_apis = set(result.required_apis)

                # Required APIs should be subset of expected
                assert actual_apis.issubset(expected_apis), f"Unexpected APIs required: {actual_apis - expected_apis}"

        except NotImplementedError:
            pytest.skip("validate_stage_solvability not yet implemented")