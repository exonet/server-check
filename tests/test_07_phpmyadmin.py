import pytest
import collections
from server_check import exceptions
from server_check import phpmyadmin


def test_00_test_phpmyadmin(session):
    getreturn = collections.namedtuple('getreturn', 'text, status_code')
    getreturn.text = 'User: da_admin@localhost'
    getreturn.status_code = 200
    sessionSpec = {'get.return_value': getreturn}
    session.configure_mock(**sessionSpec)

    assert 'Logged in and authenticated' in phpmyadmin.test_phpmyadmin(session=session)

    # Fake invalid return
    getreturn.text = 'test'
    getreturn.status_code = 500
    sessionSpec = {'get.return_value': getreturn}
    session.configure_mock(**sessionSpec)
    with pytest.raises(exceptions.TestException) as err:
        phpmyadmin.test_phpmyadmin(session=session)
    assert 'Unable to log in' in err.value.message
