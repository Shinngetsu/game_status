
import pytest
from game_status import *

@pytest.fixture
def Status():
    class Status(GameObject):
        STR = Value(arg(0), minim(0), grow(), buff())
        maxHP = (STR + 1) * 10
        HP = Point(minim(0), maxim(maxHP), default=arg(maxHP))
    return Status


def test_defin_Status(Status):
    ins = Status(STR = 2)
    assert ins.maxHP == 30
    assert ins.HP == ins.maxHP


def test_defin_Buff():
    class MyBuff(Buff):
        effect = Value(arg(default=1.))
        duration = Point(
            arg(default=10.),
            per_turn(-1))

        HP = buff.Recover(effect)
        MP = buff.Damage(effect)
        
        @property
        def is_disabled(self):
            return self.duration < 0
    


