from typing import overload
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
# Create your tests here.
client = APIClient()




from .models import atend,Session
from class_app.models import Class,ClassStudents
from account.models import User



class AttendanceTests(APITestCase):

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
        User.objects.create(
            username = "unittestusername3",
            password = "unittestpassword",
            email= "unittestemail3@mail.com",
        )
        User.objects.create(
            username = "unittestusername4",
            password = "unittestpassword",
            email= "unittestemail4@mail.com",
        )
        User.objects.create(
            username = "unittestusername5",
            password = "unittestpassword",
            email= "unittestemail5@mail.com",
        )

        user1 = User.objects.get(username='unittestusername1')
        user2 = User.objects.get(username='unittestusername2')
        user3 = User.objects.get(username='unittestusername3')
        user4 = User.objects.get(username='unittestusername4')
        user5 = User.objects.get(username='unittestusername5')
        class_=Class.objects.create(
            name="unitclasstest1",
            description="initialized class1",
            owner=user1,
        )
        class_.teachers.add(user1)
        # class_.students.add(user2)
        # class_.students.add(user3)
        ClassStudents.objects.create(
            student=user2,
            Class=class_,
            studentid="12785468"
        )
        ClassStudents.objects.create(
            student=user3,
            Class=class_,
            studentid="12784448"
        )





        class_2=class_=Class.objects.create(
            name="unitclasstest2",
            description="initialized class2",
            owner=user1,
        )
        class_2.teachers.add(user1)
        # class_2.students.add(user4)
        # class_2.students.add(user5)

        ClassStudents.objects.create(
            student=user3,
            Class=class_2,
            studentid="11111468"
        )
        ClassStudents.objects.create(
            student=user4,
            Class=class_2,
            studentid="12789999"
        )




        at1=atend.objects.create(
            student = user4,
            Present = True
        )
        at2=atend.objects.create(
            student = user5,
            Present = False
        )

        session1=Session.objects.create(
            name="unittestsession1",
            session_class=class_2,
            # atends=(at1,at2)
        )
        session1.atends.add(at1)
        session1.atends.add(at2)




    def test_list_for_teacher(self):
        # self.client.login(username='unittestusername', password='unittestpassword')
        # self.token = Token.objects.get(user__username='unittestusername')
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        user = User.objects.get(username='unittestusername1')
        self.client.force_authenticate(user=user)
        class_pk=Class.objects.get(name="unitclasstest2").pk
        url = reverse('attendance:SessionsOfClass', kwargs={'pk': class_pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)

    def test_list_for_student(self):
        # self.client.login(username='unittestusername', password='unittestpassword')
        # self.token = Token.objects.get(user__username='unittestusername')
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        user = User.objects.get(username='unittestusername4')
        self.client.force_authenticate(user=user)
        class_pk=Class.objects.get(name="unitclasstest2").pk
        url = reverse('attendance:UserAtendsForClass', kwargs={'pk': class_pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)
    




    def test_add_session_by_teacher(self):
        # self.client.login(username='unittestusername', password='unittestpassword')
        # self.token = Token.objects.get(user__username='unittestusername')
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        user = User.objects.get(username='unittestusername1')
        self.client.force_authenticate(user=user)
        class_pk=Class.objects.get(name="unitclasstest1").pk
        url = reverse('attendance:SessionsOfClass', kwargs={'pk': class_pk})
        data={'name':"unittestsession2"}
        response = self.client.post(url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Session.objects.count(), 2)
        self.assertEqual(Session.objects.get(name='unittestsession2').name, 'unittestsession2')
        # print(response.data)


    def test_set_present(self):
        # self.client.login(username='unittestusername', password='unittestpassword')
        # self.token = Token.objects.get(user__username='unittestusername')
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        user = User.objects.get(username='unittestusername1')
        self.client.force_authenticate(user=user)
        class_pk=Class.objects.get(name="unitclasstest2").pk
        session_pk=Session.objects.get(name="unittestsession1").pk
        url = reverse('attendance:SetAtendsOfSession')
        data={'session_id':session_pk,'student':[4,5]}
        response = self.client.post(url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in atend.objects.all():
            self.assertEqual(item.Present,True)