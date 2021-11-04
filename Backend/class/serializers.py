from rest_framework import serializers
from .models import Class,University
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
from django.shortcuts import get_object_or_404



User_Model=get_user_model()


class ClassSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Class
        exclude = ["owner"]



class SetTeacherSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField(required=True)
    class_id=serializers.IntegerField(required=True)

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))[0]
        teacher=User_Model.objects.filter(id=data.get("teacher_id"))[0]
        if not(class_):
            raise serializers.ValidationError(('There is no Class whit this id'))
    
        if not(teacher):
            raise serializers.ValidationError(('There is no User(Teacher) whit this id'))

        if(teacher not in class_.students.all()):
            raise serializers.ValidationError(('There is no User(Teacher) whit this id in class'))
        return data


class SetTaSerializer(serializers.Serializer):
    ta_id = serializers.IntegerField(required=True)
    class_id=serializers.IntegerField(required=True)

    def validate(self, data):
        class_=Class.objects.filter(id=data.get("class_id"))[0]
        ta=User_Model.objects.filter(id=data.get("ta_id"))[0]
        if not(class_):
            raise serializers.ValidationError(('There is no Class whit this id'))
    
        if not(ta):
            raise serializers.ValidationError(('There is no User(ta) whit this id'))

        if(ta not in class_.students.all()):
            raise serializers.ValidationError(('There is no User(ta) whit this id in class'))
        return data