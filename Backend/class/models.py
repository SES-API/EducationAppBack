from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.



UserModel=get_user_model()

class University(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Class(models.Model):
    SEMESTER = (
        ('Spring', 'Spring'),
        ('Fall', 'Fall'),
    )

    name=models.CharField(max_length=50,unique=True)
    description=models.TextField(max_length=600,null=True)

    teachers=models.ManyToManyField(UserModel,related_name="class_teacher")
    tas=models.ManyToManyField(UserModel,related_name="class_ta")
    students=models.ManyToManyField(UserModel,related_name="class_student")

    owner=models.ForeignKey(UserModel,related_name="class_owner",on_delete=models.SET_NULL,null=True)
    university=models.ForeignKey(University, on_delete=models.SET_NULL,related_name="class_university",null=True)

    password=models.CharField(max_length=6,null=True)
    semester=models.CharField(choices=SEMESTER,max_length=10)
    image=models.ImageField(upload_to="images/class_pics",null=True)
    is_active=models.BooleanField(default=False)

    def __str__(self):
        return self.name

    
