# Tutorial Structure Contract

## Document Structure Requirements

### Required Sections
```markdown
# see()関数実践チュートリアル

## 1. はじめに
- see()関数の概要と用途
- このチュートリアルの目標
- 必要な前提知識

## 2. see()関数の基礎
- 基本的な呼び出し方法
- 返却データの構造解説
- よく使用する情報の取得方法

## 3. Stage01を例にした実践
- Stage01の構造解析
- see()を使った情報収集手順
- アクション決定のための情報活用

## 4. 完全クリア手順
- 段階的なプレイヤーアクション系列
- 各段階でのsee()実行と結果解析
- 戦略立案の思考過程

## 5. デバッグとトラブルシューティング
- よくある間違いパターン
- 期待結果と実際結果の相違時対処
- 辞書構造理解のための補助説明

## 6. 他ステージへの応用
- 基本パターンの抽出
- 異なるステージでの考え方
- 応用力向上のポイント
```

### Content Requirements

#### Each Code Example Must Include
- **目的**: なぜこのコードが必要か
- **コード**: 実行可能なPython snippet
- **実行結果**: 期待される出力（具体例）
- **解説**: 初心者向けの詳細説明

#### Each Section Must Provide
- **学習目標**: セクション完了時に習得する能力
- **実践課題**: 理解度確認用の小課題
- **次ステップ**: 次セクションへの導線

### Format Requirements

#### Code Block Format
```python
# 目的: [なぜこのコードが必要か]
info = see()
print(info["player"]["position"])
# 期待結果: [2, 3] (現在のプレイヤー位置)
# 解説: player情報から現在位置を取得します...
```

#### Example Output Format
```
実行結果例:
{
  "player": {
    "position": [0, 0],
    "direction": "N",
    "hp": 100
  },
  "surroundings": {
    "front": "empty",
    "left": "empty",
    "right": "wall",
    "back": "boundary"
  }
}
```

### Quality Gates

#### Content Validation
- [ ] 初心者が30分以内で基礎理解可能
- [ ] Stage01完全クリア手順が明確
- [ ] 全コード例が実行可能
- [ ] エラーケース対応が含まれている

#### Integration Validation
- [ ] SeeDescription.mdとの整合性確認
- [ ] 既存システムとの競合なし
- [ ] main_*.py編集要求なし

#### Accessibility Validation
- [ ] 専門用語に説明付き
- [ ] 段階的学習フロー維持
- [ ] 視覚的な構造化（見出し、リスト活用）