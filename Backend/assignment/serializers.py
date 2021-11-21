from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
import django_filters.rest_framework


User_Model=get_user_model()


class AssignmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Assignment
        fields=["id", "name","date","is_graded","class_fk","assignment_question"]
        extra_kwargs = {
            'assignment_question' : {'read_only':True},
        }


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields="__all__"
        # fields=['name', 'weight', 'assignment_fk','is_graded']


class AssignmentRetrieveSerializer(serializers.ModelSerializer):
    assignment_question=QuestionSerializer(many=True)
    class Meta:
        model = Assignment
        fields=["id", "name","date","is_graded","assignment_question"]
        extra_kwargs = {
            'class_fk' : {'read_only':True},
        }


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields="__all__"


class SetQuestionGrades(serializers.ModelSerializer):
    # value and delay should be required?
    class Meta:
        model = Grade
        fields="__all__"

    def validate(self, data):
        question=data['question']
        if not(question):
            raise serializers.ValidationError(('There is no question with this id'))
        assignment = question.assignment_fk
        class_ = assignment.class_fk
        all_class_students = class_.students.all()
        student = data['student']
        if(student not in all_class_students):
            raise serializers.ValidationError(('There is no student with {} id in this session').format(item))
        return data

