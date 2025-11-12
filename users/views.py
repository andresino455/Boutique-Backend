# users/views.py
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import CustomUser

User = get_user_model()

# Serializer para registro público
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        
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
        
        # Establecer role por defecto como 'customer'
        validated_data['role'] = 'customer'
        
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Serializer para usuario actual
class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'date_joined']

# Serializer para administración
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

# Vista para registro público
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "success": True,
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)

# Vista para obtener usuario actual
class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Devuelve los datos del usuario autenticado actualmente
        """
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)

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