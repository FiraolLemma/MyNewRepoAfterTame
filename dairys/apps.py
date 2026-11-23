from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DairysConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dairys"
    label = "dairys"
    verbose_name = _("Dairy and livestock")
