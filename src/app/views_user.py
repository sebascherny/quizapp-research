import uuid
from rest_framework.decorators import api_view
from django.shortcuts import HttpResponse
from rest_framework import status
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from app.models import User
import json
import datetime
import jwt
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

@api_view(['POST'])
def register_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if (not username) or (not password):
        return HttpResponse(json.dumps({"success": False, "detail": "Username and password are required"}), status=status.HTTP_400_BAD_REQUEST)
    if (not isinstance(password, str)) or (not isinstance(password, str)):
        return HttpResponse(json.dumps({"success": False, "detail": "Username and password must be strings"}), status=status.HTTP_400_BAD_REQUEST)
    try:
        User.objects.get(username=username)
        return HttpResponse(json.dumps({"success": False, "detail": "User already exists"}), status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        new_user = User.objects.create(username=username)
        new_user.set_password(password)
        new_user.save()
        new_user_token = TokenObtainPairSerializer.get_token(new_user)
        return HttpResponse(json.dumps({"success": True,
                                        "access": str(new_user_token.access_token),
                                        "refresh": str(new_user_token)}), status=status.HTTP_200_OK)