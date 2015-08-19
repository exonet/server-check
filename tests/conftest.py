import pytest
import collections

DomainInfo = collections.namedtuple('DomainInfo', 'domain, user, password')


@pytest.fixture(scope='module')
def domain():
    return DomainInfo('foobar.nl', 'foobar', '123456')
