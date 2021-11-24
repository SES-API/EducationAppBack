from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
import django_filters.rest_framework
from django.db.models import Avg, Max, Min

User_Model=get_user_model()


class AssignmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Assignment
        fields=["id", "name","date","is_graded","class_fk","assignment_question"]
        extra_kwargs = {
            'assignment_question' : {'read_only':True},
        }


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields=['value', 'delay', 'student', 'question']



class QuestionSerializer(serializers.ModelSerializer):
    question_grade=GradeSerializer(many=True, required=False) #Role: teacher/ta vs student

    min_grade = serializers.SerializerMethodField('calculate_min')
    max_grade = serializers.SerializerMethodField('calculate_max')
    avg_grade = serializers.SerializerMethodField('calculate_avg')

    def calculate_min(self, question):
        return Grade.objects.filter(question=question).aggregate(Min('value'))
    def calculate_max(self, question):
        return Grade.objects.filter(question=question).aggregate(Max('value'))
    def calculate_avg(self, question):
        return Grade.objects.filter(question=question).aggregate(Avg('value'))
        
    class Meta:
        model = Question
        fields=['name', 'weight','is_graded', 'avg_grade', 'min_grade', 'max_grade','question_grade']
        extra_kwargs = {
            'avg_grade' : {'read_only':True},
            'min_grade' : {'read_only':True},
            'max_grade' : {'read_only':True},
            'question_grade' : {'read_only':True},
        }



class AssignmentRetrieveSerializer(serializers.ModelSerializer):
    assignment_question=QuestionSerializer(many=True)
        
    class Meta:
        model = Assignment
        fields=["id", "name","date","is_graded","assignment_question"]
        # , 'avg_grade', 'min_grade', 'max_grade'
        extra_kwargs = {
            'class_fk' : {'read_only':True},
        }


class SetQuestionGrades(serializers.ModelSerializer):
    value = serializers.IntegerField(required=True)
    delay = serializers.IntegerField(required=False)
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
            raise serializers.ValidationError(('There is no student with this id for this question'))
        return data

