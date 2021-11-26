from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
from django.apps import apps
from class_app.models import Class


UserModel=get_user_model()

class atend(models.Model):
    students = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    Present=models.BooleanField(default=False)

class Session(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField()
    atends = models.ManyToManyField(atend,related_name="user_session")
    session_class = models.ForeignKey(Class,related_name="class_session",on_delete=models.CASCADE,null=True)




