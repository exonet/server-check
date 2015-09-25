import pytest
import collections
from server_check import exceptions
from server_check import phpmyadmin
from mock import patch, mock_open


def test_00_test_phpmyadmin():
    mocked_open = mock_open(read_data='user=foo\npasswd=bar\n')
    with patch('requests.get') as get, patch('__builtin__.open', mocked_open):
        getreturn = collections.namedtuple('getreturn', 'text, status_code')
        getreturn.text = 'User: foo@localhost'
        getreturn.status_code = 200
        get.return_value = getreturn

        assert 'Logged in and authenticated' in phpmyadmin.test_phpmyadmin()

        # Fake invalid return.
        getreturn.text = 'test'
        getreturn.status_code = 500
        get.return_value = getreturn
        with pytest.raises(exceptions.TestException) as err:
            phpmyadmin.test_phpmyadmin()
        assert 'Unable to log in' in err.value.message
