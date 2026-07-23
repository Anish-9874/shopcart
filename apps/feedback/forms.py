from django import forms

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["message"]

        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Type your feedback",
                }
            )
        }
