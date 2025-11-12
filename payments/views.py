# payments/views.py
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order
import uuid

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order
import uuid

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        amount = request.data.get("amount")

        if not order_id or not amount:
            raise ValidationError({"detail": "Faltan campos obligatorios (order_id y amount)."})

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            raise ValidationError({"order": "Orden no encontrada o no pertenece al usuario."})

        if hasattr(order, "payment"):
            raise ValidationError({"payment": "Esta orden ya tiene un pago registrado."})

        if float(amount) != float(order.total_price):
            raise ValidationError({"amount": "El monto no coincide con el total de la orden."})

        payment = Payment.objects.create(
            order=order,
            method=request.data.get("method", "unknown"),
            status="completed",
            paid_at=timezone.now(),
            amount=amount,
            transaction_id=str(uuid.uuid4())
        )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)
