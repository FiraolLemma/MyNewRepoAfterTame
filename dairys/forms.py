from django import forms

from companies.forms import OrganizationSelectionMixin
from .models import DairyProduct, DairyService


class DairyProductForm(OrganizationSelectionMixin, forms.ModelForm):
    class Meta:
        model = DairyProduct
        fields = (
            "name",
            "category",
            "description",
            "price",
            "unit",
            "quantity_available",
            "location",
            "image",
            "company",
            "farm",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class DairyServiceForm(OrganizationSelectionMixin, forms.ModelForm):
    class Meta:
        model = DairyService
        fields = ("name", "service_type", "description", "price", "location", "company", "farm")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
