from django.http import request
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly
from .models import Assignment, Question
from .serializers import *
from rest_framework.response import Response
from rest_framework import status


User_Model=get_user_model()



@method_decorator(csrf_exempt, name='dispatch')
class AssignmentList(ListCreateAPIView):
    filterset_fields = ['class_fk']
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes=[IsAuthenticated]


    def create(self, request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            class_=serializer.validated_data['class_fk']
            user=User_Model.objects.filter(id=request.user.pk)[0]
            if( user in class_.teachers.all() or user in class_.tas.all() or user == class_.headta ):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(csrf_exempt, name='dispatch')
class AddQuestion(GenericAPIView):
    serializer_class = QuestionSerializer
    permission_classes=[IsAuthenticated]

    def post(self, request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        assignment=Assignment.objects.filter(id=request.data['assignment_id'])
        if not assignment:
            return Response({'detail':'There is no assignment with this id'},status=status.HTTP_400_BAD_REQUEST)
        class_ = assignment[0].class_fk
        user=User_Model.objects.filter(id=request.user.pk)[0]
        if( user in class_.teachers.all() or user in class_.tas.all() or user == class_.headta ):
            if serializer.is_valid():
                serializer.save()
                # assignment[0].questions.add()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)
