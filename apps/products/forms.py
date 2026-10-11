from django import forms

from .models import Category, Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = "__all__"


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ["name", "description", "image"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter category name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter category description",
                    "rows": 4,
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }
