from rest_framework.viewsets import ModelViewSet
from .serializers import FeedbackSerializer
from .models import Feedback
from rest_framework.decorators import action

class FeedbackViewSet(ModelViewSet):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()




#@action is used to create custom endpoints that are not part of the standard CRUD operations
    # @action(detail=True, methods=["post"])
    # def like(self, request, pk=None):
    #     feedback = self.get_object()
    #     feedback.likes += 1
    #     feedback.save()
    #     return Response({"likes": feedback.likes})