import pytest
import collections
from server_check import exceptions
from server_check import roundcube
from mock import patch


def test_00_test_roundcube():
    with patch('requests.get') as get:
        getreturn = collections.namedtuple('getreturn', 'text, status_code')
        getreturn.text = 'Roundcube Webmail Login'
        getreturn.status_code = 200
        get.return_value = getreturn

        assert 'Roundcube accessible' in roundcube.test_roundcube()

        # Fake invalid return.
        getreturn.text = 'test'
        getreturn.status_code = 500
        get.return_value = getreturn
        with pytest.raises(exceptions.TestException) as err:
            roundcube.test_roundcube()
        assert 'not found at' in err.value.message
