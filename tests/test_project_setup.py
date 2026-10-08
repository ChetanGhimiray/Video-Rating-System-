import os
import unittest
from pathlib import Path

from app import app
from database import db


class ProjectSetupTests(unittest.TestCase):
    def test_sqlite_path_is_absolute(self):
        self.assertTrue(Path(db.SQLITE_PATH).is_absolute())

    def test_login_page_is_available(self):
        client = app.test_client()
        response = client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Login', response.get_data(as_text=True))

    def test_home_page_includes_static_css_link(self):
        client = app.test_client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/static/css/style.css', response.get_data(as_text=True))

    def test_user_dashboard_requires_login(self):
        client = app.test_client()
        response = client.get('/overall')
        self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main()
