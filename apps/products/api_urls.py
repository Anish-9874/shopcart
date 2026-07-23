from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register(r"products", api_views.ProductViewSet, basename="product")
urlpatterns = router.urls
