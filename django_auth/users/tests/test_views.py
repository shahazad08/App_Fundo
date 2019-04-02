from distutils.command import register

from django.test import RequestFactory, client
from django.urls import reverse
from rest_framework.utils import json
from users import models
from users.models import User

from django_auth.users.views import Registerapi


class TestViews:
    def login_detail(self):
        path=reverse()


class RegisterModel:
    def test_save(self):
            register = Registerapi.objects.create(
                email="sk.shahazad@gmail.com",
                first_name="shahazad",
                last_name="shaikh",
                password=500,
                confirm_password=500,
            )
            assert register.email == "sk.shahazad@gmail.com"
            assert register.password == 500
            assert register.confirm_password == 500
    assert register.email == "sk.shahazad@gmail.com"


def setUp(self):
    valid_payload = {
        'title': 'test',
        'description': "test",
        'color': "test",
        }

    response = client.post(
        reverse('create'),
        data=json.dumps(valid_payload),
        content_type='application/json'
    )
    assert response.status_code


def create():
    valid_payload = {
        'title': 'test',
        'description': "test",
        'color': "test",
       }

    response = client.post(
        reverse('create'),
        data=json.dumps(valid_payload),
        content_type='application/json'
    )
    assert response.status_code

