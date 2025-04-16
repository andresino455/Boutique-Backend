from django.contrib import admin
from django.contrib import admin
from .models import Category, Product
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)

from .models import Category, Product, ProductImage
from django.utils.html import format_html
from django.contrib import admin

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" style="border-radius: 6px;" />', obj.image.url)
        return ""
    
    image_preview.short_description = 'Vista previa'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock', 'category', 'created_at', 'product_image')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock')
    readonly_fields = ('created_at', 'product_image')
    inlines = [ProductImageInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price', 'stock', 'category', 'image', 'product_image')
        }),
        ('Fechas', {
            'fields': ('created_at',),
        }),
    )

    def product_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" style="border-radius: 6px;" />', obj.image.url)
        return "(Sin imagen)"
    
    product_image.short_description = 'Principal'
