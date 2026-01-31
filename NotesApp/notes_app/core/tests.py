from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_logout_post(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('logout'))
        # Should redirect to login page as per invalid LOGOUT_REDIRECT_URL='login' (it's a named URL pattern)
        # settings.py: LOGOUT_REDIRECT_URL = 'login'
        self.assertRedirects(response, reverse('login')) # 302
