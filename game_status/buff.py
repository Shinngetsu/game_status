
import abc
from .bases import (
    StatAct, STATS, SVAL, VALUELIKE,
    getval, StatEffect, HasStatus)
from .stats import Stat, StatBase

from typing import Self, Any

class Buff(HasStatus):
    """## 各ステータス値へのバフを適用する
    サブクラスで実装したバフステータスは、
    対象となるゲームオブジェクトのステータス値に効果を与える"""
    def turn(self, stat:STATS):
        for d in dir(self): self.act(d, stat)
    @property
    def is_disabled(self) -> bool: return True
    effect = StatAct()
    act = StatAct()


# バフステータス
class ActiveBuffStatus(Stat): pass
class Add(ActiveBuffStatus):
    @StatAct.actmethod
    def act(self, obj, stat):
        setattr(stat, self.__name,
            getattr(stat, self.__name) +
            getval(self.__stat, obj, self.__cls))
    def __init__(self, stat):
        self.__stat = stat
    def __set_name__(self, cls, name):
        self.__name = name
        self.__cls = cls
        self.act.register(cls, name, self)
    def __get__(self, obj, cls = None):
        if obj is None: return self
        return getval(self.__stat, obj, cls)

class Disable(ActiveBuffStatus):
    @StatAct.actmethod
    def act(self, obj, stat):
        if getval(self.__stat, obj, self.__cls):
            stat.buffs.remove(obj)
    def __init__(self, stat):
        self.__stat = stat
    def __set_name__(self, cls, name):
        self.__cls = cls
        self.act.register(cls, name, self)
    def __get__(self, obj, cls = None):
        if obj is None: return self
        return getval(self.__stat, obj, cls)
