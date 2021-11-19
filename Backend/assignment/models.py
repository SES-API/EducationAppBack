from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
from django.apps import apps
from class_app.models import Class
from account.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime



class Question(models.Model):
    name = models.CharField(max_length=50)
    weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)]) # eg. 40%
    students = models.ManyToManyField(User,related_name="question_student", through='Grade')

class Assignment(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField(default=datetime.date.today)
    questions = models.ManyToManyField(Question,related_name="assignment_question")
    class_fk = models.ForeignKey(Class,related_name="assignment_class",on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'class_fk',)

class Grade(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    delay = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)]) # eg. 40%
