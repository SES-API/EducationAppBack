from datetime import datetime, timedelta, timezone
from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
from django.apps import apps
from class_app.models import Class


UserModel=get_user_model()

class atend(models.Model):
    student = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    Present=models.BooleanField(null=True)

class Session(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField(null=True,default=datetime.today)
    start_time = models.TimeField(default=datetime.now)
    end_time = models.TimeField(default=(datetime.now() + timedelta(hours=2)))
    atends = models.ManyToManyField(atend,related_name="user_session")
    session_class = models.ForeignKey(Class,related_name="class_session",on_delete=models.CASCADE,null=True)




