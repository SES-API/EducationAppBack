from django.contrib import admin
from django.urls import path,include,re_path
from .views import *

app_name='assignment'


urlpatterns = [
    # add an assignment by teacher/ta (get class_id in body)
    path('', CreateAssignment.as_view(), name='create_assignment'),

    # get/update/delete an assignment ( pk is assignment id )
    path('<int:pk>', AssignmentObject.as_view(), name='assignment_detail'),
    
    # add aquestion to an assignment ( pk is assignment id )
    path('add_question/<int:pk>', AddQuestion.as_view(), name='add_question'),
    
    # get/update/delete a question ( pk is question id )
    path('question/<int:pk>', QuestionObject.as_view(), name='question_detail'),

    # add question grades for students
    path('add_grade/', GradeQuestion.as_view(), name='add_grade'),

    # list of class assignment ( pk is class id )
    path('class/<int:pk>', AssignmentList.as_view(), name='assignments'),

    # list of assignment grades ( pk is assignment id )
    path('grades/<int:pk>', AssignmentGrades.as_view(), name='assignment_grades'),

    # list of class grades ( pk is class id )
    path('class/grades/<int:pk>', ClassGrades.as_view(), name='class_grades'),
]