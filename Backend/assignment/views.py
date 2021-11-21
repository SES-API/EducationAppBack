from django.http import request
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly
from .models import Assignment, Question
from .serializers import *
from .permissions import OBJ__IsAssignmentClassTeacherOrTa, OBJ__IsQuestionClassTeacherOrTa
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



# get/update/delete an assignment
@method_decorator(csrf_exempt, name='dispatch')
class AssignmentObject(RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentRetrieveSerializer
    permission_classes=[OBJ__IsAssignmentClassTeacherOrTa]



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
                for student in class_.students.all():
                    question.students.add(student)
                assignment[0].questions.add(question)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)



# get/update/delete a question
@method_decorator(csrf_exempt, name='dispatch')
class QuestionObject(RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes=[OBJ__IsQuestionClassTeacherOrTa]



# add one question grade for a student
@method_decorator(csrf_exempt, name='dispatch')
class GradeQuestion(GenericAPIView):
    serializer_class = SetQuestionGrades
    permission_classes=[IsAuthenticated]

    def post(self,request):
        serializer=self.get_serializer(data=request.data)
        if(serializer.is_valid()):
            question=serializer.validated_data["question"]
            assignment = question.assignment_fk
            class_ = assignment.class_fk
            if(request.user == class_.headta or request.user in class_.teachers.all() or request.user in class_.tas.all()):
                serializer.save() #?
                return Response({'detail':'done'},status=status.HTTP_200_OK)  
            else:
                return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)  
        
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



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



# see grades of one assignment by Role (teacher/ta - student)
@method_decorator(csrf_exempt, name='dispatch')
class AssignmentGradeList(ListAPIView):
    filterset_fields = ['question', 'student']
    serializer_class = GradeSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        assignment_id = self.kwargs['pk']
        class_ = Assignment.objects.filter(id=assignment_id)[0].class_fk
        questions = Question.objects.filter(assignment_fk=assignment_id)
        query_set = Grade.objects.none()

        if( user in class_.tas.all() or user in class_.teachers.all() or user == class_.headta):
            for question in questions:
                query_set = query_set | Grade.objects.filter(question=question)
            return query_set
        if( user in class_.students.all()):
            for question in questions:
                query_set = query_set | Grade.objects.filter(question=question , student=user)
            return query_set

