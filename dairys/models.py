from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class DairyCategory(models.Model):
    MAIN_CATEGORY_CHOICES = [
        ("milk", _("Fresh Milk & Dairy Products")),
        ("items", _("Dairy Farm Items")),
        ("livestock", _("Dairy Cattle & Livestock")),
        ("training", _("Dairy Farm Training")),
        ("consulting", _("Dairy Farm Consulting")),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True)
    main_category = models.CharField(max_length=20, choices=MAIN_CATEGORY_CHOICES, default="items")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["main_category", "name"]
        verbose_name = _("Dairy category")
        verbose_name_plural = _("Dairy categories")

    def __str__(self):
        return self.name


class TrainingEnrollment(models.Model):
    TOPIC_CHOICES = [
        ("clean_milk_hygiene", _("Clean milk production & hygiene")),
        ("cattle_feeding", _("Cattle feeding & ration formulation")),
        ("calf_rearing", _("Calf rearing")),
        ("processing_workshop", _("Dairy processing workshops")),
    ]
    FORMAT_CHOICES = [
        ("in_person", _("In-person")),
        ("online", _("Online")),
    ]

    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    topic = models.CharField(max_length=100, choices=TOPIC_CHOICES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.get_topic_display()}"


class DairyProduct(models.Model):
    MAIN_CATEGORY_CHOICES = [
        ("milk", _("Fresh Milk & Dairy Products")),
        ("items", _("Dairy Farm Items")),
        ("livestock", _("Dairy Cattle & Livestock")),
    ]
    ITEM_GROUP_CHOICES = [
        ("milking", _("Milking & Handling")),
        ("cooling", _("Cooling & Storage")),
        ("processing", _("Processing")),
        ("feeding", _("Feeding & Bedding")),
        ("infrastructure", _("Infrastructure & Health")),
    ]
    MILK_SOURCE_CHOICES = [
        ("cow", _("Cow")),
        ("goat", _("Goat")),
        ("camel", _("Camel")),
    ]
    MILK_UNIT_CHOICES = [
        ("liters", _("Liters")),
        ("kg", _("Kg")),
        ("containers", _("Containers")),
    ]
    LIVESTOCK_TYPE_CHOICES = [
        ("dairy_cow", _("Dairy cow")),
        ("heifer", _("Heifer")),
        ("calf", _("Calf")),
        ("bull", _("Breeding bull / sire")),
        ("goat", _("Goat")),
        ("sheep", _("Sheep")),
    ]

    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    main_category = models.CharField(
        max_length=20,
        choices=MAIN_CATEGORY_CHOICES,
        default="items",
        db_index=True,
    )
    subcategory = models.CharField(max_length=100, blank=True)
    item_group = models.CharField(max_length=24, choices=ITEM_GROUP_CHOICES, blank=True)
    main_image = models.ImageField(upload_to="dairys/products/", blank=True)
    unit = models.CharField(max_length=30, blank=True)
    quantity_available = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=160, blank=True)
    milk_source = models.CharField(max_length=20, choices=MILK_SOURCE_CHOICES, blank=True)
    milk_unit = models.CharField(max_length=20, choices=MILK_UNIT_CHOICES, blank=True)
    collection_date = models.DateField(blank=True, null=True)
    livestock_type = models.CharField(max_length=20, choices=LIVESTOCK_TYPE_CHOICES, blank=True)
    breed = models.CharField(max_length=100, blank=True)
    age_months = models.PositiveIntegerField(blank=True, null=True)
    lactation_status = models.CharField(max_length=100, blank=True)
    daily_milk_yield = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text=_("Average liters per day"),
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        DairyCategory,
        on_delete=models.SET_NULL,
        related_name="products",
        blank=True,
        null=True,
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        related_name="dairy_products",
        blank=True,
        null=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dairy_products",
    )
    farm = models.ForeignKey(
        "companies.Farm",
        on_delete=models.SET_NULL,
        related_name="dairy_products",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.main_category == "items":
            return reverse("dairys:item_detail", kwargs={"item_id": self.pk})
        if self.main_category == "livestock":
            return reverse(
                "dairys:cattle_livestock_detail",
                kwargs={"cattle_livestock_id": self.pk},
            )
        return reverse("dairys:product_detail", kwargs={"slug": self.slug})

    @property
    def seller_name(self):
        return self.created_by.get_full_name() or self.created_by.username


class DairyService(models.Model):
    CONSULTING_SERVICE_TYPE_VALUES = (
        "farm_setup",
        "herd_health",
        "breeding_ai",
        "milk_yield",
    )
    SERVICE_KIND_CHOICES = [
        ("training", _("Dairy Farm Training")),
        ("consulting", _("Dairy Farm Consulting")),
    ]
    SERVICE_TYPE_CHOICES = [
        ("clean_milk_hygiene", _("Clean milk production & hygiene")),
        ("cattle_feeding", _("Cattle feeding & ration formulation")),
        ("calf_rearing", _("Calf rearing")),
        ("processing_workshop", _("Dairy processing workshops")),
        ("farm_setup", _("Farm setup & barn layout advisory")),
        ("herd_health", _("Herd health & mastitis prevention")),
        ("breeding_ai", _("Breeding / AI planning")),
        ("milk_yield", _("Milk yield optimization")),
    ]
    TRAINING_FORMAT_CHOICES = [
        ("in_person", _("In-person")),
        ("online", _("Online")),
    ]

    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    service_kind = models.CharField(max_length=20, choices=SERVICE_KIND_CHOICES, default="consulting")
    service_type = models.CharField(max_length=100, choices=SERVICE_TYPE_CHOICES)
    description = models.TextField()
    training_format = models.CharField(max_length=20, choices=TRAINING_FORMAT_CHOICES, blank=True)
    schedule = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=160, blank=True)
    service_area = models.CharField(max_length=160, blank=True)
    availability = models.CharField(max_length=160, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dairy_services",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.service_kind == "consulting":
            return f"{reverse('dairys:veterinary_consultancy')}#consultant-{self.pk}"
        return reverse("dairys:index")

    @property
    def display_price(self):
        if self.price == 0:
            return _("Free")
        return f"{self.price:,.2f} ETB"


class DairyConsultation(models.Model):
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("confirmed", _("Confirmed")),
        ("completed", _("Completed")),
        ("cancelled", _("Cancelled")),
    ]

    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    preferred_date = models.DateField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="dairy_consultations",
        blank=True,
        null=True,
    )
    service = models.ForeignKey(
        DairyService,
        on_delete=models.CASCADE,
        related_name="consultation_requests",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.service.name}"