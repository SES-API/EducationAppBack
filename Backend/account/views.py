from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from rest_framework.generics import GenericAPIView,UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import random
#-----------------------------
from .serializers import SendregisterEmailSerializer
# Create your views here.

User_Model=get_user_model



#register and change password here



#send an email when user is registering
class SendRegisterEmail(GenericAPIView):
    serializer_class=SendregisterEmailSerializer
    def post(self,request,*args, **kwargs):
        print(request.data)
        serializer=self.get_serializer(data=request.data)
        randomcode = random.randrange(111111, 999999)
        if serializer.is_valid():
            email_body = render_to_string("account/email.html",{"randomcode":randomcode,"full_name":serializer.data['full_name']})
            email = EmailMessage(
                'ACTIVATION CODE',
                email_body,
                'SES API TEAM',
                [serializer.data['email']],
            )
            email.content_subtype = "html"
            email.fail_silently = False
            email.send()
            return Response({'code':randomcode},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
