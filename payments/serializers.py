# payments/serializers.py
from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Payment
        fields = ["order_id", "method", "status", "paid_at", "amount", "transaction_id"]
        read_only_fields = ["status", "paid_at", "transaction_id"]
