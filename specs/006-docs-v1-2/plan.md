# Implementation Plan: Stamina System (v1.2.13)

**Branch**: `006-docs-v1-2` | **Date**: 2025-09-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-docs-v1-2/spec.md`

---

## Execution Flow (/plan command scope)
```
✅ 1. Load feature spec from Input path
   → Spec loaded successfully from specs/006-docs-v1-2/spec.md
✅ 2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Project Type: single (Python roguelike framework)
   → Structure Decision: Option 1 (Default single project)
✅ 3. Evaluate Constitution Check section below
   → Initial check passed (simplicity maintained, TDD enforced)
   → Update Progress Tracking: Initial Constitution Check
✅ 4. Execute Phase 0 → research.md
   → research.md generated via agent
   → All technical unknowns resolved
✅ 5. Execute Phase 1 → contracts, data-model.md, quickstart.md
   → data-model.md created (Character, HyperParameters, Stage config)
   → contracts/api-contract.md created (get_stamina() API + modified actions)
   → quickstart.md created (6 end-to-end validation scenarios)
✅ 6. Re-evaluate Constitution Check section
   → Post-design check passed
   → Update Progress Tracking: Post-Design Constitution Check
✅ 7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
✅ 8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

---

## Summary

v1.2.13では、Python初学者向けローグライク演習フレームワークに**スタミナシステム**を導入します。

**主要機能**:
- ターン消費系アクション（move, attack等）で-1スタミナ消費
- wait()で+10スタミナ回復（敵非警戒＆攻撃未受け時）
- スタミナ0でHP0（即死）
- 新API: `get_stamina()` - ターン・スタミナ消費なし
- GUI表示: "スタミナ: 現在値/最大値" + 変化ハイライト
- YAML設定: オプションで`stamina`/`max_stamina`指定可能（デフォルト20/20）
- ハイパーパラメータ: `ENABLE_STAMINA`フラグでON/OFF切替（デフォルト: OFF）

**設計方針**:
- 後方互換性維持（デフォルトOFFで既存動作保証）
- ユーザー演習ファイル（main_*.py）は変更不可
- 既存ステージファイル（スタミナ設定なし）も動作

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyYAML 6.0.1, tkinter (標準ライブラリ)
**Storage**: YAMLファイル（ステージ設定）
**Testing**: pytest（既存テストスイート）
**Target Platform**: Cross-platform（Windows/Mac/Linux）
**Project Type**: single（単一プロジェクト構成）
**Performance Goals**: <1%オーバーヘッド（アクション実行時のスタミナチェック）
**Constraints**:
- main_*.pyファイル（ユーザー演習用）は編集禁止
- 既存ステージファイル（stage01.yml～stage13.yml）との後方互換性維持
- 既存テストスイート全合格（ENABLE_STAMINA=Falseのデフォルト状態で）
**Scale/Scope**:
- 13既存ステージ + 任意の新規ステージ対応
- 1ゲームセッション = 数百〜数千アクション想定
- 教育用途（初心者プログラミング演習）

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Constitution Check (Phase 0前)

**Simplicity**:
- ✅ Projects: 1（単一プロジェクトのみ）
- ✅ Using framework directly? Yes（tkinter標準ライブラリ、PyYAML直接使用）
- ✅ Single data model? Yes（Characterデータクラスに統合、DTO不要）
- ✅ Avoiding patterns? Yes（シンプルなデータクラス＋関数型アプローチ、不要なパターン回避）

**Architecture**:
- ✅ EVERY feature as library? Yes（engine/パッケージとして実装）
- ✅ Libraries listed:
  - `engine`: コアゲームロジック（Player, Stage, Actions, API）
  - `engine.renderer`: CUI/GUI表示
  - `engine.stage_loader`: YAMLステージ読み込み
  - `engine.hyperparameter_manager`: ハイパーパラメータ管理
- ✅ CLI per library: `main.py`がCLIエントリーポイント（`--help`, `--version`対応）
- ⚠️ Library docs: llms.txt format planned? → N/A（教育用フレームワーク、外部公開ライブラリでない）

**Testing (NON-NEGOTIABLE)**:
- ✅ RED-GREEN-Refactor cycle enforced? Yes（契約テスト → 失敗確認 → 実装 → 合格）
- ✅ Git commits show tests before implementation? Yes（コミット順序厳守）
- ✅ Order: Contract→Integration→E2E→Unit strictly followed? Yes（quickstart.mdで統合テスト定義済み）
- ✅ Real dependencies used? Yes（実YAMLファイル、実tkinter GUI）
- ✅ Integration tests for: new libraries, contract changes, shared schemas? Yes（API契約変更の統合テスト）
- ✅ FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- ✅ Structured logging included? 既存ログシステム継承
- N/A Frontend logs → backend? （CUI/GUIローカルアプリのみ）
- ✅ Error context sufficient? エラーメッセージ＋スタックトレース

**Versioning**:
- ✅ Version number assigned? v1.2.13
- ✅ BUILD increments on every change? Yes（v1.2.12 → v1.2.13）
- N/A Breaking changes handled? （後方互換性維持、破壊的変更なし）

### Post-Design Constitution Check (Phase 1後)

**Simplicity Re-check**:
- ✅ No new projects added
- ✅ No wrapper classes introduced（Characterクラスに直接スタミナ追加）
- ✅ No new patterns introduced（既存Command Pattern踏襲）

**Architecture Re-check**:
- ✅ New API (`get_stamina()`) follows existing API pattern
- ✅ New hyperparameter (`enable_stamina`) follows existing manager pattern
- ✅ YAML config extension follows existing validation pattern

**Testing Re-check**:
- ✅ Contract tests defined in `contracts/api-contract.md`
- ✅ Integration tests defined in `quickstart.md`
- ✅ TDD workflow: Tests → RED → Implementation → GREEN → Refactor

---

## Project Structure

### Documentation (this feature)
```
specs/006-docs-v1-2/
├── spec.md              # Feature specification (Phase 0)
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (codebase research)
├── data-model.md        # Phase 1 output (data models)
├── quickstart.md        # Phase 1 output (E2E validation scenarios)
├── contracts/           # Phase 1 output (API contracts)
│   └── api-contract.md  # get_stamina() + modified actions
└── tasks.md             # Phase 2 output (/tasks command - NOT created yet)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT) ← 採用
rougelike/
├── engine/
│   ├── __init__.py              # Character, Position, Direction dataclasses
│   ├── api.py                   # User-facing API (get_stamina追加)
│   ├── commands.py              # Command pattern (スタミナ消費統合)
│   ├── game_state.py            # GameStateManager (スタミナチェック統合)
│   ├── stage_loader.py          # YAML loader (スタミナパース追加)
│   ├── renderer.py              # CUI/GUI renderer (スタミナ表示追加)
│   ├── hyperparameter_manager.py # ENABLE_STAMINA追加
│   └── ...
├── stages/
│   ├── stage01.yml～stage13.yml # 既存ステージ（変更不要）
│   └── test_stamina_*.yml       # テスト用ステージ（新規）
├── tests/
│   ├── contract/                # 契約テスト（新規）
│   │   └── test_stamina_api_contract.py
│   ├── integration/             # 統合テスト（既存＋新規）
│   │   └── test_stamina_integration.py
│   └── unit/                    # ユニットテスト（既存＋新規）
│       ├── test_character_stamina.py
│       └── test_stage_loader_stamina.py
├── main.py                      # ユーザーテンプレート（ENABLE_STAMINA追加）
├── main_*.py                    # ユーザー演習ファイル（変更禁止）
└── docs/
    └── v1.2.13.md               # リリースノート
```

**Structure Decision**: Option 1（単一プロジェクト構成）を採用。理由: 教育用フレームワークで、マイクロサービス化の必要なし。

---

## Phase 0: Outline & Research

### Research Tasks Executed

1. ✅ **Player Class/Model**:
   - 発見: `engine/__init__.py` の `Character` dataclass
   - 既存フィールド: `hp`, `max_hp`, `attack_power`, `collected_items`, `disposed_items`
   - 統合箇所: `stamina`, `max_stamina`フィールド追加、`consume_stamina()`, `recover_stamina()`, `stamina_percentage()`メソッド追加

2. ✅ **Action System**:
   - 発見: `engine/commands.py` のCommand Pattern実装
   - ターン消費アクション: `TurnLeftCommand`, `TurnRightCommand`, `MoveCommand`, `AttackCommand`, `PickupCommand`, `DisposeCommand`, `WaitCommand`
   - 統合箇所: `GameStateManager.execute_command()`でスタミナ消費＋枯渇チェック

3. ✅ **Stage Loading System**:
   - 発見: `engine/stage_loader.py` の `StageLoader` クラス
   - 既存パース: `player.hp`, `player.max_hp`, `player.direction`
   - 統合箇所: `_validate_player()`で`stamina`/`max_stamina`オプショナルフィールドパース、デフォルト20/20

4. ✅ **GUI Rendering**:
   - 発見: `engine/renderer.py` の `Renderer` クラス
   - CUI: `render_game_info()` でテキスト情報表示
   - GUI: サイドバーの`_draw_player_info()`でプレイヤー情報描画
   - 統合箇所: スタミナ表示追加、`StatusChangeTracker`でハイライト対応

5. ✅ **Hyperparameter System**:
   - 発見: `engine/hyperparameter_manager.py` の `HyperParameterManager`
   - 既存パラメータ: `delay_ms`, `speed_level`
   - 統合箇所: `HyperParametersData`に`enable_stamina: bool = False`追加

6. ✅ **Enemy AI System**:
   - 発見: `engine/game_state.py` の敵AI処理
   - 警戒状態: `enemy.alerted` フラグ
   - 統合箇所: `WaitCommand`実行時に`all(not enemy.alerted for enemy in enemies)`チェック＋攻撃判定

### Research Decisions

| 決定事項 | 理由 | 代替案却下理由 |
|---------|------|--------------|
| Characterデータクラスに統合 | 既存Player/Enemy共通構造を踏襲 | 別途PlayerStaminaクラス作成 → 不要な複雑化 |
| ハイパーパラメータでトグル管理 | 既存パターン踏襲、ユーザー設定容易 | 環境変数 → 教育用途で複雑化 |
| YAMLオプションフィールド | 後方互換性維持 | 必須フィールド → 既存ステージ破壊 |
| デフォルトOFF | 既存動作保証、段階的導入 | デフォルトON → 破壊的変更 |

**Output**: [research.md](research.md) with all technical details resolved

---

## Phase 1: Design & Contracts

*Prerequisites: research.md complete*

### 1. Data Model Design

**Output**: [data-model.md](data-model.md)

**Key Entities**:
- `Character` (extended): `stamina: int`, `max_stamina: int`, `consume_stamina()`, `recover_stamina()`, `stamina_percentage()`
- `HyperParametersData` (extended): `enable_stamina: bool = False`
- `StatusChange` (extended): `old_stamina: Optional[int]`, `new_stamina: Optional[int]`
- Stage YAML schema (extended): `player.stamina`, `player.max_stamina` (optional)

**Relationships**:
```
HyperParameters.enable_stamina → GameStateManager.execute_command()
Character.stamina ← Actions (consume) / wait() (recover)
Character.stamina → Renderer (display)
Stage YAML → StageLoader → Character.stamina/max_stamina
```

### 2. API Contract Design

**Output**: [contracts/api-contract.md](contracts/api-contract.md)

**New API**:
- `get_stamina() -> int`: 現在スタミナ取得（ターン・スタミナ消費なし）

**Modified APIs**:
- `turn_left()`, `turn_right()`, `move()`, `attack()`, `pickup()`, `dispose()`: -1スタミナ消費（ENABLE_STAMINA=True時）
- `wait()`: -1スタミナ消費 ＋ 安全時+10回復

**Contract Test Scenarios** (契約テストケース、api-contract.mdに記載):
- `test_get_stamina_returns_current_value()`
- `test_get_stamina_no_turn_consumption()`
- `test_move_consumes_stamina_when_enabled()`
- `test_move_no_stamina_consumption_when_disabled()`
- `test_wait_recovers_stamina_when_safe()`
- `test_wait_no_recovery_when_enemy_alerted()`
- その他24契約テストシナリオ

### 3. Integration Test Scenarios

**Output**: [quickstart.md](quickstart.md)

**6 Quickstart Scenarios**:
1. 基本的なスタミナ消費（消費 → 枯渇 → 死亡）
2. スタミナ回復（wait()で+10、上限チェック）
3. 敵警戒時の回復なし
4. 後方互換性（ENABLE_STAMINA=False）
5. GUI表示確認
6. ステージ設定読み込み（YAML）

### 4. Test-Driven Development Workflow

**Contract Tests** (Phase 1完了後、/tasks実行前):
```bash
# 契約テストファイル生成（次フェーズ）
tests/contract/test_stamina_api_contract.py

# 実行 → 全て失敗（RED phase）
pytest tests/contract/test_stamina_api_contract.py
# Expected: FAILED (実装前)
```

**Implementation Order** (Phase 2タスク):
1. Character dataclass拡張 → 契約テスト合格
2. HyperParameterManager拡張 → 契約テスト合格
3. StageLoader拡張 → 契約テスト合格
4. Command execution統合 → 契約テスト合格
5. API追加 → 契約テスト合格
6. Renderer更新 → 統合テスト合格

---

## Phase 2: Task Planning Approach

*This section describes what the /tasks command will do - DO NOT execute during /plan*

### Task Generation Strategy

**Source Documents**:
- [data-model.md](data-model.md): エンティティ → モデル作成タスク
- [contracts/api-contract.md](contracts/api-contract.md): 契約 → 契約テストタスク
- [quickstart.md](quickstart.md): シナリオ → 統合テストタスク

**Task Categorization**:
1. **Contract Test Tasks** (優先度: 高):
   - `[P]` 契約テストファイル作成（独立ファイル、並列実行可能）
   - 各契約ごとに1タスク（例: `get_stamina()`契約テスト作成）

2. **Model Creation Tasks** (優先度: 高):
   - `[P]` Character dataclass拡張（stamina, max_stamina, メソッド追加）
   - `[P]` HyperParametersData拡張（enable_stamina追加）
   - `[P]` StatusChange拡張（stamina tracking追加）

3. **Implementation Tasks** (依存関係順):
   - StageLoader拡張（YAMLパース）← Character依存
   - GameStateManager統合（スタミナ消費・チェック）← Character + HyperParameters依存
   - WaitCommand拡張（スタミナ回復）← GameStateManager依存
   - API追加（get_stamina()）← GameStateManager依存
   - Renderer更新（スタミナ表示）← Character依存

4. **Integration Test Tasks**:
   - 各quickstartシナリオ → 統合テストファイル作成
   - E2Eテスト実行 → 全合格確認

5. **Validation Tasks**:
   - 既存テスト実行（後方互換性確認）
   - 全13ステージ実行確認
   - パフォーマンステスト（<1%オーバーヘッド確認）

### Ordering Strategy

**TDD原則**:
1. ✅ 契約テスト作成 → RED phase確認
2. ✅ モデル実装 → GREEN phase達成
3. ✅ 統合テスト作成 → RED phase確認
4. ✅ 統合実装 → GREEN phase達成
5. ✅ Refactor（必要に応じて）

**依存関係順序**:
```
Phase A (並列実行可能 [P]):
  ├─ 契約テストファイル作成
  ├─ Character dataclass拡張
  ├─ HyperParametersData拡張
  └─ StatusChange拡張

Phase B (Phase A依存):
  ├─ StageLoader拡張（Character依存）
  └─ GameStateManager統合（Character + HyperParameters依存）

Phase C (Phase B依存):
  ├─ WaitCommand拡張（GameStateManager依存）
  ├─ API追加（GameStateManager依存）
  └─ Renderer更新（Character依存）

Phase D (Phase C依存):
  └─ 統合テスト実行 → 全合格

Phase E (Phase D依存):
  └─ 既存テスト実行 → 後方互換性確認
```

### Estimated Task Count

| カテゴリ | タスク数 | 並列実行 |
|---------|---------|---------|
| 契約テスト作成 | 6タスク | Yes [P] |
| モデル拡張 | 3タスク | Yes [P] |
| ステージロード統合 | 2タスク | No |
| コマンド実行統合 | 3タスク | No |
| API追加 | 1タスク | No |
| レンダラー更新 | 2タスク | Partial |
| 統合テスト作成・実行 | 6タスク | Partial |
| 既存テスト検証 | 2タスク | No |
| ドキュメント更新 | 2タスク | Yes [P] |

**合計**: 約27タスク

**並列実行可能**: 9タスク（契約テスト6 + モデル3）

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

---

## Phase 3+: Future Implementation

*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following TDD principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

---

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

**結論**: 憲法違反なし、シンプル設計維持

---

## Progress Tracking

*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md generated
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md generated
- [x] Phase 2: Task planning complete (/plan command - approach described above)
- [ ] Phase 3: Tasks generated (/tasks command) - **NEXT STEP**
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (simplicity maintained, TDD enforced)
- [x] Post-Design Constitution Check: PASS (no new violations introduced)
- [x] All NEEDS CLARIFICATION resolved (research.md completed)
- [x] Complexity deviations documented (none - table empty)

**Artifacts Generated**:
- [x] specs/006-docs-v1-2/spec.md (Phase 0)
- [x] specs/006-docs-v1-2/plan.md (This file)
- [x] specs/006-docs-v1-2/research.md (Phase 0)
- [x] specs/006-docs-v1-2/data-model.md (Phase 1)
- [x] specs/006-docs-v1-2/contracts/api-contract.md (Phase 1)
- [x] specs/006-docs-v1-2/quickstart.md (Phase 1)
- [ ] specs/006-docs-v1-2/tasks.md (Phase 2 - awaiting /tasks command)

---

## Next Steps

**Ready for /tasks command**:
```bash
/tasks  # Generate tasks.md from design artifacts
```

**Expected /tasks Output**:
- Load plan.md, data-model.md, contracts/, quickstart.md
- Generate 25-30 ordered tasks in tasks.md
- Mark parallel tasks with [P]
- Follow TDD order: Tests → Implementation → Validation

**After /tasks Complete**:
1. Review tasks.md for completeness
2. Execute tasks sequentially (or parallel where marked [P])
3. Follow TDD: RED → GREEN → Refactor
4. Run quickstart.md scenarios after implementation
5. Verify all existing tests pass (backward compatibility)
6. Update docs/v1.2.13.md with release notes

---

*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
*Generated by /plan command on 2025-09-30*