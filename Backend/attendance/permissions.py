from rest_framework.permissions import BasePermission


class OBJ__IsClassOwnerORTeacherORTa(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        obj=obj.session_class
        return bool(
            request.user and
            request.user in obj.tas.all()
            or
            request.user and
            request.user == obj.headta
            or
            request.user and
            request.user in obj.teachers.all()
            or
            request.user and
            request.user == obj.owner
        )  