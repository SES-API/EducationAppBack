from django.http import request
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly
from .models import Assignment, Question
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError


User_Model=get_user_model()


# add an assignment
@method_decorator(csrf_exempt, name='dispatch')
class CreateAssignment(CreateAPIView):
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



# list of class assignment
@method_decorator(csrf_exempt, name='dispatch')
class AssignmentList(ListAPIView):
    filterset_fields = ['is_graded']
    serializer_class = AssignmentSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        class_id = self.kwargs['pk']
        class_ = Class.objects.filter(id=class_id)[0]
        user = self.request.user
        if (user in class_.teachers.all() or
            user in class_.tas.all() or
            user in class_.students.all() or
            user == class_.headta):
            return Assignment.objects.filter(class_fk=class_id)
        return None

    def get(self, request, pk):
        data=AssignmentSerializer(self.get_queryset(),many=True).data
        if(data):
            return Response(data, status=status.HTTP_200_OK)
        response = {
                'status': 'forbidden',
                'code': status.HTTP_403_FORBIDDEN,
                'message': 'You do not have permission to perform this action.',
                'data': []
        }
        return Response(response, status=status.HTTP_403_FORBIDDEN)


# add aquestion to an assignment
@method_decorator(csrf_exempt, name='dispatch')
class AddQuestion(GenericAPIView):
    serializer_class = QuestionSerializer
    permission_classes=[IsAuthenticated]

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        assignment=Assignment.objects.filter(id=pk)
        if not assignment:
            return Response({'detail':'There is no assignment with this id'},status=status.HTTP_400_BAD_REQUEST)
        class_ = assignment[0].class_fk
        user=request.user
        if( user in class_.teachers.all() or user in class_.tas.all() or user == class_.headta ):
            if serializer.is_valid():
                question = serializer.save()
                assignment[0].questions.add(question)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)