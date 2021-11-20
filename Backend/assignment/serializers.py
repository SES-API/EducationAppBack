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
    # (min_grade, max_grade, avg_grade) = calculate()

    # def calculate(self):
    #     grades = Grade.objects.all()
    #     min_g = None
    #     max_g = None
    #     avg_g = None
    #     for q in self.assignment_question:

    class Meta:
        model = Assignment
        fields=["id", "name","date","is_graded","class_fk","assignment_question","min_grade", "max_grade", "avg_grade"]
        extra_kwargs = {
            # 'assignment_question' : {'read_only':True},
            'class_fk' : {'read_only':True},
        }


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields="__all__"


class SetQuestionGrades(serializers.ModelSerializer):
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


# class AssignmentGradeSerializer(serializers.ModelSerializer):
    # assignment_grade = serializers.SerializerMethodField('calculate_grade')

    # def calculate_grade(self, obj):
    #     assignment_id = obj.pk
    #     assignment_questions = Assignment.objects.filter(id=assignment_id)[0].assignment_question
    #     sum_grade = 0
    #     sum_weight = 0
    #     for question in assignment_questions.all():
    #         weight = question.weight
    #         sum_weight += weight
    #         grades = Grade.objects.filter(question = question)
    #         for grade in grades:
    #             sum_grade += grade.delay * grade.value * weight
    #     return sum_grade/sum_weight

    # class Meta:
    #     model = Grade
    #     fields=["question", "student", "value", "delay"]