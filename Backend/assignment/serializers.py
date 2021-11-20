from rest_framework import serializers
from .models import *
from django.shortcuts import get_object_or_404
import django_filters.rest_framework


class AssignmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Assignment
        fields="__all__"
        extra_kwargs = {
            'questions' : {'read_only':True}
        }


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields="__all__"