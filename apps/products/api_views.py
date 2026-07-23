from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import BasicAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.viewsets import ModelViewSet

from apps.products.models import Product
from apps.products.serializers import ProductSerializer


@method_decorator(cache_page(60 * 5), name="list")
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "price"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name"]
    ordering = ["id"]  # Default ordering by id
