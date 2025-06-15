# coding: utf-8

from bases import StatEffect, StatBase, STATS, SVAL, getval
import operator as op
from mathobj import rjoins, MathObj

# 属性
class Stat(StatBase[STATS, SVAL], MathObj):
    """ステータス値のディスクリプタ"""
    def _unary(self, uf): return Calc(uf, self)
    def _binary(self, bf, b): return Calc(bf, self, b)
    def _rbinary(self, bf, a): return Calc(bf, a, self)
    def __getattr__(self, k): return Calc(getattr, self, k)
    def __getitem__(self, k): return Calc(op.getitem, self, k)
    def __call__(self, *a, **ka): return Calc(self, *a, **ka)

class Value(Stat):
    """筋力などの固定値"""
    def __init__(self, *ops:StatEffect):
        self._ops = ops
    def __set_name__(self, cls, name):
        self._vname = f'_{cls.__name__}__{name}_v'
        for o in self._ops: o.set_name(cls, name)
    def __get__(self, obj, cls=None):
        if obj is None: return self
        res = None
        if hasattr(obj, self._vname):
            res = getattr(obj, self._vname)
        for b in self._ops: res = b.get(res, obj, cls)
        return res

class Point(Stat):
    """HPなどの流動的な値"""
    def __init__(self, *ops:StatEffect, default=None):
        self._ops = ops ; self._def = default
    def __set_name__(self, cls, name):
        self._name = name
        self._vname = f'_{cls.__name__}__{name}_v'
        for o in self._ops: o.set_name(cls, name)
    def __get__(self, obj, cls=None):
        if obj is None: return self
        if hasattr(obj, self._vname):
            return getattr(obj, self._vname)
        return getval(self._def, obj, cls)
    def __set__(self, obj, val):
        for b in self._ops: val = b.get(val, obj, type(obj))
        setattr(obj, self._vname, val)

class Calc(Stat):
    """計算値"""
    def __init__(self, f, *a): self.func = f ; self.args = a
    def _binary(self, bf, b):
        if bf is self.func:
            return Calc(bf, *self.args, b) 
        return Calc(bf, self, b)
    def _rbinary(self, bf, a):
        if bf is self.func:
            return Calc(bf, a, *self.args) 
        return Calc(bf, a, self)
    def __get__(self, obj, cls=None):
        if obj is None: return self
        if self.func in rjoins:
            args = [getval(a, obj, cls) for a in self.args[::-1]]
            val = args[0]
            for a in args[1:]:
                val = self.func(a, val)
        else:
            args = [getval(a, obj, cls) for a in self.args]
            val = args[0]
            for a in args[1:]:
                val = self.func(val, a)
        return val


