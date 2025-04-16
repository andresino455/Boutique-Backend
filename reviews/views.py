from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.exceptions import ValidationError

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product = self.request.data.get('product')
        user = self.request.user
        if Review.objects.filter(product_id=product, user=user).exists():
            raise ValidationError("Ya has dejado una review para este producto.")
        serializer.save(user=user)

class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id).order_by('-created_at')
