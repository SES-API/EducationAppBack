from django.contrib import admin
from django.urls import path,include,re_path

from .views import SendRegisterEmail


app_name='account'
urlpatterns = [

    path('send_register_email/',SendRegisterEmail.as_view(),name='send_register_view')
]