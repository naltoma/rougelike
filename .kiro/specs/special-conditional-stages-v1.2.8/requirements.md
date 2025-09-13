# Requirements Document

## Introduction
Python初学者向けローグライク演習フレームワークに特殊条件付きステージ（Stage11-13）を追加し、大型敵システムと特殊敵システムを実装します。これにより、学習者は複雑な戦闘ルールと条件分岐を通じて高度な戦略的思考とプログラミング技術を習得できます。

## Requirements

### Requirement 1: 大型敵2x2システム実装
**User Story:** As a 学習者, I want 大型敵2x2と戦闘する, so that 複数マス敵との戦闘戦略を学習できる

#### Acceptance Criteria
1. WHEN システムがステージを初期化する THEN システムは 2x2マス大型敵を正しく配置する
2. IF 大型敵の現在HPが最大HPの50%以上である THEN システムは 大型敵を平常モード状態で表示する
3. WHILE 大型敵が平常モード状態である THE システムは 大型敵の行動を無効化する（反撃・巡視・追跡・移動なし）
4. WHEN プレイヤーが大型敵を攻撃し AND 大型敵の残HPが50%を下回る THEN システムは 大型敵を1ターンで怒りモードに移行させる
5. WHILE 大型敵が怒りモード状態である THE システムは 大型敵の描画を怒り状態表示で描画する
6. WHEN 大型敵が怒りモードに移行完了する THEN システムは 次ターンで大型敵の周囲1マス全体に範囲攻撃を実行する
7. WHERE see()コマンドの範囲内に大型敵がいる場合 THE システムは 大型敵の現在モード（平常/怒り）と攻撃範囲を表示する
8. WHEN 大型敵が範囲攻撃を実行完了する THEN システムは 大型敵を平常モードに戻し AND 以降のプレイヤー攻撃で即座に怒りモードに移行する

### Requirement 2: 大型敵3x3システム実装  
**User Story:** As a 学習者, I want さらに大きな3x3大型敵と戦闘する, so that より複雑な大型敵戦術を習得できる

#### Acceptance Criteria
1. WHEN システムがステージを初期化する THEN システムは 3x3マス大型敵を正しく配置する
2. IF 3x3大型敵が配置される THEN システムは プレイヤー攻撃100回で倒せるHPを設定する
3. WHILE 3x3大型敵が平常モード状態である THE システムは 3x3大型敵の行動を無効化する（反撃・巡視・追跡・移動なし）
4. WHEN 3x3大型敵の残HPが50%を下回る THEN システムは 2x2大型敵と同じ怒りモード動作を実行する
5. WHERE 3x3大型敵が範囲攻撃を実行する場合 THE システムは 3x3大型敵の周囲1マス全体を攻撃範囲として設定する

### Requirement 3: 特殊敵2x3システム実装
**User Story:** As a 学習者, I want 特殊な条件を持つ2x3敵と戦闘する, so that 条件付き戦闘ロジックを理解できる

#### Acceptance Criteria
1. WHEN システムがステージを初期化する THEN システムは 2x3マス特殊敵にHP/ATK各10000を設定する
2. WHILE 特殊敵が平常状態である THE システムは 特殊敵の行動を反撃のみに制限する（移動・巡視・追跡なし）
3. IF 特殊条件が違反される THEN システムは 特殊敵を怒りモードに移行し AND プレイヤーを追跡攻撃する
4. WHEN 大型敵2x2が撃破され AND 大型敵3x3が撃破される THEN システムは 特殊敵を消去しステージクリアとする

### Requirement 4: Stage11実装
**User Story:** As a 学習者, I want Stage11で大型敵2x2と戦闘する, so that 怒りモードと範囲攻撃の基本戦術を学習できる

#### Acceptance Criteria
1. WHEN プレイヤーがStage11を開始する THEN システムは 攻撃50回で倒せる大型敵2x2を1体配置する
2. IF 大型敵の残HPが50%を下回る THEN システムは 怒りモード→範囲攻撃→平常モードのサイクルを開始する
3. WHERE 大型敵が範囲攻撃を実行する場合 THE システムは 攻撃範囲を視覚的に表示する
4. WHEN プレイヤーが大型敵を撃破する THEN システムは Stage11をクリア状態にする

### Requirement 5: Stage12実装
**User Story:** As a 学習者, I want Stage12で複数の大型敵と戦闘する, so that 複数大型敵との戦術的優先順位を学習できる

#### Acceptance Criteria
1. WHEN プレイヤーがStage12を開始する THEN システムは 大型敵2x2と大型敵3x3を1体ずつ配置する
2. IF 大型敵2x2の設定が必要な場合 THEN システムは Stage11と同じ設定を適用する
3. WHEN 両方の大型敵が撃破される THEN システムは Stage12をクリア状態にする

### Requirement 6: Stage13実装
**User Story:** As a 学習者, I want Stage13で特殊条件付き戦闘を体験する, so that 高度な戦略的順序判断を習得できる

#### Acceptance Criteria
1. WHEN プレイヤーがStage13を開始する THEN システムは 大型敵2x2、大型敵3x3、特殊敵2x3を配置する
2. IF 特殊条件が「大型敵2x2を先攻撃→大型敵3x3を後攻撃」である THEN システムは この順序を監視する
3. WHEN 特殊条件が遵守される AND 両大型敵が撃破される THEN システムは 特殊敵を自動消去し AND Stage13をクリア状態にする
4. IF 特殊条件が違反される THEN システムは 特殊敵を怒りモードにし AND プレイヤー追跡攻撃を開始する

### Requirement 7: システム統合・設定管理
**User Story:** As a 開発者, I want 既存v1.2.7システムとの統合を保持する, so that 機能追加が既存機能を破壊しない

#### Acceptance Criteria
1. WHEN 新機能が実装される THEN システムは main_*.pyファイルを編集しない
2. IF 新しい設定が追加される THEN システムは 設定を一元管理場所に配置する
3. WHILE 新機能が動作する THE システムは 既存のwait()API、敵AI視覚システムとの互換性を維持する
4. WHERE 新ステージが追加される場合 THE システムは 既存のYAML形式ステージ定義規則に従う
5. WHEN 新敵システムが実装される THEN システムは 既存のGUI Enemy Info Panelとの統合を保持する

### Requirement 8: 教育的価値・学習支援
**User Story:** As a 学習者, I want 特殊条件付きステージを通じて学習する, so that 高度なプログラミング思考力を身につけられる

#### Acceptance Criteria
1. WHERE 学習者がStage11-13に取り組む場合 THE システムは 段階的な難易度上昇を提供する
2. IF 学習者が特殊条件を理解していない THEN システムは 適切なエラーメッセージと学習ヒントを提供する
3. WHEN 学習者がステージをクリアする THEN システムは 学習成果を既存のセッションログシステムに記録する
4. WHILE 学習者が戦闘中である THE システムは see()コマンドで敵状態の観察学習を支援する