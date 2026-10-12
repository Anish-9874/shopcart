# from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from .models import Feedback
from .serializers import FeedbackSerializer


class FeedbackViewSet(ModelViewSet):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()


# @action creates custom endpoints beyond standard CRUD operations.
# @action(detail=True, methods=["post"])
# def like(self, request, pk=None):
#     feedback = self.get_object()
#     feedback.likes += 1
#     feedback.save()
#     return Response({"likes": feedback.likes})
