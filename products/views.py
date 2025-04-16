from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from django.db.models import Q

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .recommendations import get_recommended_products
from rest_framework.permissions import AllowAny

# Productos
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # <--- Esto permite acceso público
    pagination_class = None  # ✅ Desactiva paginación también aquí
    def get_queryset(self):
        queryset = Product.objects.all().order_by("-created_at")
        category = self.request.query_params.get("category")
        search = self.request.query_params.get("search")

        if category:
            queryset = queryset.filter(category_id=category)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # <--- Esto permite acceso público

# Categorías
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # <--- Esto permite acceso público
    pagination_class = None  # ✅ Desactiva paginación también aquí

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # <--- Esto permite acceso público

# Productos relacionados (ML)
@api_view(['GET'])
@permission_classes([AllowAny])  # <--- Esto permite acceso público
def related_products(request, product_id):
    print(f'🔍 Buscando productos relacionados para: {product_id}')

    try:
        recommended_products = get_recommended_products(product_id)
        print(f'✅ Recomendaciones: {[p.name for p in recommended_products]}')
        serializer = ProductSerializer(recommended_products, many=True, context={"request": request})
        return Response(serializer.data)

    except Exception as e:
        print(f'❌ Error en related_products: {e}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
