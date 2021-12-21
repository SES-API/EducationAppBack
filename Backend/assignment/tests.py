from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from account.models import User
from class_app.models import Class
from assignment.models import Assignment, Question



# Define this after the ModelTestCase

class AssignmentTest(TestCase):

    def setUp(self):
        User.objects.create(username= "test_teacher", password= "Ab654321", email= "test_teacher_email@test.com")
        User.objects.create(username= "test_student1", password= "Ab654321", email= "test_student1_email@test.com")
        User.objects.create(username= "test_student2", password= "Ab654321", email= "test_student2_email@test.com")

        self.student1 = User.objects.get(username="test_student1")
        self.student2 = User.objects.get(username="test_student2")
        self.teacher = User.objects.get(username="test_teacher")

        Class.objects.create(name="test_class")
        self.class_ = Class.objects.get(name="test_class")
        self.class_.teachers.set([self.teacher])
        self.class_.students.set([self.student1])
        self.class_.students.set([self.student2])

        self.assignment = Assignment.objects.create(name="setup_test_assignment", weight= "3", class_id= self.class_, not_graded_count=0)
        self.question = Question.objects.create(name="setup_test_question", full_grade=30, assignment_id=self.assignment, not_graded_count=2)

        self.client = APIClient()


    def test_api_create_assignment(self):    
        url = reverse("assignment:create_assignment")

        self.client.force_authenticate(user=self.teacher)

        data = {"name" : "test_assignment", "weight" : "3", "class_id" : f"{self.class_.id}"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {"name" : "test_assignment", "weight" : "3", "class_id" : f"{self.class_.id}"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.force_authenticate(user=self.student1)
        
        data = {"name" : "test_assignment_new", "weight" : "3", "class_id" : f"{self.class_.id}"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



    def test_api_assignment_detail(self):
        assignment = Assignment.objects.create(name="test_assignment", weight= "3", class_id= self.class_)
        url = reverse("assignment:assignment_detail", kwargs={"pk": assignment.id})

        self.client.force_authenticate(user=self.student1)

        # response = self.client.get(url, format="json")
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {"name" : "test_assignment", "weight" : "5", "class_id" : f"{self.class_.id}"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {"name" : "test_assignment", "weight" : "5", "class_id" : f"{self.class_.id}"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['weight'], 5)

        data = {"name" : "test_assignment", "weight" : "100", "class_id" : f"{self.class_.id}"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



    def test_api_add_question(self):
        url = reverse("assignment:add_question", kwargs={"pk": self.assignment.id})

        self.client.force_authenticate(user=self.student1)

        data = {"name" : "test_question", "full_grade" : "20"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        self.client.force_authenticate(user=self.teacher)

        data = {"name" : "test_question", "full_grade" : "20"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {"name" : "test_question", "full_grade" : "30"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # def test_api_add_grade(self):
    #     url = reverse("assignment:add_grade")

    #     self.client.force_authenticate(user=self.student1)

    #     data = [{"question_id": f"{self.question.id}", "value":"20", "user_id": f"{self.student1.id}", "delay":"0"},
    #         {"question_id": f"{self.question.id}", "value":"20", "user_id": f"{self.student2.id}", "delay":"0"}]
    #     response = self.client.post(url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    #     self.client.force_authenticate(user=self.teacher)

    #     response = self.client.post(url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

