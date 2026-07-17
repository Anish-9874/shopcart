from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'carts', api_views.CartViewSet)
router.register(r'cart-items', api_views.CartItemViewSet)
router.register(r'orders', api_views.OrderViewSet)
router.register(r'order-items', api_views.OrderItemViewSet)


urlpatterns = router.urls