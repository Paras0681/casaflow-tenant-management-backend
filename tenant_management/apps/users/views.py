from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer,LoginSerializer,RegisterSerializer
from apps.users.models import Account, User
#This is the LoginAPI view for user authentication
class LoginAPIView(APIView):
    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)   
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPIView(APIView):
    def post(self,request):
        user = User.objects.filter(email=request.data.get('email')).first()
        if user:
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(email=request.data.get('email'))
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User registered successfully",
                'user':  {user.id, user.email},
                "email": user.email,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUsersAPIView(APIView):
    def get(self, request):
        if request.user.is_staff:
            users = User.objects.all()
        else:
            users = User.objects.filter(email=request.user.email)
        serializer = UserSerializer(users)
        return Response(serializer.data, status=status.HTTP_200_OK)
