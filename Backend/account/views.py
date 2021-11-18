from logging import error
from django.db.models.query import QuerySet
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import random
import threading
#-----------------------------
from .serializers import *
from .permissions import *
# Create your views here.

User_Model = get_user_model()



#register after the user confirmed their email

@method_decorator(csrf_exempt, name='dispatch')
class RegisterationView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


#change password

@method_decorator(csrf_exempt, name='dispatch')
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

@method_decorator(csrf_exempt, name='dispatch')
class SendRegisterEmail(GenericAPIView):
    serializer_class=SendregisterEmailSerializer
    def post(self,request,*args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        randomcode = random.randrange(1111, 9999)
        msg="Registration"
        if serializer.is_valid():
            email_body = render_to_string("account/email.html",{"message":msg,"randomcode":randomcode,"full_name":serializer.data['username']})
            email = EmailMessage(
                'ACTIVATION CODE',
                email_body,
                'SES API TEAM',
                [serializer.data['email']],
            )
            email.content_subtype = "html"
            email.fail_silently = False
            EmailThread(email).run()
            return Response({'code':randomcode},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#send an email for reset password when forgot password

@method_decorator(csrf_exempt, name='dispatch')
class SendResetPasswordEmail(GenericAPIView):
    serializer_class=SendpasswordresetEmailSerializer
    def post(self,request,*args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        randomcode = random.randrange(1111, 9999)
        msg="Reset Password"
        if serializer.is_valid():
            if(get_object_or_404(User_Model, email=serializer.validated_data['email']).first_name   or   get_object_or_404(User_Model, email=serializer.validated_data['email']).last_name):
                full_name=(get_object_or_404(User_Model, email=serializer.validated_data['email']).get_full_name)

            else:
                full_name=(get_object_or_404(User_Model, email=serializer.validated_data['email']).username)
            email_body = render_to_string("account/email.html",{"message":msg,"randomcode":randomcode,"full_name":full_name})
            email = EmailMessage(
                'ACTIVATION CODE',
                email_body,
                'SES API TEAM',
                [serializer.data['email']],
            )
            email.content_subtype = "html"
            email.fail_silently = False
            EmailThread(email).run()
            return Response({'code':randomcode},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#reset password view after confirm reset password email

@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(UpdateAPIView):
    serializer_class=ResetPasswordSerializer
    model = User_Model
    permissions=(AllowAny)
    def update(self,request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # self.object = User_Model.objects.filter(email=serializer.validated_data['email'])
            self.object=get_object_or_404(User_Model, email=serializer.validated_data['email'])
            self.object.set_password(serializer.data.get("new_password1"))
            self.object.save()
            response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully',
                    'data': []
            }
            return Response(response,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#user info view

@method_decorator(csrf_exempt, name='dispatch')
class GetUserInfo(APIView):
    def get(self, request):
        if not(request.user.is_anonymous):
            serializer = GetUserDataSerializer(request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Authentication credentials were not provided."},status=status.HTTP_401_UNAUTHORIZED)


#login view

@method_decorator(csrf_exempt, name='dispatch')
class TokenAuthenticationView(ObtainAuthToken):
    
    def post(self, request):
        result = super(TokenAuthenticationView, self).post(request)
        currentUserModel = get_user_model()
        try:
            user = currentUserModel.objects.get(username=request.data['username'])
            update_last_login(None, user)
        except Exception as exc:
            return None
        return result



# put profile info

@method_decorator(csrf_exempt, name='dispatch')
class UpdateProfileView(UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated & IsProfileOwner]
    queryset = User_Model.objects.all()



# get profile info

@method_decorator(csrf_exempt, name='dispatch')
class GetProfileView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

    def get(self, request, pk):
        profile = get_object_or_404(User_Model, pk=pk)
        serializer = ProfileSerializer(profile)
        if(serializer.data['is_hidden'] == True):
            response = {
                    'status': 'forbidden',
                    'code': status.HTTP_403_FORBIDDEN,
                    'message': 'This profile is hidden by its user',
                    'data': []
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)




# delete account

@method_decorator(csrf_exempt, name='dispatch')
class DeleteUserView(DestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated & IsProfileOwner]
    queryset = User_Model.objects.all()
