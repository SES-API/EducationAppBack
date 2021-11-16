from django.http import request
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly
from .permissions import *
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from itertools import chain


User_Model = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class ClassList(ListCreateAPIView):
    filterset_fields = ['university', 'semester','students']
    queryset = Class.objects.all() 
    serializer_class = ClassListSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        class_=serializer.save()
        class_.teachers.add(request.user)
        class_.owner=request.user
        class_.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class ClassObject(RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassRetriveSerializer
    permission_classes=[OBJ__IsClassOwnerORTeacherORTaOrStudentReadOnly]



@method_decorator(csrf_exempt, name='dispatch')
class MyClasses(ListAPIView):
    def get_queryset(self):
        user=self.request.user
        queryset= list(chain(user.class_student.all(), user.class_ta.all(),user.class_teacher.all(),user.class_owner.all()))
        return queryset
    
    serializer_class = ClassListSerializer





@method_decorator(csrf_exempt, name='dispatch')
class SetTeacher(GenericAPIView):
    serializer_class=SetTeacherSerializer
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            class_=Class.objects.filter(id=serializer.validated_data['class_id'])[0]
            teacher=User_Model.objects.filter(id=serializer.validated_data['teacher_id'])[0]
            if(request.user == class_.owner or request.user in class_.teachers.all()):
                class_.teachers.add(teacher)
                if(teacher in  class_.students.all()):
                    class_.students.remove(teacher)
                elif(teacher in  class_.tas.all()):
                    class_.tas.remove(teacher)
                class_.save()
            else:
                return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)
            return Response({'detail':'done'},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(csrf_exempt, name='dispatch')
class SetTa(GenericAPIView):
    serializer_class=SetTaSerializer
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            class_=Class.objects.filter(id=serializer.validated_data['class_id'])[0]
            ta=User_Model.objects.filter(id=serializer.validated_data['ta_id'])[0]

            if(request.user == class_.owner or request.user == class_.headta or request.user in class_.teachers.all()):
                class_.tas.add(ta)
                class_.students.remove(ta)
                class_.save()
            else:
                return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)

            return Response({'detail':'done'},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(csrf_exempt, name='dispatch')
class JoinClass(GenericAPIView):
    serializer_class = JoinClassSerializer
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            class_=Class.objects.filter(id=serializer.validated_data['class_id'])[0]
            user=User_Model.objects.filter(id=request.user.pk)[0]
            if( user in class_.teachers.all() or user in class_.tas.all() or user in class_.students.all() ):
                response = {
                    'status': 'forbidden',
                    'code': status.HTTP_403_FORBIDDEN,
                    'message': 'User already in class',
                    'data': []
                }
                return Response(response)
            if(user == class_.owner):
                response = {
                    'status': 'forbidden',
                    'code': status.HTTP_403_FORBIDDEN,
                    'message': 'The class owner cannot join the class',
                    'data': []
                }
                return Response(response)
            class_.students.add(user)
            class_.save()
            return Response({'detail':'done'},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(csrf_exempt, name='dispatch')
class LeaveClass(GenericAPIView):
    serializer_class = LeaveClassSerializer
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            class_=Class.objects.filter(id=serializer.validated_data['class_id'])[0]
            user=User_Model.objects.filter(id=request.user.pk)[0]
            if( user in class_.teachers.all() or user in class_.tas.all() or user in class_.students.all() ):
                class_.students.remove(user)
                class_.teachers.remove(user)
                class_.tas.remove(user)
                class_.save()
            else:
                response = {
                    'status': 'forbidden',
                    'code': status.HTTP_403_FORBIDDEN,
                    'message': 'User is not in class',
                    'data': []
                }
                return Response(response)
            return Response({'detail':'done'},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)