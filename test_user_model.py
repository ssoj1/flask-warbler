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

TEST_USER_1 = User(
    email="test@test1.com",
    username="testuser1",
    password="HASHED_PASSWORD111"
    )

TEST_USER_2 = User(
    email="test2@test2.com",
    username="testuser2",
    password="HASHED_PASSWORD222"
    )

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        
        user = TEST_USER_1
        db.session.add(user)
        db.session.commit()

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
        breakpoint()
        self.assertEqual(user.__repr__(), 
            (f"<User #{user.id}: {user.username}, {user.email}>"))

# Does the repr method work as expected?
# return f"<User #{self.id}: {self.username}, {self.email}>"
# def test_create_dessert(self):
#     with app.test_client() as client:
#         resp = client.post(
#             "/desserts", json={
#                 "name": "TestCake2",
#                 "calories": 20,
#             })
#         self.assertEqual(resp.status_code, 201)

#         # don't know what ID it will be, so test then remove
#         self.assertIsInstance(resp.json['dessert']['id'], int)
#         data = resp.json.copy()
#         del data['dessert']['id']

#         self.assertEqual(
#             data,
#             {"dessert": {'name': 'TestCake2', 'calories': 20}})

#         self.assertEqual(Dessert.query.count(), 2)
# Does is_following successfully detect when user1 is following user2?
# Does is_following successfully detect when user1 is not following user2?
# Does is_followed_by successfully detect when user1 is followed by user2?
# Does is_followed_by successfully detect when user1 is not followed by user2?
# Does User.signup successfully create a new user given valid credentials?
# Does User.signup fail to create a new user if any of the validations (eg uniqueness, non-nullable fields) fail?
# Does User.authenticate successfully return a user when given a valid username and password?
# Does User.authenticate fail to return a user when the username is invalid?
# Does User.authenticate fail to return a user when the password is invalid?