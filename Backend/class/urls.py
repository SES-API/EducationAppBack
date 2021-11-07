from django.contrib import admin
from django.urls import path,include,re_path
from .views import *

app_name='class'


urlpatterns = [
    path('', ClassList.as_view(), name='classes'),
    path('<int:pk>', ClassObject.as_view(), name='class_object'),
    #set ta and teacher for a class urls:
    path('set_teacher/', SetTeacher.as_view(), name='set_teacher'),
    path('set_ta/', SetTa.as_view(), name='set_ta'),
    path('myclasses/', MyClasses.as_view(), name='myclasses'),
    # join and leave class as an student
    path('join_class/', JoinClass.as_view(), name='join_class'),
    path('leave_class/', LeaveClass.as_view(), name='leave_class')
]