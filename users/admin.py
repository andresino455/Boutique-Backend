# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Campos a mostrar en la lista de usuarios
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # Campos para búsqueda rápida
    filter_horizontal = ('groups', 'user_permissions')
    
    # Campos en la vista de edición
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información personal'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Roles y permisos'), {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('Fechas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Campos al crear nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email',
                'role',
                'password1', 
                'password2',
                'is_active',
                'is_staff'
            ),
        }),
    )
    
    # Acciones personalizadas
    actions = ['make_seller', 'make_customer', 'make_admin']
    
    def make_seller(self, request, queryset):
        updated = queryset.update(role='seller')
        self.message_user(request, f'{updated} usuarios marcados como vendedores.')
    make_seller.short_description = "Marcar como vendedores"
    
    def make_customer(self, request, queryset):
        updated = queryset.update(role='customer')
        self.message_user(request, f'{updated} usuarios marcados como clientes.')
    make_customer.short_description = "Marcar como clientes"
    
    def make_admin(self, request, queryset):
        updated = queryset.update(role='admin')
        self.message_user(request, f'{updated} usuarios marcados como administradores.')
    make_admin.short_description = "Marcar como administradores"


    