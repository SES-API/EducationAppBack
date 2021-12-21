from typing import overload
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
# Create your tests here.
factory = APIRequestFactory()
client = APIClient()




from .models import Class
from account.models import User



class ClassTests(APITestCase):

    def setUp(self):
        User.objects.create(
            username = "unittestusername1",
            password = "unittestpassword",
            email= "unittestemail1@mail.com",
        )
        User.objects.create(
            username = "unittestusername2",
            password = "unittestpassword",
            email= "unittestemail2@mail.com",
        )



        user = User.objects.get(username='unittestusername1')
        class_=Class.objects.create(
            name="unitclasstest",
            description="initialized class",
            owner=user,
        )
        class_.teachers.add(user)
    
    def test_createclass(self):
        # self.client.login(username='unittestusername', password='unittestpassword')
        # self.token = Token.objects.get(user__username='unittestusername')
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        user = User.objects.get(username='unittestusername1')
        self.client.force_authenticate(user=user)
        url = reverse('class:classes')
        data = {'name': 'unitclasstest2'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Class.objects.count(), 2)
        self.assertEqual(Class.objects.get(name='unitclasstest2').name, 'unitclasstest2')

    def test_getclass_with_name(self):
        url = reverse('class:classes')
        url+="?name=unitclasstest"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_getclass(self):
        url = reverse('class:classes')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_unique_class_wtih_id(self):
        # self.client.login(username='unittestusername', password='unittestpassword')
        # self.token = Token.objects.get(user__username='unittestusername')
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        user = User.objects.get(username='unittestusername1')
        class_pk=Class.objects.get(name="unitclasstest").pk
        self.client.force_authenticate(user=user)
        url = reverse('class:class_object', kwargs={'pk': class_pk})
        response = self.client.get(url, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)