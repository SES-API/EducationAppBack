from re import L
from django.db import models
from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Session,atend

User_Model=get_user_model()

class ClassPersonSerializer2(serializers.ModelSerializer):
    profile_link = serializers.SerializerMethodField('get_profile_link')

    def get_profile_link(self, model):
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/').strip("/")
        profile_link = base_url + "/account/profile/" + f"{model.id}"
        return profile_link

    class Meta:
        model = User_Model
        fields=['id','first_name','last_name','profile_pic', 'profile_link']




class StudentAtend(serializers.ModelSerializer):
    students=ClassPersonSerializer2()
    class Meta:
        model = atend
        fields="__all__"



class SessionsSerializers(serializers.ModelSerializer):
    atends=StudentAtend(many=True,read_only=True)
    class Meta:
        model = Session
        fields="__all__"
        # exclude = [""]
        extra_kwargs = {
            # '' : {'':},
        }

class MyAtendSerializers(serializers.ModelSerializer):
    session_name = serializers.SerializerMethodField()
    session_date = serializers.SerializerMethodField()
    session_id = serializers.SerializerMethodField()
    students=ClassPersonSerializer2()


    class Meta:
        model = atend
        fields="__all__"
        # exclude = [""]
        extra_kwargs = {
            # '' : {'':},
        }

    def get_session_name(self,obj):
        session=Session.objects.filter(atends=obj)[0]
        return session.name

    def get_session_date(self,obj):
        session=Session.objects.filter(atends=obj)[0]
        return session.date

    def get_session_id(self,obj):
        session=Session.objects.filter(atends=obj)[0]
        return session.pk

# class SetSessionAtendsSerializers(serializers.Serializer):
#     session_id=serializers.IntegerField()
#     students_id=serializers.PrimaryKeyRelatedField(many=True,queryset=User_Model.objects.all())


#     def validate(self, data):
#         sesion=Session.objects.get(pk=data["session_id"])
#         if not(sesion):
#             raise serializers.ValidationError(('There is no session with this id'))
#         else:
#             for item in data["students_id"]:
#                 if(item not in sesion.atends.students):
#                     raise serializers.ValidationError(('There is no student with {} id').format(item))
#         return data



class SetSessionAtendsSerializers(serializers.ModelSerializer):
    students=serializers.PrimaryKeyRelatedField(many=True,queryset=User_Model.objects.all())
    session_id=serializers.IntegerField()


    class Meta:
        model = atend
        exclude=['Present']

    def validate(self, data):
        sesion=Session.objects.get(pk=data["session_id"])
        if not(sesion):
            raise serializers.ValidationError(('There is no session with this id'))
        else:
            atends=sesion.atends.all()
            ids=[]
            for item in atends:
                ids.append(item.students)
            for item in data["students"]:
                if(item not in ids):
                    raise serializers.ValidationError(('There is no student with {} id in this session').format(item))
        return data