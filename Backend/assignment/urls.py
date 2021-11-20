from django.contrib import admin
from django.urls import path,include,re_path
from .views import *

app_name='assignment'


urlpatterns = [
    path('', CreateAssignment.as_view(), name='create_assignment'),
    # pk is assignment id
    path('<int:pk>', AssignmentObject.as_view(), name='assignment_detail'),
    # pk is class id:
    path('list/<int:pk>', AssignmentList.as_view(), name='assignments'),
    # pk is assignment id:
    path('add_question/<int:pk>', AddQuestion.as_view(), name='add_question')
]