from django.contrib import admin
from django.urls import path,include,re_path
from .views import *

app_name='class'


urlpatterns = [
    path('', ClassList.as_view(), name='classes'),
    path('<int:pk>', ClassObject.as_view(), name='class_object'),
    #set ta and teacher for a class urls:
    path('set_teacher/', SetTeacher.as_view(), name='set_teacher'),
    path('set_headta/', SetHeadTa.as_view(), name='set_headta'),
    path('set_ta/', SetTa.as_view(), name='set_ta'),

    path('set_headta_email/', SetHeadTaWithEmail.as_view(), name='set_headta_email'),
    path('add_ta_email/', AddTaWithEmail.as_view(), name='add_ta_email'),

    path('myclasses/', MyClasses.as_view(), name='myclasses'),
    # join and leave class as an student
    path('join_class/', JoinClass.as_view(), name='join_class'),
    path('leave_class/', LeaveClass.as_view(), name='leave_class'),
    #university list and create with srach base on name
    path('university/', UniversityList.as_view(), name='leave_class'),

    path('students_id_list/<int:pk>', ClassStudentsListForTeacherOrTa.as_view(), name='class_object_with_student_id'),
]