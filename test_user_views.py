"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Like

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        Like.query.delete()
        Follows.query.delete()
        Message.query.delete()
        User.query.delete()

        db.session.commit()

        self.client = app.test_client()

        testuser1 = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        testuser1.id = 111
        self.testuser1_id = 111
        testuser2 = User.signup(username="testuser2",
                                    email="test@test2.com",
                                    password="testuser2",
                                    image_url=None)
        testuser2.id = 222
        self.testuser2_id = 222
        db.session.add_all([testuser1, testuser2])
        db.session.commit()

        test_message_u1 = Message(text='test message from user 1', user_id=111)
        test_message_u1.id = 11
        self.test_message_u1_id = 11
        test_message_u2 = Message(text='test message from user 2', user_id=222)
        test_message_u2.id = 22
        self.test_message_u2_id = 22

        self.new_follow = Follows(user_being_followed_id=111, user_following_id=222)

        db.session.add_all([test_message_u1, test_message_u2, self.new_follow])
        db.session.commit()

    
    def tearDown(self):
        """Get rid of any fouled transactions"""
        db.session.rollback()

    def test_list_users(self):
        """Test get request to /users - checks if html shows test users"""
        with self.client as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser</p>", html)
            self.assertIn("testuser2</p>", html)

    def test_users_show(self):
        """Test get request to /users/{user_id} - checks if html includes user details"""
        with self.client as client:
            resp = client.get(f'/users/{self.testuser1_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser</a>", html)

    def test_non_existing_users_show(self):
        """Test get request to non-existing user page - checks if 404 is returned"""
        with self.client as client:
            resp = client.get('/users/999999999', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)

    def test_show_following(self):
        """Test get request to following page. Checks HTML for users that are being followed."""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id
            resp = client.get(f'/users/{self.testuser2_id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser</p>', html)

    def test_show_following_as_wrong_user(self):
        """Test get request to following page. Checks HTML for users that are being followed. 
        If unauthorized, returns redirect and shows flash message. """

        with self.client as client:
            resp = client.get(f'/users/{self.testuser1_id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_show_followers(self):
        """Test get request to followers page. Checks HTML for users that following the user."""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1_id
            resp = client.get(f'/users/{self.testuser1_id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser2</p>', html)

    def test_show_followers_as_wrong_user(self):
        """Test get request to followers page. Checks HTML for users that following the user. 
        If unauthorized, returns redirect and shows flash message. """

        with self.client as client:
            resp = client.get(f'/users/{self.testuser1_id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_add_follow(self):
        """Test if new followed user is added to following list"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1_id
            resp = client.post(f'/users/follow/{self.testuser2_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser2</p>', html)

    def test_unauthorized_add_follow(self):
        """Test if logged out users cannot follow users and are given a unauthorized message"""

        with self.client as client:
            resp = client.post(f'/users/follow/{self.testuser2_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_stop_follow(self):
        """Test if followed user is deleted from following list"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id
            resp = client.post(f'/users/stop-following/{self.testuser1_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('testuser</p>', html)

    def test_unauthorized_stop_follow(self):
        """Test if new followed user is added to following list"""

        with self.client as client:
            resp = client.post(f'/users/stop-following/{self.testuser1_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_update_profile(self):
        """Test if html is updated with new user details"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id
            resp = client.post('/users/profile', data={"bio": "i am a new bio"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('i am a new bio', html)

    def test_unauthorized_update_profile(self):
        """Test if html is updated with new user details"""

        with self.client as client:
            resp = client.post('/users/profile', data={"bio": "i am a new bio"}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            breakpoint()
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_delete_profile(self):
        """Test if user is deleted from post route"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id
            resp = client.post('/users/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # self.assertRaises(IntegrityError)

    # def test_unauthorized_delete_profile(self):
    #     """Test if user is not deleted from post route if unauthorized"""

    #     with self.client as client:
    #         resp = client.post('/users/profile', data={"bio": "i am a new bio"}, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Access unauthorized', html)

#delete_user(): post --> '/users/delete'
    #if not authorized, returns redirect ('/') and flashes 'access unauthorized'
    #logs out --> check for the session deletion
    #return redirect to /signup
    #user should not exist in the database