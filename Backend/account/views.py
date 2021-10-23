from logging import error
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from rest_framework.generics import GenericAPIView, UpdateAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import random
import threading
#-----------------------------
from .serializers import *
# Create your views here.

User_Model=get_user_model



#register
class RegisterationView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



#change password
class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request,*args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.object.set_password(serializer.data.get("new_password1"))
            self.object.save()
            response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully',
                    'data': []
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


#send an email when user is registering
class SendRegisterEmail(GenericAPIView):
    serializer_class=SendregisterEmailSerializer
    def post(self,request,*args, **kwargs):
        print(request.data)
        serializer=self.get_serializer(data=request.data)
        randomcode = random.randrange(111111, 999999)
        msg="Registration"
        if serializer.is_valid():
            email_body = render_to_string("account/email.html",{"message":msg,"randomcode":randomcode,"full_name":serializer.data['full_name']})
            email = EmailMessage(
                'ACTIVATION CODE',
                email_body,
                'SES API TEAM',
                [serializer.data['email']],
            )
            email.content_subtype = "html"
            email.fail_silently = False
            # email.send()
            EmailThread(email).run()
            return Response({'code':randomcode},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#send an email for reset password when forgot password
class SendResetPasswordEmail(GenericAPIView):
    serializer_class=SendpasswordresetEmailSerializer
    def post(self,request,*args, **kwargs):
        print(request.data)
        serializer=self.get_serializer(data=request.data)
        randomcode = random.randrange(111111, 999999)
        msg="Reset Password"
        if serializer.is_valid():
            if(get_user_model().objects.filter(email=serializer.validated_data['email'])[0].first_name   or   get_user_model().objects.filter(email=serializer.validated_data['email'])[0].last_name):
                email_body = render_to_string("account/email.html",{"message":msg,"randomcode":randomcode,"full_name":(get_user_model().objects.filter(email=serializer.validated_data['email']))[0].get_full_name})
               
            else:
                email_body = render_to_string("account/email.html",{"message":msg,"randomcode":randomcode,"full_name":(get_user_model().objects.filter(email=serializer.validated_data['email']))[0].username})
            email = EmailMessage(
                'ACTIVATION CODE',
                email_body,
                'SES API TEAM',
                [serializer.data['email']],
            )
            email.content_subtype = "html"
            email.fail_silently = False
            # email.send()
            EmailThread(email).start()
            return Response({'code':randomcode})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#reset password view after confirm reset password email
class ResetPasswordView(UpdateAPIView):
    serializer_class=ResetPasswordSerializer
    model =get_user_model()
    # permission_classes = [AllowAny]
    permissions=(AllowAny)
    def update(self,request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.object=User_Model.objects.filter(email=serializer.validated_data['email'])
            self.object.set_password(serializer.data.get("new_password1"))
            self.object.start()
            response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully',
                    'data': []
            }
            return Response(response,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetUserInfo(APIView):
    def get(self, request):
        if not(request.user.is_anonymous):
            serializer = GetUserDataSerializer(request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Authentication credentials were not provided."},status=status.HTTP_401_UNAUTHORIZED)
    
    
