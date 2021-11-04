from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from rest_framework.generics import GenericAPIView, ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly
from .permissions import *
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status



@method_decorator(csrf_exempt, name='dispatch')
class ClassList(ListCreateAPIView):
    filterset_fields = ['university', 'semester','students']
    queryset = Class.objects.all() 
    serializer_class = ClassSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        my_data=request.data.copy()
        my_data['owner']=str(request.user.pk)
        print(my_data)
        serializer = self.get_serializer(data=my_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class ClassObject(RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes=[OBJ__IsClassOwnerORTeacherORTaOrReadOnly]



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
                class_.save()
            else:
                return Response({'detail':'Forbidden'},status=status.HTTP_403_FORBIDDEN)
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

            if(request.user == class_.owner or request.user in class_.tas.all() or request.user in class_.teachers.all()):
                class_.tas.add(ta)
                class_.save()
            else:
                return Response({'detail':'Forbidden'},status=status.HTTP_403_FORBIDDEN)

            return Response({'detail':'done'},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)