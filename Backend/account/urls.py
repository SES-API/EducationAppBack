from django.contrib import admin
from django.urls import path,include,re_path

from .views import SendRegisterEmail,SendResetPasswordEmail,ResetPasswordView


app_name='account'
urlpatterns = [

    path('send_register_email/',SendRegisterEmail.as_view(),name='send_register_email'),
    path('send_reset_password_email/',SendResetPasswordEmail.as_view(),name='send_reset_password_email'),
    path('reset_password/',ResetPasswordView.as_view(),name='reset_password')
]