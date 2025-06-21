
import pytest
from game_status import *

@pytest.fixture
def Status():
    class Status(GameObject):
        STR = Value(arg(0), minim(0), grow(), buffed())
        maxHP = (STR + 1) * 10
        HP = Point(arg(maxHP), minim(0), maxim(maxHP))
    return Status


def test_defin_Status(Status):
    ins = Status(STR = 2)
    assert ins.maxHP == 30
    assert ins.HP == ins.maxHP


@pytest.fixture
def MyBuff():
    class MyBuff(buff.Buff):
        effect = Value(arg(default=1.))
        duration = Point(
            arg(default=10.),
            turn(-1))

        HP = buff.Add(effect)
        MP = buff.Add(-effect)

        @property
        def is_disabled(self):
            return self.duration < 0
        
    return MyBuff


def test_defin_Buff(MyBuff):
    ins = MyBuff()


