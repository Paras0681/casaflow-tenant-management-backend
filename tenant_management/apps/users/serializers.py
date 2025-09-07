from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from rest_framework import serializers
from apps.users.models import Account
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid redentials.")
        else:
            raise serializers.ValidationError("Email and password required.", code='authorization')

        data['user'] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'address', 'room_number', 'phone_number', 'occupation', 'email', 'password']

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        user = User.objects.create_user(
            email=email,
            password=password
        )
        account = Account.objects.create(user=user, **validated_data)
        return account