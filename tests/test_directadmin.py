from betamax import Betamax
from requests import Session
import os
import pytest
import server_check

with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'


class TestDirectAdmin:

    def setUp(self):

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
        self.setUp()
        from server_check import directadmin
        assert 'OK' in directadmin.test_mysql_connection()

    def test_01_create_random_domain(self):
        self.setUp()
        from server_check import directadmin

        with Betamax(self.session).use_cassette('create_random_domain'):
            self.domain, self.user, self.password = directadmin.create_random_domain('admin', 'Ohrah6Ni!', self.session)
            print "User: %s Password: %s" % (self.user, self.password)
            assert (self.user in self.domain and self.user != "" and self.password != "")  # 6-char username should be in domain.nl

    def test_02_validPassword(self):
        from server_check import directadmin
        assert directadmin.validPassword('Aa12bcC') == True
        assert directadmin.validPassword('abc') == False

    #def test_03_enable_spamassassin(self):
    #    from server_check import directadmin
    #    with Betamax(self.session).use_cassette('enable_spamassassin'):
    #        print "User: %s Password: %s" % (self.user, self.password)
    #        self.assertTrue(directadmin.enable_spamassassin(
    #            'admin', 'Ohrah6Ni!', self.domain, self.session))

    #def test_04_remove_account(self):
    #    from server_check import directadmin
    #    with Betamax(self.session).use_cassette('remove_account'):
    #        self.assertTrue(directadmin.remove_account('admin', 'Ohrah6Ni!', self.user, self.session))
