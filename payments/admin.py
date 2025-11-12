from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'method', 'status', 'paid_at', 'transaction_id']
    list_filter = ['status', 'method']
    search_fields = ['order__id', 'transaction_id']
    readonly_fields = ['transaction_id', 'paid_at']

    def get_order_user(self, obj):
        return obj.order.user.email  # o obj.order.user.username si prefieres
    get_order_user.short_description = "Cliente"
