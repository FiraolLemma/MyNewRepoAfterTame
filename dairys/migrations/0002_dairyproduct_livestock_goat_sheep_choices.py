import django.core.validators
from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("dairys", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dairyproduct",
            name="livestock_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("dairy_cow", _("Dairy cow")),
                    ("heifer", _("Heifer")),
                    ("calf", _("Calf")),
                    ("bull", _("Breeding bull / sire")),
                    ("goat", _("Goat")),
                    ("sheep", _("Sheep")),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="dairyproduct",
            name="daily_milk_yield",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text=_("Average liters per day"),
                max_digits=6,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
    ]
