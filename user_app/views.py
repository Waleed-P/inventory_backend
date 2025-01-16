from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class Registration(APIView):
    
    def post(self, request):
        # Get the data from the request body
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if all necessary fields are present
        if not username or not password:
            return Response({"detail": "Missing fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a user
        user = User.objects.create_user(username=username, password=password)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Return the response with the user info and tokens
        data = {
            'response': "Registration successful",
            'username': user.username,
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
        return Response(data, status=status.HTTP_201_CREATED)
