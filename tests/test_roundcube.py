from betamax import Betamax
from requests import Session
import pytest
from server_check import exceptions


with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'


@pytest.fixture(scope='session')
def session():
    return Session()


def test_00_test_roundcube(session):
    from server_check import roundcube
    with Betamax(session).use_cassette('test_roundcube'):
        assert 'Roundcube accessible' in roundcube.test_roundcube(session=session)
        with pytest.raises(exceptions.TestException) as err:
            roundcube.test_roundcube('http://localhost/not-roundcube/', session)
        assert 'not found at' in err.value.message
