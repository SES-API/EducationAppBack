from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class OBJ__IsAssignmentClassTeacherOrTa(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        class_ = obj.class_fk
        return bool(
            request.method in SAFE_METHODS and request.user in class_.students.all()
            or
            request.user and
            request.user in class_.tas.all()
            or
            request.user and
            request.user in class_.teachers.all()
            or
            request.user and
            request.user == class_.headta
        )   


class OBJ__IsQuestionClassTeacherOrTa(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        class_ = obj.assignment_fk.class_fk
        return bool(
            request.method in SAFE_METHODS and request.user in class_.students.all()
            or
            request.user and
            request.user in class_.tas.all()
            or
            request.user and
            request.user in class_.teachers.all()
            or
            request.user and
            request.user == class_.headta
        )   
 