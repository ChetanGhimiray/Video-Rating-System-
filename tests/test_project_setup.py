import os
import unittest
from pathlib import Path

from app import app
from database import db


class ProjectSetupTests(unittest.TestCase):
    def test_sqlite_path_is_absolute(self):
        self.assertTrue(Path(db.SQLITE_PATH).is_absolute())

    def test_home_page_includes_static_css_link(self):
        client = app.test_client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/static/css/style.css', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
