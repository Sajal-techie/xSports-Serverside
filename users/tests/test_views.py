from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient
from users.models import Users, Academy,UserProfile, Sport
from real_time.models import Notification
from unittest.mock import patch

class SignupViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup') 


        self.valid_player_data = {
            'email': 'newplayer@example.com',
            'username': 'newplayer',
            'sport': 'football',
            'state': 'California',
            'district': 'Los Angeles',
            'dob': '1990-01-01',
            'password': 'testpass123',
        }
        
        self.valid_academy_data = {
            'email': 'newacademy@example.com',
            'username': 'newacademy',
            'sport[]': ['football', 'basketball'],  
            'state': 'New York',
            'district': 'Manhattan',
            'dob': '1980-01-01',
            'password': 'testpass123',
            'license': 'ABC123',
            'is_academy': 'true',
        }

    def test_signup_missing_email(self):
        data = self.valid_player_data.copy()
        del data['email']
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email field is Required", str(response.data['message']))
    
    def test_signup_invalid_email(self):
        data = self.valid_player_data.copy()
        data["email"] = 'invalid email' 
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email is not Valid", str(response.data["message"]))

    def test_signup_existing_email(self):
        Users.objects.create_user(email='existing@gmail.com', password='testpass123')
        data = self.valid_player_data.copy()
        data["email"] = "existing@gmail.com"
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Account with Email already exist try login", str(response.data["message"]))

    def test_signup_academy_missing_license(self):
        data = self.valid_academy_data.copy()
        del data['license']
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("License is required", str(response.data["message"]))

    @patch('users.views.CustomUsersSerializer')
    @patch('users.task.send_otp.delay')
    def test_successfull_player_signup(self, mock_send_otp, mock_serializer):
        mock_serializer.return_value.is_valid.return_value = True
        response = self.client.post(self.signup_url, self.valid_player_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Registration Successfull, Check Email For Verification")
        mock_send_otp.assert_called_once_with(self.valid_player_data['email'])

    @patch('users.views.CustomUsersSerializer')
    @patch('users.task.send_otp.delay')
    def test_successfull_academy_signup(self, mock_send_otp, mock_serializer):
        mock_serializer.return_value.is_valid.return_value = True
        response = self.client.post(self.signup_url, self.valid_academy_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Registration Successfull, Check Email For Verification")
        mock_send_otp.assert_called_once_with(self.valid_academy_data['email'])
    
    @patch('users.views.CustomUsersSerializer')
    def test_signup_serializer_error(self, mock_serializer):
        mock_serializer.return_value.is_valid.side_effect = ValidationError("Serializer error")
        response = self.client.post(self.signup_url, self.valid_player_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Serializer error", str(response.data))


class VerifyOtpViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.verify_otp_url = reverse('otp_verification')
        self.user = Users.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            is_verified=False,
            otp='123456'
        )

    def test_verify_otp_missing_email(self):
        """Test OTP verification with missing email"""
        response = self.client.put(self.verify_otp_url, {'otp': '123456'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email is required', str(response.data['message']))

    def test_verify_otp_missing_otp(self):
        """Test OTP verification with missing OTP"""
        response = self.client.put(self.verify_otp_url, {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('OTP is required', str(response.data['message']))
        
    def test_verify_otp_expired(self):
        """Test OTP verification when OTP has expired"""
        self.user.otp = None
        self.user.save()
        response = self.client.put(self.verify_otp_url, {'email': 'testuser@example.com', 'otp': '123456'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'OTP Expired try resending otp')
    
    def test_verify_otp_invalid(self):
        """Test OTP verification with invalid OTP"""
        response = self.client.put(self.verify_otp_url, {'email': 'testuser@example.com', 'otp': '654321'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid OTP')
    

    def test_verify_otp_valid(self):
        """Test successful OTP verification"""
        response = self.client.put(self.verify_otp_url, {'email': 'testuser@example.com', 'otp': '123456'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'OTP Verified')

    def test_verify_otp_method_not_allowed(self):
        """Test that only PUT method is allowed for OTP verification"""
        response = self.client.post(self.verify_otp_url, {'email': 'testuser@example.com', 'otp': '123456'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_verify_otp_already_verified(self):
        """Test OTP verification for an already verified user"""
        self.user.is_verified = True
        self.user.save()
        response = self.client.put(self.verify_otp_url, {'email': 'testuser@example.com', 'otp': '123456'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Already verfied Try logging in again')


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login') 
        
        self.user = Users.objects.create_user(
            email='user@example.com',
            password='testpass123',
            username='testuser',
            is_verified=True,
            is_active=True
        )
        
        self.academy_user = Users.objects.create_user(
            email='academy@example.com',
            password='testpass123',
            username='academyuser',
            is_verified=True,
            is_active=True,
            is_academy=True
        )
        Academy.objects.create(user=self.academy_user, is_certified=True)
        
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



class ForgetPasswordViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.forget_password_url = reverse('forget_pass')
        
        self.user = Users.objects.create_user(
            email='testuser@example.com',
            password='oldpassword123'
        )

    def test_forget_password_missing_email(self):
        """Test forget password with missing email"""
        response = self.client.post(self.forget_password_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Email is required')

    def test_forget_password_non_existent_email(self):
        """Test forget password with non-existent email"""
        response = self.client.post(self.forget_password_url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Email is not valid, Try signin')

    @patch('users.task.send_otp.delay')
    def test_forget_password_valid_email_without_password(self, mock_send_otp):
        """Test forget password with valid email but without new password"""
        response = self.client.post(self.forget_password_url, {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Email is valid')
        mock_send_otp.assert_called_once_with('testuser@example.com')

    def test_forget_password_valid_email_with_password(self):
        """Test forget password with valid email and new password"""
        response = self.client.post(self.forget_password_url, {
            'email': 'testuser@example.com',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password Resetted successfully')
        
        # Verify that the password was actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_forget_password_method_not_allowed(self):
        """Test that only POST method is allowed for forget password"""
        response = self.client.get(self.forget_password_url, {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch('users.task.send_otp.delay')
    def test_forget_password_otp_sending_failure(self, mock_send_otp):
        """Test forget password when OTP sending fails"""
        mock_send_otp.side_effect = Exception('OTP sending failed')
        response = self.client.post(self.forget_password_url, {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Internal Server Error')
