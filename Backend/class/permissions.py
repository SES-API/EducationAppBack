from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS



class OBJ__IsClassOwnerORTeacherORTaOrReadOnly(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or
            request.user and
            request.user in obj.tas.all()
            or
            request.user and
            request.user in obj.teachers.all()
            or
            request.user and
            request.user == obj.owner
        )   
 