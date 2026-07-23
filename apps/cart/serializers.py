from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem


class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)  # NESTED SERIALIZER
    product = serializers.StringRelatedField(
        read_only=True
    )  # ACCESSING STRING(SUCH AS NAME) INSTEAD OF ID

    class Meta:
        model = CartItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(
        read_only=True
    )  # IF WE DO (many=True ) it is for many to many relations

    class Meta:
        model = Order
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"
