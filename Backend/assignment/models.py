from django.db import models
from django.contrib.auth import get_user_model
from ..class.models import Class
# Create your models here.


UserModel=get_user_model()

class Assignment(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField()
    delay = models.FloatField() # eg. 40%
    questions = models.ManyToManyField(Question,related_name="assignment_question", through='grade')
    class_id = models.ForeignKey(Class,related_name="assignment_class",on_delete=models.CASCADE)



class Question(models.Model):
    name = models.CharField(max_length=50)
    coefficient = models.FloatField() # eg. 40%
    students = models.ManyToManyField(UserModel,related_name="question_student")
