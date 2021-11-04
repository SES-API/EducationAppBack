from django.contrib import admin
from django.urls import path,include,re_path
from .views import *

app_name='class'


urlpatterns = [
    path('', ClassList.as_view(), name='classes'),
    path('<int:pk>', ClassObject.as_view(), name='class_object')

]