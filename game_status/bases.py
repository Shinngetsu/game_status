# coding: utf-8
'''
# 基本の定義
- class StatAct
  - ステータス値に紐づく操作
- class StatBase
  - ステータス値のディスクリプタ
- class HasStatus
  - ステータスを所持するオブジェクトの基本クラス
- class GameObject
  - ゲームオブジェクトの素体
- class StatEffect
  - ステータス値への効果
- def getval(VALUELIKE, STATS, type[STATS])
  - ステータスなら値取得、さもなくばaをそのまま返す
- def getdep(VALUELIKE)
  - ステータスの依存関係を取得する
'''
import abc, functools as fts
import graphlib

import typing, collections.abc as ctyping

STATS = typing.TypeVar("STATS")
SVAL = typing.TypeVar("SVAL")

class StatAct:
    """# ステータス値に紐づく操作
    - ステータス値ごとの操作を登録
    - 登録された操作を実行する
    ### 使い道
    経験値で成長する値の成長処理などに使います。
    ### 使用例
    ```python
    class Status(GameObject):
        action1 = StatAct() # action1という関数を登録

        @StatAct
        def action2(self, name, a, b):
            "未登録時のデフォルト処理"
            ...
        
        action3 = StatAct()
        action3.register("STR", lambda self: ...) # registerでアクションを設定

        STR = Value(grow(.1)) # 一部のエフェクトは自動的にアクションを設定する

    ins = Status()
    
    ins.action1("STR") # 何も起こらない
    ins.action2("STR", 1, 2) # デフォルト処理が呼び出される
    ins.action3("STR", 1) # 登録されたアクションが実行される
    ins.gainexp("STR", 10) # STRで登録された経験値追加処理が呼び出される
    ```"""
    class actfunc:
        """# 操作関数
        - クラスのStatAct要素に登録できる
        ### 使用例
        ```python
        from game_status import *
        @StatAct.actfunc # 操作
        def heal(obj, a):
            obj.HP += a
        
        class Status(GameObject):
            HP = Point(arg(default=100), minim(0), maxim(100))
        # できあいの定義に登録
        heal.register(Status, "HP")

        ins = Status()
        ins.heal("HP", 10) # こんな風に使えます

        ```
        これはStatEffectがクラスの実装にちょっかい出すためのものです。
        """
        def __init__(self, func): self._func = func
        @property
        def name(self): return self._func.__name__
        def register(self, cls, sname):
            """ステータスクラスに適用"""
            if not hasattr(cls, self.name):
                setattr(cls, self.name, StatAct())
            statact = getattr(cls, self.name)
            assert isinstance(statact, StatAct)
            statact.register(sname, self)
        def __call__(self, obj, *a, **ka):
            return self._func(obj, *a, **ka)
        
    class actmethod(actfunc):
        """# 操作メソッド
        - actfuncのメソッド版
        ### 使用例
        ```python
        class HealSystem:
            def __init__(self, target):
                self.target = target
            @StatAct.actmethod # 操作メソッド
            def heal(self, obj, a):
                setattr(obj, self.target,
                    getattr(obj, self.target) + a)
            def register(self, cls):
                self.heal.register(cls, self.target, self)
        
        class Status(GameObject):
            HP = Point(minim(0), maxim(100), default=100)
            MP = Point(minim(0), maxim(100), default=100)
        # できあいの定義に登録
        HealSystem("HP").register(cls)
        HealSystem("MP").register(cls)
        
        ins = Status()
        ins.heal("HP", 10)
        ins.heal("MP", 10)
        ```
        これはStatEffectがクラスの実装にちょっかい出すためのものです。
        """
        
        def register(self, cls, sname, managed_obj):
            """ステータスクラスに適用"""
            if not hasattr(cls, self.name):
                setattr(cls, self.name, StatAct())
            statact = getattr(cls, self.name)
            assert isinstance(statact, StatAct)
            statact.register(sname, fts.partial(self, managed_obj))
        def __call__(self, iself, obj, *a, **ka):
            return self._func(iself, obj, *a, **ka)
    
    def __init__(self, default=None):
        self._acts = {}
        if default is None:
            self._default = (lambda name, *a, **ka: None)
        else:
            self._default = default
    def register(self, name, act):
        """操作を登録する"""
        self._acts |= {name:act}
    def callwith(self,
                obj,
                func:ctyping.Callable[
                    [str],
                    tuple[tuple, dict[str, typing.Any]]]):
        "登録された処理をオブジェクトのステータス値ごとに呼び出す"
        for k, v in self._acts.items():
            a, ka = func(k)
            yield v(obj, *a, **ka)
    def keys(self): return self._acts.keys()
    def values(self): return self._acts.values()
    def items(self): return self._acts.items()
    def __get__(self, obj, cls=None):
        if obj is None: return self
        def call(name, *a, **ka):
            if name in self._acts: self._acts[name](obj, *a, **ka)
            else: self._default(obj, name, *a, **ka)
        return call

class StatBase(typing.Generic[STATS, SVAL]):
    '''# ステータス値のディスクリプタ
    HasStatusが想定するステータスの実装
    '''
    @property
    def _name(self) -> str: return self.__name
    @property
    def _has_name(self) -> bool: return "_StatBase__name" in dir(self)
    @property
    def _dependencies(self) -> set[str]: return set()
    def __set_name__(self, cls:type[STATS], name:str):
        """宣言時に呼び出される"""
        self.__name = name
    def __get__(self, obj:STATS|None, cls:type[STATS]|None=None) -> SVAL:
        """ステータス値を取得する"""
        if obj is None: return self
    def __repr__(self):
        res = self.__class__.__name__
        res += "(" + ', '.join(
            f'{k}= {repr(v)}'
            for k, v in vars(self).items()
            if not callable(v)) + ")"
        return res

class HasStatus:
    """# ステータスを所持するオブジェクトの基本クラス
    ステータス値の依存関係グラフをチェックし、正しい順番で初期化します。
    
    ```python
    from game_status import *
    # エラーします
    class InvalidObj(HasStatus):
        A = Point(arg(default=B+3)) # Bに依存
        B = A + 30 # Aに依存
    
    # エラーしません
    class SafeObj(HasStatus):
        A = Point(arg(default=B)) # Bに依存
        B = Point(arg(default=100)) # 依存なし
    obj = SafeObj(B = 200) # B -> A の順番で初期化されます
    assert obj.A == 200
    assert obj.B == 200
    ```
    """
    @StatAct
    def _init(self, name, value):
        """初期化時の値指定"""
    @StatAct
    def _default_init(self, name):
        """初期化時に引数が指定されなかったときの値指定"""
    def __init__(self, **ka):
        ordered = graphlib.TopologicalSorter(
            self._dependency_graph).static_order()
        for n in ordered:
            if n in ka: self._init(n, ka[n])
            else: self._default_init(n)
    _dependency_graph = {} # {name: {other, ...}, ...}
    def __init_subclass__(cls):
        for k, v in tuple(vars(cls).items()):
            if isinstance(v, StatBase):
                cls._dependency_graph = (
                    cls._dependency_graph |
                    {k:v._dependencies})
        try: graphlib.TopologicalSorter(cls._dependency_graph).prepare()
        except graphlib.CycleError:
            raise Exception("依存関係の循環を検知しました。")
    def __repr__(self):
        res = self.__class__.__name__
        res += "(" + ', '.join(
            f'{k}= {repr(v)}'
            for k, v in vars(self).items()
            if not callable(v)) + ")"
        return res

class GameObject(HasStatus):
    """# ゲームオブジェクトの素体
    このクラスを継承し各ステータス値を設定することで、キャラやアイテムの動作を作ります。いろいろと実装を含むので、もしそれが気に食わないなら集約で所持することをお勧めします。
    ## 例
    ```python
    class Apple(GameObject):
        freshness = Value(arg(100), turn(-1))
        price = Value(default(20 * (freshness < 0)))
        on_eat_HpRecover = (
            (freshness >= 50) * 10 +
            (freshness >= 0 ) * 20 +
            -10)

        name = "りんご" + "（腐敗）" * (freshness < 0)
        description = (
            "みずみずしい新鮮なりんご。" * (freshness >= 50) +
            "ちょっとしんなりし始めているりんご。" * (50 > freshness >= 0) +
            "ハエがたかり異臭を放つりんご。" * (freshness < 0) +
            "食べると体力が" +
            on_eat_HpRecover + "ポイント" +
                "減少" * (on_eat_HpRecover <  0) +
                "回復" * (on_eat_HpRecover >= 0) + "する。")

        @property
        def is_rotten(self): return self.freshness < 0
    ```"""
    
    def __init__(self, buffs=(), /, **ka):
        self._buffs = list(buffs)
        super().__init__(**ka)

    @property
    def buffs(self) -> list:
        """バフのリスト"""
        return self._buffs
    @StatAct
    def _turn_act(self, name:str):
        """ターン経過時の各ステータス値に対する処理"""
    def _pre_turn(self):
        """ターン経過時の一般処理(オーバーライドして使用)"""
    def _post_turn(self):
        """ターン経過後の一般処理(オーバーライドして使用)"""
    def turn(self):
        """ターン経過時の処理を実行"""
        self._pre_turn()
        for n, v in vars(type(self)).items():
            if isinstance(v, StatBase): self._turn_act(n)
        for b in self.buffs[:]: b.turn(self)
        self._post_turn()

VALUELIKE = StatBase[STATS, SVAL] | SVAL

def getval(
        a:VALUELIKE,
        obj:STATS, cls:type[STATS]) -> SVAL:
    """ステータスなら値取得、さもなくばaをそのまま返す"""
    if isinstance(a, StatBase): return a.__get__(obj, cls)
    return a
def getdep(a:VALUELIKE):
    """ステータスの依存関係を取得する"""
    if isinstance(a, StatBase): return a._dependencies
    return set()
