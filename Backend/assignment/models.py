from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
from django.apps import apps
from class_app.models import Class
from django.core.validators import MaxValueValidator, MinValueValidator


UserModel=get_user_model()


class Question(models.Model):
    name = models.CharField(max_length=50)
    weight = models.FloatField() # eg. 40%
    students = models.ManyToManyField(UserModel,related_name="question_student")

class Assignment(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField()
    delay = models.FloatField() # eg. 40%
    questions = models.ManyToManyField(Question,related_name="assignment_question", through='Grade')
    class_id = models.ForeignKey(Class,related_name="assignment_class",on_delete=models.CASCADE)

class Grade(models.Model):
    person = models.ForeignKey(Question, on_delete=models.CASCADE)
    group = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])