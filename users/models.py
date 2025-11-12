# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    
    ROLE_CHOICES = [
        ('customer', 'Cliente'),
        ('seller', 'Vendedor'),
        ('admin', 'Administrador'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return self.username

    @property
    def is_customer(self):
        return self.role == 'customer'
    
    @property
    def is_seller(self):
        return self.role == 'seller'
    
    @property
    def is_admin(self):
        return self.role == 'admin'