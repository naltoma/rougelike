# Implementation Plan: GUI Dynamic Display Enhancement v1.2.11

**Branch**: `003-docs-v1-2` | **Date**: 2025-09-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-docs-v1-2/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → ✅ Feature spec loaded successfully
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → ✅ Project Type: single (Python educational framework)
   → ✅ Structure Decision: Option 1 (DEFAULT single project structure)
3. Evaluate Constitution Check section below
   → ✅ Initial Constitution Check: PASS (simple enhancement, no violations)
   → ✅ Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → ✅ Technical context analysis complete, no NEEDS CLARIFICATION
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md
6. Re-evaluate Constitution Check section
   → ✅ Post-Design Constitution Check validation
   → ✅ Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
GUI強化機能（v1.2.11）: 動的ステージ名表示とステータス変化強調表示による学習体験向上。Python/pygame環境でのレンダラー拡張によりmain_*.pyファイルからSTAGE_ID動的読み取り、エンティティステータス変化の視覚的強調（赤字太字↓減少、緑字太字↑増加）を実現する。

## Technical Context
**Language/Version**: Python 3.11
**Primary Dependencies**: pygame, pathlib, typing
**Storage**: YAML stage files, Python module variables
**Testing**: unittest (existing framework)
**Target Platform**: Cross-platform desktop (Windows/macOS/Linux)
**Project Type**: single - Educational framework enhancement
**Performance Goals**: 60 fps GUI rendering, <50ms status update response
**Constraints**: No modification of main_*.py files (user exercise files)
**Scale/Scope**: Single module enhancement, ~20 existing stage files

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (enhancement to existing educational framework)
- Using framework directly? ✅ (pygame direct usage, no wrapper classes)
- Single data model? ✅ (status tracking without DTOs)
- Avoiding patterns? ✅ (direct renderer modification, no Repository/UoW)

**Architecture**:
- EVERY feature as library? ✅ (status tracking, stage name display as separate modules)
- Libraries listed: status_tracker (status change detection), stage_name_resolver (STAGE_ID reading)
- CLI per library: ✅ (status_tracker --format json, stage_name_resolver --validate)
- Library docs: ✅ (llms.txt format planned for both libraries)

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? ✅ (tests first, then implementation)
- Git commits show tests before implementation? ✅ (will be enforced)
- Order: Contract→Integration→E2E→Unit strictly followed? ✅ (GUI contract tests first)
- Real dependencies used? ✅ (actual pygame rendering, real STAGE_ID files)
- Integration tests for: ✅ (new status_tracker library, STAGE_ID contract changes)
- FORBIDDEN: Implementation before test, skipping RED phase ❌

**Observability**:
- Structured logging included? ✅ (status change events, stage name resolution events)
- Frontend logs → backend? N/A (single-process GUI application)
- Error context sufficient? ✅ (file reading errors, rendering errors)

**Versioning**:
- Version number assigned? ✅ (v1.2.11)
- BUILD increments on every change? ✅ (following existing pattern)
- Breaking changes handled? ✅ (backwards compatible enhancement)

## Project Structure

### Documentation (this feature)
```
specs/003-docs-v1-2/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: DEFAULT to Option 1 (single project structure as existing framework)

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - ✅ No NEEDS CLARIFICATION items - technical context is complete
   - ✅ pygame status tracking patterns researched
   - ✅ Python module dynamic inspection patterns analyzed

2. **Generate and dispatch research agents**:
   ```
   ✅ Research pygame text rendering with color/bold formatting
   ✅ Research Python module variable reading from main_*.py files
   ✅ Research status change detection patterns in game engines
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: pygame font rendering with color/weight attributes
   - Rationale: Built-in pygame support, no external dependencies
   - Alternatives considered: tkinter, terminal escape codes

**Output**: research.md with technical implementation approach

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - StatusChangeTracker: previous_values, current_values, change_deltas
   - StageNameResolver: stage_id, file_path, resolved_name
   - DisplayStateManager: emphasis_state, color_config, text_formatting

2. **Generate API contracts** from functional requirements:
   - StatusChangeTracker.track_changes(entity_status) → ChangeResult
   - StageNameResolver.resolve_stage_name(file_path) → str
   - DisplayStateManager.format_status_text(value, change) → FormattedText
   - Output OpenAPI schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - test_status_change_tracking.py (track decrease/increase/no-change)
   - test_stage_name_resolution.py (STAGE_ID reading from main_*.py)
   - test_display_formatting.py (red/green/default text formatting)
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - GUI shows correct stage name from STAGE_ID variable
   - HP decrease shows red bold text with ↓ change value
   - HP increase shows green bold text with ↑ change value
   - No change shows default formatting

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/bash/update-agent-context.sh claude` for Claude Code
   - Add pygame status rendering, Python module inspection techniques
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models before services before UI rendering
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 18-22 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No constitutional violations - simple enhancement within existing framework*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*