from django.urls import path
from .views import OrderCreateView
from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    OrderStatusUpdateView,
    order_stats
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('create/', OrderCreateView.as_view(), name='order-create'),

    path('admin/orders/', OrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/', OrderDetailView.as_view(), name='admin-order-detail'),
    path('admin/orders/<int:pk>/update-status/', OrderStatusUpdateView.as_view(), name='admin-order-update-status'),
    path('admin/orders/stats/', order_stats, name='admin-order-stats'),
]
