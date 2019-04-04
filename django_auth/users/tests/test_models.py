import os
from django.test import TestCase

from django_auth import django_auth
from django_auth.users.models import User
from django_auth.django_auth import settings
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_auth.settings")
# os.environ['DJANGO_SETTINGS_MODULE'] = 'django_auth.settings'
DJANGO_SETTINGS_MODULE = django_auth.settings

class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.object.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = User.object.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_last_name_label(self):
        author = User.object.get(id=1)
        last_label = author._meta.get_field('last_name').verbose_name
        self.assertEquals(last_label, 'last name')

    def test_first_name_max_length(self):
        author = User.object.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)




