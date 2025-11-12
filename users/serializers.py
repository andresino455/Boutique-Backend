# users/views.py - Serializer corregido
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import CustomUser

# users/views.py - Versión simplificada
class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'is_active', 'is_staff', 'date_joined', 'password']
        read_only_fields = ['id', 'date_joined']

    def validate(self, attrs):
        # Validación de email único
        email = attrs.get('email')
        if email:
            queryset = CustomUser.objects.filter(email=email)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            if queryset.exists():
                raise serializers.ValidationError({"email": "Este email ya está registrado."})
            
        # Validación de username único
        username = attrs.get('username')
        if username:
            queryset = CustomUser.objects.filter(username=username)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            if queryset.exists():
                raise serializers.ValidationError({"username": "Este nombre de usuario ya existe."})
            
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        if not password:
            raise serializers.ValidationError({"password": "La contraseña es requerida."})
            
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance
# Vistas de administración
class UserAdminListView(generics.ListAPIView):
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

class UserAdminCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAdminUser]

class UserAdminUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAdminUser]

class UserAdminDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAdminUser]