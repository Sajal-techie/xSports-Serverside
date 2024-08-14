from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import Users, Academy,UserProfile, Sport
from selection_trial.models import Trial
from user_profile.models import Follow, FriendRequest
from real_time.models import Notification
from unittest.mock import patch

class SignupViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')  # Assume you've named your URL

    def test_successful_signup(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'sport': 'football',
            'state': 'TestState',
            'district': 'TestDistrict',
            'dob': '1990-01-01'
        }
        with patch('users.views.send_otp.delay') as mock_send_otp:
            response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Users.objects.count(), 1)
        mock_send_otp.assert_called_once_with('test@example.com')

    def test_invalid_signup(self):
        data = {'email': 'invalid'}  # Missing required fields
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class VerifyOtpViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.verify_otp_url = reverse('otp_verification')
        self.user = Users.objects.create_user(email='test@example.com', password='testpass123')
        self.user.otp = '123456'
        self.user.save()

    def test_successful_otp_verification(self):
        data = {'email': 'test@example.com', 'otp': '123456'}
        response = self.client.put(self.verify_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_invalid_otp(self):
        data = {'email': 'test@example.com', 'otp': '000000'}
        response = self.client.put(self.verify_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')  # Assuming you have a URL name 'login' for this view
        
        # Create a regular user
        self.user = Users.objects.create_user(
            email='user@example.com',
            password='testpass123',
            username='testuser',
            is_verified=True,
            is_active=True
        )
        
        # Create an academy user
        self.academy_user = Users.objects.create_user(
            email='academy@example.com',
            password='testpass123',
            username='academyuser',
            is_verified=True,
            is_active=True,
            is_academy=True
        )
        Academy.objects.create(user=self.academy_user, is_certified=True)
        
        # Create an admin user
        self.admin_user = Users.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            username='adminuser',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

    def test_login_missing_email(self):
        response = self.client.post(self.login_url, {'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'email field is required')

    def test_login_missing_password(self):
        response = self.client.post(self.login_url, {'email': 'user@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'password field is required')

    def test_login_nonexistent_email(self):
        response = self.client.post(self.login_url, {'email': 'nonexistent@example.com', 'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Email Does Not Exists')

    def test_login_invalid_password(self):
        response = self.client.post(self.login_url, {'email': 'user@example.com', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid Password')

    def test_admin_login_as_user(self):
        response = self.client.post(self.login_url, {'email': 'admin@example.com', 'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Admin cannot loggin as user')

    def test_user_login_as_admin(self):
        response = self.client.post(self.login_url, {'email': 'user@example.com', 'password': 'testpass123', 'is_staff': True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You are not an admin ')

    def test_login_blocked_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.login_url, {'email': 'user@example.com', 'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You are blocked')

    def test_academy_login_as_player(self):
        response = self.client.post(self.login_url, {'email': 'academy@example.com', 'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You are signed in as acadmey try academy login')

    def test_player_login_as_academy(self):
        response = self.client.post(self.login_url, {'email': 'user@example.com', 'password': 'testpass123', 'is_academy': True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You are signed in as player try player login')

    @patch('users.views.send_otp.delay')
    def test_login_unverified_user(self, mock_send_otp):
        self.user.is_verified = False
        self.user.save()
        response = self.client.post(self.login_url, {'email': 'user@example.com', 'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'You are not verified')
        mock_send_otp.assert_called_once_with('user@example.com')

    def test_login_uncertified_academy(self):
        Academy.objects.filter(user=self.academy_user).update(is_certified=False)
        response = self.client.post(self.login_url, {'email': 'academy@example.com', 'password': 'testpass123', 'is_academy': True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You are not approved by admin ')

    def test_successful_player_login(self):
        UserProfile.objects.create(user=self.user, profile_photo='photo.jpg')
        Notification.objects.create(receiver=self.user)
        response = self.client.post(self.login_url, {'email': 'user@example.com', 'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login Successful')
        self.assertEqual(response.data['role'], 'player')
        self.assertIn('profile_photo', response.data)
        self.assertIn('notification_count', response.data)

    def test_successful_academy_login(self):
        response = self.client.post(self.login_url, {'email': 'academy@example.com', 'password': 'testpass123', 'is_academy': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login Successful')
        self.assertEqual(response.data['role'], 'academy')

    def test_successful_admin_login(self):
        response = self.client.post(self.login_url, {'email': 'admin@example.com', 'password': 'testpass123', 'is_staff': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login Successful')
        self.assertEqual(response.data['role'], 'admin')

class ResendOtpViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.resend_otp_url = reverse('resend_otp')

    @patch('users.views.send_otp.delay')
    def test_resend_otp(self, mock_send_otp):
        data = {'email': 'test@example.com'}
        response = self.client.post(self.resend_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_otp.assert_called_once_with('test@example.com')

class ForgetPasswordViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.forget_password_url = reverse('forget_pass')
        self.user = Users.objects.create_user(email='test@example.com', password='oldpass123')

    @patch('users.views.send_otp.delay')
    def test_forget_password_send_otp(self, mock_send_otp):
        data = {'email': 'test@example.com'}
        response = self.client.post(self.forget_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_otp.assert_called_once_with('test@example.com')

    def test_forget_password_reset(self):
        data = {'email': 'test@example.com', 'password': 'newpass123'}
        response = self.client.post(self.forget_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
