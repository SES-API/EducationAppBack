from django.contrib import admin
from django.urls import path,include,re_path
from .views import SessionsOfClass,SetAtendsOfSession

app_name='attendance'


urlpatterns = [
    path('<int:pk>', SessionsOfClass.as_view(), name='SessionsOfClass'),
    path('setpresent', SetAtendsOfSession.as_view(), name='SetAtendsOfSession'),
    
]