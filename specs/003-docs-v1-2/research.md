# Research Report: GUI Dynamic Display Enhancement v1.2.11

## Technical Research Summary

### 1. Pygame Text Rendering with Color/Bold Formatting

**Decision**: Use pygame.font.Font with separate rendering calls for colored/bold text
**Rationale**:
- Built-in pygame support eliminates external dependencies
- Font.render() with color parameter provides clean color control
- Font.set_bold() or separate bold font instance for weight control
- High performance for real-time GUI updates

**Implementation Approach**:
```python
# Color definitions
RED_COLOR = (255, 0, 0)      # For decreased values
GREEN_COLOR = (0, 255, 0)    # For increased values
DEFAULT_COLOR = (255, 255, 255)  # For unchanged values

# Font instances
normal_font = pygame.font.Font(None, 24)
bold_font = pygame.font.Font(None, 24)
bold_font.set_bold(True)

# Render with emphasis
text_surface = bold_font.render("90/100 ↓10", True, RED_COLOR)
```

**Alternatives considered**:
- tkinter: Rejected due to different UI framework requirements
- Terminal escape codes: Rejected as this is a GUI application
- Rich text libraries: Rejected to avoid additional dependencies

### 2. Python Module Variable Reading from main_*.py Files

**Decision**: Use importlib.util for dynamic module loading and variable extraction
**Rationale**:
- Safe dynamic import without modifying sys.path permanently
- Handles Python module parsing correctly
- Provides error handling for missing variables
- No dependency on file parsing or regex approaches

**Implementation Approach**:
```python
import importlib.util
from pathlib import Path

def resolve_stage_id(file_path: str) -> str:
    spec = importlib.util.spec_from_file_location("temp_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, 'STAGE_ID', 'unknown_stage')
```

**Alternatives considered**:
- Regex file parsing: Rejected due to Python syntax complexity
- ast module parsing: Rejected as more complex than needed
- exec() with file reading: Rejected due to security concerns

### 3. Status Change Detection Patterns in Game Engines

**Decision**: Implement previous/current value comparison with delta calculation
**Rationale**:
- Simple state tracking with minimal memory overhead
- Clear change detection logic for turn-based games
- Supports multiple entity types (player, enemies)
- Easy to extend for different status types (HP, attack, etc.)

**Implementation Approach**:
```python
class StatusChangeTracker:
    def __init__(self):
        self.previous_states: Dict[str, Dict[str, int]] = {}

    def track_changes(self, entity_id: str, current_status: Dict[str, int]) -> Dict[str, int]:
        if entity_id not in self.previous_states:
            self.previous_states[entity_id] = {}

        changes = {}
        for key, current_value in current_status.items():
            previous_value = self.previous_states[entity_id].get(key, current_value)
            delta = current_value - previous_value
            if delta != 0:
                changes[key] = delta

        self.previous_states[entity_id] = current_status.copy()
        return changes
```

**Alternatives considered**:
- Observer pattern: Rejected as overkill for simple status tracking
- Event system: Rejected due to added complexity
- Database storage: Rejected as unnecessary for session-based tracking

## Integration Points

### Current Framework Integration
- **Renderer Enhancement**: Extend existing GuiRenderer class in engine/renderer.py
- **Stage Loading**: Integrate with existing stage_loader.py for file path resolution
- **Game State**: Leverage existing GameState entity structure
- **Testing Framework**: Use existing unittest structure in tests/ directory

### Performance Considerations
- Status change detection: O(n) where n = number of status values per entity
- STAGE_ID resolution: O(1) after initial load, cached per session
- Rendering updates: 60fps target maintained with incremental text surface updates

### Error Handling Strategy
- Missing STAGE_ID variable: Fallback to "unknown_stage" display
- File reading errors: Log error and show "error_loading_stage"
- Status value type errors: Skip invalid values, continue with valid ones
- Rendering errors: Fallback to default text formatting

## Conclusion

Technical approach is well-defined with minimal risk. All required functionality can be implemented using existing pygame and Python standard library features. No external dependencies required beyond current framework stack.