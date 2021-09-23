"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        Message.query.delete()
        Follows.query.delete()
        User.query.delete()

        self.client = app.test_client()
        
        test_user_1 = User(
            email="test@test1.com",
            username="testuser1",
            password="HASHED_PASSWORD111"
            )

        test_user_2 = User(
            email="test2@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD222"
            )

        db.session.add_all([test_user_1, test_user_2])
        db.session.commit()

        self.user_1 = User.query.filter(User.email=="test@test1.com").first()
        self.user_2 = User.query.filter(User.email=="test2@test2.com").first()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_user_repr(self):
        """Does the repr method return 
        f"<User #{self.id}: {self.username}, {self.email}>"""
    
        user = User.query.filter(User.email=="test@test1.com").first()

        self.assertEqual(user.__repr__(), 
            (f"<User #{user.id}: {user.username}, {user.email}>"))

    def test_is_following(self):
        """Does is_following correctly detect when a user is and is not
        following another user"""

        new_follow = Follows(user_being_followed_id = self.user_1.id, 
                            user_following_id = self.user_2.id)

        db.session.add(new_follow)
        db.session.commit()

        self.assertTrue(self.user_2.is_following(self.user_1))
        self.assertFalse(self.user_1.is_following(self.user_2))

    def test_is_followed_by(self):
        """Does is_follwed_by correctly detect when a user is and is not
        being followed by another user"""

        new_follow = Follows(user_being_followed_id = self.user_1.id, 
                            user_following_id = self.user_2.id)

        db.session.add(new_follow)
        db.session.commit()

        self.assertTrue(self.user_1.is_followed_by(self.user_2))
        self.assertFalse(self.user_2.is_followed_by(self.user_1))




# Does User.signup successfully create a new user given valid credentials?
# Does User.signup fail to create a new user if any of the validations (eg uniqueness, non-nullable fields) fail?
# Does User.authenticate successfully return a user when given a valid username and password?
# Does User.authenticate fail to return a user when the username is invalid?
# Does User.authenticate fail to return a user when the password is invalid?