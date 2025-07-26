# coding: utf-8

from .bases import StatBase, STATS, SVAL, getval, StatAct, getdep
import operator as op
from mathobj import rjoins, MathObj
import typing

class Stat(StatBase[STATS, SVAL], MathObj):
    """# ステータス値のディスクリプタ
    ValueやPointの計算式としての実装。
    ```python
    # 定義
    class MyStat(Stat):
        def __init__(self, value):
            self.__value = value
        def __get__(self, obj, cls=None):
            if obj is None: return self
            return self.__value
    
    # 使用
    class Stats(GameObject):
        A = MyStat(100)
        B = A * 2
    
    obj = Stats()
    assert obj.A == 100
    assert obj.B == 200
    ```"""
    def _unary(self, uf): return Calc(uf, self)
    def _binary(self, bf, b): return Calc(bf, self, b)
    def _rbinary(self, bf, a): return Calc(bf, a, self)
    def __getattr__(self, k): return Calc(getattr, self, k)
    def __getitem__(self, k): return Calc(op.getitem, self, k)
    def __call__(self, *a, **ka): return Calc(self, *a, **ka)


class StatEffect(typing.Generic[STATS, SVAL]):
    """# ステータス値への効果
    ValueやPointに設定できるエフェクトの基本クラスです。
    ```python
    from game_status import *
    class MyStatEffect(StatEffect):
        def set_name(self, cls, name):
            print(f'MyStatEffect.set_name called! ({cls=}, {name=})')
        def get(self, val, obj, cls):
            print(f'MyStatEffect.get called! ({val=}, {obj=}, {cls=})')
            return val
    ```"""
    def set_name(self, cls:type[STATS], name:str):
        """Attrディスクリプタの__set_name__が呼び出されたときに呼ばれる"""
        self.__name = name
    def get(self, val:SVAL, obj:STATS, cls:type[STATS]) -> SVAL:
        """Attrディスクリプタの__get__が呼び出されたときに呼ばれる"""
        return val
    @property
    def dependencies(self) -> set[str]:
        return set()
    def __repr__(self):
        res = self.__class__.__name__
        res += "(" + ', '.join(
            f'{k}= {repr(v)}'
            for k, v in vars(self).items()
            if not callable(v)) + ")"
        return res


class Value(Stat):
    """筋力などの固定値"""
    def __init__(self, *ops:StatEffect):
        self._ops = ops
    @StatAct.actmethod
    def _set_true_value(self, obj, value):
        setattr(obj, self._vname, value)
    @property
    def _dependencies(self):
        res = set()
        for o in self._ops: res |= o.dependencies
        return res
    def __set_name__(self, cls, name):
        self._vname = f'_{cls.__name__}__{name}_v'
        for o in self._ops: o.set_name(cls, name)
        self._set_true_value.register(cls, name, self)
        super().__set_name__(cls, name)
    def __get__(self, obj, cls=None):
        if obj is None: return self
        res = None
        if hasattr(obj, self._vname):
            res = getattr(obj, self._vname)
        for b in self._ops: res = b.get(res, obj, cls)
        return res
    def __repr__(self):
        if self._has_name: return self._name
        return f'Value({", ".join(repr(i) for i in self._ops)})'

class Point(Stat):
    """HPなどの流動的な値"""
    def __init__(self, *ops:StatEffect):
        self._ops = ops
    @StatAct.actmethod
    def _set_true_value(self, obj, value):
        setattr(obj, self._vname, value)
    @property
    def _dependencies(self):
        res = set()
        for o in self._ops: res |= o.dependencies
        return res
    def __set_name__(self, cls, name):
        self._vname = f'_{cls.__name__}__{name}_v'
        for o in self._ops: o.set_name(cls, name)
        self._set_true_value.register(cls, name, self)
        super().__set_name__(cls, name)
    def __get__(self, obj, cls=None):
        if obj is None: return self
        return getattr(obj, self._vname)

class Calc(Stat):
    """計算値"""
    def __init__(self, f, *a, **ka):
        self.func = f ; self.args = a
        self.kwargs = ka
    @property
    def _dependencies(self):
        res = set()
        for o in list(self.args) + list(self.kwargs.values()):
            if isinstance(o, StatBase):
                if o._has_name: res |= {o._name}
                else: res |= o._dependencies
        return res
    def __get__(self, obj, cls=None):
        if obj is None: return self
        func = getval(self.func, obj, cls)
        if self.func in rjoins:
            args = [getval(a, obj, cls) for a in self.args[::-1]][::-1]
        else:
            args = [getval(a, obj, cls) for a in self.args]
        ka = {k:getval(v, obj, cls) for k, v in self.kwargs.items()}
        return func(*args, **ka)
    def __repr__(self):
        if self._has_name: return self._name
        return f'{self.func.__name__}({", ".join(a for a in self.args)})'


