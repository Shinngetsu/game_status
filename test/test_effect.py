
import pytest
from game_status import *

@pytest.fixture
def Status():
    class Status(GameObject):
        pass
    return Status

@pytest.mark.timeout(10)
def test_minim(Status):
    eff = minim(0)
    eff.set_name(Status, 'VALUE')
    ins = Status()
    
    assert eff.get(50, ins, Status) == 50
    assert eff.get(-10, ins, Status) == 0

@pytest.mark.timeout(10)
def test_maxim(Status):
    eff = maxim(100)
    eff.set_name(Status, 'VALUE')
    ins = Status()
    
    assert eff.get(50, ins, Status) == 50
    assert eff.get(110, ins, Status) == 100


