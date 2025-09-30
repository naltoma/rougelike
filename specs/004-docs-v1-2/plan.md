# Implementation Plan: Detrimental Items and Item Management System

**Branch**: `004-docs-v1-2` | **Date**: 2025-09-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-docs-v1-2/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Implement a detrimental item system (bombs) that causes HP damage when collected, with new player operations is_available() for item checking and dispose() for item removal. Update stage generation and validation scripts to handle the new item type while ensuring stage completion logic considers disposed items as collected.

## Technical Context
**Language/Version**: Python 3.8+
**Primary Dependencies**: pygame>=2.5.0, PyYAML>=6.0, pytest>=7.4.0
**Storage**: YAML files for stage configurations, JSON for session logs
**Testing**: pytest with coverage, mock, and benchmark plugins
**Target Platform**: Desktop (cross-platform Python application)
**Project Type**: single - educational game framework with CLI and GUI
**Performance Goals**: Real-time turn-based game performance, instant API response
**Constraints**: Educational focus, preserve existing main_*.py files, minimal learning curve
**Scale/Scope**: Framework for 20+ educational stages, student exercise system

**User Provided Context**: 実装計画を立ててください。

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (educational game framework - single project structure)
- Using framework directly? Yes (pygame, pytest used directly)
- Single data model? Yes (Item model extended, no DTOs needed)
- Avoiding patterns? Yes (direct API functions, no complex patterns)

**Architecture**:
- EVERY feature as library? No (extending existing educational framework)
- Libraries listed: engine/ modules (item_system, api, commands)
- CLI per library: generate_stage.py, validate_stage.py existing
- Library docs: N/A (educational framework, not library project)

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes (tests written first)
- Git commits show tests before implementation? Yes (will enforce)
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes (actual YAML files, game state)
- Integration tests for: item system, API extensions, stage generation
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? Yes (existing logging framework)
- Frontend logs → backend? Yes (unified pygame/CLI logging)
- Error context sufficient? Yes (educational error handling exists)

**Versioning**:
- Version number assigned? v1.2.12 (following project convention)
- BUILD increments on every change? Yes (following existing pattern)
- Breaking changes handled? No breaking changes (API additions only)

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
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

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: [DEFAULT to Option 1 unless Technical Context indicates web/mobile app]

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/bash/update-agent-context.sh claude` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Item model extension → unit test + implementation [P]
- HP system integration → unit test + implementation [P]
- API functions (is_available, dispose) → contract tests + implementation
- Command system → DisposeCommand test + implementation [P]
- Stage completion logic → integration tests + implementation
- Generator/validator scripts → script tests + implementation [P]

**Ordering Strategy**:
- TDD order: All tests before implementation
- Dependency order: Models → Commands → API → Integration → Scripts
- Core system tests first, then integration, then script updates
- Mark [P] for parallel execution within phases

**Estimated Output**: 22-25 numbered, ordered tasks in tasks.md

**Key Task Categories**:
1. Model Extension Tests (Items, Player HP) - Parallel
2. Model Extension Implementation - Parallel
3. Command System Tests (DisposeCommand) - Parallel
4. Command System Implementation - Parallel
5. API Layer Tests (is_available, dispose) - Sequential
6. API Layer Implementation - Sequential
7. Stage Completion Integration Tests - Sequential
8. Stage Completion Implementation - Sequential
9. Script Update Tests (generator, validator) - Parallel
10. Script Update Implementation - Parallel
11. End-to-End Integration Tests - Sequential

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


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
- [x] Complexity deviations documented (none required)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*