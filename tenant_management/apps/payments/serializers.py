from rest_framework import serializers
from .models import Payments

class PaymentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='account.first_name', read_only=True)
    class Meta:
        model = Payments
        fields = [
            "account",
            "uploaded_by",
            "invoice_id",
            "payment_id",
            "payment_utr",
            "payment_receipt_url",
            "amount", 
            "marked_paid_at",
            "created_at",
        ]
    def create(self, validated_data):
        return super().create(validated_data)
