from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer
from payments.models import Payment  # si lo necesitas en otro serializer
from django.db import transaction
# Serializer para ítems de orden (solo lectura)
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


# Serializer para crear ítems
class OrderCreateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


# Serializer para mostrar órdenes completas
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'is_paid', 'total_price', 'shipping_address', 'items']
        read_only_fields = ['user']

class OrderCreateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderCreateItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['shipping_address', 'total_price', 'items']

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        order = Order.objects.create(user=user, **validated_data)

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # 🛑 Validar stock suficiente
            if product.stock < quantity:
                raise serializers.ValidationError({
                    "detail": f"No hay suficiente stock para el producto '{product.name}'"
                })

            # 🧾 Crear item
            OrderItem.objects.create(order=order, **item_data)

            # 📉 Actualizar stock
            product.stock -= quantity
            product.save()

        return order
