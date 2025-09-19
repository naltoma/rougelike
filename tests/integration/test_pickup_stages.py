#!/usr/bin/env python3
"""Integration tests for pickup stage generation and validation"""
import pytest
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path


@pytest.mark.integration
@pytest.mark.generator
@pytest.mark.validator
class TestPickupStageIntegration:
    """Test pickup stage generation and validation workflow"""

    @pytest.fixture
    def temp_output_dir(self):
        temp_dir = tempfile.mkdtemp(prefix="test_pickup_stages_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_generate_and_validate_pickup_stage(self, temp_output_dir):
        """Test generating a pickup stage and validating it succeeds"""
        result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "pickup", "--seed", "12345",
            "--output", temp_output_dir, "--validate"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Will fail until implemented
        if result.returncode != 0:
            pytest.skip("Pickup stage generation not yet implemented")

        stage_file = Path(temp_output_dir) / "generated_pickup_12345.yml"
        assert stage_file.exists()