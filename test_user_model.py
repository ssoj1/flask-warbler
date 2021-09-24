"""User model tests."""

# run these tests like:
#
#    python3 -m unittest test_user_model.py


import os
from unittest import TestCase

from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows, Like
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
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
    """Test user model and instance methods."""

    def setUp(self):
        """Create test client, add sample data."""

        Like.query.delete()
        Message.query.delete()
        Follows.query.delete()
        User.query.delete()
  
        self.client = app.test_client()
        hashed_pwd = bcrypt.generate_password_hash("HASHED_PASSWORD111",4).decode('UTF-8')
        test_user_1 = User(
            email="test@test1.com",
            username="testuser1",
            password=hashed_pwd
            )

        test_user_2 = User(
            email="test2@test2.com",
            username="testuser2",
            password=hashed_pwd
            )

        db.session.add_all([test_user_1, test_user_2])
        db.session.commit()

        self.user_1 = User.query.filter(User.email=="test@test1.com").first()
        self.user_2 = User.query.filter(User.email=="test2@test2.com").first()

    def tearDown(self):
        """Rollback fouled transactions from tests"""
        db.session.rollback()

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

    def test_user_signup(self):
        """Does User.signup class method create a new user instance
        with valid credentials"""

        user = User.signup(
            username="test_user_signup",
            email="test_user_signup@gmail.com",
            password="test_user_signup_pwd",
            image_url=".jpg"
        )

        db.session.commit()
        find_test_user = User.query.filter(User.username=="test_user_signup").first()
        self.assertTrue(find_test_user)
        self.assertEqual(find_test_user.email,"test_user_signup@gmail.com")

    def test_invalid_user_signup(self):
        """Does User.signup class method fail to create a new user with invalid inputs"""

        user_username = User.signup(
            username="testuser1",
            email="test_user_signup@gmail.com",
            password="test_user_signup_pwd",
            image_url=".jpg"
        )

        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        user_email = User.signup(
            username="test_user_signup",
            email="test@test1.com",
            password="test_user_signup_pwd",
            image_url=".jpg"
        )

        self.assertRaises(IntegrityError, db.session.commit)


    def test_user_authenticate(self):
        """Does User.authenticate class method return a user
        given a valid username & password"""

        user = User.authenticate(
            username="testuser1", 
            password="HASHED_PASSWORD111")
        self.assertTrue(isinstance(user, User))

        user_wrong_username = User.authenticate(
            username="not_the_username", 
            password="HASHED_PASSWORD111")
        self.assertFalse(user_wrong_username)

        user_wrong_pwd = User.authenticate(
            username="testuser1", 
            password="not_the_password")
        self.assertFalse(user_wrong_pwd)

    def test_like_or_unlike_message(self):
        """Does like_or_unlike_message properly like or unlike a message"""

        new_message = Message(text="Heyo", user_id=self.user_1.id)

        db.session.add(new_message)
        db.session.commit()
  
        message_id = new_message.id
        
        self.user_2.like_or_unlike_message(message_id)
        user_liking = Like.query.filter(Like.liked_message_id == message_id).first()

        self.assertTrue(user_liking.user_liking_id == self.user_2.id)

