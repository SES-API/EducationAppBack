from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
from django.apps import apps
from class_app.models import Class
from account.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime



class Assignment(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField(default=datetime.date.today)
    class_id = models.ForeignKey(Class,related_name="assignment_class",on_delete=models.CASCADE)
    is_graded = models.BooleanField(default=True)
    not_graded_count = models.IntegerField(default=0) # how many question is not graded
    weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    min_grade = models.FloatField(default=None, null=True)
    max_grade = models.FloatField(default=None, null=True)
    avg_grade = models.FloatField(default=None, null=True)

    class Meta:
        unique_together = ('name', 'class_id',)


class Question(models.Model):
    name = models.CharField(max_length=50)
    full_grade = models.FloatField(validators=[MinValueValidator(0)]) # eg. 40
    assignment_id = models.ForeignKey(Assignment,related_name="assignment_question",on_delete=models.CASCADE, null=True)
    is_graded = models.BooleanField(default=False)
    not_graded_count = models.IntegerField() # how many student is not graded
    min_grade = models.FloatField(default=None, null=True)
    max_grade = models.FloatField(default=None, null=True)
    avg_grade = models.FloatField(default=None, null=True)

    class Meta:
        unique_together = ('name', 'assignment_id',)



class Grade(models.Model):
    question_id = models.ForeignKey(Question, related_name="question_grade", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name="student_grade",on_delete=models.CASCADE)
    value = models.FloatField(default=0, validators=[MinValueValidator(0)])
    delay = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)]) # eg. 40%
    final_grade = models.FloatField(null=True, blank=True)


class AssignmentGrade(models.Model):
    assignment_id = models.ForeignKey(Assignment,related_name="assignment_grade",on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, related_name="student_assignment_grade",on_delete=models.CASCADE)
    value = models.FloatField(null=True, blank=True)


class ClassGrade(models.Model):
    class_id = models.ForeignKey(Class,related_name="class_grade",on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, related_name="student_class_grade",on_delete=models.CASCADE)
    value = models.FloatField(null=True, blank=True)
