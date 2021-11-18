from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS



class OBJ__IsClassOwnerORTeacherORTaOrStudentReadOnly(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS and request.user in obj.students.all()
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
 