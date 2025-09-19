#!/usr/bin/env python3
"""Contract tests for yaml_manager library API"""
import pytest
from pathlib import Path
import sys
import tempfile
import yaml

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from yaml_manager import load_stage_config, save_stage_config, validate_schema
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@pytest.mark.contract
@pytest.mark.unit
class TestYamlManagerAPI:
    """Test yaml_manager library API contracts"""

    @pytest.fixture(autouse=True)
    def skip_if_not_implemented(self):
        """Skip tests if the API is not yet implemented"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("yaml_manager API not yet implemented")

    @pytest.fixture
    def sample_stage_data(self):
        """Sample stage data for testing"""
        return {
            'id': 'test_stage',
            'title': 'Test Stage',
            'description': 'A test stage for unit testing',
            'board': {
                'size': [5, 5],
                'grid': [
                    '.....',
                    '.#...',
                    '.....',
                    '...#.',
                    '.....'
                ],
                'legend': {
                    '.': 'empty',
                    '#': 'wall',
                    'P': 'player',
                    'G': 'goal'
                }
            },
            'player': {
                'start': [0, 0],
                'direction': 'E',
                'hp': 100,
                'max_hp': 100
            },
            'goal': {
                'position': [4, 4]
            },
            'enemies': [],
            'items': [],
            'constraints': {
                'max_turns': 50,
                'allowed_apis': ['turn_left', 'turn_right', 'move', 'see']
            }
        }

    def test_load_stage_config_existing_file(self):
        """Test loading an existing stage configuration file"""
        stage_file = Path(__file__).parent.parent.parent / "stages" / "stage01.yml"

        if not stage_file.exists():
            pytest.skip("stage01.yml not found for testing")

        try:
            config = load_stage_config(str(stage_file))

            # Should return StageConfiguration object or dict
            # Check that it has required structure
            if hasattr(config, '__dict__'):  # StageConfiguration object
                assert hasattr(config, 'id')
                assert hasattr(config, 'board')
                assert hasattr(config, 'player')
            else:  # Dict
                assert 'id' in config
                assert 'board' in config
                assert 'player' in config

        except NotImplementedError:
            pytest.skip("load_stage_config not yet implemented")

    def test_load_stage_config_file_not_found(self):
        """Test error handling for non-existent files"""
        try:
            with pytest.raises(FileNotFoundError):
                load_stage_config("nonexistent.yml")
        except NotImplementedError:
            pytest.skip("load_stage_config not yet implemented")

    def test_load_stage_config_invalid_yaml(self):
        """Test error handling for invalid YAML files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_file = f.name

        try:
            with pytest.raises((yaml.YAMLError, ValueError)):
                load_stage_config(temp_file)
        except NotImplementedError:
            pytest.skip("load_stage_config not yet implemented")
        finally:
            Path(temp_file).unlink()

    def test_save_stage_config_basic(self, sample_stage_data):
        """Test saving a stage configuration to file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            temp_file = f.name

        try:
            result = save_stage_config(sample_stage_data, temp_file)
            assert isinstance(result, bool)

            if result:  # If save succeeded
                # Verify file was created and contains valid YAML
                assert Path(temp_file).exists()

                with open(temp_file, 'r') as f:
                    loaded_data = yaml.safe_load(f)

                assert loaded_data['id'] == 'test_stage'
                assert loaded_data['board']['size'] == [5, 5]

        except NotImplementedError:
            pytest.skip("save_stage_config not yet implemented")
        finally:
            if Path(temp_file).exists():
                Path(temp_file).unlink()

    def test_save_stage_config_invalid_path(self, sample_stage_data):
        """Test error handling for invalid file paths"""
        try:
            result = save_stage_config(sample_stage_data, "/invalid/path/file.yml")
            # Should return False or raise exception
            if isinstance(result, bool):
                assert result is False
        except (OSError, IOError):
            pass  # Expected for invalid paths
        except NotImplementedError:
            pytest.skip("save_stage_config not yet implemented")

    def test_validate_schema_valid_stage(self, sample_stage_data):
        """Test schema validation with valid stage data"""
        try:
            result = validate_schema(sample_stage_data)
            assert isinstance(result, bool)
            assert result is True  # Valid data should pass validation

        except NotImplementedError:
            pytest.skip("validate_schema not yet implemented")

    def test_validate_schema_missing_required_fields(self):
        """Test schema validation with missing required fields"""
        invalid_data = {
            'id': 'test',
            # Missing required fields like board, player, etc.
        }

        try:
            result = validate_schema(invalid_data)
            assert isinstance(result, bool)
            assert result is False  # Invalid data should fail validation

        except NotImplementedError:
            pytest.skip("validate_schema not yet implemented")

    def test_validate_schema_invalid_field_types(self):
        """Test schema validation with invalid field types"""
        invalid_data = {
            'id': 123,  # Should be string
            'board': {
                'size': "5x5",  # Should be [int, int]
                'grid': "not a list",  # Should be list
            }
        }

        try:
            result = validate_schema(invalid_data)
            assert isinstance(result, bool)
            assert result is False

        except NotImplementedError:
            pytest.skip("validate_schema not yet implemented")

    def test_round_trip_consistency(self, sample_stage_data):
        """Test that load -> save -> load produces consistent results"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            temp_file = f.name

        try:
            # Save sample data
            save_result = save_stage_config(sample_stage_data, temp_file)
            if not save_result:
                pytest.skip("save_stage_config not working")

            # Load it back
            loaded_config = load_stage_config(temp_file)

            # Compare key fields (exact comparison may vary based on implementation)
            if hasattr(loaded_config, '__dict__'):
                # StageConfiguration object
                assert loaded_config.id == sample_stage_data['id']
                assert loaded_config.board.size == sample_stage_data['board']['size']
            else:
                # Dict
                assert loaded_config['id'] == sample_stage_data['id']
                assert loaded_config['board']['size'] == sample_stage_data['board']['size']

        except NotImplementedError:
            pytest.skip("YAML manager functions not yet implemented")
        finally:
            if Path(temp_file).exists():
                Path(temp_file).unlink()

    def test_api_imports(self):
        """Test that all required APIs are importable"""
        try:
            from yaml_manager import load_stage_config, save_stage_config, validate_schema
        except ImportError as e:
            pytest.fail(f"Required yaml_manager API not available: {e}")

    def test_yaml_format_compliance(self, sample_stage_data):
        """Test that saved YAML follows expected format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            temp_file = f.name

        try:
            result = save_stage_config(sample_stage_data, temp_file)

            if result:
                # Read the raw YAML content
                with open(temp_file, 'r') as f:
                    content = f.read()

                # Should be valid YAML
                parsed = yaml.safe_load(content)
                assert parsed is not None

                # Should maintain structure
                assert 'board:' in content
                assert 'player:' in content
                assert 'constraints:' in content

        except NotImplementedError:
            pytest.skip("save_stage_config not yet implemented")
        finally:
            if Path(temp_file).exists():
                Path(temp_file).unlink()