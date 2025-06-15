from bases import StatEffect, StatAct, getval

class grow(StatEffect):
    """基礎値にレベルアップ概念を導入する"""
    def __init__(self, freq=1.): self.freq = freq
    @StatAct.actmethod
    def gainexp(self, obj, exp):
        setattr(obj, self._vname, getattr(obj, self._vname) + exp*self.freq)
        setattr(obj, self._pname, getattr(obj, self._pname) - exp)
    @StatAct.actmethod
    def gainpot(self, obj, pot):
        setattr(obj, self._pname, getattr(obj, self._pname) + pot)
    def set_name(self, cls, name):
        self._vname = f'_{cls.__name__}__{name}_v'
        self._pname = f'_{cls.__name__}__{name}_p'
        self.gainexp.register(cls)
        self.gainpot.register(cls)

class buff(StatEffect):
    """バフを適用"""
    @StatAct.actmethod
    def addbuff(self, obj, buff):
        if not hasattr(obj, "buffs"):
            setattr(obj, "buffs", [])
        getattr(obj, "buffs").append(buff)
    def set_name(self, cls, name):
        self._name = name
        self.addbuff.register(cls)
    def get(self, val, obj, cls):
        if hasattr(obj, "buffs"):
            buffs = getattr(obj, "buffs")
        else:
            buffs = []
        for b in buffs:
            val = b.effect(obj, self._name, val)
        return val

class bonus(StatEffect):
    """基礎値に加算"""
    def __init__(self, attr): self._attr = attr
    def get(self, val, obj, cls):
        return val + getval(self._attr, obj, cls)

class maxim(StatEffect):
    """最大値"""
    def __init__(self, m): self._m = m
    def get(self, val, obj, cls):
        return min(val, getval(self._m, obj, cls))

class minim(StatEffect):
    """最小値"""
    def __init__(self, m): self._m = m
    def get(self, val, obj, cls):
        return max(val, getval(self._m, obj, cls))

class default(StatEffect):
    """Noneの場合は置き換える"""
    def __init__(self, v): self._val = v
    def get(self, val, obj, cls):
        return getval(self._val, obj, cls) if val is None else val

class turn(StatEffect):
    """ターンごとに加算される値"""
    def __init__(self, v): self._val = v
    @StatAct.actmethod
    def _turn_act(self, obj):
        setattr(obj, self._name,
            getattr(obj, self._name)
          + getval(self._val, obj, type(obj)))
    def set_name(self, cls, name):
        self._name = name
        self._turn_act.register(cls)
