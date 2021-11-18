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


@method_decorator(csrf_exempt, name='dispatch')
class AssignmentList(ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [OBJ__IsClassTeacherORTa]

    def create(self, request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddQuestion():
    pass