
import pytest
from game_status import *

def test_defin_GameObjWithValue_NoErr():
    class Status(GameObject):
        STR = Value()
    ins = Status()

def test_defin_GameObjWithPoint_NoErr():
    class Status(GameObject):
        HP = Point(arg(100))
    ins = Status()

