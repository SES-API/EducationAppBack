from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS



class OBJ__IsClassTeacherORTa(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and
            request.user in obj.class_id.tas.all()
            or
            request.user and
            request.user in obj.class_id.teachers.all()
            or
            request.user and
            request.user == obj.class_id.headta
        )   
 