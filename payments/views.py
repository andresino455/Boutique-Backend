# payments/views.py
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order
import uuid

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order_id = self.request.data.get("order_id")
        amount = self.request.data.get("amount")

        try:
            order = Order.objects.get(id=order_id, user=self.request.user)
        except Order.DoesNotExist:
            raise ValidationError({"order": "Orden no válida o no pertenece al usuario."})

        if hasattr(order, "payment"):
            raise ValidationError({"payment": "La orden ya tiene un pago registrado."})

        if float(amount) != float(order.total_price):
            raise ValidationError({"amount": "El monto no coincide con el total de la orden."})

        serializer.save(
            order=order,
            status="completed",
            paid_at=timezone.now(),
            transaction_id=self.request.data.get("transaction_id", str(uuid.uuid4()))
        )

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)
