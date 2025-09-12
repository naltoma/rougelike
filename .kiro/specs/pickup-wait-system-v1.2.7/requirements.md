# Requirements Document

## Introduction

v1.2.7では、pickup機能とwait機能を導入し、stage07-09を実装することで、Python初学者に対してより高度な戦略的思考と効率的プログラミング学習を提供する。本機能により、武器取得による戦術的優位性、待機による敵行動制御、敵AI移動ルーチンとの相互作用を通じた複合的学習体験を実現する。

## Requirements

### Requirement 1: Pickup System Implementation
**User Story:** Python初学者として、ステージ上のアイテム（武器）を取得してキャラクターの能力を向上させることで、戦略的思考とプログラミングスキルを習得したい

#### Acceptance Criteria

1. WHEN プレイヤーがpickup()関数を呼び出す THEN システムはプレイヤーの正面にアイテムが存在するかチェックする
2. IF プレイヤーの正面にアイテムが存在する THEN システムはそのアイテムをプレイヤーのインベントリに追加する
3. WHEN 武器アイテムが取得される THEN システムは自動的に武器を装備してプレイヤーの攻撃力を増加させる
4. IF プレイヤーの正面にアイテムが存在しない THEN システムは「アイテムがありません」のエラーメッセージを表示する
5. WHERE GUIモードの場合 THE システムはアイテム取得時に視覚的フィードバック（アイテム消去、装備状態表示）を提供する

### Requirement 2: Wait System Implementation
**User Story:** Python初学者として、その場で待機することで敵の行動を観察し、戦術的なタイミングを学習したい

#### Acceptance Criteria

1. WHEN プレイヤーがwait()関数を呼び出す THEN システムはプレイヤーのターンを消費して敵のターンに移行する
2. WHILE プレイヤーが待機している THE システムは敵AIの1ターン分の行動を実行する
3. WHEN wait()実行時に敵がプレイヤーに隣接している THEN システムは敵AIの標準行動（方向転換・攻撃判定含む）を実行する
4. WHEN wait()が実行される THEN システムはプレイヤーの位置と向きを変更しない
5. WHERE デバッグモードの場合 THE システムは「1ターン待機しました」のメッセージを表示する

### Requirement 3: Stage07 - Weapon Pickup Strategy
**User Story:** Python初学者として、武器取得戦略を通じて条件分岐とリスク管理のプログラミング概念を習得したい

#### Acceptance Criteria

1. WHEN stage07が初期化される THEN システムは敵のHP・攻撃力を増加させてプレイヤー1回攻撃では撃破不可能にする
2. IF プレイヤーが武器を取得せずに敵を攻撃する THEN システムは敵のカウンター攻撃でプレイヤーを撃破してゲーム終了にする
3. WHEN プレイヤーが武器を取得する THEN システムは攻撃力を増加させて1回攻撃で敵撃破を可能にする
4. WHERE 敵の配置について THE システムは敵を正面からのみ攻撃可能な位置に配置する
5. IF ステージクリア条件が満たされる THEN システムは「武器取得による戦術的勝利」のフィードバックを表示する

### Requirement 4: Stage08 - Loop Programming Enhancement
**User Story:** Python初学者として、拡大されたステージでループ処理を効率的に活用する方法を学習したい

#### Acceptance Criteria

1. WHEN stage08が初期化される THEN システムはステージサイズを従来の2倍に拡大する
2. IF プレイヤーがループ処理を使用しない場合 THEN システムは非効率な解法に対する教育的フィードバックを提供する
3. WHEN プレイヤーがfor文やwhile文を使用する THEN システムはコード行数削減の達成メトリクスを記録する
4. WHERE ステージ08以降のすべてのステージについて THE システムは2倍サイズを維持する
5. IF ステージクリアが達成される THEN システムは「ループ処理による効率化」の学習成果を表示する

### Requirement 5: Stage09 - Enemy AI Movement System
**User Story:** Python初学者として、動的な敵AIとの相互作用を通じて複合的な問題解決能力を習得したい

#### Acceptance Criteria

1. WHEN stage09の敵AIが初期化される THEN システムは敵に1マス壁周囲の時計回り巡回行動パターンを設定する
2. IF プレイヤーが敵の視界範囲内に入る THEN システムは敵を巡回モードから追跡モードに切り替える
3. WHILE 敵が追跡モードの場合 THE システムは敵をプレイヤーに向かって移動させる
4. WHEN プレイヤーが敵の視界から外れる THEN システムは敵を巡回モードに戻す
5. WHERE プレイヤーが視界を回避して武器取得する場合 THE システムは「視界回避戦略成功」の評価を記録する

### Requirement 6: Game Balance Adjustments
**User Story:** 教育フレームワーク利用者として、適切な学習難易度とリスク・リワードバランスを体験したい

#### Acceptance Criteria

1. WHEN v1.2.7の敵が生成される THEN システムは敵のHP・攻撃力をプレイヤーのデフォルト攻撃力で1回撃破不可能に設定する
2. IF プレイヤーが武器未装備で敵から攻撃を受ける THEN システムは1回の敵攻撃でプレイヤーを撃破する
3. WHEN プレイヤーが武器を装備した状態で攻撃する THEN システムは1回攻撃での敵撃破を可能にする
4. WHERE pickup・wait機能が追加される THE システムは既存のattack・move機能との互換性を維持する
5. IF stage07-09のいずれかでゲームオーバーが発生する THEN システムは戦略改善のための具体的なヒントを提供する

### Requirement 7: API Integration and Compatibility
**User Story:** Python初学者として、新しいpickup・wait機能を既存のAPIと一貫した方法で使用したい

#### Acceptance Criteria

1. WHEN pickup()関数が呼び出される THEN システムは既存のmove()・attack()と同じエラーハンドリング方式を適用する
2. IF wait()関数が不適切な状況で呼び出される THEN システムは教育的エラーメッセージを表示する
3. WHEN 新しい機能がsee()で状況確認される THEN システムはアイテム存在・敵状態・視界情報を含む辞書を返す
4. WHERE CUIモードの場合 THE システムはpickup・wait行動の結果をテキストで明確に表示する
5. IF ステージでpickup・wait機能が許可されていない THEN システムは「この機能は現在のステージでは使用できません」のメッセージを表示する

### Requirement 8: Educational Feedback and Analytics
**User Story:** 教員として、学生のpickup・wait機能習得状況と戦略的思考の発達を把握したい

#### Acceptance Criteria

1. WHEN 学生がpickup()を初回使用する THEN システムはアイテム取得学習の開始をセッションログに記録する