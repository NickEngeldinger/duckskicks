import os
import duckskicks
import unittest
import tempfile

class DuckskicksTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, duckskicks.app.config['DATABASE'] = tempfile.mkstemp()
        duckskicks.app.config['TESTING'] = True
        self.app = duckskicks.app.test_client()
        duckskicks.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(duckskicks.app.config['DATABASE'])

    def test_empty_db(self):
		rv = self.app.get('/sneakers')
		assert 'No sneakers here so far' in rv.data

    def login(self, username, password):
		return self.app.post('/login', data=dict(
			username=username,
			password=password
		), follow_redirects=True)

    def logout(self):
    	return self.app.get('/logout', 	follow_redirects=True)

    def test_login_logout(self):
    	rv = self.login('admin', 'default')
    	assert 'You were logged in' in rv.data
    	rv = self.logout()
    	assert 'You were logged out' in rv.data
    	rv = self.login('adminTaco', 'default')
    	assert 'Invalid username' in rv.data
    	rv = self.login('admin', 'defaultTaco')
    	assert 'Invalid password' in rv.data

    def test_add_sneaker_login(self):
    	rv = self.logout()
    	rv = self.app.get('/add_sneaker')
    	#assert 'You must be logged in' in rv.data
    	rv = self.login('admin', 'default')
    	assert 'Add Sneaker' in rv.data



if __name__ == '__main__':
    unittest.main()