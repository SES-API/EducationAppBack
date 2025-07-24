from django.contrib import admin
from django.urls import path,include,re_path
from .views import *


app_name='account'

urlpatterns = [
    path('register/', RegisterationView.as_view(), name='register'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('send_register_email/',SendRegisterEmail.as_view(),name='send_register_email'),
    path('send_reset_password_email/',SendResetPasswordEmail.as_view(),name='send_reset_password_email'),
    path('reset_password/',ResetPasswordView.as_view(),name='reset_password'),
    path('user/', GetUserInfo.as_view(), name='user'),
    path('login/', TokenAuthenticationView.as_view(), name='login'),
    path('profile/<int:pk>', GetProfileView.as_view(), name='profile'),
    path('settings/profile/', UpdateProfileView.as_view(), name='settings_profile'),
    path('settings/delete/', DeleteUserView.as_view(), name='settings_delete'),
    #add, see list, search by name of degree
    path('degree/', DegreeList.as_view(), name='degree'),

]