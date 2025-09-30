# Research: Detrimental Items and Item Management System

## Technical Decisions

### Item Type Extension
**Decision**: Extend existing Item model to support "bomb" type with damage attribute
**Rationale**: Existing Item class in engine/__init__.py already supports type field, damage can be added as optional attribute
**Alternatives considered**:
- Creating separate BombItem class (rejected - increases complexity)
- Using item effects system (rejected - overkill for simple damage mechanic)

### API Design for is_available()
**Decision**: Add is_available() as non-turn-consuming information gathering API
**Rationale**: Follows existing pattern of see() and get_stage_info() functions that don't consume turns
**Alternatives considered**:
- Making it consume turns (rejected - inconsistent with information gathering pattern)
- Auto-checking before pickup (rejected - removes player agency)

### API Design for dispose()
**Decision**: Add dispose() as turn-consuming action API similar to move(), attack()
**Rationale**: Disposal is an action that changes game state, should consume turns like other actions
**Alternatives considered**:
- Making it non-turn-consuming (rejected - actions that change state should consume turns)
- Auto-disposal on is_available() check (rejected - removes player choice)

### Stage Completion Logic
**Decision**: Modify collect_all_items condition to count disposed bombs as "collected"
**Rationale**: Game design requirement - players shouldn't be forced to take damage to complete stages
**Alternatives considered**:
- Separate completion condition (rejected - complicates stage design)
- Ignore bombs in completion (rejected - breaks existing stage logic)

### HP System Integration
**Decision**: Extend existing game state to track player HP, apply damage on bomb pickup
**Rationale**: Simple integer HP system sufficient for educational framework
**Alternatives considered**:
- Complex health/status system (rejected - overengineering)
- No HP tracking (rejected - contradicts requirement)

### Stage Generation Updates
**Decision**: Extend existing stage_generator/ to include bomb items in generation options
**Rationale**: Reuse existing generation infrastructure, add bomb as new item type choice
**Alternatives considered**:
- Separate bomb generator (rejected - code duplication)
- Manual bomb placement only (rejected - limits educational variety)

### Stage Validation Updates
**Decision**: Update validate_stage.py to use is_available() checks before pickup/dispose decisions
**Rationale**: Validator should demonstrate proper item management patterns for students
**Alternatives considered**:
- Simple pickup avoidance (rejected - doesn't demonstrate new APIs)
- Hardcoded bomb detection (rejected - doesn't use new API design)

## Implementation Strategy

### Core Changes Required
1. Item model extension for damage attribute
2. Game state HP tracking
3. API layer extensions (is_available, dispose functions)
4. Command system extensions (DisposeCommand)
5. Stage completion logic updates
6. Generator script updates
7. Validator script updates

### Testing Strategy
1. Unit tests for new Item attributes
2. Unit tests for HP damage mechanics
3. Integration tests for new API functions
4. Stage completion integration tests
5. Generator/validator script tests
6. End-to-end stage playthrough tests

### Educational Considerations
- Clear error messages for invalid dispose attempts
- Consistent API naming following existing patterns
- Documentation updates for new student-facing APIs
- Example stages demonstrating bomb mechanics

## Dependencies Analysis

### Existing Systems to Modify
- engine/api.py: Add is_available(), dispose() functions
- engine/commands.py: Add DisposeCommand
- engine/game_state.py: Add HP tracking
- engine/__init__.py: Extend Item class
- stage_generator/: Add bomb generation logic
- stage_validator/: Add is_available() usage patterns

### No New External Dependencies
All required functionality can be implemented using existing dependencies (pygame, PyYAML, pytest).

## Risk Assessment

### Low Risk
- Item model extension (well-defined existing pattern)
- API additions (following established conventions)
- Stage generation updates (extending existing system)

### Medium Risk
- Stage completion logic changes (affects existing stages - needs careful testing)
- HP system integration (new concept, needs validation)

### Mitigation Strategies
- Comprehensive backward compatibility testing
- Gradual rollout with existing stages first
- Clear documentation of new mechanics