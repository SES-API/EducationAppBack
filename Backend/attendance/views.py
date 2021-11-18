from django.contrib.auth import authenticate, get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly
# from .permissions import *
from .models import Session,atend
from class_app.models import Class
from .serializers import SessionsSerializers,SetSessionAtendsSerializers
from rest_framework.response import Response
from rest_framework import serializers, status
from django.db.models import Q
# Create your views here.


User_Model = get_user_model()

class SessionsOfClass(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = SessionsSerializers
    def get(self, request,pk):
        class_=Class.objects.get(id=pk)
        if(class_):
            query=Session.objects.filter(session_class=class_)
            serializer=self.get_serializer(query,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'detail':'there is no class with this id'},status=status.HTTP_404_NOT_FOUND)
    def post(self,request,pk):
        class_=Class.objects.get(id=pk)
        serializer=self.get_serializer(data=request.data)
        if(serializer.is_valid()):
            session=serializer.save()
            for user in class_.students.all():
                atend_=atend(students=user,Present=False)
                atend_.save()
                session.atends.add(atend_)
            session.session_class=class_
            session.save()
            
            return Response({'detail':'done'},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

class SetAtendsOfSession(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = SetSessionAtendsSerializers
    def post(self,request):
        serializer=self.get_serializer(data=request.data)
        if(serializer.is_valid()):
            sesion=Session.objects.get(pk=serializer.validated_data["session_id"])
            class_=sesion.session_class
            if(request.user == class_.headta or request.user in class_.teachers.all() or request.user in class_.tas.all()):
                for atend in sesion.atends.all():
                    #print(atend.students.pk)
                    if atend.students in serializer.validated_data["students"]:
                        print("true")
                        atend.Present=True
                        atend.save()
                return Response({'detail':'done'},status=status.HTTP_200_OK)  
            else:
              return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)  
        
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)