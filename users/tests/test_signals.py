from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import UserSettings


class UserSettingsSignalTest(TestCase):
    def setUp(self):
        self.UserModel = get_user_model()

    def test_user_settings_creation(self):
        # create a new user
        new_user = self.UserModel.objects.create_user(username='testuser', password='password123')
        new_user.save()

        # check if UserSettings instance was created for the new user
        user_settings = UserSettings.objects.filter(user=new_user)
        self.assertTrue(user_settings.exists(), "UserSettings instance was not created for the new user")

        # optionally, you can also check the count to ensure only one instance is created
        self.assertEqual(user_settings.count(), 1, "More than one UserSettings instance was created for the new user")
