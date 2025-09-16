from rest_framework import serializers
from .models import Payments

class PaymentSerializer(serializers.ModelSerializer):
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
            "paid_at",
            "created_at",
        ]
    def create(self, validated_data):
        return super().create(validated_data)
