
from .bases import (
    StatAct, STATS, SVAL, VALUELIKE,
    getval, StatEffect, HasStatus)
from .stats import Stat, StatBase

from typing import Self, Any

class Buff(HasStatus):
    """## 各ステータス値へのバフを適用する
    サブクラスで実装したバフステータスは対象となるゲームオブジェクトのステータス値に効果を与えます
    ### 例
    ```python
    from game_status import *

    # バフの定義
    class Poison(buff.Buff):
        effect = Value(arg(default=1.)) # 効果倍率
        duration = Point(arg(), turn(-1)) # 効果時間(1ターンに1減少)

        # 効果
        HP = buff.Add(-effect) # 1ターンにHPを効果倍率分減少する

        # 終了条件(オーバーライドしなければ1ターンのみのバフになります)
        @property
        def is_disabled(self): return self.effect < 0
    
    # 動作
    class PlayerStat(GameObject):
        HP = Point(arg(default=100), minim(0), maxim(100))
    
    player = PlayerStat()
    player.buffs.append(Poison(duration=10))
    for t in range(10):
        assert player.HP == 100 - t
        player.turn()
    
    assert player.HP == 90
    assert len(player.buffs) == 0

    ```"""
    def turn(self, stat:STATS):
        for d in dir(self): self.act(d, stat)
    @property
    def is_disabled(self) -> bool: return True
    effect = StatAct()
    act = StatAct()


# バフステータス
class ActiveBuffStatus(Stat): pass
class Add(ActiveBuffStatus):
    ''' ## 加算バフ
    
    '''
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
