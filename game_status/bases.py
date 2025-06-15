import abc, functools as fts

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
        @StatAct.actfunc # 操作
        def heal(obj, a):
            obj.HP += a
        
        class Status(GameObject):
            HP = Point(minim(0), maxim(100), default=100)
        # できあいの定義に登録
        heal.register(Status, "HP")

        ins = Status()
        ins.heal("HP", 10) # こんな風に使えます

        ```
        これはStatEffectがクラスの実装にちょっかい出すためのものです。
        """
        def __init__(self, func): self.__func = func
        @property
        def name(self): return self.__func.__name__
        def register(self, cls, sname):
            """ステータスクラスに適用"""
            if not hasattr(cls, self.name):
                setattr(cls, self.name, StatAct())
            statact = getattr(cls, self.name)
            assert isinstance(statact, StatAct)
            statact.register(sname, self)
        def __call__(self, obj, *a, **ka):
            return self.__func(obj, *a, **ka)
        
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
                self.heal.register(cls, self.target)
        
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
        def __call__(self, iself, obj, *a, **ka):
            return self.__func(iself, obj, *a, **ka)
    
    def __init__(self, default=None):
        self._acts = {}
        if default is None:
            self._default = (lambda name, *a, **ka: None)
        else:
            self._default = default
    def register(self, name, act):
        """操作を登録する"""
        self._acts |= {name:act}
    def __get__(self, obj, cls=None):
        if obj is None: return self
        return fts.partial(self.__call__, obj)
    def __call__(self, obj, name, *a, **ka):
        """登録された操作を実行する"""
        if name in self._acts: self._acts[name](obj, *a, **ka)
        else: self._default(obj, name, *a, **ka)

class GameObject:
    """ゲームオブジェクトの素体"""
    def __init__(self):
        self._buffs = []
    @property
    def buffs(self) -> list[Buff]:
        """バフのリスト"""
        return self._buffs
    @StatAct
    def _turn_act(self, name):
        """ターン経過時の各ステータス値に対する処理"""
    def _turn(self):
        """ターン経過時の一般処理(オーバーライドして使用)"""
    def turn(self):
        """ターン経過時の処理を実行"""
        self._turn()
        for n, v in vars(type(self)).items():
            if isinstance(v, StatBase): self._turn_act(self, n)
        for b in self.buffs[:]: b.turn(self.buffs)

class StatEffect(typing.Generic[STATS, SVAL]):
    """ステータス値への効果"""
    def set_name(self, cls:type[STATS], name:str):
        """Attrディスクリプタの__set_name__が呼び出されたときに呼ばれる"""
    def get(self, val:SVAL, obj:STATS, cls:type[STATS]) -> SVAL:
        """Attrディスクリプタの__get__が呼び出されたときに呼ばれる"""
        return val

class StatBase(typing.Generic[STATS, SVAL]):
    """ステータス値のディスクリプタ"""
    def __set_name__(self, cls:type[STATS], name:str):
        """宣言時に呼び出される"""
    def __get__(self, obj:STATS|None, cls:type[STATS]|None=None) -> SVAL:
        """ステータス値を取得する"""
        if obj is None: return self

VALUELIKE = StatBase[STATS, SVAL] | SVAL

def getval(
        a:VALUELIKE,
        obj:STATS, cls:type[STATS]) -> SVAL:
    """ステータスなら値取得、さもなくばaをそのまま返す"""
    if isinstance(a, StatBase): return a.__get__(obj, cls)
    return a
