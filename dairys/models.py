from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

PRODUCT_CATEGORY_SPECS = (
    ("fresh-milk", "Raw milk", "milk", ""),
    ("milk-butter", "Butter", "milk", ""),
    ("milk-cheese", "Cheese", "milk", ""),
    ("yogurt", "Yogurt", "milk", ""),
    ("milk-ergo", "Ergo", "milk", ""),
    ("milk-ayib", "Ayib", "milk", ""),
    ("milk-items", "Milking machines", "items", "milking"),
    ("milking-buckets", "Milking buckets", "items", "milking"),
    ("milk-cans-churns", "Milk cans / churns", "items", "milking"),
    ("cooling-storage", "Milk storage containers", "items", "cooling"),
    ("milk-cooling-gear", "Milk cooling tanks / gear", "items", "cooling"),
    ("processing", "Cream separators", "items", "processing"),
    ("dairy-churners", "Churners", "items", "processing"),
    ("pasteurizers", "Pasteurizers", "items", "processing"),
    ("feed-equipment", "Cattle feeding equipment", "items", "feeding"),
    ("feed-troughs", "Feed troughs", "items", "feeding"),
    ("calf-feeders", "Calf feeders", "items", "feeding"),
    ("feed-supplies", "Hay / silage / concentrates", "items", "feeding"),
    ("bedding", "Bedding", "items", "feeding"),
    ("infrastructure-health", "Construction materials", "items", "infrastructure"),
    ("veterinary-hygiene", "Veterinary / hygiene supplies", "items", "infrastructure"),
    ("dairy-cattle", "Dairy cows", "livestock", ""),
    ("heifers", "Heifers", "livestock", ""),
    ("calves", "Calves", "livestock", ""),
    ("breeding-bulls", "Breeding bulls / sires", "livestock", ""),
)


def ensure_product_categories():
    for slug, name, main_category, _item_group in PRODUCT_CATEGORY_SPECS:
        DairyCategory.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "main_category": main_category},
        )


class DairyCategory(models.Model):
    class MainCategory(models.TextChoices):
        MILK = "milk", _("Fresh Milk & Dairy Products")
        ITEMS = "items", _("Dairy Farm Items")
        LIVESTOCK = "livestock", _("Dairy Cattle & Livestock")
        TRAINING = "training", _("Dairy Farm Training")
        CONSULTING = "consulting", _("Dairy Farm Consulting")

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=110)
    main_category = models.CharField(max_length=20, choices=MainCategory.choices, default=MainCategory.ITEMS)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = _("Dairy category")
        verbose_name_plural = _("Dairy categories")
        ordering = ["main_category", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class DairyProduct(models.Model):
    class ItemGroup(models.TextChoices):
        MILKING = "milking", _("Milking & Handling")
        COOLING = "cooling", _("Cooling & Storage")
        PROCESSING = "processing", _("Processing")
        FEEDING = "feeding", _("Feeding & Bedding")
        INFRASTRUCTURE = "infrastructure", _("Infrastructure & Health")

    class MilkSource(models.TextChoices):
        COW = "cow", _("Cow")
        GOAT = "goat", _("Goat")
        CAMEL = "camel", _("Camel")

    class MilkUnit(models.TextChoices):
        LITERS = "liters", _("Liters")
        KG = "kg", _("Kg")
        CONTAINERS = "containers", _("Containers")

    class LivestockType(models.TextChoices):
        COW = "dairy_cow", _("Dairy cow")
        HEIFER = "heifer", _("Heifer")
        CALF = "calf", _("Calf")
        BULL = "bull", _("Breeding bull / sire")

    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True, max_length=180)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    main_category = models.CharField(
        max_length=20,
        choices=[
            (DairyCategory.MainCategory.MILK, _("Fresh Milk & Dairy Products")),
            (DairyCategory.MainCategory.ITEMS, _("Dairy Farm Items")),
            (DairyCategory.MainCategory.LIVESTOCK, _("Dairy Cattle & Livestock")),
        ],
        default=DairyCategory.MainCategory.ITEMS,
        db_index=True,
    )
    category = models.ForeignKey(DairyCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    subcategory = models.CharField(max_length=100, blank=True)
    item_group = models.CharField(max_length=24, choices=ItemGroup.choices, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dairy_products")
    company = models.ForeignKey("companies.Company", on_delete=models.SET_NULL, related_name="dairy_products", null=True, blank=True)
    farm = models.ForeignKey("companies.Farm", on_delete=models.SET_NULL, related_name="dairy_products", null=True, blank=True)
    main_image = models.ImageField(upload_to="dairys/products/", blank=True)
    unit = models.CharField(max_length=30, blank=True)
    quantity_available = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=160, blank=True)
    milk_source = models.CharField(max_length=20, choices=MilkSource.choices, blank=True)
    milk_unit = models.CharField(max_length=20, choices=MilkUnit.choices, blank=True)
    collection_date = models.DateField(null=True, blank=True)
    livestock_type = models.CharField(max_length=20, choices=LivestockType.choices, blank=True)
    breed = models.CharField(max_length=100, blank=True)
    age_months = models.PositiveIntegerField(null=True, blank=True)
    lactation_status = models.CharField(max_length=100, blank=True)
    daily_milk_yield = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text=_("Average liters per day"))
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            number = 1
            while DairyProduct.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{number}"
                number += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("dairys:product_detail", kwargs={"slug": self.slug})

    @property
    def display_price(self):
        return f"ETB {self.price:.2f}"


class DairyService(models.Model):
    class ServiceKind(models.TextChoices):
        TRAINING = "training", _("Dairy Farm Training")
        CONSULTING = "consulting", _("Dairy Farm Consulting")

    class Format(models.TextChoices):
        IN_PERSON = "in_person", _("In-person")
        ONLINE = "online", _("Online")

    class ServiceType(models.TextChoices):
        CLEAN_MILK = "clean_milk_hygiene", _("Clean milk production & hygiene")
        CATTLE_FEEDING = "cattle_feeding", _("Cattle feeding & ration formulation")
        CALF_REARING = "calf_rearing", _("Calf rearing")
        PROCESSING_WORKSHOP = "processing_workshop", _("Dairy processing workshops")
        FARM_SETUP = "farm_setup", _("Farm setup & barn layout advisory")
        HERD_HEALTH = "herd_health", _("Herd health & mastitis prevention")
        BREEDING = "breeding_ai", _("Breeding / AI planning")
        MILK_YIELD = "milk_yield", _("Milk yield optimization")

    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dairy_services")
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True, max_length=180)
    service_kind = models.CharField(max_length=20, choices=ServiceKind.choices, default=ServiceKind.CONSULTING)
    service_type = models.CharField(max_length=100, choices=ServiceType.choices)
    description = models.TextField()
    training_format = models.CharField(max_length=20, choices=Format.choices, blank=True)
    schedule = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=160, blank=True)
    service_area = models.CharField(max_length=160, blank=True)
    availability = models.CharField(max_length=160, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            number = 1
            while DairyService.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{number}"
                number += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("dairys:dairy_service_detail", kwargs={"slug": self.slug})

    @property
    def display_price(self):
        return f"ETB {self.price:.2f}"


class TrainingEnrollment(models.Model):
    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    topic = models.CharField(
        max_length=100,
        choices=[
            (DairyService.ServiceType.CLEAN_MILK, _("Clean milk production & hygiene")),
            (DairyService.ServiceType.CATTLE_FEEDING, _("Cattle feeding & ration formulation")),
            (DairyService.ServiceType.CALF_REARING, _("Calf rearing")),
            (DairyService.ServiceType.PROCESSING_WORKSHOP, _("Dairy processing workshops")),
        ],
    )
    format = models.CharField(max_length=20, choices=DairyService.Format.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.topic}"


class DairyConsultation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    service = models.ForeignKey(DairyService, on_delete=models.CASCADE, related_name="consultation_requests")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="dairy_consultations")
    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    preferred_date = models.DateField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
