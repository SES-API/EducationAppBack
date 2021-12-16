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
    serializer_class = CreateAssignmentSerializer
    permission_classes=[IsAuthenticated]

    def create(self, request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            class_=serializer.validated_data['class_id']
            user=request.user
            if( user in class_.teachers.all() or user in class_.tas.all() or user == class_.headta ):
                assignment = serializer.save()
                # add value=None grades for all students
                for student in class_.students.all():
                    AssignmentGrade.objects.create(user_id=student, assignment_id=assignment, value=None)
                    if ClassGrade.objects.filter(user_id=student, class_id=class_).first() == None:
                        ClassGrade.objects.create(user_id=student, class_id=class_, value= None) 
                # 
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# get/update/delete an assignment
@method_decorator(csrf_exempt, name='dispatch')
class AssignmentObject(RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentRetrieveSerializer
    permission_classes=[OBJ__IsAssignmentClassTeacherOrTa]

    def get_serializer_context(self):
        assignment_id = self.kwargs['pk']
        class_ = Assignment.objects.filter(id=assignment_id).first().class_id
        user = self.request.user
        if (user in class_.teachers.all() or
            user in class_.tas.all() or
            user == class_.headta):
            return {'user_id': self.request.user.id , 'is_student':False, 'class_id':class_.id, 'assignment_id': assignment_id }
        return {'user_id': self.request.user.id , 'is_student':True, 'class_id':class_.id, 'assignment_id': assignment_id }



# add aquestion to an assignment
@method_decorator(csrf_exempt, name='dispatch')
class AddQuestion(GenericAPIView):
    serializer_class = AddQuestionSerializer
    permission_classes=[IsAuthenticated]

    def get_serializer_context(self):
        return {'assignment_id': self.kwargs['pk']}

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        assignment=Assignment.objects.filter(id=pk)
        if not assignment:
            return Response({'detail':'There is no assignment with this id'},status=status.HTTP_400_BAD_REQUEST)
        class_ = assignment.first().class_id
        user=request.user
        if( user in class_.teachers.all() or user in class_.tas.all() or user == class_.headta ):
            if serializer.is_valid():
                question = serializer.save()
                question.assignment_id = assignment.first()
                question.save()
                # add value=None grades for all students
                for student in class_.students.all():
                    Grade.objects.create(user_id=student, question_id=question, value=None, delay=None, final_grade=None)
                # 
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail':'You do not have permission to perform this action.'},status=status.HTTP_403_FORBIDDEN)



# get/update/delete a question
@method_decorator(csrf_exempt, name='dispatch')
class QuestionObject(RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes=[OBJ__IsQuestionClassTeacherOrTa]

    def get_serializer_context(self):
        question_id = self.kwargs['pk']
        assignment_id = Question.objects.filter(id=question_id).first().assignment_id
        return {'assignment_id':assignment_id}



# add question grades for a students
@method_decorator(csrf_exempt, name='dispatch')
class GradeQuestion(GenericAPIView):
    serializer_class = SetQuestionGrades
    permission_classes=[IsAuthenticated]

    def get_serializer_context(self):
        return {'user':self.request.user}

    def post(self,request):
        serializer=self.get_serializer(data=request.data, many=True)
        if(serializer.is_valid()):
            return Response({'detail':'done'},status=status.HTTP_200_OK)          
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



# list of class assignment
@method_decorator(csrf_exempt, name='dispatch')
class AssignmentList(ListAPIView):
    filterset_fields = ['is_graded', 'date']
    serializer_class = AssignmentRetrieveSerializer
    permission_classes=[IsAuthenticated]

    def get_serializer_context(self):
        class_id = self.kwargs['pk']
        class_ = Class.objects.filter(id=class_id).first()
        user = self.request.user
        if (user in class_.teachers.all() or
            user in class_.tas.all() or
            user == class_.headta):
            return {'user_id': self.request.user.id , 'is_student':False}
        return {'user_id': self.request.user.id , 'is_student':True}
        

    def get_queryset(self):
        class_id = self.kwargs['pk']
        class_ = Class.objects.filter(id=class_id).first()
        user = self.request.user
        if (user in class_.teachers.all() or
            user in class_.tas.all() or
            user in class_.students.all() or
            user == class_.headta):
            return Assignment.objects.filter(class_id=class_id)
        return Assignment.objects.none()




# list of assignment grades
@method_decorator(csrf_exempt, name='dispatch')
class AssignmentGrades(ListAPIView):
    filterset_fields = ['user_id']
    serializer_class = AssignmentGradeSerializer
    permission_classes=[IsAuthenticated]

    def get_serializer_context(self):
        assignment_id = self.kwargs['pk']
        assignment = Assignment.objects.filter(id=assignment_id).first()
        class_ = assignment.class_id
        user = self.request.user
        if (user in class_.teachers.all() or
            user in class_.tas.all() or
            user == class_.headta):
            return {'user_id': self.request.user.id , 'is_student':False}
        return {'user_id': self.request.user.id , 'is_student':True}
        

    def get_queryset(self):
        assignment_id = self.kwargs['pk']
        assignment = Assignment.objects.filter(id=assignment_id).first()
        class_ = assignment.class_id
        user = self.request.user
        if (user in class_.teachers.all() or
            user in class_.tas.all() or
            user in class_.students.all() or
            user == class_.headta):
            return AssignmentGrade.objects.filter(assignment_id=assignment_id)
        return AssignmentGrade.objects.none()



# list of class grades
@method_decorator(csrf_exempt, name='dispatch')
class ClassGrades(ListAPIView):
    filterset_fields = ['user_id']
    serializer_class = ClassGradeSerializer
    permission_classes=[IsAuthenticated]

    def get_serializer_context(self):
        class_id = self.kwargs['pk']
        class_ = Class.objects.filter(id=class_id).first()
        user = self.request.user
        if (user in class_.teachers.all() or
            user in class_.tas.all() or
            user == class_.headta):
            return {'user_id': self.request.user.id , 'is_student':False}
        return {'user_id': self.request.user.id , 'is_student':True}
        

    def get_queryset(self):
        class_id = self.kwargs['pk']
        class_ = Class.objects.filter(id=class_id).first()
        user = self.request.user
        if (user in class_.teachers.all() or
            user in class_.tas.all() or
            user in class_.students.all() or
            user == class_.headta):
            return ClassGrade.objects.filter(class_id=class_id)
        return ClassGrade.objects.none()
