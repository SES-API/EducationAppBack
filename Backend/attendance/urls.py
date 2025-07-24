from django.contrib import admin
from django.urls import path,include,re_path
from .views import SessionDestroy, SessionsOfClass, SessionsUpdate,SetAtendsOfSession,UserAtendsForClass

app_name='attendance'


urlpatterns = [
    path('class_session/<int:pk>', SessionsOfClass.as_view(), name='SessionsOfClass'),
    path('my/<int:pk>', UserAtendsForClass.as_view(), name='UserAtendsForClass'),
    path('setpresent', SetAtendsOfSession.as_view(), name='SetAtendsOfSession'),
    path('session/update/<int:pk>', SessionsUpdate.as_view(), name='SessionsUpdate'),
    path('session/remove/<int:pk>', SessionDestroy.as_view(), name='SessionDestroy'),
    
]