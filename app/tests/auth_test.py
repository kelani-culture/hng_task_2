import os
import unittest
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db import SessionLocal 
from app.auth import JwtGenerator
from app.main import app, get_db
from app.models import Base, User

from httpx import Client

# Define the base URL of your application
DEBUG = os.getenv('DEBUG').lower() == "true"

#TODO change host endpoint on deployment
BASE_URL = "http://localhost:8000"  if DEBUG else 'https://conscious-hare-hng-931619d8.koyeb.app/' 

class TestUserAuthentication(unittest.TestCase):
    def setUp(self):
        self.client = Client(base_url=BASE_URL)
        self.register_url = "/auth/register"
        self.login_url = "/auth/login"
        self.default_user = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        self.db = SessionLocal()
    def check_user_exist(self):
        user = self.db.query(User).filter(User.email == self.default_user['email']).first()
        if not user:
            return False
        return True

    @unittest.skipUnless(check_user_exist is True, "User exist in database")
    def test_register_user_successfully(self):
        response = self.client.post(self.register_url, json=self.default_user)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["user"]["firstName"], "John")
        self.assertEqual(data["data"]["user"]["lastName"], "Doe")
        self.assertEqual(data["data"]["user"]["email"], "john.doe@example.com")
        self.assertIn("access_token", data["data"])

    def test_register_user_missing_fields(self):
        incomplete_user = {
            "first_name": "John",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(self.register_url, json=incomplete_user)
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["errors"][0]["fields"], "body")
        self.assertEqual(data["errors"][0]["message"], "Field required")

    def test_register_user_duplicate_email(self):
        # Register the first user
        self.client.post(self.register_url, json=self.default_user)
        
        # Attempt to register a second user with the same email
        another_user = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "john.doe@example.com",  # Duplicate email
            "password": "password1234",
            "phone": "0987654321"
        }
        response = self.client.post(self.register_url, json=another_user)
        self.assertEqual(response.status_code, 400)
        data = response.json()

    def test_login_user_successfully(self):
        # Register a user
        self.client.post(self.register_url, json=self.default_user)
 
        # Login with the registered user
        login_cred = {
            "email": self.default_user["email"],
            "password": self.default_user["password"]
        }
        response = self.client.post(self.login_url, json=login_cred)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("access_token", data["data"])

    def test_login_user_invalid_credentials(self):
        login_cred = {
            "email": "non.existent@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, json=login_cred)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["status"], "Bad request")
        self.assertEqual(data["message"], "Authentication failed")
