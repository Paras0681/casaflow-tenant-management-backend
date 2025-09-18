from rest_framework import serializers
from apps.users.models import Account, User
from .models import TenantsData, TenantsFiles, Property, Room
from apps.tenants.utils.pdf_generator import save_invoice_for_tenant
import os
from django.conf import settings

class TenantsProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = Account
        fields = [
            'account_id', 
            'email', 
            'first_name', 
            'last_name', 
            'phone_number', 
            'occupation', 
            'lease_start_date', 
            'address', 
            'room_number'
        ]
    
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
    
class TenantsFilesSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    class Meta:
        model = TenantsFiles
        fields = [
            "id",
            "room",
            "room_number",
            "file_url",
            "download_url",
            "file_type",
            "description",
            "unit_reading",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at", "room_number"]


class TenantsDataSerialzier(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = TenantsData
        fields = [
            "id",
            "rent_amount",
            "room_number",
            "lightbill_amount",
            "other_charges",
            "total_amount",
            "per_tenant_share",
            "payment_status",
            "paid_at",
            "created_at",
            "invoice_url",
        ]
        read_only_fields = ["id", "created_at", "paid_at", "invoice_url"]

    def create(self, validated_data):
        data = validated_data
        invoice_url, invoice_id= save_invoice_for_tenant(
            data,
            account=self.context['account'],
            qr_code_path=os.path.join(
                settings.BASE_DIR, 
                "static", 
                "images", 
                "qr_code.png"
                ).replace("\\", "/"
            )
        )
        tenants_data = TenantsData.objects.create(
                **validated_data, 
                account=self.context['account'], 
                room=self.context['room'],
                payment_status="not_paid",
                invoice_url = invoice_url,
                invoice_id=invoice_id
        )
        return tenants_data


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            "id",
            "name",
            "address",
            "total_floors", 
            "total_rooms", 
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        property = Property.objects.create(**validated_data)
        return property


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "property",
            "room_number",
            "active_tenants",
            "max_occupants",
            "created_at",
            "updated_at"
        ]

    def create(self, validated_data):
        property_instance = validated_data.pop("property")
        room = Room.objects.create(property=property_instance, **validated_data)
        return room
