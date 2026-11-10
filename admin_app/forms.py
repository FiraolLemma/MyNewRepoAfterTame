from django import forms
from django.utils.translation import gettext_lazy as _


class DashboardSearchForm(forms.Form):
    q = forms.CharField(
        label=_("Search records"),
        required=False,
        max_length=100,
        widget=forms.SearchInput(
            attrs={
                "placeholder": _("Farm, product, manager, or order"),
                "autocomplete": "off",
            }
        ),
    )