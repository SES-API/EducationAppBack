from django.contrib import admin
from django.urls import path,include,re_path
from .views import *

app_name='assignment'


urlpatterns = [
    path('', CreateAssignment.as_view(), name='create_assignment'),
    path('list/<int:pk>', AssignmentList.as_view(), name='assignments'),
    path('add_question/<int:pk>', AddQuestion.as_view(), name='add_question')
]