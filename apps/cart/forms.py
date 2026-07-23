from django import forms


class CheckoutForm(forms.Form):

    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Full Name"}
        ),
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Phone Number"}
        ),
    )

    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Delivery Address",
            }
        )
    )

    payment_method = forms.ChoiceField(
        choices=[
            ("COD", "Cash on Delivery"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
