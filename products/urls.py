# products/urls.py - Actualizado
from django.urls import path
from .views import admin_dashboard_stats
from .views import (
    ProductListView,
    ProductDetailView,
    ProductAdminListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    CategoryListView,
    CategoryDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    related_products,
    ProductInventoryListView,
    InventoryMovementCreateView,
    InventoryMovementListView,
    low_stock_alerts
)

urlpatterns = [
    # Rutas públicas
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('products/<int:product_id>/related/', related_products, name='related-products'),
    
    # Rutas de administración
    path('admin/products/', ProductAdminListView.as_view(), name='admin-product-list'),
    path('admin/products/create/', ProductCreateView.as_view(), name='admin-product-create'),
    path('admin/products/<int:pk>/update/', ProductUpdateView.as_view(), name='admin-product-update'),
    path('admin/products/<int:pk>/delete/', ProductDeleteView.as_view(), name='admin-product-delete'),
    path('admin/categories/create/', CategoryCreateView.as_view(), name='admin-category-create'),
    path('admin/categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='admin-category-update'),
    path('admin/categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='admin-category-delete'),

    # URLs de inventario
    path('admin/inventory/products/', ProductInventoryListView.as_view(), name='inventory-products'),
    path('admin/inventory/movements/', InventoryMovementListView.as_view(), name='inventory-movements'),
    path('admin/inventory/movements/create/', InventoryMovementCreateView.as_view(), name='inventory-movement-create'),
    path('admin/inventory/alerts/low-stock/', low_stock_alerts, name='low-stock-alerts'),
    path('admin/dashboard/stats/', admin_dashboard_stats, name='admin-dashboard-stats'),
]