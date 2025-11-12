from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'total_price', 'is_paid']
    list_filter = ['is_paid', 'created_at']
    inlines = [OrderItemInline]
    search_fields = ['id', 'user__email']
