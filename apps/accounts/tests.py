from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AccountsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user_creates_account_and_returns_profile_fields(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "TestPass123!",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "newuser")
        self.assertEqual(response.json()["email"], "new@example.com")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_user_without_username_returns_validation_error(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "nousername@example.com",
                "password": "TestPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.json())

    def test_register_user_with_duplicate_username_returns_validation_error(self):
        User.objects.create_user(
            username="duplicate", email="dup@example.com", password="TestPass123!"
        )

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "duplicate",
                "email": "another@example.com",
                "password": "TestPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.json())

    def test_register_user_with_weak_password_returns_validation_error(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "weakpassuser",
                "email": "weak@example.com",
                "password": "123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json())

    def test_profile_requires_authenticated_user(self):
        response = self.client.get("/api/auth/profile/")

        self.assertEqual(response.status_code, 401)

    def test_profile_returns_authenticated_user_details(self):
        user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="TestPass123!",
            first_name="Profile",
            last_name="User",
        )
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/auth/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "profileuser")
        self.assertEqual(response.json()["email"], "profile@example.com")
        self.assertEqual(response.json()["first_name"], "Profile")
