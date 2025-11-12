from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from django.db.models import Q
from utils.pagination import OptionalPagination

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .recommendations import get_recommended_products
from rest_framework.permissions import AllowAny


# Productos
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # <--- Esto permite acceso público
    pagination_class = OptionalPagination
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
    pagination_class = OptionalPagination
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


# Vistas de administración para productos
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo administradores

class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo administradores

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo administradores

# Vistas de administración para categorías
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

# Vista para obtener todos los productos (sin paginación para admin)
class ProductAdminListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None  # Sin paginación para admin


# products/views.py - Agregar estas vistas
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from .models import Product, InventoryMovement
from .serializers import ProductSerializer, InventoryMovementSerializer

# Vista para obtener productos con información de stock (para admin)
class ProductInventoryListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None
    
    def get_queryset(self):
        return Product.objects.all().select_related('category').order_by('name')

# Vista para crear movimientos de inventario
class InventoryMovementCreateView(generics.CreateAPIView):
    queryset = InventoryMovement.objects.all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        movement = serializer.save(created_by=self.request.user)
        
        # Actualizar el stock del producto
        product = movement.product
        if movement.movement_type == 'entrada':
            product.stock += movement.quantity
        elif movement.movement_type == 'salida':
            product.stock = max(0, product.stock - movement.quantity)  # No permitir stock negativo
        elif movement.movement_type == 'ajuste':
            product.stock = movement.quantity
            
        product.save()

# Vista para obtener historial de movimientos
class InventoryMovementListView(generics.ListAPIView):
    serializer_class = InventoryMovementSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None
    
    def get_queryset(self):
        return InventoryMovement.objects.all().select_related('product', 'created_by').order_by('-created_at')

# Vista para alertas de stock bajo
@api_view(['GET'])
def low_stock_alerts(request):
    # Productos con stock menor a 10 unidades
    low_stock_products = Product.objects.filter(stock__lt=10).select_related('category')
    serializer = ProductSerializer(low_stock_products, many=True)
    return Response(serializer.data)

# dashboard/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category
from orders.models import Order, OrderItem
from users.models import CustomUser

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard_stats(request):
    # Fecha de hoy y hace 30 días
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    
    try:
        # Estadísticas de productos
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(stock__lt=10).count()
        
        # Estadísticas de órdenes
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        today_orders = Order.objects.filter(created_at__date=today.date()).count()
        
        # Ventas
        total_sales = Order.objects.filter(is_paid=True).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        # Ventas de los últimos 30 días
        recent_sales = Order.objects.filter(
            created_at__gte=last_30_days,
            is_paid=True
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # Ventas de hoy
        today_sales = Order.objects.filter(
            created_at__date=today.date(),
            is_paid=True
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # Usuarios
        total_users = CustomUser.objects.count()
        new_users_today = CustomUser.objects.filter(
            date_joined__date=today.date()
        ).count()
        
        # Productos más vendidos (últimos 30 días)
        top_products = OrderItem.objects.filter(
            order__created_at__gte=last_30_days
        ).values(
            'product__name', 'product__image'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_sold')[:5]
        
        # Ventas por día (últimos 7 días)
        sales_by_day = []
        for i in range(7):
            day = today - timedelta(days=i)
            day_sales = Order.objects.filter(
                created_at__date=day.date(),
                is_paid=True
            ).aggregate(total=Sum('total_price'))['total'] or 0
            sales_by_day.append({
                'date': day.strftime('%Y-%m-%d'),
                'day_name': day.strftime('%a'),
                'sales': float(day_sales)
            })
        sales_by_day.reverse()
        
        # Órdenes por estado
        orders_by_status = Order.objects.values('status').annotate(
            count=Count('id')
        )
        
        stats = {
            # Tarjetas principales
            'cards': {
                'today_sales': float(today_sales),
                'total_products': total_products,
                'pending_orders': pending_orders,
                'low_stock_alerts': low_stock_products,
                'total_users': total_users,
                'today_orders': today_orders,
                'total_sales': float(total_sales),
                'recent_sales': float(recent_sales),
            },
            
            # Gráficos y listas
            'top_products': list(top_products),
            'sales_by_day': sales_by_day,
            'orders_by_status': list(orders_by_status),
            
            # Cambios porcentuales (podrías calcular comparando con el período anterior)
            'changes': {
                'sales_change': '+12%',  # Estos podrías calcularlos comparando períodos
                'orders_change': '+8%',
                'users_change': '+5%',
                'products_change': '+3%'
            }
        }
        
        return Response(stats)
        
    except Exception as e:
        print(f"Error en dashboard stats: {e}")
        return Response(
            {'error': 'Error al cargar las estadísticas'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )