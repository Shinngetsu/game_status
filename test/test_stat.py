
import pytest
from game_status import *

@pytest.mark.timeout(10)
def test_defin_GameObjWithValue_NoErr():
    class Status(GameObject):
        STR = Value()
    ins = Status()

@pytest.mark.timeout(10)
def test_defin_GameObjWithPoint_NoErr():
    class Status(GameObject):
        HP = Point(arg(100))
    ins = Status()

