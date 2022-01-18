from django.contrib.auth import authenticate, get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import DestroyAPIView, GenericAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView,RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly
# from .permissions import *
from .models import Session,atend
from class_app.models import Class
from .serializers import MyAtendSerializers, SessionsSerializers,SetSessionAtendsSerializers
from rest_framework.response import Response
from rest_framework import serializers, status
from django.db.models import Q
# Create your views here.
from .permissions import OBJ__IsClassOwnerORTeacherORTa

User_Model = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class SessionsOfClass(GenericAPIView):
    filterset_fields = ['name','date','atends']
    permission_classes=[IsAuthenticated]
    serializer_class = SessionsSerializers
    def get_serializer_context(self):
        class_=Class.objects.filter(id=self.kwargs['pk'])
        context = super(SessionsOfClass, self).get_serializer_context()
        context.update({"class_id": class_.id})
        return context
    def get(self, request,pk):
        class_=Class.objects.filter(id=pk)
        if(class_):
            class_=class_[0]
            if(request.user == class_.headta or request.user in class_.teachers.all() or request.user in class_.tas.all()):
                query=self.filter_queryset(Session.objects.filter(session_class=class_))
                serializer=self.get_serializer(query,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail':'there is no class with this id'},status=status.HTTP_404_NOT_FOUND)
    def post(self,request,pk):
        class_=Class.objects.filter(id=pk)
        serializer=self.get_serializer(data=request.data)
        if(class_):
            class_=class_[0]
            if(serializer.is_valid()):
                if(request.user == class_.headta or request.user in class_.teachers.all() or request.user in class_.tas.all()):
                    session=serializer.save()
                    for user in class_.students.all():
                        atend_=atend(student=user,Present=None)
                        atend_.save()
                        session.atends.add(atend_)
                    session.session_class=class_
                    session.save()
                else:
                    return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)
                
                return Response({'detail':'done'},status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail':'there is no class with this id'},status=status.HTTP_404_NOT_FOUND)


class SessionsUpdate(UpdateAPIView):
    permission_classes=[OBJ__IsClassOwnerORTeacherORTa]
    serializer_class = SessionsSerializers
    queryset=Session.objects.all()



class SessionDestroy(DestroyAPIView):
    permission_classes=[OBJ__IsClassOwnerORTeacherORTa]
    serializer_class = SessionsSerializers
    queryset=Session.objects.all()


@method_decorator(csrf_exempt, name='dispatch')
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
                    #print(atend.student.pk)
                    if atend.student in serializer.validated_data["student"]:
                        # print("true")
                        atend.Present=True
                        atend.save()
                    else:
                        atend.Present=False
                        atend.save()
                return Response({'detail':'done'},status=status.HTTP_200_OK)  
            else:
              return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)  
        
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class UserAtendsForClass(GenericAPIView):
    filterset_fields = ['Present']
    permission_classes=[IsAuthenticated]
    serializer_class = MyAtendSerializers
    def get_serializer_context(self):
        class_=Class.objects.filter(id=self.kwargs['pk'])
        context = super(SessionsOfClass, self).get_serializer_context()
        context.update({"class_id": class_.id})
        return context
    def get(self, request,pk):
        class_=Class.objects.filter(id=pk)
        if(class_):
            class_=class_[0]
            if(request.user in class_.students.all()):
                query=self.filter_queryset(atend.objects.filter(user_session__session_class=class_,student=request.user))
                serializer=self.get_serializer(query,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail':'there is no class with this id'},status=status.HTTP_404_NOT_FOUND)