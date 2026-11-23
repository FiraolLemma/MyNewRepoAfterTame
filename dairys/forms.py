from django import forms

from companies.forms import OrganizationSelectionMixin
from .models import (
    DairyCategory,
    DairyConsultation,
    DairyProduct,
    DairyService,
    PRODUCT_CATEGORY_SPECS,
    TrainingEnrollment,
)


PRODUCT_MAIN_CATEGORIES = (
    DairyCategory.MainCategory.MILK,
    DairyCategory.MainCategory.ITEMS,
    DairyCategory.MainCategory.LIVESTOCK,
)
SERVICE_TYPES_BY_KIND = {
    DairyService.ServiceKind.TRAINING: (
        DairyService.ServiceType.CLEAN_MILK,
        DairyService.ServiceType.CATTLE_FEEDING,
        DairyService.ServiceType.CALF_REARING,
        DairyService.ServiceType.PROCESSING_WORKSHOP,
    ),
    DairyService.ServiceKind.CONSULTING: (
        DairyService.ServiceType.FARM_SETUP,
        DairyService.ServiceType.HERD_HEALTH,
        DairyService.ServiceType.BREEDING,
        DairyService.ServiceType.MILK_YIELD,
    ),
}


class DairyProductForm(OrganizationSelectionMixin, forms.ModelForm):
    class Meta:
        model = DairyProduct
        fields = [
            "name", "description", "price", "main_category", "category",
            "item_group", "main_image", "unit", "quantity_available",
            "location", "milk_source", "milk_unit", "collection_date",
            "livestock_type", "breed", "age_months", "lactation_status",
            "daily_milk_yield", "company", "farm",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "collection_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }
        labels = {
            "main_category": "Main category",
            "category": "Subcategory",
            "item_group": "Dairy farm item group",
            "unit": "Listing unit details (optional)",
            "milk_unit": "Unit / volume",
            "collection_date": "Freshness / collection date",
            "lactation_status": "Lactation / pregnancy status",
            "daily_milk_yield": "Average daily milk yield (liters)",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        self.fields["category"].queryset = DairyCategory.objects.filter(
            main_category__in=PRODUCT_MAIN_CATEGORIES
        ).order_by("main_category", "name")
        self.fields["category"].label_from_instance = (
            lambda category: f"{category.get_main_category_display()} - {category.name}"
        )
        self.fields["category"].required = True
        self.fields["milk_source"].required = False
        self.fields["milk_unit"].required = False
        self.fields["item_group"].required = False
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.ClearableFileInput)):
                field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        main_category = cleaned_data.get("main_category")
        if category and main_category and category.main_category != main_category:
            self.add_error("category", "Choose a subcategory within the selected main category.")
        if category and main_category == DairyCategory.MainCategory.ITEMS:
            category_group = next(
                (group for slug, _name, _main, group in PRODUCT_CATEGORY_SPECS if slug == category.slug),
                "",
            )
            if category_group != cleaned_data.get("item_group"):
                self.add_error("item_group", "Choose the item group for the selected subcategory.")
        if main_category == DairyCategory.MainCategory.MILK:
            if not cleaned_data.get("milk_unit"):
                self.add_error("milk_unit", "Select the product unit or volume.")
            if category and category.slug == "fresh-milk":
                if not cleaned_data.get("milk_source"):
                    self.add_error("milk_source", "Select the milk source.")
                if not cleaned_data.get("collection_date"):
                    self.add_error("collection_date", "Enter the collection date.")
        if main_category == DairyCategory.MainCategory.LIVESTOCK:
            livestock_types = {
                "dairy-cattle": DairyProduct.LivestockType.COW,
                "heifers": DairyProduct.LivestockType.HEIFER,
                "calves": DairyProduct.LivestockType.CALF,
                "breeding-bulls": DairyProduct.LivestockType.BULL,
            }
            livestock_type = cleaned_data.get("livestock_type")
            expected_type = livestock_types.get(category.slug) if category else None
            if not livestock_type:
                self.add_error("livestock_type", "Select the livestock type.")
            elif expected_type and livestock_type != expected_type:
                self.add_error("livestock_type", "Choose the type that matches the selected subcategory.")
        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=False)
        product.subcategory = product.category.name if product.category_id else ""
        if commit:
            product.save()
            self.save_m2m()
        return product


class DairyServiceForm(forms.ModelForm):
    class Meta:
        model = DairyService
        fields = [
            "name", "service_kind", "service_type", "description", "training_format",
            "schedule", "location", "service_area", "availability", "price",
            "is_available", "is_featured",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 5, "class": "form-control"})}
        labels = {
            "service_type": "Training topic / consultation type",
            "training_format": "Training format",
            "schedule": "Schedule / duration",
            "service_area": "Consultation service area",
            "availability": "Service availability",
            "price": "Fee (ETB)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_type"].choices = [
            ("", "Select a topic or service"),
            *DairyService.ServiceType.choices,
        ]
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned_data = super().clean()
        kind = cleaned_data.get("service_kind")
        service_type = cleaned_data.get("service_type")
        if kind and service_type and service_type not in SERVICE_TYPES_BY_KIND[kind]:
            self.add_error("service_type", "Choose a service type for the selected category.")
        return cleaned_data


class TrainingEnrollmentForm(forms.ModelForm):
    class Meta:
        model = TrainingEnrollment
        fields = ["name", "email", "phone", "topic", "format"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        topics = SERVICE_TYPES_BY_KIND[DairyService.ServiceKind.TRAINING]
        self.fields["topic"].choices = [
            (value, DairyService.ServiceType(value).label) for value in topics
        ]
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class DairyConsultationForm(forms.ModelForm):
    class Meta:
        model = DairyConsultation
        fields = ["name", "email", "phone", "preferred_date", "message"]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "message": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
