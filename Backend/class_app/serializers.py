from rest_framework import serializers
from .models import Class,University
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
from django.shortcuts import get_object_or_404
import django_filters.rest_framework


User_Model=get_user_model()

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields="__all__"



class StudentSerializer(serializers.ModelSerializer):
    student_id = serializers.SerializerMethodField()
    class Meta:
        model = User_Model
        fields=['student_id','id','username','first_name','last_name','email','gender','profile_pic','birthdate','degree','university', 'is_hidden']
    def get_student_id(self,obj):
        # pk=self.context.get('request').parser_context.get('kwargs').get('pk')
        # class_=Class.objects.filter(id=pk).first()
        print(self.context)
        session=ClassStudents.objects.filter(student=obj,Class=self.context['class_id'])
        if(session):
            session = session.first()
            return session.studentid


class ClassPersonSerializer(serializers.ModelSerializer):

    class Meta:  
        ref_name = "Members"
        model = User_Model
        fields=['id','username','first_name','last_name','email','gender','profile_pic','birthdate','degree','university', 'is_hidden']



class ClassListSerializer(serializers.ModelSerializer):
    # students=ClassPersonSerializer(many=True)
    teachers=ClassPersonSerializer(many=True,required=False)
    # tas=ClassPersonSerializer(many=True)
    # headta=ClassPersonSerializer(many=False)
    # semseter=SemesterSerializer(many=False)
    class Meta:
        model = Class
        fields="__all__"
        # exclude = ["owner"]
        extra_kwargs = {
            'password' : {'write_only':True},
            'students' : {'read_only':True},
            'teachers' : {'read_only':True},
            'tas' : {'read_only':True},
            'headta' : {'read_only':True},
        }
class ClassRetriveSerializer(serializers.ModelSerializer):
    students=StudentSerializer(many=True)
    teachers=ClassPersonSerializer(many=True)
    tas=ClassPersonSerializer(many=True)
    headta=ClassPersonSerializer(many=False)
    # semester=SemesterSerializer()
    semester_name=serializers.SerializerMethodField()
    class Meta:
        model = Class
        exclude = ["owner"]
        extra_kwargs = {
            'students' : {'read_only':True},
            'teachers' : {'read_only':True},
            'tas' : {'read_only':True},
            'headta' : {'read_only':True},
        }
    def get_semester_name(self,obj):
        if(obj.semester):
            return obj.semester.semester
        else:
            return "None"

    def validate(self, data):
        password = data.get('password')
        if(password != None):
            data['has_password'] = True
        else:
            data['has_password'] = False
        return data
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We pass the "upper serializer" context to the "nested one"
        self.fields['students'].context.update(self.context)
            



#-----------------------------------------------------------------------------------
class SetTeacherSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField(required=True)
    class_id=serializers.IntegerField(required=True)

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))
        teacher=User_Model.objects.filter(id=data.get("teacher_id"))
        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))
    
        if not(teacher):
            raise serializers.ValidationError(('There is no User(Teacher) with this id'))
        if(teacher[0] in class_[0].teachers.all()):
            raise serializers.ValidationError(('This User Already is Teacher'))
        if(teacher[0] not in class_[0].students.all() and teacher[0] not in class_[0].tas.all() and teacher[0] != class_[0].headta):
            raise serializers.ValidationError(('There is no User(Teacher) with this id in class'))
        
        return data



class SetHeadTaSerializer(serializers.Serializer):
    headta_id = serializers.IntegerField(required=True)
    class_id=serializers.IntegerField(required=True)

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))
        headta=User_Model.objects.filter(id=data.get("headta_id"))
        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))
    
        if not(headta):
            raise serializers.ValidationError(('There is no User(headta) with this id'))
        if(headta[0] == class_[0].headta):
            raise serializers.ValidationError(('This User Already is HeadTA'))
        if(headta[0] not in class_[0].students.all() and headta[0] not in class_[0].tas.all() and headta[0] not in class_[0].teachers.all()):
            raise serializers.ValidationError(('There is no User(headta) with this id in class'))
        return data


class SetTaSerializer(serializers.Serializer):
    ta_id = serializers.IntegerField(required=True)
    class_id=serializers.IntegerField(required=True)

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))
        ta=User_Model.objects.filter(id=data.get("ta_id"))
        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))
    
        if not(ta):
            raise serializers.ValidationError(('There is no User(ta) with this id'))
        if(ta[0] in class_[0].tas.all()):
            raise serializers.ValidationError(('This User Already is TA'))
        if(ta[0] not in class_[0].students.all() and ta[0] != class_[0].headta and ta[0] not in class_[0].teachers.all()):
            raise serializers.ValidationError(('There is no User(ta) with this id in class'))
        return data


class SetStudentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField(required=True)
    class_id=serializers.IntegerField(required=True)

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))
        student=User_Model.objects.filter(id=data.get("student_id"))
        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))
    
        if not(student):
            raise serializers.ValidationError(('There is no User(student) with this id'))
        if(student[0] in class_[0].students.all()):
            raise serializers.ValidationError(('This User Already is Student'))
        if(student[0] not in class_[0].tas.all() and student[0] != class_[0].headta and student[0] not in class_[0].teachers.all()):
            raise serializers.ValidationError(('There is no User(student) with this id in class'))
        if(student[0] in class_[0].teachers.all()):
            raise serializers.ValidationError(('A teacher cannot be a student'))
        return data
#-----------------------------------------------------------------------------------
class SetHeadTaWithEmailSerializer(serializers.Serializer):
    headta_email = serializers.EmailField(required=True)
    class_id=serializers.IntegerField(required=True)

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))
        headta=User_Model.objects.filter(email=data.get("headta_email"))
        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))
    
        if not(headta):
            raise serializers.ValidationError(('There is no User(headta) with this id'))
        if(headta[0] == class_[0].headta):
            raise serializers.ValidationError(('This User Already is HeadTA'))
        return data

class AddTaWithEmailSerializer(serializers.Serializer):
    ta_email = serializers.EmailField(required=True)
    class_id=serializers.IntegerField(required=True)

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))
        ta=User_Model.objects.filter(email=data.get("ta_email"))
        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))
    
        if not(ta):
            raise serializers.ValidationError(('There is no User(headta) with this id'))
        if(ta[0] in class_[0].tas.all()):
            raise serializers.ValidationError(('This User Already is TA'))
        if(ta[0] in class_[0].students.all() or ta[0] in class_[0].teachers.all() or ta[0] == class_[0].headta):
            raise serializers.ValidationError(('This User Already is in class as another role'))
        return data

class AddTeacherWithEmailSerializer(serializers.Serializer):
    teacher_email = serializers.EmailField(required=True)
    class_id=serializers.IntegerField(required=True)

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))
        teacher=User_Model.objects.filter(email=data.get("teacher_email"))
        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))
    
        if not(teacher):
            raise serializers.ValidationError(('There is no User(teacher) with this id'))
            
        if(teacher[0] in class_[0].teachers.all()):
            raise serializers.ValidationError(('This User Already is teacher'))

        if(teacher[0] in class_[0].students.all() or teacher[0] in class_[0].tas.all() or teacher[0] == class_[0].headta):
            raise serializers.ValidationError(('This User Already is in class as another role'))
        return data
#-----------------------------------------------------------------------------------


class JoinClassSerializer(serializers.Serializer):
    class_id=serializers.IntegerField(required=True)
    student_id=serializers.CharField(required=True)
    password = serializers.CharField(required=False, default="Default_Password")

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))
        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))
        items=ClassStudents.objects.filter(studentid=data["student_id"])
        if (items):
            for std in items:
                if(std.Class.id==data['class_id']):
                    raise serializers.ValidationError(('Repetitious student_id'))

        if(len(data["student_id"])<6 or len(data["student_id"])>10 ):
            raise serializers.ValidationError(('Student number must be between 6 and 10 digits'))


        if(class_[0].password != None):
            if(data['password'] == 'Default_Password'):
                raise serializers.ValidationError(('Password is required for this class'))
            if(class_[0].password != data['password']):
                raise serializers.ValidationError(('The class password is incorrect'))

        return data


class LeaveClassSerializer(serializers.Serializer):
    class_id=serializers.IntegerField(required=True)
    
    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))
        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))
    
        return data




class UniversityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields="__all__"
        # extra_kwargs = {
        # }
class ClassStudentSerializer(serializers.ModelSerializer):
    student=ClassPersonSerializer()
    class Meta:
        model = ClassStudents
        fields="__all__"

