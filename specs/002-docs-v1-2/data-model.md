# Data Model: see()関数チュートリアル

## Document Entities

### Tutorial Document
**Purpose**: see()関数の学習用教材構造
**Fields**:
- title: チュートリアルタイトル
- sections: セクション構造（理論→実践→応用）
- target_audience: プログラミング初心者
- learning_objectives: see()理解、stage01クリア、応用力習得

**Validation Rules**:
- 各セクションは「狙い」「期待結果」「実際の結果例」を含む
- 初心者理解レベルを維持（専門用語の説明付き）
- 段階的学習フローを保持

### Stage01 Example
**Purpose**: 具体的な学習ケース
**Fields**:
- stage_config: stage01.ymlの構造解析
- player_actions: アクション系列（turn_left, turn_right, move, see）
- see_outputs: 各時点でのsee()実行結果
- solution_path: クリアまでの完全手順

**Validation Rules**:
- 実行可能なアクション系列であること
- see()の結果が実際のゲーム状態と一致すること
- 初心者が追跡可能な段階的説明であること

### Code Examples
**Purpose**: 実行可能なPythonコード片
**Fields**:
- code_snippet: 実際のPythonコード
- expected_output: 期待される実行結果
- explanation: コードの動作説明
- error_cases: よくある間違いとその対処

**Validation Rules**:
- 構文的に正しいPythonコードであること
- see()関数の実際の仕様に合致すること
- 初心者が理解しやすいコメント付きであること

## Relationships

### Tutorial → Examples
- 1つのチュートリアルは複数のコード例を含む
- 各例は学習段階に対応付けられる

### Examples → Stage01
- Stage01の状況に基づいた具体的なコード例
- see()の返却値とゲーム状態の対応関係

### Tutorial → Integration
- 既存SeeDescription.mdとの相補関係
- 段階的学習システムとの統合点

## State Transitions

### Learning Progression States
1. **Unknown**: see()を知らない初心者状態
2. **Basic Understanding**: see()の基本概念理解
3. **Practical Application**: stage01での実践使用
4. **Independent Problem Solving**: 自力でクリア戦略立案

**Transition Rules**:
- Unknown → Basic: チュートリアル理論部分完読
- Basic → Practical: stage01コード例実行
- Practical → Independent: 完全クリア手順理解

### Document Development States
1. **Draft**: 初期構造作成
2. **Content Complete**: 全セクション内容作成完了
3. **Validated**: 初心者テストによる検証済み
4. **Integrated**: システム統合完了

## Constraints

### Technical Constraints
- main_*.pyファイル編集禁止（ユーザ演習用）
- 既存SeeDescription.md構造保持
- 設定一カ所集約原則遵守

### Educational Constraints
- 初心者理解レベル維持
- 段階的学習フロー保持
- 実践性と理論のバランス

### Integration Constraints
- 既存学習システムとの整合性
- ドキュメント一貫性保持
- バージョン管理との連携（v1.2.10）