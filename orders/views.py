from django.shortcuts import render

from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view
from django.db.models import Q

# views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer


# orders/views.py - Asegúrate de que el queryset incluya prefetch_related
class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).select_related('user').prefetch_related(
            'items__product'  
        ).order_by('-created_at')
    

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = Order.objects.all().select_related('user').prefetch_related('items').order_by('-created_at')
        
        # Filtros
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
            
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
            
        return queryset

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all().select_related('user').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
# Estadísticas de órdenes
@api_view(['GET'])
def order_stats(request):
    from django.db.models import Count, Sum, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Estadísticas básicas
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    
    # Ventas del último mes
    last_month = timezone.now() - timedelta(days=30)
    monthly_sales = Order.objects.filter(
        created_at__gte=last_month, 
        status='delivered'
    ).aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
    
    # Órdenes por estado
    orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
    
    return Response({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'monthly_sales': float(monthly_sales),
        'orders_by_status': list(orders_by_status)
    })

class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        old_status = instance.status
        new_status = serializer.validated_data['status']
        
        self.perform_update(serializer)
        
        # Aquí podrías agregar notificaciones o lógica adicional cuando cambia el estado
        print(f"Orden #{instance.id} cambió de {old_status} a {new_status}")
        
        return Response({
            'message': f'Estado actualizado correctamente a {new_status}',
            'order': OrderSerializer(instance).data
        })
