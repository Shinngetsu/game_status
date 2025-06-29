
import pytest, time
from game_status import *

@pytest.mark.timeout(10)
def test_defin_Status():
    class Status(GameObject):
        STR = Value(arg(0), minim(0), grow(), buffed())
        maxHP = (STR + 1) * 10
        HP = Point(arg(maxHP), minim(0), maxim(maxHP))
    ins = Status(STR = 2)
    assert ins.maxHP == 30
    assert ins.HP == ins.maxHP


@pytest.mark.timeout(10)
def test_defin_Buff():
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
    ins = MyBuff()


@pytest.mark.timeout(10)
def test_defin_Apple():
    class Apple(GameObject):
        freshness = Value(arg(100), turn(-1))
        price = Value(default(20 * (freshness > 0)))
        on_eat_HpRecover = (
            (freshness >= 50) * 10 +
            (freshness >= 0 ) * 20 +
            -10)

        name = "りんご" + "（腐敗）" * (freshness < 0)
        description = (
            "みずみずしい新鮮なりんご。" * (freshness >= 50) +
            "ちょっとしんなりし始めているりんご。" * (50 > freshness >= 0) +
            "ハエがたかり異臭を放つりんご。" * (freshness < 0) +
            "食べると体力が" +
            Calc(str, on_eat_HpRecover) + "ポイント" +
                "減少" * (on_eat_HpRecover <  0) +
                "回復" * (on_eat_HpRecover >= 0) + "する。")

        @property
        def is_rotten(self): return self.freshness < 0

        def __repr__(self):
            return f"{self.__class__.__name__}({self.freshness=}, {self.price=})"
    ins = Apple(freshness=100)
    assert ins.is_rotten == False
    assert ins.name == "りんご"
    assert ins.description
