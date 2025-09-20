# Tasks: see()関数チュートリアルドキュメント作成

**Input**: Design documents from `/specs/002-docs-v1-2/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.11+, Markdown
   → Structure: Single project (documentation only)
2. Load design documents:
   → data-model.md: Tutorial Document, Stage01 Example, Code Examples
   → contracts/: tutorial-structure.md, validation-criteria.md
   → research.md: Documentation decisions, integration approach
3. Generate documentation creation tasks by category:
   → Setup: File structure, reference validation
   → Content: Section writing with examples
   → Integration: System compatibility checks
   → Validation: User testing and reviews
4. Apply task rules:
   → Different sections = mark [P] for parallel writing
   → Sequential sections = no [P] for consistency
   → Content before validation
5. Number tasks sequentially (T001, T002...)
6. Generate parallel execution examples
7. Validate task completeness:
   → All contract sections covered?
   → All data model entities included?
   → Validation criteria addressed?
8. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (independent sections, no content dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup and Structure
- [ ] T001 Create basic tutorial file structure in docs/tutorial_see.md
- [ ] T002 Validate existing file dependencies (stage01.yml, SeeDescription.md)
- [ ] T003 [P] Analyze stage01.yml structure for tutorial examples

## Phase 3.2: Content Creation (Core Sections)
**Following tutorial-structure.md contract requirements**
- [ ] T004 [P] Write "1. はじめに" section with see()概要と目標 in docs/tutorial_see.md
- [ ] T005 [P] Write "2. see()関数の基礎" section with basic usage examples in docs/tutorial_see.md
- [ ] T006 [P] Write "3. Stage01を例にした実践" section introduction in docs/tutorial_see.md
- [ ] T007 Stage01構造解析とsee()による情報収集手順 in docs/tutorial_see.md (depends on T006)
- [ ] T008 Write "4. 完全クリア手順" with step-by-step player actions in docs/tutorial_see.md (depends on T007)
- [ ] T009 [P] Write "5. デバッグとトラブルシューティング" section in docs/tutorial_see.md
- [ ] T010 [P] Write "6. 他ステージへの応用" section in docs/tutorial_see.md

## Phase 3.3: Code Examples and Validation
**Each code example must include 目的・コード・実行結果・解説**
- [ ] T011 [P] Create basic see() usage code examples for section 2
- [ ] T012 [P] Create stage01-specific see() examples for section 3
- [ ] T013 [P] Create complete solution code examples for section 4
- [ ] T014 [P] Create debugging examples and error handling for section 5
- [ ] T015 Integrate all code examples into tutorial sections (depends on T004-T014)

## Phase 3.4: Integration and Compatibility
- [ ] T016 Validate tutorial consistency with SeeDescription.md
- [ ] T017 Test stage01 code examples for accuracy and executability
- [ ] T018 Verify no main_*.py files require editing
- [ ] T019 Check tutorial integration with existing documentation system

## Phase 3.5: Content Validation and Quality
**Following validation-criteria.md contract requirements**
- [ ] T020 [P] Validate beginner-friendly language and terminology explanations
- [ ] T021 [P] Test tutorial completion time (<30 minutes)
- [ ] T022 [P] Verify all code examples execute correctly
- [ ] T023 Validate learning progression (Unknown→Basic→Practical→Independent)
- [ ] T024 Check file size and determine if docs/see_tutorial/ split is needed
- [ ] T025 Final review and polish of tutorial content

## Dependencies
- T001-T003 (Setup) before content creation (T004-T010)
- T006 blocks T007 (Stage01 intro before detailed analysis)
- T007 blocks T008 (Analysis before complete solution)
- T004-T014 before integration (T015)
- T015 before validation phases (T016-T025)
- T016-T019 (Integration) before final validation (T020-T025)

## Parallel Example
```
# Launch T004, T005, T009, T010 together (independent sections):
Task: "Write はじめに section with see()概要と目標 in docs/tutorial_see.md"
Task: "Write see()関数の基礎 section with basic usage examples in docs/tutorial_see.md"
Task: "Write デバッグとトラブルシューティング section in docs/tutorial_see.md"
Task: "Write 他ステージへの応用 section in docs/tutorial_see.md"

# Launch T011-T014 together (independent code examples):
Task: "Create basic see() usage code examples for section 2"
Task: "Create stage01-specific see() examples for section 3"
Task: "Create complete solution code examples for section 4"
Task: "Create debugging examples and error handling for section 5"
```

## Task Generation Rules Applied
*From design documents analysis*

1. **From Contracts**:
   - tutorial-structure.md → T004-T010 (6 required sections)
   - validation-criteria.md → T020-T025 (quality validation)

2. **From Data Model**:
   - Tutorial Document entity → T001, T015 (structure and integration)
   - Stage01 Example entity → T003, T007, T008 (analysis and examples)
   - Code Examples entity → T011-T014 (code creation)

3. **From Research**:
   - Documentation decisions → T001, T024 (structure and split decisions)
   - Integration approach → T016, T019 (compatibility checks)

## Success Criteria
Following validation-criteria.md requirements:

### Content Quality Gates
- [ ] 初心者が30分以内で基礎理解可能 (T021)
- [ ] Stage01完全クリア手順が明確 (T008, T017)
- [ ] 全コード例が実行可能 (T017, T022)
- [ ] エラーケース対応が含まれている (T009, T014)

### Integration Validation Gates
- [ ] SeeDescription.mdとの整合性確認 (T016)
- [ ] 既存システムとの競合なし (T018, T019)
- [ ] main_*.py編集要求なし (T018)

### Accessibility Validation Gates
- [ ] 専門用語に説明付き (T020)
- [ ] 段階的学習フロー維持 (T023)
- [ ] 視覚的な構造化実現 (T025)

## Notes
- [P] tasks = independent sections that can be written in parallel
- Content validation only after all sections are complete
- Each code example must be tested for executability
- Tutorial may need splitting if >10,000 characters (T024)
- Focus on educational quality over technical complexity