from django import forms

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, "★★★★★ — Excellent"),
        (4, "★★★★☆ — Very Good"),
        (3, "★★★☆☆ — Good"),
        (2, "★★☆☆☆ — Fair"),
        (1, "★☆☆☆☆ — Poor"),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        required=True,
    )

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": ("Share your experience with this product..."),
            }
        ),
    )

    class Meta:
        model = Feedback
        fields = ["rating", "message"]

    def clean_rating(self):
        rating = int(self.cleaned_data["rating"])

        if rating < 1 or rating > 5:
            raise forms.ValidationError("Please select a rating from 1 to 5 stars.")

        return rating
