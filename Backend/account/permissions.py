from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsProfileOwner(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return request.user.pk == obj.pk   
