from bases import AttrEffect, StatAct, getval

### AttrEffect ###
class grow(AttrEffect):
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

class buff(AttrEffect):
    """バフを適用"""
    def set_name(self, cls, name): self._name = name
    def get(self, obj, cls, val):
        for b in obj.buffs:
            val = b.effect(obj, self._name, val)
        return val

class bonus(AttrEffect):
    """基礎値に加算"""
    def __init__(self, attr): self._attr = attr
    def get(self, obj, cls, val):
        return val + getval(obj, cls, self._attr)

class maxim(AttrEffect):
    """最大値"""
    def __init__(self, m): self._m = m
    def get(self, obj, cls, val):
        return min(val, getval(obj, cls, self._m))

class minim(AttrEffect):
    """最小値"""
    def __init__(self, m): self._m = m
    def get(self, obj, cls, val):
        return max(val, getval(obj, cls, self._m))

class default(AttrEffect):
    """Noneの場合は置き換える"""
    def __init__(self, v): self._val = v
    def get(self, obj, cls, val):
        return getval(obj, cls, self._val) if val is None else val

class turn(AttrEffect):
    """ターンごとに加算される値"""
    def __init__(self, v): self._val = v
    @StatAct.actmethod
    def _turn_act(self, obj):
        setattr(obj, self._name,
            getattr(obj, self._name)
          + getval(obj, type(obj), self._val))
    def set_name(self, cls, name):
        self._name = name
        self._turn_act.register(cls)
