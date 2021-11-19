from django.contrib import admin
from django.urls import path,include,re_path
from .views import SessionsOfClass,SetAtendsOfSession,UserAtendsForClass

app_name='attendance'


urlpatterns = [
    path('<int:pk>', SessionsOfClass.as_view(), name='SessionsOfClass'),
    path('my/<int:pk>', UserAtendsForClass.as_view(), name='UserAtendsForClass'),
    path('setpresent', SetAtendsOfSession.as_view(), name='SetAtendsOfSession'),
    
]