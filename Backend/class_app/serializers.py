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

class ClassPersonSerializer(serializers.ModelSerializer):
    # profile_link = serializers.SerializerMethodField('get_profile_link')

    # def get_profile_link(self, model):
    #     request = self.context.get("request")
    #     base_url = request.build_absolute_uri('/').strip("/")
    #     profile_link = base_url + "/account/profile/" + f"{model.id}"
    #     return profile_link

    class Meta:
        model = User_Model
        fields=['id','username','first_name','last_name','email','gender','profile_pic','birthdate','degree','university']



class ClassListSerializer(serializers.ModelSerializer):
    # students=ClassPersonSerializer(many=True)
    teachers=ClassPersonSerializer(many=True)
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
    students=ClassPersonSerializer(many=True)
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
        if(headta[0] not in class_[0].students.all() and headta[0] not in class_[0].tas.all()):
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
        if(ta[0] not in class_[0].students.all() and ta[0] != class_[0].headta):
            raise serializers.ValidationError(('There is no User(ta) with this id in class'))
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

