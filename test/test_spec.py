
import pytest
from game_status import *
from game_status import buff

@pytest.fixture
@pytest.mark.xfail(
    raises=(NameError, ModuleNotFoundError),
    reason="テストに必要な依存関係がまだ作成されていません")
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


@pytest.fixture
@pytest.mark.xfail(
    raises=(NameError, ModuleNotFoundError),
    reason="テストに必要な依存関係がまだ作成されていません")
def MyBuff():
    class MyBuff(Buff):
        effect = Value(arg(default=1.))
        duration = Point(
            arg(default=10.),
            per_turn(-1))

        HP = buff.Add(effect)
        MP = buff.Add(-effect)
        
        @property
        def is_disabled(self):
            return self.duration < 0
    return MyBuff


def test_defin_Buff(MyBuff):
    ins = MyBuff()


