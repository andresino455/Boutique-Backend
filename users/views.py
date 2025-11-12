# users/views.py
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model


User = get_user_model()



# users/views.py - Agregar estas vistas
from rest_framework import generics, permissions
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import CustomUser

# Serializer para administración
class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'date_joined']

# Serializer para crear usuarios (admin)
class UserCreateAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Las contraseñas no coinciden."})
        
        # Verificar si el email ya existe
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Este email ya está registrado."})
            
        # Verificar si el username ya existe
        if CustomUser.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Este nombre de usuario ya existe."})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Serializer para actualizar usuarios (admin)
class UserUpdateAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        
    def validate_email(self, value):
        # Excluir el usuario actual al verificar duplicados
        if self.instance and CustomUser.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
        
    def validate_username(self, value):
        # Excluir el usuario actual al verificar duplicados
        if self.instance and CustomUser.objects.filter(username=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Este nombre de usuario ya existe.")
        return value

class UserAdminListView(generics.ListAPIView):
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserUpdateAdminSerializer  # Usar el mismo serializer para lista
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

class UserAdminCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserCreateAdminSerializer
    permission_classes = [permissions.IsAdminUser]

class UserAdminUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateAdminSerializer
    permission_classes = [permissions.IsAdminUser]

class UserAdminDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAdminUser]

# users/views.py - Agregar al final del archivo

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Serializer para usuario actual
class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'date_joined']

# Vista para obtener usuario actual
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Devuelve los datos del usuario autenticado actualmente
        """
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)