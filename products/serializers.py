# products/serializers.py - Actualizado
from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'category']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category', 
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'image', 'category', 'category_id', 'created_at']



# products/serializers.py - Agregar estos serializers
from .models import InventoryMovement

# products/serializers.py - Agregar este serializer
class InventoryMovementSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = ['id', 'product', 'product_name', 'product_image', 'movement_type', 
                 'quantity', 'reason', 'created_by', 'created_at']

class ProductWithStockSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    low_stock_alert = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'image', 
                 'category', 'created_at', 'low_stock_alert']
    
    def get_low_stock_alert(self, obj):
        # Considerar stock bajo si es menor a 10 unidades
        return obj.stock < 10