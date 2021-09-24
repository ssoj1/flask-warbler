"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

        # #self.new_follow = Follows(user_being_followed_id=111, user_following_id=222)

        db.session.add_all([test_message_u1, test_message_u2])
        db.session.commit()

    def tearDown(self):
        """Get rid of any fouled transactions"""
        db.session.rollback()

    def test_message_add(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1_id

            # Now, that session setting is saved, so we can have
            # the rest of our test
            Message.query.delete()
            db.session.commit()

            resp = client.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1_id

            Message.query.delete()
            db.session.commit()

            resp = client.post("/messages/new", data={"text": ""})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            msg = Message.query.all()
            self.assertEqual(msg, [])
            self.assertIn("Add my message", html)
    
    def test_message_add_while_logged_out(self):
        """ Test that a user can't add a message while logged out """

        with self.client as client:

            Message.query.delete()
            db.session.commit()

            resp = client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            msg = Message.query.all()
            self.assertEqual(msg, [])
            self.assertIn("Access unauthorized", html)


    def test_message_show(self):
        """Testing that the correct message shows during get request, and whether
        message like button is toggled when liked"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id

            resp = client.get(f"/messages/{self.test_message_u1_id}")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test message from user 1', html)

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id

            resp = client.post(f"/messages/{self.test_message_u1_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'http://localhost/messages/{self.test_message_u1_id}')


    def test_message_destroy(self):
        """ Can a user delete their own message and check that the message 
        doesn't appear after deleted"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1_id

            resp = client.post(f'/messages/{self.test_message_u1_id}/delete', 
                                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('test message from user 1', html)


    def test_delete_message_of_other_user(self):
        """Test that a user can't delete another user's message """

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id

            resp = client.post(f'/messages/{self.test_message_u1_id}/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 
                            f"http://localhost/users/{self.testuser2_id}")

    def test_like_message_from_user_page(self):
        """Test wether redirect to /users/user_id occurs after liking/unliking 
        a message"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2_id

            resp = client.post(f'/users/{self.testuser1_id}/{self.test_message_u1_id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f"http://localhost/users/{self.testuser1_id}")

    def test_show_liked_messages(self):
        """Test that a liked messages appear properly and unliked messages
        do not appear"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1_id

            user_1 = User.query.get(self.testuser1_id)

            user_1.like_or_unlike_message(self.test_message_u2_id)

            resp = client.get(f'/users/{self.testuser1_id}/likes')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test message from user 2', html)
            self.assertNotIn('test message from user 1', html)
