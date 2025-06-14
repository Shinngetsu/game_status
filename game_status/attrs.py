# coding: utf-8
from mathobj import rjoins
from bases import AttrBase, AttrEffect, getval
import operator as op

### attr ###
class attr[STATS, SVAL](AttrBase[STATS, SVAL]):
    """ステータス値のディスクリプタ"""
    def _unary(self, uf): return calc(uf, self)
    def _binary(self, bf, b): return calc(bf, self, b)
    def _rbinary(self, bf, a): return calc(bf, a, self)
    def __getattr__(self, k): return calc(getattr, self, k)
    def __getitem__(self, k): return calc(op.getitem, self, k)
    def __call__(self, *a, **ka): return calc(self, *a, **ka)

class stat(attr):
    """基礎値"""
    def __init__(self, *ops:AttrEffect): self._ops = ops
    def __set_name__(self, cls, name):
        self._vname = f'_{cls.__name__}__{name}_v'
        for o in self._ops: o.set_name(cls, name)
    def __get__(self, obj, cls=None):
        if obj is None: return self
        res = getattr(obj, self._vname) if hasattr(obj, self._vname) else None
        for b in self._ops: res = b.get(obj, cls, res)
        return res

class point(attr):
    """代入可能な値"""
    def __init__(self, *ops:AttrEffect, default=None):
        self._ops = ops ; self._def = default
    def __set_name__(self, cls, name):
        self._name = name
        self._vname = f'_{cls.__name__}__{name}_v'
        for o in self._ops: o.set_name(cls, name)
    def __get__(self, obj, cls=None):
        if obj is None: return self
        if hasattr(obj, self._vname): return getattr(obj, self._vname)
        return getval(obj, cls, self._def)
    def __set__(self, obj, val):
        for b in self._ops: val = b.get(obj, type(obj), val)
        setattr(obj, self._vname, val)

class calc(attr):
    """計算値"""
    def __init__(self, f, *a): self.func = f ; self.args = a
    def _binary(self, bf, b):
        if bf is self.func: return calc(bf, *self.args, b) 
        return calc(bf, self, b)
    def _rbinary(self, bf, a):
        if bf is self.func: return calc(bf, a, *self.args) 
        return calc(bf, a, self)
    def __get__(self, obj, cls=None):
        if obj is None: return self
        if self.func in rjoins:
            args = [getval(obj, cls, a) for a in self.args[::-1]]
            val = args[0]
            for a in args[1:]: val = self.func(a, val)
        else:
            args = [getval(obj, cls, a) for a in self.args]
            val = args[0]
            for a in args[1:]: val = self.func(val, a)
        return val


