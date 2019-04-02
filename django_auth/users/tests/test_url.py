from django.urls import reverse, resolve
import pytest
from users.models import User


pytestmark = pytest.mark.django_db


class TestUrls:

    def test_signup_url(self):
        path = reverse('signup')
        assert resolve(path).view_name == 'signup'


    def test_createnote(self):
        path=reverse('api/note/create')
        assert resolve(path).view_name=='create'

    def getnote(self):
        path=reverse('api/note/get',kwargs={'pk':1})
        assert resolve(path).view_name=='get'

    def updatenote(self):
        path=reverse('api/note/update')
        assert resolve(path).view_name=='update'



