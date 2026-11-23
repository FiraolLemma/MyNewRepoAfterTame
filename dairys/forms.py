from django import forms
from companies.forms import OrganizationSelectionMixin

from .models import DairyProduct


class DairyProductForm(OrganizationSelectionMixin, forms.ModelForm):
    class Meta:
        model = DairyProduct
        fields = (
            "name",
            "description",
            "price",
            "subcategory",
            "milk_source",
            "milk_unit",
            "unit",
            "quantity_available",
            "location",
            "collection_date",
            "main_image",
            "company",
            "farm",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "quantity_available": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "collection_date": forms.DateInput(attrs={"type": "date"}),
            "main_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "form-select" if isinstance(field.widget, forms.Select) else "form-control",
            )

    def clean_name(self):
        return self.cleaned_data["name"].strip()