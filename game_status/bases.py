import abc
from mathobj import MathObj

import typing, collections.abc as ctyping

STATS = typing.TypeVar("STATS")
SVAL = typing.TypeVar("SVAL")

class Buff(abc.ABC):
    """# 各ステータス値へのバフを適用する
    e_<statname>メソッドを定義することで、
    特定のステータス値に対する効果を定義できる。"""
    @property
    @abc.abstractmethod
    def name(self): return type(self).__name__
    def effect(self, stat, vname, val):
        return (getattr(self, f'e_{vname}')(stat, val)
                if hasattr(self, f'e_{vname}') else val)
    @abc.abstractmethod
    def turn(self, buffs): pass



class StatAct:
    """## ステータス値に紐づく操作
    - 操作をステータス値ごとに登録"""
    class actfunc:
        """操作関数"""
        def __init__(self, func): self.__func = func
        @property
        def name(self): return self.__func.__name__
        def register(self, cls):
            """ステータスクラスに適用"""
            if not hasattr(cls, self.name):
                setattr(cls, self.name, StatAct())
            statact = getattr(cls, self.name)
            assert isinstance(statact, StatAct)
            statact.register(self.name)
        def __call__(self, obj, *a, **ka):
            return self.__func(obj, *a, **ka)
    class actmethod(actfunc):
        """操作メソッド"""
        def __call__(self, iself, obj, *a, **ka):
            return self.__func(iself, obj, *a, **ka)
    def __init__(self, default=None):
        self._acts = {}
        if default is None:
            self._default = (lambda name, *a, **ka: None)
        else:
            self._default = default
    def register(self, name, value):
        """操作を登録する"""
        self._acts |= {name:value}
    def __call__(self, obj, name, *a, **ka):
        """登録された操作を実行する"""
        if name in self._acts: self._acts[name](obj, *a, **ka)
        else: self._default(obj, name, *a, **ka)

class GameObject(abc.ABC):
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

class StatBase(typing.Generic[STATS, SVAL], MathObj):
    """ステータス値のディスクリプタ"""
    def __set_name__(self, cls:type[STATS], name:str):
        """宣言時に呼び出される"""
    def __get__(self, obj:STATS|None, cls:type[STATS]|None=None) -> SVAL:
        """ステータス値を取得する"""
        if obj is None: return self

def getval(
        a:StatBase[STATS, SVAL]|SVAL,
        obj:STATS, cls:type[STATS]) -> SVAL:
    """ステータスなら値取得、さもなくばaをそのまま返す"""
    if isinstance(a, StatBase): return a.__get__(obj, cls)
    return a
