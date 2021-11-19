from rest_framework import serializers
from .models import *
from django.shortcuts import get_object_or_404
import django_filters.rest_framework
# from rest_framework.validators import UniqueTogetherValidator



class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields="__all__"

        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Question.objects.all(),
        #         fields=['name', 'assignment_id']
        #     )

class AssignmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Assignment
        fields="__all__"
        extra_kwargs = {
            'questions' : {'read_only':True}
        }