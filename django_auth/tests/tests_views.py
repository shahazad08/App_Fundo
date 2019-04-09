import pytest
from django.urls import reverse
from rest_framework.test import APITestCase
# from django.core.wsgi import get_wsgi_application
# from  import urls
# from django_auth.users import urls
# from django_auth.users.views import Registerapi


class TestCases(APITestCase):
    @pytest.mark.django_db
    def login_success(self):
        url = reverse('rest_login')
        data = {"username": "", "password": ""}
        response = self.client.post(url, data, format='json')
        z = response.json()['success']
        self.assertEqual(z, False)
        # url = reverse("login")
        # user_data = {
        #     "email": "sk.shahazad@gmail.com",
        #     "password": "azim1234",
        # }
        # response = self.client.post(url, user_data)
        # z = response.json()['success']
        # self.assertEquals(z, True)




class TestCase(APITestCase):
    @pytest.mark.django_db
    def test_reg_success(self):
        # application = get_wsgi_application()
        url='register'
        user_data = {
            "email": "sk.shahazad@gmail.com",
            "first_name": "Shahazad",
            "last_name": "Shaikh",
            "password": "azim1234",
        }
        response = self.client.post(url, user_data)
        print("Response",response)
        z = response.json()['success']
        self.assertEqual(z, True)

