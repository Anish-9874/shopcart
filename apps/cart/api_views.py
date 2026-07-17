from rest_framework.viewsets import ModelViewSet
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
from .models import Cart, CartItem, Order, OrderItem
from rest_framework.pagination import PageNumberPagination, CursorPagination


class CartPagination1(PageNumberPagination):
    page_size = 5;

class CartPagination2(CursorPagination):
    page_size = 2;
    ordering = "id"


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer



class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    pagination_class = CartPagination2


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    