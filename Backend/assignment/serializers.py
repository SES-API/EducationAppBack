from rest_framework import serializers
from django.contrib.auth import get_user_model
import django_filters.rest_framework
from class_app.serializers import StudentSerializer
from .signals import *

User_Model=get_user_model()




class GradeListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if self.context.get('is_student') == True:
            user_id = self.context.get('user_id')
            data = data.filter(user_id=user_id)
        return super(GradeListSerializer, self).to_representation(data)



class GradeSerializer(serializers.ModelSerializer):
    user_id = StudentSerializer()
    class Meta:
        model = Grade
        list_serializer_class = GradeListSerializer
        fields=['value', 'delay', 'user_id', 'final_grade']



class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    question_grade=GradeSerializer(many=True, required=False)
    is_graded = serializers.SerializerMethodField('get_is_graded')

    def get_is_graded(self, question):
        is_student = self.context.get('is_student')
        if(is_student):
            user_id = self.context.get('user_id')
            question_grade = Grade.objects.filter(user_id=user_id, question_id=question)
            if(question_grade):
                question_grade = question_grade[0]
                if (question_grade.value):
                    return True
            return False
        else:
            return question.is_graded

    def get_serializer_context(self):
        context={'user_id' : self.context.get('user_id'), 'is_student' : self.context.get('is_student')}
        return context

    def validate(self, data):
        for question in Question.objects.filter(assignment_id = self.context['assignment_id']):
            if question.id!=data.get('id') and data.get('name') == question.name:
                raise serializers.ValidationError(('There is another question with this name in this assignment.'))
        return data

    class Meta:
        model = Question
        fields=['id','name', 'full_grade', 'not_graded_count', 'is_graded','question_grade']
        # , 'avg_grade', 'min_grade', 'max_grade'
        extra_kwargs = {
            'assignment_id' : {'read_only':True},
            # 'avg_grade' : {'read_only':True},
            # 'min_grade' : {'read_only':True},
            # 'max_grade' : {'read_only':True},
            'question_grade' : {'read_only':True},
            'not_graded_count' : {'read_only':True},
            'is_graded' : {'read_only':True},
        }



class AddQuestionSerializer(serializers.ModelSerializer):
    def get_serializer_context(self):
        context={'user_id' : self.context.get('user_id'), 'is_student' : self.context.get('is_student')}
        return context

    def validate(self, data):
        assignment_id = self.context['assignment_id']
        assignment = Assignment.objects.filter(id=assignment_id).first()
        student_count = assignment.class_id.students.count()
        data['not_graded_count'] = student_count
        data['is_graded'] = True
        if(student_count!=0):
            data['is_graded'] = False
        for question in Question.objects.filter(assignment_id = assignment_id):
            if data.get('name') == question.name:
                raise serializers.ValidationError(('There is another question with this name in this assignment.'))
        assignment.is_graded = False
        assignment.not_graded_count += 1
        # assignment_grades = AssignmentGrade.objects.filter(assignment_id=assignment)
        # for asg_grade in assignment_grades:
        #     asg_grade.value = None
        #     asg_grade.save()
        # assignment.min_grade = None
        # assignment.max_grade = None
        # assignment.avg_grade = None
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
        fields=['id', 'name','date', 'weight', 'is_graded', 'not_graded_count','class_id']
        extra_kwargs = {
            'not_graded_count' : {'read_only':True},
            'is_graded' : {'read_only':True},
        }

    def validate(self, data):
        if(data.get('weight') == 0):
            raise serializers.ValidationError(("Assignmnet's weight cannot be zero."))
        return data


class AssignmentGradeListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if self.context.get('is_student') == True:
            user_id = self.context.get('user_id')
            data = data.filter(user_id=user_id)
        return super(AssignmentGradeListSerializer, self).to_representation(data)


class AssignmentGradeSerializer(serializers.ModelSerializer):
    user_id = StudentSerializer()
    class Meta:
        model = AssignmentGrade
        list_serializer_class = AssignmentGradeListSerializer
        fields=['value', 'user_id', 'assignment_id']



class AssignmentRetrieveSerializer(serializers.ModelSerializer):
    assignment_question=QuestionSerializer(many=True)
    assignment_grade=AssignmentGradeSerializer(many=True, read_only=True)
    is_graded = serializers.SerializerMethodField('get_is_graded')

    def get_is_graded(self, assignment):
        is_student = self.context.get('is_student')
        if(is_student):
            user_id = self.context.get('user_id')
            assginment_grade = AssignmentGrade.objects.filter(user_id=user_id, assignment_id=assignment)
            if(assginment_grade):
                assginment_grade = assginment_grade[0]
                if (assginment_grade.value):
                    return True
            return False
        else:
            return assignment.is_graded

    def get_serializer_context(self):
        context={'user_id' : self.context.get('user_id'), 'is_student' : self.context.get('is_student')}
        return context

    def validate(self, data):
        if(data.get('weight') == 0):
            raise serializers.ValidationError(("Assignmnet's weight cannot be zero."))

        # for assignment in Assignment.objects.filter(class_id = self.context['class_id']):
        #     if data.get('name') != self.instance.name:
        #         if data.get('name') == assignment.name:
        #             raise serializers.ValidationError(('There is another assignment with this name in this class.'))
        return data

    def update(self, instance, validated_data):
        if (validated_data.get('name')):
            instance.name = validated_data.get('name')
        if(validated_data.get('date')):
            instance.date = validated_data.get('date')
        if(validated_data.get('weight')):
            instance.weight = validated_data.get('weight')
        instance.save()

        questions = validated_data.get('assignment_question')
        question_names = set()
        if(questions):
            for q in questions:
                if(q.get('name')):
                    if question_names.__contains__(q.get('name')):
                        raise serializers.ValidationError(('Questions of one assignment must have unique names.'))
                    question_names.add(q['name'])

            for q in questions:
                q_id = q.get('id', None)
                if(q_id):
                    q_instance = instance.assignment_question.filter(id=q_id).first()
                    if(q_instance == None):
                        raise serializers.ValidationError((f'There is no question with id:{q_id} in this assignment'))
                    q_name = q.get('name')
                    if(q_name and q_instance.name != q_name):
                        q_instance.name = q_name
                        q_instance.save()
                    q_full_grade = q.get('full_grade')
                    old_grade = q_instance.full_grade
                    if(q_full_grade and q_full_grade != old_grade):
                        q_instance.full_grade = q_full_grade
                        q_instance.save()
                        for grade in Grade.objects.filter(question_id=q_id):
                            if(grade.value):
                                val = round( grade.value * (q_full_grade/old_grade), 2)
                                grade.value = val
                                grade.final_grade = round((val*grade.delay), 2)
                                grade.save()
                else:
                    Question.objects.create(assignment_id = instance.id ,**q)

        return instance


    class Meta:
        model = Assignment
        fields=['id', 'name','date', 'weight','assignment_question', 'assignment_grade', 'avg_grade', 'min_grade', 'max_grade', 'is_graded', 'not_graded_count', 'class_id']
        extra_kwargs = {
            'class_id' : {'read_only':True},
            'avg_grade' : {'read_only':True},
            'min_grade' : {'read_only':True},
            'max_grade' : {'read_only':True},
            'assignment_question' : {'read_only':True},
            'assignment_grade' : {'read_only':True},
        }



class SetQuestionGrades(serializers.ModelSerializer):
    value = serializers.FloatField(required=True)
    delay = serializers.FloatField(required=False, default=1)
    class Meta:
        model = Grade
        fields='__all__'


    def set_question_grade(self, data):
        if data['value'] != -1 :
            question=data['question_id']
            assignment = question.assignment_id
            student = data['user_id']
            grade = Grade.objects.filter(question_id = question, user_id=student)
            if(grade):
                grade = grade.first()
                if(grade.value != data['value'] or grade.delay != data['delay']):
                    grade.value = data['value']
                    grade.delay = data['delay']
                    grade.final_grade = round((grade.value*grade.delay), 2)
                    grade.save()
            else:
                grade = Grade.objects.create(user_id=student, question_id=question, value=data['value'], delay=data['delay'])
                grade.final_grade = round((grade.value*grade.delay), 2)
                grade.save()

            calculate_assignment_grades(assignment, student)
            # calculate_question_properties(question)
            count_graded_question(question)


    def validate(self, data):
        question=data['question_id']
        if not(question):
            raise serializers.ValidationError(('There is no question with this id.'))
        
        # if data.get('value') > question.full_grade:
        #     raise serializers.ValidationError((f'Maximum grade for question {question.name} is {question.full_grade}'))
        
        if data.get('value') != -1 :
            if data.get('value') > question.full_grade or data.get('value') < 0:
                raise serializers.ValidationError((f'Grade for question {question.name} should be from 0 to {question.full_grade}'))

        if data.get('delay') == -1 :
            data['delay'] = 1

        if data.get('delay') > 1 or data.get('delay') < 0:
            raise serializers.ValidationError((f'Delay should be from 0 to 1'))

        
        assignment = question.assignment_id
        class_ = assignment.class_id
        all_class_students = class_.students.all()
        student = data['user_id']
        if(student not in all_class_students):
            raise serializers.ValidationError(('There is no student with this id for this question.'))
        
        if(self.context['user'] == class_.headta or self.context['user'] in class_.teachers.all() or self.context['user'] in class_.tas.all()):
            self.set_question_grade(data)
            return data
        else:
            raise serializers.ValidationError(('You do not have permission to perform this action.'))



# class ClassGradeListSerializer(serializers.ListSerializer):
#     def to_representation(self, data):
#         if self.context.get('is_student') == True:
#             user_id = self.context.get('user_id')
#             data = data.filter(user_id=user_id)
#         return super(ClassGradeListSerializer, self).to_representation(data)


# class ClassGradeSerializer(serializers.ModelSerializer):
#     user_id = StudentSerializer()
#     class Meta:
#         model = ClassGrade
#         list_serializer_class = ClassGradeListSerializer
#         fields=['value', 'user_id', 'class_id']