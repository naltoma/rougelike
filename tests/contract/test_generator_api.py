#!/usr/bin/env python3
"""Contract tests for stage_generator library API"""
import pytest
from pathlib import Path
import sys

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from stage_generator.data_models import StageType, GenerationParameters
    from stage_generator import generate_stage, save_stage
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@pytest.mark.contract
@pytest.mark.generator
class TestGeneratorAPI:
    """Test stage_generator library API contracts"""

    @pytest.fixture(autouse=True)
    def skip_if_not_implemented(self):
        """Skip tests if the API is not yet implemented"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("stage_generator API not yet implemented")

    def test_stage_type_enum_values(self):
        """Test that StageType enum has all required values"""
        expected_types = ["move", "attack", "pickup", "patrol", "special"]

        for stage_type in expected_types:
            assert hasattr(StageType, stage_type.upper())
            enum_value = getattr(StageType, stage_type.upper())
            assert enum_value.value == stage_type

    def test_generation_parameters_creation(self):
        """Test GenerationParameters dataclass creation"""
        params = GenerationParameters(
            stage_type=StageType.MOVE,
            seed=123,
            output_path="test/",
            validate=True
        )

        assert params.stage_type == StageType.MOVE
        assert params.seed == 123
        assert params.output_path == "test/"
        assert params.validate is True

    def test_generation_parameters_defaults(self):
        """Test GenerationParameters default values"""
        params = GenerationParameters(
            stage_type=StageType.ATTACK,
            seed=456
        )

        assert params.output_path is None
        assert params.validate is False

    def test_filename_generation(self):
        """Test GenerationParameters filename generation"""
        params = GenerationParameters(StageType.MOVE, seed=789)
        filename = params.get_filename()
        assert filename == "generated_move_789.yml"

        params = GenerationParameters(StageType.SPECIAL, seed=12345)
        filename = params.get_filename()
        assert filename == "generated_special_12345.yml"

    def test_stage_id_generation(self):
        """Test GenerationParameters stage ID generation"""
        params = GenerationParameters(StageType.PICKUP, seed=999)
        stage_id = params.get_stage_id()
        assert stage_id == "generated_pickup_999"

    def test_generate_stage_function_signature(self):
        """Test that generate_stage function exists with correct signature"""
        import inspect

        sig = inspect.signature(generate_stage)
        params = list(sig.parameters.keys())
        assert "params" in params

        # Should accept GenerationParameters and return StageConfiguration
        # This will be verified when we can actually call it

    def test_generate_stage_with_valid_parameters(self):
        """Test generate_stage with valid parameters"""
        params = GenerationParameters(StageType.MOVE, seed=123)

        try:
            result = generate_stage(params)
            # If implemented, should return StageConfiguration
            assert hasattr(result, 'id')
            assert hasattr(result, 'title')
            assert hasattr(result, 'board')
            assert hasattr(result, 'player')
            assert hasattr(result, 'goal')
        except NotImplementedError:
            pytest.skip("generate_stage not yet implemented")

    def test_generate_stage_error_handling(self):
        """Test generate_stage error handling for invalid inputs"""
        # Invalid seed range
        params = GenerationParameters(StageType.MOVE, seed=-1)

        try:
            with pytest.raises(ValueError):  # Or custom InvalidSeedError
                generate_stage(params)
        except NotImplementedError:
            pytest.skip("generate_stage not yet implemented")

    def test_save_stage_function_signature(self):
        """Test that save_stage function exists with correct signature"""
        import inspect

        sig = inspect.signature(save_stage)
        params = list(sig.parameters.keys())
        assert "config" in params
        assert "filepath" in params

    def test_save_stage_return_type(self):
        """Test that save_stage returns boolean"""
        # This test will be implemented once we have StageConfiguration
        pytest.skip("Waiting for StageConfiguration implementation")

    def test_api_imports(self):
        """Test that all required APIs are importable"""
        try:
            from stage_generator import generate_stage, save_stage
            from stage_generator.data_models import GenerationParameters, StageConfiguration
            from stage_generator.data_models import StageType
        except ImportError as e:
            pytest.fail(f"Required API not available: {e}")

    def test_seed_reproducibility_contract(self):
        """Test that same parameters produce same results"""
        params1 = GenerationParameters(StageType.MOVE, seed=555)
        params2 = GenerationParameters(StageType.MOVE, seed=555)

        try:
            result1 = generate_stage(params1)
            result2 = generate_stage(params2)

            # Should produce identical configurations
            assert result1.id == result2.id
            assert result1.board.grid == result2.board.grid
            assert result1.player.start == result2.player.start
            assert result1.goal.position == result2.goal.position

        except NotImplementedError:
            pytest.skip("generate_stage not yet implemented")

    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results"""
        params1 = GenerationParameters(StageType.MOVE, seed=111)
        params2 = GenerationParameters(StageType.MOVE, seed=222)

        try:
            result1 = generate_stage(params1)
            result2 = generate_stage(params2)

            # Should produce different configurations
            # At least one aspect should differ
            differs = (
                result1.board.grid != result2.board.grid or
                result1.player.start != result2.player.start or
                result1.goal.position != result2.goal.position
            )
            assert differs, "Different seeds should produce different stages"

        except NotImplementedError:
            pytest.skip("generate_stage not yet implemented")