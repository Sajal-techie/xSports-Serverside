from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Sport, UserProfile, Academy

class UsersModelTest(TestCase):

    def test_create_user(self):
        user = get_user_model().objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        superuser = get_user_model().objects.create_superuser(
            email='superuser@example.com',
            username='superuser',
            password='superpassword'
        )
        self.assertEqual(superuser.email, 'superuser@example.com')
        self.assertTrue(superuser.check_password('superpassword'))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


class SportModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='sportuser@example.com',
            username='sportuser',
            password='testpassword'
        )
        self.sport = Sport.objects.create(sport_name='Football', user=self.user)

    def test_sport_creation(self):
        self.assertEqual(self.sport.sport_name, 'Football')
        self.assertEqual(self.sport.user, self.user)
        self.assertEqual(str(self.sport), 'sportuserFootballsport instance')


class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='profileuser@example.com',
            username='profileuser',
            password='testpassword'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='This is a bio',
            state='California',
            district='Los Angeles'
        )

    def test_userprofile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.bio, 'This is a bio')
        self.assertEqual(self.profile.state, 'California')
        self.assertEqual(self.profile.district, 'Los Angeles')
        self.assertEqual(str(self.profile), 'profileuserprofile instanceThis is a bio')
