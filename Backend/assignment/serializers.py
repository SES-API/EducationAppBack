from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
import django_filters.rest_framework
from django.db.models import Avg, Max, Min
from class_app.serializers import ClassPersonSerializer


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
    student = ClassPersonSerializer()
    class Meta:
        model = Grade
        list_serializer_class = GradeListSerializer
        fields=['value', 'delay', 'student', 'final_grade']


class AssignmentGradeListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if self.context.get("is_student") == True:
            user_id = self.context.get("user_id")
            data = data.filter(student=user_id)
        return super(AssignmentGradeListSerializer, self).to_representation(data)


class AssignmentGradeSerializer(serializers.ModelSerializer):
    student = ClassPersonSerializer()
    class Meta:
        model = AssignmentGrade
        list_serializer_class = AssignmentGradeListSerializer
        fields=['value', 'student', 'assignment']


class QuestionSerializer(serializers.ModelSerializer):
    question_grade=GradeSerializer(many=True, required=False)

    def get_serializer_context(self):
        context={'user_id' : self.context.get("user_id"), 'is_student' : self.context.get("is_student")}
        return context


    def validate(self, data):
        for question in Question.objects.filter(assignment_fk = self.context['assignment_fk']):
            if data.get('name') == question.name:
                raise serializers.ValidationError(("There is another question with this name in this assignment."))
        return data

    class Meta:
        model = Question
        fields=['id','name', 'weight','is_graded', 'avg_grade', 'min_grade', 'max_grade','question_grade']
        extra_kwargs = {
            'assignment_fk' : {'read_only':True},
            'avg_grade' : {'read_only':True},
            'min_grade' : {'read_only':True},
            'max_grade' : {'read_only':True},
            'question_grade' : {'read_only':True},
        }



class AssignmentRetrieveSerializer(serializers.ModelSerializer):
    assignment_question=QuestionSerializer(many=True)
    assignment_grade=AssignmentGradeSerializer(many=True)

    def get_serializer_context(self):
        context={'user_id' : self.context.get("user_id"), 'is_student' : self.context.get("is_student")}
        return context

    def validate(self, data):
        for assignment in Assignment.objects.filter(class_fk = self.context['class_fk']):
            if data.get('name') == assignment.name:
                raise serializers.ValidationError(("There is another assignment with this name in this class."))
        return data

    class Meta:
        model = Assignment
        fields=["id", "name","date","assignment_question", "assignment_grade", 'avg_grade', 'min_grade', 'max_grade',"is_graded"]
        extra_kwargs = {
            'class_fk' : {'read_only':True},
            'avg_grade' : {'read_only':True},
            'min_grade' : {'read_only':True},
            'max_grade' : {'read_only':True},
            'assignment_grade' : {'read_only':True},
        }




class SetQuestionGrades(serializers.ModelSerializer):
    value = serializers.IntegerField(required=True)
    delay = serializers.FloatField(required=True)
    class Meta:
        model = Grade
        fields="__all__"


    def set_grade(self, data):
        question=data["question"]
        assignment = question.assignment_fk
        student = data["student"]

        grade = Grade.objects.filter(question = question, student=student)
        if(grade):
            grade = grade[0]
            assignment_grade = AssignmentGrade.objects.filter(assignment=assignment, student=student)
            val = round((grade.final_grade * question.weight),2)
            assignment_grade= assignment_grade[0]
            assignment_grade.value -= val
            grade.value = data["value"]
            grade.delay = data["delay"]
            grade.final_grade = round((grade.value*(1-grade.delay)), 2)
            grade.save()
            val = round((grade.final_grade * question.weight),2)
            assignment_grade.value += val
            assignment_grade.save()
        else:
            grade = Grade.objects.create(student=student, question=question, value=data['value'], delay=data['delay'])
            grade.final_grade = round((grade.value*(1-grade.delay)), 2)
            grade.save()

            assignment_grade = AssignmentGrade.objects.filter(assignment=assignment, student=student)
            val = round((grade.final_grade * question.weight),2)
            print(val)
            if(assignment_grade):
                assignment_grade= assignment_grade[0]
                assignment_grade.value += val
                assignment_grade.save()
            else:
                AssignmentGrade.objects.create(assignment=assignment, student=student, value=val)

    def check_graded_assignment(self, assignment):
        if assignment.assignment_question.count() == 0:
            return False
        for question in assignment.assignment_question.all():
            if question.is_graded == False:
                assignment.is_graded = False
                assignment.save()
                return False
        assignment.is_graded = True
        assignment.save()
        return True

    def check_graded_question(self, question):
        if Grade.objects.filter(question=question).count() >= question.assignment_fk.class_fk.students.all().count():
            question.is_graded = True
            question.save()
            return True
        else:
            question.is_graded = False
            question.save()
            return False

    def claculate_aggregates(self, assignment, question):
        question.min_grade = Grade.objects.filter(question=question).aggregate(Min('final_grade'))['final_grade__min']
        question.max_grade = Grade.objects.filter(question=question).aggregate(Max('final_grade'))['final_grade__max']
        question.avg_grade = Grade.objects.filter(question=question).aggregate(Avg('final_grade'))['final_grade__avg']
        question.is_graded = self.check_graded_question(question)
        question.save()

        assignment.min_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Min('value'))['value__min']
        assignment.max_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Max('value'))['value__max']
        assignment.avg_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Avg('value'))['value__avg']
        assignment.is_graded = self.check_graded_assignment(assignment)
        assignment.save()
    

    def validate(self, data):
        question=data['question']
        if not(question):
            raise serializers.ValidationError(('There is no question with this id.'))
        assignment = question.assignment_fk
        class_ = assignment.class_fk
        all_class_students = class_.students.all()
        student = data['student']
        if(student not in all_class_students):
            raise serializers.ValidationError(('There is no student with this id for this question.'))
        
        if(self.context['user'] == class_.headta or self.context['user'] in class_.teachers.all() or self.context['user'] in class_.tas.all()):
            self.set_grade(data)
            self.claculate_aggregates(assignment, question)
            return data
        else:
            raise serializers.ValidationError(('You do not have permission to perform this action.'))
