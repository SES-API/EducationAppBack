from django.contrib import admin
from django.urls import path,include,re_path
from .views import *

app_name='assignment'


urlpatterns = [
    # add an assignment by teacher/ta (get class_fk in body)
    path('', CreateAssignment.as_view(), name='create_assignment'),

    # get /update/delete an assignment ( pk is assignment id )
    # todo --------> if student: see grade for each question, if teacher/ta see all grades for each question
    # todo --------> min/max/avg one question
    # todo --------> min/max/avg one assignment
    path('<int:pk>', AssignmentObject.as_view(), name='assignment_detail'),
    
    # add aquestion to an assignment ( pk is assignment id )
    path('add_question/<int:pk>', AddQuestion.as_view(), name='add_question'),
    
    # get/update/delete a question ( pk is question id )
    path('question/<int:pk>', QuestionObject.as_view(), name='question_detail'),

    # add one question grade for a student 
    # todo ---------> set all grades 0 at first
    path('add_grade/', GradeQuestion.as_view(), name='add_grade'),

    # list of class assignment ( pk is class id )
    path('class/<int:pk>', AssignmentList.as_view(), name='assignments'),

    # see grades of one assignment by Role (teacher/ta - student)
    path('assignment_grades/<int:pk>', AssignmentGradeList.as_view(), name='question_grades'),
]

# todo ---------> where and when should i change 'is_graded'=true ?