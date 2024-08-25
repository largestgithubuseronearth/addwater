# TODO
import pytest

from addwater.components.online import OnlineManager

test_manager = OnlineManager(themeurl="www.example.com")

def test_is_update_available():
    assert test_manager._is_update_available(45, 60) == True
    assert test_manager.__is_update_available(90, 10) == False
    with pytest.raises(ValueError):
        test_manager._is_update_available("meat", 50)
        test_manager._is_update_available(42958, "a")
        test_manager._is_update_available(4.0, 235)
        test_manager._is_update_available(4, 9.0)
        test_manager._is_update_available(4, 9.7)
        test_manager._is_update_available([4,79])

    assert test_manager.is_update_available(398, 398) == False
