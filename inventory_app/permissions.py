from rest_framework import permissions
from rest_framework import exceptions
from .models import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
import jwt
import os





class IsLoginUserOnly(permissions.BasePermission):
    print("Permissions entered ")
    def has_permission(self, request, view):
        print("Entered has_permission")
        try:
            # print("Access token: ", access_token)

            # Reuse the utility function to extract member_id
            user_id = request.user.id
            print("User ID: ", user_id)
            if user_id:
                if User.objects.filter(id=user_id).exists():
                    return True
                else:
                    raise PermissionDenied({
                        "status": "Failed",
                        "message": "User not found.",
                        "response_code": status.HTTP_404_NOT_FOUND,
                    })
        except Exception as e:
            raise PermissionDenied({
                "status": "Failed",
                "message": "Unauthorized user",
                "response_code": status.HTTP_403_FORBIDDEN,
            })
        raise PermissionDenied({
        "status": "Failed",
        "message": "Unauthorized user",
        "response_code": status.HTTP_403_FORBIDDEN,
    })

