import pytest
import collections
from server_check import exceptions
from server_check import roundcube


def test_00_test_roundcube(session):
    getreturn = collections.namedtuple('getreturn', 'text, status_code')
    getreturn.text = 'Roundcube Webmail Login'
    getreturn.status_code = 200
    sessionSpec = {'get.return_value': getreturn}
    session.configure_mock(**sessionSpec)

    assert 'Roundcube accessible' in roundcube.test_roundcube(session=session)

    # Fake invalid return
    getreturn.text = 'test'
    getreturn.status_code = 500
    sessionSpec = {'get.return_value': getreturn}
    session.configure_mock(**sessionSpec)
    with pytest.raises(exceptions.TestException) as err:
        roundcube.test_roundcube(session=session)
    assert 'not found at' in err.value.message
