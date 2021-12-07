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
    class_fk = models.ForeignKey(Class,related_name="assignment_class",on_delete=models.CASCADE)
    is_graded = models.BooleanField(default=False)
    not_graded_count = models.IntegerField()
    weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)]) # eg. 40%
    min_grade = models.FloatField(default=None, null=True)
    max_grade = models.FloatField(default=None, null=True)
    avg_grade = models.FloatField(default=None, null=True)

    class Meta:
        unique_together = ('name', 'class_fk',)


class Question(models.Model):
    name = models.CharField(max_length=50)
    full_grade = models.FloatField(validators=[MinValueValidator(0)]) # eg. 40
    assignment_fk = models.ForeignKey(Assignment,related_name="assignment_question",on_delete=models.CASCADE, null=True)
    is_graded = models.BooleanField(default=False)
    not_graded_count = models.IntegerField()
    min_grade = models.FloatField(default=None, null=True)
    max_grade = models.FloatField(default=None, null=True)
    avg_grade = models.FloatField(default=None, null=True)

    class Meta:
        unique_together = ('name', 'assignment_fk',)

    # def get_full_grade(self):
    #     return self.full_grade


class Grade(models.Model):
    question = models.ForeignKey(Question, related_name="question_grade", on_delete=models.CASCADE)
    student = models.ForeignKey(User, related_name="student_grade",on_delete=models.CASCADE)
    # value = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(question.get_full_grade())])
    value = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    delay = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)]) # eg. 40%
    final_grade = models.FloatField(null=True, blank=True)


class AssignmentGrade(models.Model):
    assignment = models.ForeignKey(Assignment,related_name="assignment_grade",on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(User, related_name="student_assignment_grade",on_delete=models.CASCADE)
    value = models.FloatField(null=True, blank=True)


class ClassGrade(models.Model):
    class_fk = models.ForeignKey(Class,related_name="class_grade",on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(User, related_name="student_class_grade",on_delete=models.CASCADE)
    value = models.FloatField(null=True, blank=True)
