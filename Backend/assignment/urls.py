from django.contrib import admin
from django.urls import path,include,re_path
from .views import *

app_name='assignment'


urlpatterns = [
    path('', AssignmentList.as_view(), name='assignments'),
    path('add_question/', AddQuestion.as_view(), name='add_question')

]