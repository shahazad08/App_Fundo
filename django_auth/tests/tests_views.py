import pytest
from django.urls import reverse
from rest_framework.test import APITestCase
from django_auth.django_auth import *
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_auth.settings")

class TestCases(APITestCase):
    @pytest.mark.django_db
    def login_success(self):
        url = reverse('login')
        data = {"email": "", "password": ""}
        response = self.client.post(url, data, format='json')
        z = response.json()['success']
        self.assertEqual(z, False)



class TestCase(APITestCase):
    @pytest.mark.django_db
    def test_product_details(self):
        expected_results = {
            'email':'sk.shahazad@gmail.com',
            'first_name': 'Shahazad',
            'last_name': 'Shaikh',
            'password': 'azim1234'
        }
        response = reverse('/register/')
        # response = self.client.get('/api/products/1/')
        actual_results = response.json()
        self.assertEqual(expected_results, actual_results)
    # def test_reg_success(self):
    #     # application = get_wsgi_application()
    #     url='register'
    #     user_data = {
    #         "email": "sk.shahazad@gmail.com",
    #         "first_name": "Shahazad",
    #         "last_name": "Shaikh",
    #         "password": "azim1234",
    #     }
    #     response = self.client.post(url, user_data)
    #     print("Response",response)
    #     z = response.json()['success']
    #     self.assertEqual(z, True)

