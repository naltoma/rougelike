# Quickstart Guide: GUI Dynamic Display Enhancement v1.2.11

## Overview
This feature enhances the roguelike educational framework GUI with dynamic stage name display and status change highlighting to improve student learning experience.

## Quick Validation Steps

### 1. Stage Name Display Test
```bash
# Test with different main_*.py files
cd /Users/tnal/2025/lecture/prog1-exe/rougelike

# Run with stage09 (should show "Stage: stage09")
python main_stage09.py

# Run with stage01 (should show "Stage: stage01")
python main_stage01.py

# Verify the stage name changes in GUI left-upper corner
```

**Expected Results**:
- GUI displays "Stage: stage09" when running main_stage09.py
- GUI displays "Stage: stage01" when running main_stage01.py
- Stage name updates dynamically based on STAGE_ID variable

### 2. Status Change Highlighting Test
```bash
# Use main_stage09.py which has combat scenarios
python main_stage09.py

# Perform actions that cause HP changes:
# 1. Take damage (HP should decrease → red bold text with ↓)
# 2. Use healing items (HP should increase → green bold text with ↑)
# 3. Move without taking action (HP unchanged → default text)
```

**Expected Results**:
- HP decrease: `90/100 ↓10` in red bold text
- HP increase: `100/100 ↑10` in green bold text
- No change: `100/100` in default white text

### 3. Multiple Entity Status Test
```bash
# Test with enemies present
python main_stage09.py

# Check that both player and enemy status changes are highlighted:
# - Player takes damage → red highlighting
# - Enemy takes damage → red highlighting
# - Both entities when no change → default formatting
```

## Manual Testing Scenarios

### Scenario 1: Dynamic Stage Name Resolution
1. **Setup**: Ensure main_stage09.py has `STAGE_ID = "stage09"`
2. **Action**: Launch GUI with `python main_stage09.py`
3. **Verify**: Left-upper corner shows "Stage: stage09"
4. **Modify**: Change STAGE_ID to "stage05" in main_stage09.py
5. **Rerun**: Launch GUI again
6. **Verify**: Left-upper corner now shows "Stage: stage05"

### Scenario 2: Status Decrease Highlighting
1. **Setup**: Start game with full HP (100/100)
2. **Action**: Perform action that causes damage
3. **Verify**: Status shows red bold text with decrease indicator
4. **Example**: `90/100 ↓10` in red bold font
5. **Next Turn**: No damage taken
6. **Verify**: Status returns to default `90/100` formatting

### Scenario 3: Status Increase Highlighting
1. **Setup**: Start with reduced HP (90/100)
2. **Action**: Use healing item or ability
3. **Verify**: Status shows green bold text with increase indicator
4. **Example**: `100/100 ↑10` in green bold font
5. **Next Turn**: No healing action
6. **Verify**: Status returns to default `100/100` formatting

### Scenario 4: No Change Behavior
1. **Setup**: Any HP value
2. **Action**: Perform action that doesn't affect HP (move, turn)
3. **Verify**: Status displays in default white text
4. **Verify**: No change indicators (↓ or ↑) displayed
5. **Verify**: Normal font weight (not bold)

## Edge Case Testing

### Edge Case 1: Missing STAGE_ID
1. **Setup**: Remove or comment out STAGE_ID in main_*.py
2. **Action**: Launch GUI
3. **Expected**: Display shows "Stage: unknown_stage" or error fallback
4. **Verify**: No crashes or exceptions

### Edge Case 2: Invalid Status Values
1. **Setup**: Corrupt game state with non-integer status values
2. **Action**: Trigger status update
3. **Expected**: Skip invalid values, continue with valid ones
4. **Verify**: GUI remains functional

### Edge Case 3: Multiple Simultaneous Changes
1. **Setup**: Scenario where HP, attack, and defense all change in one turn
2. **Action**: Execute the scenario
3. **Expected**: All changed values show appropriate highlighting
4. **Verify**: Each status type highlighted independently

## Performance Validation

### Performance Test 1: 60 FPS Rendering
1. **Setup**: GUI running with status changes every turn
2. **Monitor**: Frame rate should maintain 60 FPS
3. **Stress Test**: Rapid status changes for 100+ turns
4. **Expected**: No frame drops or lag

### Performance Test 2: Memory Usage
1. **Setup**: Long gaming session (500+ turns)
2. **Monitor**: Memory usage should remain stable
3. **Expected**: No memory leaks from status tracking

## Automated Test Execution
```bash
# Run all contract tests (should FAIL before implementation)
cd /Users/tnal/2025/lecture/prog1-exe/rougelike
python -m pytest tests/contract/test_status_change_tracking.py -v
python -m pytest tests/contract/test_stage_name_resolution.py -v
python -m pytest tests/contract/test_display_formatting.py -v

# Run integration tests (should FAIL before implementation)
python -m pytest tests/integration/test_gui_dynamic_display.py -v

# After implementation - all tests should PASS
python -m pytest tests/ -k "gui_dynamic" -v
```

## Success Criteria Summary

✅ **Stage Name Display**:
- Dynamically reads STAGE_ID from any main_*.py file
- Updates GUI display to show correct stage name
- Handles missing STAGE_ID gracefully

✅ **Status Change Highlighting**:
- Decreased values: Red bold text with ↓ symbol
- Increased values: Green bold text with ↑ symbol
- Unchanged values: Default white text formatting
- Applies to all numeric status parameters (HP, attack, etc.)

✅ **Performance & Compatibility**:
- Maintains 60 FPS rendering performance
- No modifications to main_*.py files
- Works with existing stage files and game mechanics
- Robust error handling for edge cases

✅ **User Experience**:
- Clear visual feedback for status changes
- Improved learning experience for students
- Intuitive color coding (red=bad, green=good)
- Consistent with existing GUI design patterns