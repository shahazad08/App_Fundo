import pprint

import pytest
from django.urls import reverse
from rest_framework.test import APITestCase

from django_auth.django_auth import *
from django.test import TestCase, Client


# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_auth.settings")

class TestCases(TestCase):
    # def test_about_page_status_code(self):
    #     response = self.client.get('django_auth/users/register/')
    #     self.assertEquals(response.status_code, 200)

    # @classmethod
    # def setUpClass(self):
    #     # creating instance of a client.
    #     self.client = Client()
    #
    # def test_addAccount(self):
    #     response = self.client.get('django_auth/users/register/',{'email':'sk.shahazad@gmail.com','first_name': 'Shahazad','last_name':'shaikh','password':'azim1234'})
    #
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_getLogin(self):
    #     # Issue a GET request.
    #     response = reverse('api/login/')
    #
    #     # Check that the response is 200 OK.
    #     self.assertEqual(response.status_code, 200)

    @pytest.mark.django_db
    def test_login_success(self):
        url = self.client.get('/login/')
        data = {"email": "", "password": ""}
        response = self.client.post(url, data, format='json')
        z = response.json()['success']
        self.assertEqual(z, False)

        # self.assertEqual(expected_results, actual_results)
# #
# class TestCase(APITestCase):
#     @pytest.mark.django_db
#     def test_product_details(self):
#         url = reverse('/register/')
#         expected_results = {
#             'email': 'sk.shahazad@gmail.com',
#             'first_name': 'Shahazad',
#             'last_name': 'Shaikh',
#             'password': 'azim1234'
#         }
#         response = self.client.post(url, expected_results, format='json')
#         # response = self.client.get('register')
#         actual_results = response.json()
#         self.assertEqual(expected_results, actual_results)
#
#
#     @pytest.mark.django_db
#     def test_createnote(self):
#         expected_results = {
#             'title': 'Notes',
#             'description': 'Notes Monitioring',
#             'color': 'Red',
#         }
#         url = reverse('Note/register')
#         # response = self.client.get('create/')
#         response = self.client.get('/api/note/create/')
#         actual_results = response.json()
#         self.assertEqual(expected_results, url)
#
#
#     @pytest.mark.django_db
#     def test_updatenote(self):
#         expected_results = {
#             'title': 'Notes',
#             'description': 'Notes Monitioring',
#             'color': 'Red',
#             # 'remiander': '12:12:2019'
#         }
#         response = self.client.get('/api/note/update/')
#         actual_results = response.json()
#         self.assertEqual(expected_results, actual_results)
#
#     @pytest.mark.django_db
#     def test_color(self):
#         response = self.client.get('api/note/<int:pk>/color/')
#         self.assertEquals(response.status_code, 200)
