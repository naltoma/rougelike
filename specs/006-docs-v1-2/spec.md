# Feature Specification: Stamina System (v1.2.13)

**Feature Branch**: `006-docs-v1-2`
**Created**: 2025-09-30
**Status**: Draft
**Input**: User description: "docs/v1.2.13.md の実装に向けて要件定義してください。"

## Execution Flow (main)
```
1. Parse user description from Input
   → Feature description found in docs/v1.2.13.md
2. Extract key concepts from description
   → Actors: Player, Enemies
   → Actions: Move, attack, pickup, wait, turn_left, turn_right, dispose, see, get_stage_info
   → Data: Stamina (current/max), HP, ENABLE_STAMINA flag
   → Constraints: Stamina toggle ON/OFF, default OFF, stamina consumption rules
3. For each unclear aspect:
   → All key aspects are clearly defined in source document
4. Fill User Scenarios & Testing section
   → User flow: Enable stamina → perform actions → stamina decreases → wait to recover → stamina reaches 0 → player dies
5. Generate Functional Requirements
   → Each requirement is testable based on provided specifications
6. Identify Key Entities (if data involved)
   → Player entity with stamina attributes
7. Run Review Checklist
   → No [NEEDS CLARIFICATION] markers
   → No implementation details included
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
初心者プログラミング学習者が、ローグライクゲームの演習において、より戦略的なリソース管理を学ぶために、スタミナシステムを利用できるようにする。スタミナシステムは任意で有効化でき、無効時には従来の動作を維持する。

### Acceptance Scenarios

1. **Given** スタミナシステムが無効（ENABLE_STAMINA = False）の状態、**When** プレイヤーが任意のアクションを実行、**Then** スタミナは消費されず、従来通りの動作をする

2. **Given** スタミナシステムが有効（ENABLE_STAMINA = True）で初期スタミナ20の状態、**When** プレイヤーがmoveアクションを実行、**Then** スタミナが1減少し19になる

3. **Given** スタミナシステムが有効でスタミナが1の状態、**When** プレイヤーがmoveアクションを実行しスタミナが0になる、**Then** プレイヤーのHPが0になり死亡扱いとなる

4. **Given** スタミナシステムが有効で敵に見つかっていない状態、**When** プレイヤーがwaitアクションを実行、**Then** スタミナが10回復する（最大スタミナを上限とする）

5. **Given** スタミナシステムが有効で敵がalert状態、**When** プレイヤーがwaitアクションを実行、**Then** スタミナは回復しない

6. **Given** スタミナシステムが有効な状態、**When** プレイヤーがget_stamina()を呼び出す、**Then** 現在のスタミナ値が返され、ターンもスタミナも消費されない

7. **Given** ステージ設定ファイルにスタミナの記載がない、**When** ステージを読み込む、**Then** 初期スタミナ20、最大スタミナ20がデフォルト値として設定される

8. **Given** ステージ設定ファイルにスタミナの記載がある、**When** ステージを読み込む、**Then** 記載された初期スタミナ、最大スタミナが設定される

9. **Given** スタミナシステムが有効な状態、**When** GUI画面を表示、**Then** プレイヤー情報に「stamina: 現在値/最大値」が表示される

10. **Given** プレイヤーが移動不可能な場所にmoveしようとした場合、**When** moveアクションが失敗、**Then** スタミナは1減少する（アクション成否に関わらず消費）

### Edge Cases
- スタミナが最大値の状態でwaitした場合、回復量は上限を超えない
- スタミナが0になった瞬間にHPが0になり、その後のアクションは実行不可能
- 既存のステージ設定ファイル（スタミナ未記載）でもエラーなく動作する
- waitで回復する条件（敵が非alert状態かつwaitターンに攻撃を受けない）が両方満たされる必要がある

## Requirements *(mandatory)*

### Functional Requirements

**スタミナシステムの切り替え**
- **FR-001**: システムはスタミナ制のON/OFFを切り替え可能でなければならない
- **FR-002**: スタミナシステムのデフォルト状態はOFF（無効）でなければならない
- **FR-003**: スタミナシステムが無効の場合、従来の動作を完全に維持しなければならない

**スタミナの消費**
- **FR-004**: ターン消費系アクション（move, turn_left, turn_right, attack, pickup, dispose）を実行すると、スタミナが1減少しなければならない
- **FR-005**: 調査系アクション（wait, see, get_stage_info, get_stamina）は、ターンもスタミナも消費してはならない
- **FR-006**: アクションの成否に関わらず、ターン消費系アクションはスタミナを消費しなければならない（例: 移動不可能な場所へのmoveでも-1）

**スタミナの回復**
- **FR-007**: waitアクションの実行時、敵がalert状態でなく、かつwaitターンに攻撃を受けなかった場合、スタミナが10回復しなければならない
- **FR-008**: スタミナの回復は最大スタミナを上限としなければならない

**スタミナ枯渇時の処理**
- **FR-009**: スタミナが0になった場合、プレイヤーのHPは0になり死亡扱いとしなければならない

**スタミナの初期化と設定**
- **FR-010**: ステージ設定ファイルにスタミナの記載がない場合、初期スタミナ20、最大スタミナ20をデフォルト値として設定しなければならない
- **FR-011**: ステージ設定ファイルにスタミナの記載がある場合、その値を採用しなければならない

**スタミナ情報の可視化**
- **FR-012**: GUI画面のプレイヤー情報に「stamina: 現在値/最大値」を表示しなければならない

**スタミナ情報の取得API**
- **FR-013**: システムは現在のスタミナ値を返す機能を提供しなければならない
- **FR-014**: スタミナ値取得はターンもスタミナも消費してはならない

**既存ファイルの保護**
- **FR-015**: システムはmain_*.pyファイル（ユーザ演習用ファイル）を編集してはならない

### Key Entities

- **Player (プレイヤー)**: ゲーム内で学習者が操作するキャラクター。HP、最大HP、スタミナ、最大スタミナ、位置、向きの属性を持つ
- **Stamina (スタミナ)**: プレイヤーのリソース管理パラメータ。現在値と最大値を持ち、アクションによって増減する
- **Stage Configuration (ステージ設定)**: ステージごとのプレイヤー初期設定を定義する情報。スタミナ値の記載はオプション

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---