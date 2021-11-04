from rest_framework import serializers
from .models import Class,University
from django.contrib.auth import get_user_model



User_Model=get_user_model()


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields ="__all__"