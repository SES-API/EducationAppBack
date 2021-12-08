from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.base import Model
# Create your models here.


UserModel=get_user_model()


class Semester(models.Model):
    semester=models.CharField(max_length=60)
    def __str__(self):
        return self.semester


class University(models.Model):
    name=models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Class(models.Model):

    name=models.CharField(max_length=50)
    description=models.TextField(max_length=600,null=True)

    teachers=models.ManyToManyField(UserModel,related_name="class_teacher")
    headta=models.ForeignKey(UserModel,related_name="class_headta",on_delete=models.SET_NULL,null=True)
    tas=models.ManyToManyField(UserModel,related_name="class_ta")
    students=models.ManyToManyField(UserModel,related_name="class_student",through="ClassStudents")
    owner=models.ForeignKey(UserModel,related_name="class_owner",on_delete=models.SET_NULL,null=True)
    university=models.ForeignKey(University, on_delete=models.SET_NULL,related_name="class_university",null=True)
    password=models.CharField(max_length=6,null=True)
    has_password = models.BooleanField(default=False)
    # semester=models.CharField(max_length=30)
    semester=models.ForeignKey(Semester,on_delete=models.SET_NULL,related_name="class_semester",null=True)
    image=models.ImageField(upload_to="images/class_pics",null=True)
    is_active=models.BooleanField(default=False)

    def __str__(self):
        return self.name

    
class ClassStudents(models.Model):
    student = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    Class = models.ForeignKey(Class, on_delete=models.CASCADE)
    studentid=models.CharField(max_length=10)


    class Meta:
        unique_together = ('studentid', 'Class',)


