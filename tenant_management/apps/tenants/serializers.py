from rest_framework import serializers
from apps.users.models import Account
from apps.users.models import User

class TenantsProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = Account
        fields = ['account_id', 'email', 'first_name', 'last_name', 'phone_number', 'occupation', 'lease_start_date', 'address', 'room_number']
    
    def create(self, validated_data): 
        user = User.objects.get(email=self.context['request'].user.email)
        account = Account.objects.create(
            user=user,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            occupation=validated_data['occupation'],
            lease_start_date=validated_data['lease_start_date'],
            address=validated_data['address'],
            room_number=validated_data['room_number']
        )
        return account