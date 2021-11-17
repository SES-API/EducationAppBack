from rest_framework import serializers
from .models import Class,University
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
from django.shortcuts import get_object_or_404



User_Model=get_user_model()


class ClassPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Model
        # fields = "__all__"
        fields=['id','username','first_name','last_name','email','profile_pic']




class ClassListSerializer(serializers.ModelSerializer):
    # students=ClassPersonSerializer(many=True)
    # teachers=ClassPersonSerializer(many=True)
    # tas=ClassPersonSerializer(many=True)
    class Meta:
        model = Class
        fields="__all__"
        # exclude = ["owner"]
        extra_kwargs = {
            'password' : {'write_only':True},
            'students' : {'read_only':True},
            'teachers' : {'read_only':True},
            'tas' : {'read_only':True},
        }

class ClassRetriveSerializer(serializers.ModelSerializer):
    students=ClassPersonSerializer(many=True)
    teachers=ClassPersonSerializer(many=True)
    tas=ClassPersonSerializer(many=True)
    class Meta:
        model = Class
        exclude = ["owner"]
        extra_kwargs = {
            'students' : {'read_only':True},
            'teachers' : {'read_only':True},
            'tas' : {'read_only':True},
        }


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
        if(teacher[0] not in class_[0].students.all() and teacher[0] not in class_[0].tas.all()):
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
        if(ta[0] not in class_[0].students.all()):
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
    password = serializers.CharField(required=False, default="Default_Password")

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))

        if not(class_):
            raise serializers.ValidationError(('There is no Class with this id'))

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