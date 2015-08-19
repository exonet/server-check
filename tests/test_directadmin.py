import unittest
from betamax import Betamax
from requests import Session
import os

with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'


class TestDirectAdmin(unittest.TestCase):

    def setUp(self):
        self.user = ""
        self.domain = ""
        self.password = ""

        # create cassettes dir
        if not os.path.exists('tests/fixtures/cassettes'):
            try:
                os.makedirs('tests/fixtures/cassettes')
            except StandardError, e:
                print e

        # create the mysql config file
        if not os.path.exists('/usr/local/directadmin/conf'):
            try:
                os.makedirs('/usr/local/directadmin/conf')
            except StandardError, e:
                print e

            # Write the credentials
            with open('/usr/local/directadmin/conf/mysql.conf', 'w') as fh:
                fh.write('user=root\n')
                fh.write('passwd=\n')

        self.session = Session()

    def test_00_mysql_connection(self):
        from server_check import directadmin
        self.assertIn('OK', directadmin.test_mysql_connection())

    def test_01_create_random_domain(self):
        from server_check import directadmin

        with Betamax(self.session).use_cassette('create_random_domain'):
            self.domain, self.user, self.password = directadmin.create_random_domain('admin', 'W8xXbar8!', self.session)
            self.assertIn(self.user, self.domain)  # 6-char username should be in domain.nl

    def test_02_validPassword(self):
        from server_check import directadmin
        self.assertTrue(directadmin.validPassword('Aa12bcC'))
        self.assertFalse(directadmin.validPassword('abc'))

    def test_03_enable_spamassassin(self):
        from server_check import directadmin
        with Betamax(self.session).use_cassette('enable_spamassassin'):
            self.assertTrue(directadmin.enable_spamassassin(
                self.user, self.password, self.domain, self.session))

    def test_04_remove_account(self):
        from server_check import directadmin
        with Betamax(self.session).use_cassette('create_random_domain'):
            self.assertTrue(directadmin.remove_account('admin', 'W8xXbar8!', self.user, self.session))
