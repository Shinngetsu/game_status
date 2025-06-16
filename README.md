# game_status
- ディスクリプタでゲームオブジェクトの計算構造を表現できるようにする
- バフなどのインフラも用意しています
- まだまだ作りかけです…

## 特徴
- ステータスに対する操作の実装
- 依存関係を計算式で表現

## 使い方
### インポート
```python
from game_status import *
```
### ゲームオブジェクトの定義
```python
class Status(GameObject):
  STR = game.Value(default(0), grow(), buffed(), minim(0))
  "耐久値:基本値=0, 成長する, バフを受け付ける, 最小値=０"

  HP_max = (STR + 1) * 10
  "体力の最大値（STRをもとに計算）"

  HP = Point(minim(0), maxim(HP_max), default=HP_max)
  "体力値:最小値=０, 最大値=体力最大値, 基本値=体力最大値"
```
バフの定義
```python
class RecoverHP(buff.Buff):
  duration = Point(per_turn(-1), minim(0), default=arg('duration', default=1))
  "効果時間"

  effect = Value(default(arg('effect', default=1.)))
  "品質"

  HP = buff.Add(effect)
  "HPの変化"

  @property # バフの終了条件
  def is_disabled(self): return self.duration == 0
```

## これから
- スペック（仕様）テストの充実
- もっと分かりやすい設計の模索
- エラーの見直し
  - 循環依存の検出など
- リアルタイム性
  - 経過時間を考慮できるようにする
  - 処理高速化の模索
