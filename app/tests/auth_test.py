import os
import unittest
from typing import Optional

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth import JwtGenerator
from app.main import app, get_db
from app.models import Base, User

load_dotenv()

DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL"
)  # Replace with your test database URL

# Setup the test database
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

from faker import Faker

fake = Faker()


USER_CRED = {
    "first_name": fake.first_name(),
    "last_name": fake.last_name(),
    "email": fake.email(),
    "password": fake.password(),
    "phone": "09041563211",
}


class TestUserBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.db = TestingSessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db.begin_nested()
        # url
        self.register_url = "/auth/register"

    def tearDown(self):
        self.db.rollback()


class TestUserCreation(TestUserBase):
    def test_create_user(self):
        response = self.client.post(
            self.register_url,
            json=USER_CRED,
        )
        self.assertEqual(response.status_code, 201)
        # self.assertEqual(response.json()['data']["first_name"], user.first_name)


class TestUserExist(TestUserBase):
    def test_create_existing_user(self):
        # Try to create a user with the same username
        response = self.client.post(
            self.register_url,
            json=USER_CRED,
        )
        bad_resp = {
            "status": "Bad Request",
            "message": "Registration unsuccessful",
            "statusCode": 400,
        }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), bad_resp)


class TestUserLogin(TestUserBase):
    userId: Optional[str] = None
    access_token: Optional[str] = None

    def setUp(self):
        self.login_url = "/auth/login"
        self.login_cred = {
            "email": USER_CRED["email"],
            "password": USER_CRED["password"],
        }
        self.db.begin_nested()
        self.jwt = JwtGenerator()

    def check_access_token(self):
        if self.access_token is None or self.userId:
            return False
        return True

    def test_login_user(self):
        response = self.client.post(self.login_url, json=self.login_cred)
        self.assertEqual(response.status_code, 200)
        if response.status_code == 200:
            self.__class__.access_token = response.json()["data"][
                "access_token"
            ]
            self.__class__.userId = response.json()["data"]["user"]["userId"]

    @unittest.skipUnless(check_access_token, "skip unsuccessful login")
    def test_valid_access_token(self):
        """
        test  if user data exists in token
        """
        print("Access token is valid")
        self.assertIsNotNone(
            self.access_token, "Access TOken should not be None"
        )
        self.assertIsNotNone(self.userId, "User Id shouuld Not be None")
        token_id = self.jwt.get_current_user(self.access_token)
        self.assertTrue(token_id, self.userId)

    @unittest.skipUnless(
        check_access_token is False,
        "skip successful login",
    )
    def test_invalid_access_token(self):
        """
        check for invalid access token
        """
        print("Access token is invalid")
        self.assertIsNone(self.access_token, "Access TOken should  be None")
        self.assertIsNone(self.userId, "User Id should be None")
        token_id = self.jwt.get_current_user(self.access_token)
        self.assertFalse(token_id, self.userId)

