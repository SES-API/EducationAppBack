from re import L
from django.db import models
from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Session,atend
from class_app.serializers import StudentSerializer

#for signals
from class_app.models import ClassStudents
from django.dispatch import receiver
from django.db.models.signals import post_save

User_Model=get_user_model()

# class ClassPersonSerializer2(serializers.ModelSerializer):
#     profile_link = serializers.SerializerMethodField('get_profile_link')

#     def get_profile_link(self, model):
#         request = self.context.get("request")
#         base_url = request.build_absolute_uri('/').strip("/")
#         profile_link = base_url + "/account/profile/" + f"{model.id}"
#         return profile_link

#     class Meta:
#         model = User_Model
#         fields=['id','first_name','last_name','profile_pic', 'profile_link']




class StudentAtend(serializers.ModelSerializer):
    student=StudentSerializer()
    class Meta:
        model = atend
        fields="__all__"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We pass the "upper serializer" context to the "nested one"
        self.fields['student'].context.update(self.context)
        



class SessionsSerializers(serializers.ModelSerializer):
    atends=StudentAtend(many=True,read_only=True)
    class Meta:
        model = Session
        # fields="__all__"
        exclude = ["session_class"]
        extra_kwargs = {
            # '' : {'':},
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We pass the "upper serializer" context to the "nested one"
        self.fields['atends'].context.update(self.context)

class MyAtendSerializers(serializers.ModelSerializer):
    session_name = serializers.SerializerMethodField()
    session_date = serializers.SerializerMethodField()
    session_id = serializers.SerializerMethodField()
    student=StudentSerializer()


    class Meta:
        model = atend
        fields="__all__"
        # exclude = [""]
        extra_kwargs = {
            # '' : {'':},
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We pass the "upper serializer" context to the "nested one"
        self.fields['student'].context.update(self.context)

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
    student=serializers.PrimaryKeyRelatedField(many=True,queryset=User_Model.objects.all())
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
                ids.append(item.student)
            for item in data["student"]:
                if(item not in ids):
                    raise serializers.ValidationError(('There is no student with {} id in this session').format(item))
        return data




@receiver(post_save, sender=ClassStudents)
def add_to_sessions(sender, **kwargs):
    class_ = kwargs['instance'].Class
    user = kwargs['instance'].student
    for session in class_.class_session.all():
        atend_=atend(student=user,Present=None)
        atend_.save()
        session.atends.add(atend_)
        session.save()
