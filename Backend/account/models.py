from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
# Create your models here.

class User(AbstractUser):
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    password = models.CharField(
        blank=False,
        max_length=30,
        validators=[RegexValidator(regex="^(?=.*[A-Z])",message='Password must contain at least one uppercase letter.'),
            RegexValidator(regex="^(?=.*[0-9])",message='Password must contain at least one number.'),
            RegexValidator(regex="^(?=.{8,})",message='Password must be eight characters or longer.')]
        )
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    degree = models.CharField(max_length=30, null=True, blank=True)
    university = models.CharField(max_length=50, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='images/profile_pics/', null=True, blank=True)
    is_hidden = models.BooleanField(default=False)