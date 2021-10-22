from django.contrib import admin
from django.urls import path,include,re_path
# from rest_framework import routers
from .views import *


app_name='account'

# router = routers.SimpleRouter()
# router.register('register', RegisterationView)


urlpatterns = [
    path('register/', RegisterationView.as_view(), name='register'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('send_register_email/',SendRegisterEmail.as_view(),name='send_register_email'),
    path('send_reset_password_email/',SendResetPasswordEmail.as_view(),name='send_reset_password_email'),
    path('reset_password/',ResetPasswordView.as_view(),name='reset_password')
]