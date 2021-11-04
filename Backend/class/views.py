from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly
from .permissions import *
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status




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


class ClassObject(RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all() 
    serializer_class = ClassSerializer
    permission_classes=[OBJ__IsClassOwnerORTeacherORTaOrReadOnly]