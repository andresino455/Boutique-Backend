from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer
from payments.models import Payment  # si lo necesitas en otro serializer
from django.db import transaction


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'product_price', 'quantity', 'price']
        read_only_fields = ['id']

# Serializer para crear ítems
class OrderCreateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


# Serializer para mostrar órdenes completas
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'user_name', 'username', 'created_at', 
            'is_paid', 'total_price', 'shipping_address', 'status', 'items'
        ]
        read_only_fields = ['id', 'created_at', 'user']

class OrderCreateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

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
