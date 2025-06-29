from .bases import StatEffect, StatAct, getval, StatBase, getdep

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
        self.gainexp.register(cls, name, self)
        self.gainpot.register(cls, name, self)

class buffed(StatEffect):
    """バフを適用"""
    @StatAct.actmethod
    def addbuff(self, obj, buff):
        if not hasattr(obj, "buffs"):
            setattr(obj, "buffs", [])
        getattr(obj, "buffs").append(buff)
    def set_name(self, cls, name):
        self._name = name
        self.addbuff.register(cls, name, self)
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
    @StatAct.actmethod
    def _get_dependency(self, obj):
        if isinstance(self._attr, StatBase):
            return {self._attr}
        return set()
    def set_name(self, cls, name):
        self._get_dependency.register(cls, name, self)
    def get(self, val, obj, cls):
        return val + getval(self._attr, obj, cls)
    @property
    def dependencies(self): return getdep(self._attr)

class maxim(StatEffect):
    """最大値"""
    def __init__(self, m): self._m = m
    def get(self, val, obj, cls):
        return min(val, getval(self._m, obj, cls))
    @property
    def dependencies(self): return getdep(self._m)

class minim(StatEffect):
    """最小値"""
    def __init__(self, m): self._m = m
    def get(self, val, obj, cls):
        return max(val, getval(self._m, obj, cls))
    @property
    def dependencies(self): return getdep(self._m)

class default(StatEffect):
    """基本値を設定する"""
    def __init__(self, v): self.__val = v
    @StatAct.actmethod
    def _default_init(self, obj):
        obj._set_true_value(self.__name,
                            getval(self.__val, obj, self.__cls))
    def set_name(self, cls, name):
        self.__name = name
        self.__cls = cls
        self._default_init.register(cls, name, self)
    @property
    def dependencies(self): return getdep(self.__val)

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
        self._turn_act.register(cls, name, self)
    @property
    def dependencies(self): return getdep(self._val)

class arg(StatEffect):
    """コンストラクタの引数で設定できる"""
    def __init__(self, default=None):
        self.__default = default
    @StatAct.actmethod
    def _init(self, obj, value):
        obj._set_true_value(self.__name,
                            value)
    @StatAct.actmethod
    def _default_init(self, obj):
        obj._set_true_value(self.__name,
                            getval(self.__default, obj, self.__cls))
    def set_name(self, cls, name):
        self.__name = name
        self.__cls = cls
        self._init.register(cls, name, self)
        self._default_init.register(cls, name, self)
    @property
    def dependencies(self): return getdep(self.__default)
