from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
import django_filters.rest_framework
from django.db.models import Avg, Max, Min
from class_app.serializers import ClassPersonSerializer
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from class_app.models import ClassStudents

User_Model=get_user_model()


def count_graded_question(question):
    student_num = question.assignment_fk.class_fk.students.all().count()
    grades_num = Grade.objects.filter(question=question).count()
    not_graded = student_num - grades_num
    question.not_graded_count = not_graded

    if not_graded > 0:
        question.is_graded = False
    else:
        question.is_graded = True
    
    question.save()


def count_graded_assignment(assignment):
    not_graded = 0
    for question in assignment.assignment_question.all():
        if question.is_graded == False:
            not_graded += 1
    assignment.not_graded_count = not_graded

    if not_graded == 0:
        assignment.is_graded = True
    else:
        assignment.is_graded = False

    assignment.save()


@receiver(post_delete, sender=ClassStudents)
@receiver(post_save, sender=ClassStudents)
def student_num_changed(sender, **kwargs):
    class_ = kwargs['instance'].Class
    assignments = Assignment.objects.filter(class_fk = class_)
    for assignment in assignments:
        questions = Question.objects.filter(assignment_fk = assignment)
        for question in questions:
            count_graded_question(question)
        count_graded_assignment(assignment)


@receiver(post_delete, sender=Question)
def question_deleted(sender, **kwargs):
    print("1111111111111111")
    question = kwargs['instance']
    assignment = question.assignment_fk
    count_graded_assignment(assignment)
    students = assignment.class_fk.students.all()
    for student in students:
        has_asg_grade = True
        val=0
        valuesum=0
        totalsum=0
        for q in assignment.assignment_question.all():
            totalsum+=q.full_grade
            q_grade = q.question_grade.filter(student=student)
            if(q_grade):
                valuesum+=q_grade[0].value
            else:
                has_asg_grade = False
        val=round( ((valuesum*100)/totalsum), 2)

        if(has_asg_grade):
            assignment_grade = AssignmentGrade.objects.filter(assignment=assignment, student=student)
            if(assignment_grade):
                assignment_grade= assignment_grade[0]
                assignment_grade.value = val
                assignment_grade.save()
            else:
                AssignmentGrade.objects.create(assignment=assignment, student=student, value=val)
        else:
            assignment_grade = AssignmentGrade.objects.filter(assignment=assignment, student=student)
            assignment_grade.delete()

    asg_min_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Min('value'))['value__min']
    if(asg_min_grade):
        assignment.min_grade = round(asg_min_grade, 2)
    else:
        assignment.min_grade = None
    asg_max_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Max('value'))['value__max']
    if(asg_max_grade):
        assignment.max_grade = round(asg_max_grade, 2)
    else:
        assignment.max_grade = None
    asg_avg_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Avg('value'))['value__avg']
    if(asg_avg_grade):
        assignment.avg_grade = round(asg_avg_grade, 2)
    else:
        assignment.avg_grade = None
    assignment.save()




@receiver(post_save, sender=Grade)
def my_handler(sender, **kwargs):
    new_grade = kwargs['instance']
    question = new_grade.question
    assignment = question.assignment_fk

    q_min_grade = Grade.objects.filter(question=question).aggregate(Min('final_grade'))['final_grade__min']
    if(q_min_grade):
        question.min_grade = round(q_min_grade, 2)
    else:
        question.min_grade = None
    q_max_grade = Grade.objects.filter(question=question).aggregate(Max('final_grade'))['final_grade__max']
    if(q_max_grade):
        question.max_grade = round(q_max_grade, 2)
    else:
        question.max_grade = None
    q_avg_grade = Grade.objects.filter(question=question).aggregate(Avg('final_grade'))['final_grade__avg']
    if(q_avg_grade):
        question.avg_grade = round(q_avg_grade, 2)
    else:
        question.avg_grade = None
    question.save()

    has_asg_grade = True
    student = new_grade.student
    val=0
    valuesum=0
    totalsum=0
    for q in assignment.assignment_question.all():
        totalsum+=q.full_grade
        q_grade = q.question_grade.filter(student=student)
        if(q_grade):
            valuesum+=q_grade[0].value
        else:
            has_asg_grade = False
    val=round( ((valuesum*100)/totalsum), 2)

    if(has_asg_grade):
        assignment_grade = AssignmentGrade.objects.filter(assignment=assignment, student=student)
        if(assignment_grade):
            assignment_grade= assignment_grade[0]
            assignment_grade.value = val
            assignment_grade.save()
        else:
            AssignmentGrade.objects.create(assignment=assignment, student=student, value=val)
    else:
        assignment_grade = AssignmentGrade.objects.filter(assignment=assignment, student=student)
        assignment_grade.delete()


    asg_min_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Min('value'))['value__min']
    if(asg_min_grade):
        assignment.min_grade = round(asg_min_grade, 2)
    else:
        assignment.min_grade = None
    asg_max_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Max('value'))['value__max']
    if(asg_max_grade):
        assignment.max_grade = round(asg_max_grade, 2)
    else:
        assignment.max_grade = None
    asg_avg_grade = AssignmentGrade.objects.filter(assignment=assignment).aggregate(Avg('value'))['value__avg']
    if(asg_avg_grade):
        assignment.avg_grade = round(asg_avg_grade, 2)
    else:
        assignment.avg_grade = None
    assignment.save()



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
    id = serializers.IntegerField(required=False)
    question_grade=GradeSerializer(many=True, required=False)

    def get_serializer_context(self):
        context={'user_id' : self.context.get('user_id'), 'is_student' : self.context.get('is_student')}
        return context

    def validate(self, data):
        for question in Question.objects.filter(assignment_fk = self.context['assignment_fk']):
            if question.id!=data.get('id') and data.get('name') == question.name:
                raise serializers.ValidationError(('There is another question with this name in this assignment.'))
        return data

    class Meta:
        model = Question
        fields=['id','name', 'full_grade', 'not_graded_count', 'is_graded','question_grade', 'avg_grade', 'min_grade', 'max_grade']
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
        assignment = Assignment.objects.filter(id=assignment_fk)[0]
        student_count = assignment.class_fk.students.count()
        data['not_graded_count'] = student_count
        data['is_graded'] = True
        if(student_count!=0):
            data['is_graded'] = False
        for question in Question.objects.filter(assignment_fk = assignment_fk):
            if data.get('name') == question.name:
                raise serializers.ValidationError(('There is another question with this name in this assignment.'))
        assignment.is_graded = False
        assignment.not_graded_count += 1
        assignment_grades = AssignmentGrade.objects.filter(assignment=assignment)
        for assignment_grade in assignment_grades:
            assignment_grade.delete()
        assignment.min_grade = None
        assignment.max_grade = None
        assignment.avg_grade = None
        assignment.save()
        return data

    class Meta:
        model = Question
        fields=['id','name', 'full_grade', 'not_graded_count', 'is_graded']
        extra_kwargs = {
            'not_graded_count' : {'read_only':True},
            'is_graded' : {'read_only':True},
        }



class CreateAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields=['id', 'name','date', 'weight', 'is_graded', 'not_graded_count','class_fk']
        extra_kwargs = {
            'not_graded_count' : {'read_only':True},
            'is_graded' : {'read_only':True},
        }


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
    assignment_grade=AssignmentGradeSerializer(many=True, read_only=True)

    def get_serializer_context(self):
        context={'user_id' : self.context.get('user_id'), 'is_student' : self.context.get('is_student')}
        return context

    def validate(self, data):
        for assignment in Assignment.objects.filter(class_fk = self.context['class_fk']):
            if data.get('name') == assignment.name:
                raise serializers.ValidationError(('There is another assignment with this name in this class.'))
        return data

    def update(self, instance, validated_data):
        if (validated_data.get('name')):
            instance.name = validated_data.get('name')
        if(validated_data.get('date')):
            instance.date = validated_data.get('date')
        instance.save()

        questions = validated_data.get('assignment_question')
        question_names = set()
        for q in questions:
            if question_names.__contains__(q['name']):
                raise serializers.ValidationError(('Questions of one assignment must have unique names.'))
            question_names.add(q['name'])

        for q in questions:
            q_id = q.get('id', None)
            if(q_id):
                q_instance = instance.assignment_question.filter(id=q_id)[0]
                q_name = q.get('name')
                if(q_name and q_instance.name != q_name):
                    q_instance.name = q_name
                    q_instance.save()
                q_full_grade = q.get('full_grade')
                old_grade = q_instance.full_grade
                if(q_full_grade and q_full_grade != old_grade):
                    q_instance.full_grade = q_full_grade
                    q_instance.save()
                    for grade in Grade.objects.filter(question=q_id):
                        val = round( grade.value * (q_full_grade/old_grade), 2)
                        grade.value = val
                        grade.final_grade = round((val*(1-grade.delay)), 2)
                        grade.save()
            else:
                Question.objects.create(assignment_fk = instance.id ,**q)

        return instance


    class Meta:
        model = Assignment
        fields=['id', 'name','date','assignment_question', 'assignment_grade', 'avg_grade', 'min_grade', 'max_grade', 'is_graded', 'not_graded_count']
        extra_kwargs = {
            'class_fk' : {'read_only':True},
            'avg_grade' : {'read_only':True},
            'min_grade' : {'read_only':True},
            'max_grade' : {'read_only':True},
            'assignment_question' : {'read_only':True},
            'assignment_grade' : {'read_only':True},
        }



class SetQuestionGrades(serializers.ModelSerializer):
    value = serializers.IntegerField(required=True)
    delay = serializers.FloatField(required=True)
    class Meta:
        model = Grade
        fields='__all__'


    def set_question_grade(self, data):
        question=data['question']
        assignment = question.assignment_fk
        student = data['student']
        grade = Grade.objects.filter(question = question, student=student)
        if(grade):
            grade = grade[0]
            grade.value = data['value']
            grade.delay = data['delay']
            grade.final_grade = round((grade.value*(1-grade.delay)), 2)
            grade.save()
        else:
            grade = Grade.objects.create(student=student, question=question, value=data['value'], delay=data['delay'])
            grade.final_grade = round((grade.value*(1-grade.delay)), 2)
            grade.save()


    # def count_graded_question(self, question):
    #     student_num = question.assignment_fk.class_fk.students.all().count()
    #     grades_num = Grade.objects.filter(question=question).count()
    #     not_graded = student_num - grades_num
    #     question.not_graded_count = not_graded

    #     if not_graded > 0:
    #         question.is_graded = False
    #     else:
    #         question.is_graded = True
        
    #     question.save()


    # def count_graded_assignment(self, assignment):
    #     not_graded = 0
    #     for question in assignment.assignment_question.all():
    #         if question.is_graded == False:
    #             not_graded += 1
    #     assignment.not_graded_count = not_graded

    #     if not_graded == 0:
    #         assignment.is_graded = True
    #     else:
    #         assignment.is_graded = False

    #     assignment.save()


    def validate(self, data):
        question=data['question']
        if not(question):
            raise serializers.ValidationError(('There is no question with this id.'))
        
        if data.get('value') > question.full_grade:
            raise serializers.ValidationError((f'Maximum grade for question {question.name} is {question.full_grade}'))
        
        assignment = question.assignment_fk
        class_ = assignment.class_fk
        all_class_students = class_.students.all()
        student = data['student']
        if(student not in all_class_students):
            raise serializers.ValidationError(('There is no student with this id for this question.'))
        
        if(self.context['user'] == class_.headta or self.context['user'] in class_.teachers.all() or self.context['user'] in class_.tas.all()):
            self.set_question_grade(data)
            count_graded_question(question)
            count_graded_assignment(assignment)
            return data
        else:
            raise serializers.ValidationError(('You do not have permission to perform this action.'))
