from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer,LoginSerializer,RegisterSerializer, ForgetPasswordSerializer, ResetPasswordSerialzier
from apps.users.models import Account, User
import jwt
from apps.notifications.utils.send_notification import send_notification

User = get_user_model()

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


class ForgetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return  Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            payload = {
                "user_id": user.id,
                "exp": datetime.now() + timedelta(hours=1)
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            reset_link = f"http://localhost:3000/reset-password/{token}"
            title = "Password Reset"
            message = f"Click the link to reset your password: {reset_link}"
            html_message = f"<p>Click <a href='{reset_link}'>here</a> to reset your password.</p>"
            account = Account.objects.get(user=user)
            send_notification(
                user=account,
                title=title,
                message=message,
                html_message=html_message,
                notification_type="forget_password"
            )
            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        

class ResetPasswordAPIView(APIView):
    def post(self, request, token):
        data = request.data
        serializer = ResetPasswordSerialzier(data=data)
        if serializer.is_valid():
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user = User.objects.get(id=payload['user_id'])
            except jwt.ExpiredSignatureError:
                return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)
            except (jwt.InvalidTokenError, User.DoesNotExist):
                return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['password'])
            user.save()
            title = "Password Reset Successful"
            message = "Your password has been reset successfully."
            html_message = "<p>Your password has been reset successfully.</p>"
            account = Account.objects.get(user=user)
            send_notification(
                user=account,
                title=title,
                message=message,
                html_message=html_message,
                notification_type="password_reset"
            )
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)