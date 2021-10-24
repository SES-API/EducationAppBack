from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

User_Model=get_user_model()



Password_validation=[RegexValidator(regex="^(?=.*[A-Z])",message='Password must contain at least one uppercase letter.'),
                    RegexValidator(regex="^(?=.*[0-9])",message='Password must contain at least one number.'),
                    RegexValidator(regex="^(?=.{8,})",message='Password must be eight characters or longer.')]





# create users
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Model
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name'
        )
        extra_kwargs = {
            'password' : {'write_only':True},
            'id' : {'read_only':True},
            'username' : {'required':True},
            'email' : {'required':True}
        }

    def create(self, validated_data):
        user = User_Model.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            password = validated_data['password']
        )
        return user

#change password
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=30)
    new_password1 = serializers.CharField(
        required=True,
        max_length=30,
        validators = Password_validation
        )
    new_password2 = serializers.CharField(required=True, max_length=30)

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data.get('old_password')):
            raise serializers.ValidationError(('Old password was entered incorrectly.'))
        if data['new_password1']!=data['new_password2']:
            raise serializers.ValidationError("Passwords are not the same")
        return data
    

#send email before register a user:
class SendregisterEmailSerializer(serializers.Serializer):
    model = User_Model
    email = serializers.EmailField(required=True)
    full_name=serializers.CharField(required=True)

    def validate(self,data):
        if (User_Model.objects.filter(email=data['email'])):
            raise serializers.ValidationError("There is another account with this email")
        return data


#send reset password email:
class SendpasswordresetEmailSerializer(serializers.Serializer):
    model = User_Model
    email = serializers.EmailField(required=True)

    def validate(self,data):
        # if not(User_model.objects.filter(email=data['email'])):
        #     raise serializers.ValidationError("there is no email like this!")
        if not User_Model.objects.filter(email=data['email']):
            raise serializers.ValidationError("Email Does Not Exist")
        return data


#Serializer for reset password after confirm email
class ResetPasswordSerializer(serializers.Serializer):
    model = User_Model

    new_password1 = serializers.CharField(
        required=True,
        max_length=30,
        validators = Password_validation
        )
    new_password2 = serializers.CharField(required=True)
    email=serializers.EmailField(required=True)
    def validate(self,data):
        if data['new_password1']!=data['new_password2']:
            raise serializers.ValidationError("Passwords are not the same")
        if not User_Model.objects.filter(email=data['email']):
            raise serializers.ValidationError("Email Does Not Exist")
        if get_object_or_404(User_Model, email=data['email']).check_password(data['new_password1']):
            raise serializers.ValidationError("You must enter a new password This password is no different from the current password")
        return data


class GetUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Model
        exclude =['password','user_permissions','groups']
