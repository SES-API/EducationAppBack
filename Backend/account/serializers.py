from rest_framework import serializers
from django.contrib.auth import get_user_model



User_Model=get_user_model()






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