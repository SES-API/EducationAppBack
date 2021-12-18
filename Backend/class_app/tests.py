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
            username = "unittestusername",
            password = "unittestpassword",
            email= "unittestemail@mail.com",
        )
        

    def testcreateclass(self):
        # self.client.login(username='unittestusername', password='unittestpassword')
        # self.token = Token.objects.get(user__username='unittestusername')
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        user = User.objects.get(username='unittestusername')
        self.client.force_authenticate(user=user)
        url = reverse('class:classes')
        data = {'name': 'unitclasstest'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def testgetclass(self):
        url = reverse('class:classes')
        url+="?name=unittestusername"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)