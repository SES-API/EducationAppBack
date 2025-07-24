from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import User
import datetime



# Define this after the ModelTestCase
class NotLoggedInAccountTest(TestCase):

    def setUp(self):
        self.client = APIClient()


    def test_api_register(self):
        url = reverse("account:register")

        data =  {"username" : "test_user", "password" : "Ab654321", "email" : "test_email@test.com" , "first_name":"testname","last_name":"test_last_name"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data =  {"username" : "test_user", "password" : "4321", "email" : "test_email@test.com" , "first_name":"testname","last_name":"test_last_name"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_api_reset_password(self):
        user = User.objects.create(username="test_user", password="Ab654321", email="test_email@test.com")

        url = reverse("account:reset_password")

        data =  {"new_password1" : "ABcd12345", "new_password2" : "ABcd12345", "email" : "test_email@test.com"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data =  {"new_password1" : "Ab", "new_password2" : "654321", "email" : "test_email@test.com"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class LoggedInAccountTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username= "test_user", password= "Ab654321", email= "test_email@test.com")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_api_get_profile(self):        
        response = self.client.get(
            reverse("account:profile", kwargs={"pk": self.user.id}), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_api_update_profile(self):
        url = reverse("account:settings_profile")

        data = {"birthdate" : "2000-04-04"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["birthdate"], data["birthdate"])

        data = {"birthdate" : f"{datetime.date.today}"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_api_change_password(self):
        url = reverse("account:change_password")

        data =  {"new_password1" : "Ab", "new_password2" : "654321", "old_password" : "Ab654321"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        # data =  {"new_password1" : "ABcd1234", "new_password2" : "ABcd1234", "old_password" : f"{self.user.password}"}
        # response = self.client.put(url, data, format="json")
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        
    def test_api_settings_delete(self):
        url = reverse("account:settings_delete")
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(
            reverse("account:profile", kwargs={"pk": self.user.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


