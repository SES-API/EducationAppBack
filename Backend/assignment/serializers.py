from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
import django_filters.rest_framework
from django.db.models import Avg, Max, Min
from class_app.serializers import ClassPersonSerializer


User_Model=get_user_model()


class GradeListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if self.context.get('is_student') == True:
            user_id = self.context.get('user_id')
            data = data.filter(student=user_id)
        return super(GradeListSerializer, self).to_representation(data)


class GradeSerializer(serializers.ModelSerializer):
    student = ClassPersonSerializer()
    class Meta:
        model = Grade
        list_serializer_class = GradeListSerializer
        fields=['value', 'delay', 'student', 'final_grade']


class QuestionSerializer(serializers.ModelSerializer):
    question_grade=GradeSerializer(many=True, required=False)

    def get_serializer_context(self):
        context={'user_id' : self.context.get('user_id'), 'is_student' : self.context.get('is_student')}
        return context

    class Meta:
        model = Question
        fields=['id','name', 'full_grade', 'not_graded_count', 'is_graded', 'avg_grade', 'min_grade', 'max_grade','question_grade']
        extra_kwargs = {
            'assignment_fk' : {'read_only':True},
            'avg_grade' : {'read_only':True},
            'min_grade' : {'read_only':True},
            'max_grade' : {'read_only':True},
            'question_grade' : {'read_only':True},
            'not_graded_count' : {'read_only':True},
            'is_graded' : {'read_only':True},
        }


class AddQuestionSerializer(serializers.ModelSerializer):
    def get_serializer_context(self):
        context={'user_id' : self.context.get('user_id'), 'is_student' : self.context.get('is_student')}
        return context

    def validate(self, data):
        assignment_fk = self.context['assignment_fk']
        student_count = Assignment.objects.filter(id=assignment_fk)[0].class_fk.students.count()
        data['not_graded_count'] = student_count
        data['is_graded'] = True
        if(student_count!=0):
            data['is_graded'] = False
        grade_sum = 0
        for question in Question.objects.filter(assignment_fk = assignment_fk):
            grade_sum += question.full_grade
            if data.get('name') == question.name:
                raise serializers.ValidationError(('There is another question with this name in this assignment.'))
        if grade_sum + data['full_grade'] != 100:
            raise serializers.ValidationError(('question grades must have sum of 100.'))
        return data

    class Meta:
        model = Question
        fields=['id','name', 'full_grade', 'not_graded_count', 'is_graded']
        extra_kwargs = {
            'not_graded_count' : {'read_only':True},
            'is_graded' : {'read_only':True},
        }



class CreateAssignmentSerializer(serializers.ModelSerializer):
    assignment_question = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Assignment
        fields=['id', 'name','date', 'weight', 'is_graded', 'not_graded_count','class_fk','assignment_question']
        extra_kwargs = {
            'not_graded_count' : {'read_only':True},
            'is_graded' : {'read_only':True},
        }

    def create(self, validated_data):
        questions = validated_data.pop('assignment_question')
        question_names = set()
        for q in questions:
            if question_names.__contains__(q['name']):
                raise serializers.ValidationError(('Questions of one assignment must have unique names.'))
            question_names.add(q['name'])

        assignment = Assignment.objects.create(**validated_data)
        for q in questions:
            Question.objects.create(assignment_fk = assignment, **q)
        return assignment

    def validate(self, data):
        questions = data.get('assignment_question')
        data['not_graded_count'] = 0
        data['is_graded'] = True
        if questions:
            grade_sum = 0
            for q in questions:
                grade_sum += q['full_grade']
                q['not_graded_count'] = data.get('class_fk').students.count()
            if grade_sum != 100:
                raise serializers.ValidationError(('question grades must have sum of 100.'))
            data['not_graded_count'] = len(questions)
            data['is_graded'] = False
        return data

class AssignmentGradeListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if self.context.get('is_student') == True:
            user_id = self.context.get('user_id')
            data = data.filter(student=user_id)
        return super(AssignmentGradeListSerializer, self).to_representation(data)


class AssignmentGradeSerializer(serializers.ModelSerializer):
    student = ClassPersonSerializer()
    class Meta:
        model = AssignmentGrade
        list_serializer_class = AssignmentGradeListSerializer
        fields=['value', 'student', 'assignment']



class AssignmentRetrieveSerializer(serializers.ModelSerializer):
    assignment_question=QuestionSerializer(many=True)
    assignment_grade=AssignmentGradeSerializer(many=True)

    def get_serializer_context(self):
        context={'user_id' : self.context.get('user_id'), 'is_student' : self.context.get('is_student')}
        return context

    def validate(self, data):
        for assignment in Assignment.objects.filter(class_fk = self.context['class_fk']):
            if data.get('name') == assignment.name:
                raise serializers.ValidationError(('There is another assignment with this name in this class.'))
        return data

    class Meta:
        model = Assignment
        fields=['id', 'name','date','assignment_question', 'assignment_grade', 'avg_grade', 'min_grade', 'max_grade', 'is_graded', 'not_graded_count']
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
        fields='__all__'


    def set_grade(self, data):
        question=data['question']
        assignment = question.assignment_fk
        student = data['student']

        grade = Grade.objects.filter(question = question, student=student)
        if(grade):
            grade = grade[0]
            assignment_grade = AssignmentGrade.objects.filter(assignment=assignment, student=student)
            val = round((grade.final_grade * question.weight),2)
            assignment_grade= assignment_grade[0]
            assignment_grade.value -= val
            grade.value = data['value']
            grade.delay = data['delay']
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

    def count_graded_assignment(self, assignment):
        graded = 0
        for question in assignment.assignment_question.all():
            if question.not_graded_count == 0:
                graded += 1

        if graded != 0:
            assignment.is_graded = False
        else:
            assignment.is_graded = True
        assignment.save()

    def count_graded_question(self, question):
        question_num = question.assignment_fk.class_fk.students.all().count()
        grades_num = Grade.objects.filter(question=question).count()
        not_graded = question_num - grades_num

        if not_graded > 0:
            question.is_graded = False
        else:
            question.is_graded = True
        question.save()

    def claculate_aggregates(self, assignment, question):
        question.min_grade = Grade.objects.filter(question=question).aggregate(Min('final_grade'))['final_grade__min']
        question.max_grade = Grade.objects.filter(question=question).aggregate(Max('final_grade'))['final_grade__max']
        question.avg_grade = Grade.objects.filter(question=question).aggregate(Avg('final_grade'))['final_grade__avg']
        question.save()
        self.count_graded_question(question)

        assignment.min_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Min('value'))['value__min']
        assignment.max_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Max('value'))['value__max']
        assignment.avg_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Avg('value'))['value__avg']
        assignment.save()
        self.count_graded_assignment(assignment)

    

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
