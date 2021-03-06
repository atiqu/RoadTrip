import os
from roadtrip import roadtrip
import unittest
import tempfile

class RoadtripTestCase(unittest.TestCase):

    #helpers
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)


    def setUp(self):
        self.db_fd, roadtrip.app.config['DATABASE'] = tempfile.mkstemp()
        roadtrip.app.testing = True
        self.app = roadtrip.app.test_client()
        with roadtrip.app.app_context():
            roadtrip.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(roadtrip.app.config['DATABASE'])

    #tests
    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'There are no activities' in rv.data

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert b'You were logged in' in rv.data
        rv = self.logout()
        assert b'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert b'Invalid username' in rv.data
        rv = self.login('admin', 'defaultx')
        assert b'Invalid password' in rv.data

    def test_adding_activity(self):
        self.login('admin', 'default')
        rv = self.app.post(
            '/add_activity',
            data=dict(
                title="111",
                text="222",
                start_time = "333",
                end_time = "444"
            ),
            follow_redirects=True)
        assert b'111' in rv.data
        assert b'222' in rv.data
        assert b'333' in rv.data
        assert b'444' in rv.data



if __name__ == '__main__':
    unittest.main()
