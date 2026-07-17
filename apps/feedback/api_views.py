from rest_framework.viewsets import ModelViewSet
from .serializers import FeedbackSerializer
from .models import Feedback

class FeedbackViewSet(ModelViewSet):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()