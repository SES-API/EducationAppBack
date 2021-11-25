from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
import django_filters.rest_framework
from django.db.models import Avg, Max, Min

User_Model=get_user_model()


class CreateAssignmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Assignment
        fields=["id", "name","date","is_graded","class_fk","assignment_question"]
        extra_kwargs = {
            'assignment_question' : {'read_only':True},
        }

class GradeListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if self.context.get("is_student") == True:
            user_id = self.context.get("user_id")
            data = data.filter(student=user_id)
        return super(GradeListSerializer, self).to_representation(data)


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        list_serializer_class = GradeListSerializer
        fields=['value', 'delay', 'student', 'question', 'final_grade']


class AssignmentGradeListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if self.context.get("is_student") == True:
            user_id = self.context.get("user_id")
            data = data.filter(student=user_id)
        return super(AssignmentGradeListSerializer, self).to_representation(data)


class AssignmentGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentGrade
        list_serializer_class = AssignmentGradeListSerializer
        fields=['value', 'student', 'assignment']


class QuestionSerializer(serializers.ModelSerializer):
    question_grade=GradeSerializer(many=True, required=False)
    is_graded = serializers.SerializerMethodField('check_graded')
    min_grade = serializers.SerializerMethodField('calculate_min')
    max_grade = serializers.SerializerMethodField('calculate_max')
    avg_grade = serializers.SerializerMethodField('calculate_avg')

    def get_serializer_context(self):
        context={'user_id' : self.context.get("user_id"), 'is_student' : self.context.get("is_student")}
        return context


    def check_graded(self, question):
        return Grade.objects.filter(question=question).count() == question.assignment_fk.class_fk.students.all().count()
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
    assignment_grade=AssignmentGradeSerializer(many=True)
    is_graded = serializers.SerializerMethodField('check_graded')
    min_grade = serializers.SerializerMethodField('calculate_min')
    max_grade = serializers.SerializerMethodField('calculate_max')
    avg_grade = serializers.SerializerMethodField('calculate_avg')

    def calculate_min(self, assignment):
        return AssignmentGrade.objects.filter(assignment=assignment).aggregate(Min('value'))
    def calculate_max(self, assignment):
        return AssignmentGrade.objects.filter(assignment=assignment).aggregate(Max('value'))
    def calculate_avg(self, assignment):
        return AssignmentGrade.objects.filter(assignment=assignment).aggregate(Avg('value'))

    def get_serializer_context(self):
        context={'user_id' : self.context.get("user_id"), 'is_student' : self.context.get("is_student")}
        return context

    def check_graded(self, assignment):
        for question in assignment.assignment_question.all():
            if question.is_graded == False:
                return False
        return True

    class Meta:
        model = Assignment
        fields=["id", "name","date","is_graded","assignment_question", "assignment_grade", 'avg_grade', 'min_grade', 'max_grade']
        extra_kwargs = {
            'class_fk' : {'read_only':True},
        }


class SetQuestionGrades(serializers.ModelSerializer):
    value = serializers.IntegerField(required=True)
    delay = serializers.FloatField(required=True)
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
