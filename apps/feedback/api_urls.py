from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register(r"feedback", api_views.FeedbackViewSet, basename="feedback")
urlpatterns = router.urls
