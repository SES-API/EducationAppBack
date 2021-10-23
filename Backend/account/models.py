from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
# Create your models here.

class User(AbstractUser):
    username = models.CharField(unique=True, blank=False, max_length=30)
    password = models.CharField(
        blank=False,
        max_length=30,
        validators=[RegexValidator(regex="^(?=.*[A-Z])",message='Password must contain at least one uppercase letter.'),
            RegexValidator(regex="^(?=.*[0-9])",message='Password must contain at least one number.'),
            RegexValidator(regex="^(?=.{8,})",message='Password must be eight characters or longer.')]
        )
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
