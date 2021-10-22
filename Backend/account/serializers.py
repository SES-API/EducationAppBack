from rest_framework import serializers
from django.contrib.auth import get_user_model


User_Model=get_user_model()


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
        )
        user.set_password(validated_data['password'])
        # user.save()
        return user


class ChangePasswordSerializer():
    # old_password = 
    # new_password = 
    pass


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
            raise serializers.ValidationError("Email Not Exist")
        return data


#Serializer for reset password after confirm email
class ResetPasswordSerializer(serializers.Serializer):
    model = User_Model

    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
    email=serializers.EmailField(required=True)
    def validate(self,data):
        if data['new_password1']!=data['new_password2']:
            raise serializers.ValidationError("Passwords are not the same")
        if not User_Model.objects.filter(email=data['email']):
            raise serializers.ValidationError("Email Not Exist")
        return data