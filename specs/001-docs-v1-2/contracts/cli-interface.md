# CLI Interface Contract

## generate_stage.py

### Command Signature
```bash
generate_stage.py --type {move|attack|pickup|patrol|special} --seed INTEGER [OPTIONS]
```

### Required Arguments
- `--type, -t`: Stage type to generate
  - Values: move, attack, pickup, patrol, special
  - Maps to stages 01-03, 04-06, 07-09, 10, 11-13 respectively
- `--seed, -s`: Random seed for reproducible generation
  - Type: Integer
  - Range: 0 to 2^32-1

### Optional Arguments
- `--output, -o`: Output directory path
  - Default: `stages/`
  - Files saved as `generated_[type]_[seed].yml`
- `--validate, -v`: Validate solvability after generation
  - Default: False
  - Runs pathfinding validation
- `--quiet, -q`: Suppress output messages
  - Default: False
  - Only errors and final result
- `--format, -f`: Output format
  - Values: yaml (default), json
  - YAML is primary format, JSON for debugging
- `--help, -h`: Show help message
- `--version`: Show version information

### Exit Codes
- `0`: Success - stage generated (and validated if requested)
- `1`: Generation error - invalid parameters or generation failure
- `2`: Validation error - stage generated but failed validation
- `3`: File system error - cannot write to output directory

### Output Examples

**Success (without validation)**:
```
✅ Generated move stage with seed 123
   File: stages/generated_move_123.yml
   Size: 7x7, Walls: 12, Path length: ~15 steps
```

**Success (with validation)**:
```
✅ Generated attack stage with seed 456
   File: stages/generated_attack_456.yml
   Size: 8x8, Enemies: 2, Items: 0
✅ Validation passed: Solvable in 23 steps using [turn_left, turn_right, move, attack, see]
```

**Generation Error**:
```
❌ Generation failed: Invalid stage type 'invalid'
   Supported types: move, attack, pickup, patrol, special
```

**Validation Error**:
```
✅ Generated patrol stage with seed 789
   File: stages/generated_patrol_789.yml
❌ Validation failed: No solvable path found
   Details: Player cannot reach goal due to patrol enemy blocking all paths
```

## validate_stage.py

### Command Signature
```bash
validate_stage.py --file PATH [OPTIONS]
```

### Required Arguments
- `--file, -f`: Path to stage YAML file
  - Must be valid YAML stage configuration
  - Supports both hand-crafted and generated stages

### Optional Arguments
- `--detailed, -d`: Show detailed analysis
  - Default: False
  - Shows solution path, API usage, step-by-step analysis
- `--timeout, -t`: Validation timeout in seconds
  - Default: 60
  - Maximum time for pathfinding algorithm
- `--format, -F`: Output format
  - Values: text (default), json
  - JSON format for programmatic consumption
- `--help, -h`: Show help message
- `--version`: Show version information

### Exit Codes
- `0`: Success - stage is solvable
- `1`: Validation failed - stage is not solvable
- `2`: File error - cannot read or parse stage file
- `3`: Timeout error - validation took too long

### Output Examples

**Validation Success (basic)**:
```
✅ Stage stages/stage01.yml is solvable
   Solution: 8 steps using [turn_right, move, turn_left, move]
```

**Validation Success (detailed)**:
```
✅ Stage stages/generated_attack_456.yml is solvable

Solution Analysis:
  Steps: 23
  APIs used: turn_left, turn_right, move, attack, see
  Path: [0,0] → [1,0] → [1,1] → [2,1] → [3,1] → ... → [7,7]

Combat Analysis:
  Enemies defeated: 2
  - Enemy at [3,3]: 3 attacks (90 HP)
  - Enemy at [5,5]: 1 attack (10 HP)

Efficiency Rating: Good (optimal path +5 steps for combat)
```

**Validation Failure**:
```
❌ Stage stages/test_impossible.yml is not solvable

Analysis:
  Issue: No path to goal
  Cause: Goal position [9,9] unreachable from start [0,0]
  Blocked by: Walls form complete barrier at row 5

Suggestions:
  - Add opening in wall barrier
  - Move goal to reachable area
  - Adjust player starting position
```

## Library Interface Contract

### Core Generation API

```python
# stage_generator/__init__.py
from .core import generate_stage, save_stage
from .types import StageType
from .data_models import GenerationParameters, StageConfiguration

def generate_stage(params: GenerationParameters) -> StageConfiguration:
    """
    Generate a random stage based on parameters.

    Args:
        params: Generation parameters including type, seed, options

    Returns:
        StageConfiguration: Complete stage data structure

    Raises:
        InvalidSeedError: Seed value out of range
        UnsupportedStageTypeError: Unknown stage type
        GenerationTimeoutError: Generation took too long
    """

def save_stage(config: StageConfiguration, filepath: str) -> bool:
    """
    Save stage configuration to YAML file.

    Args:
        config: Complete stage configuration
        filepath: Output file path (should end in .yml)

    Returns:
        bool: True if saved successfully

    Raises:
        FileSystemError: Cannot write to path
        SerializationError: Cannot convert to YAML
    """
```

### Validation API

```python
# stage_validator/__init__.py
from .pathfinder import validate_stage_solvability
from .analyzer import analyze_solution_path
from .data_models import ValidationResult

def validate_stage_solvability(stage_path: str, timeout: int = 60) -> ValidationResult:
    """
    Validate that a stage file is solvable.

    Args:
        stage_path: Path to YAML stage file
        timeout: Maximum validation time in seconds

    Returns:
        ValidationResult: Detailed validation results

    Raises:
        FileNotFoundError: Stage file doesn't exist
        YAMLParseError: Invalid YAML format
        ValidationTimeoutError: Validation exceeded timeout
    """

def analyze_solution_path(config: StageConfiguration, detailed: bool = False) -> ValidationResult:
    """
    Analyze stage configuration for solvability.

    Args:
        config: Stage configuration to analyze
        detailed: Include step-by-step path analysis

    Returns:
        ValidationResult: Analysis results with optional detailed path
    """
```

### Utility API

```python
# yaml_manager/__init__.py
from .loader import load_stage_config
from .saver import save_stage_config
from .validator import validate_schema

def load_stage_config(filepath: str) -> StageConfiguration:
    """Load and parse stage YAML file."""

def save_stage_config(config: StageConfiguration, filepath: str) -> bool:
    """Save stage configuration to YAML file."""

def validate_schema(config: dict) -> bool:
    """Validate YAML structure matches expected schema."""
```

## Contract Tests Required

### CLI Contract Tests
1. **generate_stage.py argument parsing**
   - Valid combinations of arguments
   - Invalid argument handling
   - Help and version display

2. **generate_stage.py output verification**
   - File creation in correct location
   - YAML format compliance
   - Seed reproducibility

3. **validate_stage.py argument parsing**
   - File path validation
   - Output format options
   - Timeout handling

4. **validate_stage.py validation accuracy**
   - Correct solvable/unsolvable detection
   - Detailed analysis content
   - Performance within timeout

### Library Contract Tests
1. **StageConfiguration serialization**
   - Round-trip YAML conversion
   - Schema compliance
   - Data integrity preservation

2. **Generation reproducibility**
   - Same seed produces same stage
   - Different seeds produce different stages
   - Type-specific constraints honored

3. **Validation correctness**
   - Known solvable stages pass validation
   - Known unsolvable stages fail validation
   - Performance meets timeout requirements

---
*CLI and library contracts defined - ready for quickstart guide*