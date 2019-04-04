import os

from django.urls import reverse, resolve


from django_auth.django_auth import settings
from django.conf import settings
import pytest


from django.test import SimpleTestCase

from django_auth.users.views import Registerapi,signup, upload_images

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_auth.settings")
DJANGO_SETTINGS_MODULE = django_auth.settings
# os.environ['DJANGO_SETTINGS_MODULE'] = 'django_auth.settings'

class TestUrls(SimpleTestCase):
    def test_register_url(self):
        assert 2 == 2
        url=reverse('register')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, Registerapi)

    def test_signup_url(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).view_name, signup)

    def test_upload_images_url(self):
        url=reverse('upload_profile')
        self.assertEquals(resolve(url).func.view_class,upload_images)


