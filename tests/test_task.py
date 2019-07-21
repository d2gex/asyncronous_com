import pytest

from asyncronous_com.task import Task
from unittest.mock import patch, call


def test_run():

    app = Task()
    with patch('time.sleep') as mock_sleep:
        result = app([(2, 0.5), (3, 1), (4, 0)])
    assert result == 9
    assert mock_sleep.call_count == 3
    assert all(_call in mock_sleep.call_args_list for _call in (call(0.5), call(1.0), call(0.5)))

    with pytest.raises(ValueError):
        app([('Not integer', 0.5)])

    with pytest.raises(ValueError):
        app([(2, 'Not float')])
