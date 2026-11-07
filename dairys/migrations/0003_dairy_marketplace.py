import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clothings", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DairyCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
                ("icon", models.CharField(blank=True, max_length=50)),
            ],
            options={
                "verbose_name_plural": "Dairy categories",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="DairyProduct",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("unit", models.CharField(choices=[("liter", "Liter"), ("kg", "Kilogram"), ("piece", "Piece"), ("package", "Package")], default="piece", max_length=10)),
                ("quantity_available", models.PositiveIntegerField(default=1)),
                ("location", models.CharField(max_length=120)),
                ("image", models.ImageField(blank=True, upload_to="dairy/products/")),
                ("is_featured", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("like_count", models.PositiveIntegerField(default=0)),
                ("share_count", models.PositiveIntegerField(default=0)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="clothings.dairycategory")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dairy_products", to=settings.AUTH_USER_MODEL)),
                ("liked_by", models.ManyToManyField(blank=True, related_name="liked_dairy_products", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
                "indexes": [models.Index(fields=["category", "location"], name="dairy_prod_category_loc")],
            },
        ),
        migrations.CreateModel(
            name="DairyService",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("service_type", models.CharField(choices=[("animal_care", "Dairy animal care"), ("farm_consulting", "Farm consulting"), ("milk_collection", "Milk collection"), ("milk_processing", "Milk processing"), ("delivery", "Delivery"), ("equipment_repair", "Equipment repair"), ("training", "Dairy farming training")], max_length=30)),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("location", models.CharField(max_length=120)),
                ("is_available", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("provider", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dairy_services", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
