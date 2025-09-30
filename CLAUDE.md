# Claude Code Spec-Driven Development

Kiro-style Spec Driven Development implementation using claude code slash commands, hooks and agents.

## Project Context

### Paths
- Steering: `.kiro/steering/`
- Specs: `.kiro/specs/`
- Commands: `.claude/commands/`

### Steering vs Specification

**Steering** (`.kiro/steering/`) - Guide AI with project-wide rules and context  
**Specs** (`.kiro/specs/`) - Formalize development process for individual features

### Active Specifications
- Check `.kiro/specs/` for active specifications
- Use `/kiro:spec-status [feature-name]` to check progress

**Current Specs:**
- `python-rougelike-framework`: Python初学者向けローグライク演習フレームワーク - 段階的学習システム（初期化済み）
- `gui-critical-fixes-v1.2.1`: Step/Pause/Resetボタン機能不具合修正（v1.2.1で完了） - 詳細は [docs/v1.2.1.md](docs/v1.2.1.md) 参照
- `session-logging-enhancement-v1.2.2`: セッションログ機能統合・GUI改善（v1.2.2で完了） - 詳細は [docs/v1.2.2.md](docs/v1.2.2.md) 参照
- `google-sheets-integration-v1.2.3`: Google Apps Script Webhook連携・学生間セッションログ共有機能（v1.2.3で完了） - 詳細は [docs/v1.2.3.md](docs/v1.2.3.md) 参照
- `initial-execution-behavior-v1.2.4`: 初回起動時動作改善 - ステージクリア条件確認・試行回数管理最適化（v1.2.4で完了） - 詳細は [docs/v1.2.4.md](docs/v1.2.4.md) 参照
- `continue-execution-speed-control-v1.2.5`: Continue実行速度調整機能 - 7段階速度制御・超高速実行対応（v1.2.5で完了） - 詳細は [docs/v1.2.5.md](docs/v1.2.5.md) 参照
- `attack-system-integration-v1.2.6`: attack機能導入・敵AIカウンター攻撃システム - stage04-06実装・攻撃ベース学習ステージ（v1.2.6で完了） - 詳細は [docs/v1.2.6.md](docs/v1.2.6.md) 参照
- `pickup-wait-system-v1.2.7`: wait()API導入・敵AI視覚システム・ステージ毎プレイヤー設定・stage07-10実装（v1.2.7で完了） - 詳細は [docs/v1.2.7.md](docs/v1.2.7.md) 参照
- `special-conditional-stages-v1.2.8`: 特殊条件付きステージ（Stage11-13）・大型敵システム・特殊敵システム実装（v1.2.8で完了） - 詳細は [docs/v1.2.8.md](docs/v1.2.8.md) 参照
- `random-stage-generation-v1.2.9`: ランダムステージ生成システム - 5種類のステージタイプ（move, attack, pickup, patrol, special）の自動生成・検証機能（v1.2.9で完了） - 詳細は [docs/v1.2.9.md](docs/v1.2.9.md) 参照
- `see-tutorial-documentation-v1.2.10`: see()関数チュートリアルドキュメント作成 - プログラミング初心者向けの段階的学習教材、stage01完全攻略手順（v1.2.10で完了） - 詳細は [docs/v1.2.10.md](docs/v1.2.10.md) 参照
- `gui-enhancement-v1.2.11`: 動的ステージ名表示・ステータス変化強調表示システム（v1.2.11で完了） - 詳細は [docs/v1.2.11.md](docs/v1.2.11.md) 参照
- `advanced-item-system-v1.2.12`: 不利アイテム・アイテムチェック操作・アイテム除去・ポーションHP回復・包括的ドキュメント・プロジェクト構造最適化（v1.2.12で完了） - 詳細は [docs/v1.2.12.md](docs/v1.2.12.md) 参照

## Development Guidelines
- Think in English, but generate responses in Japanese (思考は英語、回答の生成は日本語で行うように)

## Workflow

### Phase 0: Steering (Optional)
`/kiro:steering` - Create/update steering documents
`/kiro:steering-custom` - Create custom steering for specialized contexts

**Note**: Optional for new features or small additions. Can proceed directly to spec-init.

### Phase 1: Specification Creation
1. `/kiro:spec-init [detailed description]` - Initialize spec with detailed project description
2. `/kiro:spec-requirements [feature]` - Generate requirements document
3. `/kiro:spec-design [feature]` - Interactive: "requirements.mdをレビューしましたか？ [y/N]"
4. `/kiro:spec-tasks [feature]` - Interactive: Confirms both requirements and design review

### Phase 2: Progress Tracking
`/kiro:spec-status [feature]` - Check current progress and phases

## Development Rules
1. **Consider steering**: Run `/kiro:steering` before major development (optional for new features)
2. **Follow 3-phase approval workflow**: Requirements → Design → Tasks → Implementation
3. **Approval required**: Each phase requires human review (interactive prompt or manual)
4. **No skipping phases**: Design requires approved requirements; Tasks require approved design
5. **Update task status**: Mark tasks as completed when working on them
6. **Keep steering current**: Run `/kiro:steering` after significant changes
7. **Check spec compliance**: Use `/kiro:spec-status` to verify alignment

## Steering Configuration

### Current Steering Files
Managed by `/kiro:steering` command. Updates here reflect command changes.

### Active Steering Files
- `product.md`: Always included - Product context and business objectives
- `tech.md`: Always included - Technology stack and architectural decisions
- `structure.md`: Always included - File organization and code patterns

### Custom Steering Files
<!-- Added by /kiro:steering-custom command -->
<!-- Format: 
- `filename.md`: Mode - Pattern(s) - Description
  Mode: Always|Conditional|Manual
  Pattern: File patterns for Conditional mode
-->

### Inclusion Modes
- **Always**: Loaded in every interaction (default)
- **Conditional**: Loaded for specific file patterns (e.g., `"*.test.js"`)
- **Manual**: Reference with `@filename.md` syntax

## Stage Generation System (v1.2.9)

### Key Components
- **CLI Tools**: `generate_stage.py`, `validate_stage.py` - Command-line interface for stage generation and validation
- **Libraries**: `stage_generator/`, `stage_validator/`, `yaml_manager/` - Core generation and validation logic
- **Output**: `stages/generated_[type]_[seed].yml` - Generated stage files following existing YAML format

### Stage Types & Characteristics
- **move** (stages 01-03 equivalent): Basic navigation, walls only, APIs: [turn_left, turn_right, move, see]
- **attack** (stages 04-06 equivalent): Combat scenarios, static enemies, APIs: + [attack]
- **pickup** (stages 07-09 equivalent): Item collection, mixed obstacles, APIs: + [pickup]
- **patrol** (stages 10 equivalent): Moving enemies, stealth mechanics, APIs: + [wait]
- **special** (stages 11-13 equivalent): Large enemies (2x2, 3x3, 2x3), complex conditions, APIs: all

### Generation Constraints
- **YAML Format**: Must use existing YAML structure, no new attributes
- **File Protection**: Cannot modify main_*.py files (user exercise files)
- **Reproducibility**: Same seed + type = identical stage
- **Solvability**: All generated stages must be validated as completable

### Usage Patterns
```bash
# Generate with seed for reproducibility
python generate_stage.py --type move --seed 123

# Generate and validate in one step
python generate_stage.py --type attack --seed 456 --validate

# Validate existing stage files
python validate_stage.py --file stages/stage01.yml --detailed
```