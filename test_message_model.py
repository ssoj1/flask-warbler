"""Message model tests."""

# run these tests like:
#
#    python3 -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Like, Follows


os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test message model."""

    def setUp(self):
        """Create test message, add sample data."""

        Like.query.delete()
        Message.query.delete()
        Follows.query.delete()
        User.query.delete()

        self.client = app.test_client()

        test_user_1 = User(
            email="test@test1.com",
            username="testuser1",
            password="very_sneaky"
            )

        db.session.add(test_user_1)
        db.session.commit()

        self.user_1 = User.query.filter(User.email=="test@test1.com").first()
       
        test_message = Message(text="Hello again", user_id=self.user_1.id)

        db.session.add(test_message)
        db.session.commit()

    def tearDown(self):
        """Rollback fouled transactions from tests"""
        db.session.rollback()

    def test_message_model(self):
        """ Does basic model work """

        new_message = Message(text="Not now", user_id=self.user_1.id)

        db.session.add(new_message)
        db.session.commit()

        message = Message.query.filter(Message.text == "Not now").first()

        self.assertTrue(message)
        self.assertTrue(message.user == self.user_1)
