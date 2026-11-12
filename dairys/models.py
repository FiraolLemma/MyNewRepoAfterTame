# project/Dairys/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from cart.models import CartItem

class DairyCategory(models.Model):
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('K', 'Kids'),
        ('U', 'Unisex'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    icon = models.CharField(max_length=30, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_gender_display()} - {self.name}"

class DairyItem(models.Model): 
    category = models.ForeignKey(DairyCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=1)
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='clothes'
    )
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_dairys',
        blank=True
    )

    def increment_likes(self):
        self.like_count += 1
        self.save(update_fields=['like_count'])
        return self.like_count

    def toggle_like(self, user):
        if user in self.liked_by.all():
            self.liked_by.remove(user)
        else:
            self.liked_by.add(user)
        self.like_count = self.liked_by.count()
        self.save()
        return self.like_count

    def increment_shares(self):
        self.share_count += 1
        self.save(update_fields=['share_count'])
        return self.share_count
    
    def has_liked(self, user):
        """Return whether the user has liked this legacy item."""
        if user.is_authenticated:
            return self.liked_by.filter(pk=user.pk).exists()
        return False

    def __str__(self):
        return f"{self.name} ({self.category})"

    def get_absolute_url(self):
        return reverse("dairys:dairy_detail", kwargs={"slug": self.slug})

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def is_on_sale(self):
        return self.discount_price is not None
    cart_items = GenericRelation(CartItem, content_type_field='content_type', object_id_field='object_id')

class DairyImage(models.Model):
    dairys = models.ForeignKey(DairyItem, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='dairy_images/')
    is_main = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Imafge for {self.dairys.name}"


class DairyCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Dairy categories"

    def __str__(self):
        return self.name


class DairyProduct(models.Model):
    class Unit(models.TextChoices):
        LITER = "liter", "Liter"
        KILOGRAM = "kg", "Kilogram"
        PIECE = "piece", "Piece"
        PACKAGE = "package", "Package"

    category = models.ForeignKey(
        DairyCategory,
        on_delete=models.PROTECT,
        related_name="products",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dairy_products",
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        related_name="dairy_products",
        null=True,
        blank=True,
    )
    farm = models.ForeignKey(
        "companies.Farm",
        on_delete=models.SET_NULL,
        related_name="dairy_products",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.PIECE)
    quantity_available = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=120)
    image = models.ImageField(upload_to="dairy/products/", blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_dairy_products",
        blank=True,
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("category", "location"), name="dairy_prod_category_loc"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("dairys:product_detail", kwargs={"slug": self.slug})

    @property
    def display_price(self):
        return f"ETB {self.price:.2f} / {self.get_unit_display()}"

    def toggle_like(self, user):
        if self.liked_by.filter(pk=user.pk).exists():
            self.liked_by.remove(user)
        else:
            self.liked_by.add(user)
        self.like_count = self.liked_by.count()
        self.save(update_fields=("like_count",))
        return self.like_count

    def increment_shares(self):
        self.share_count += 1
        self.save(update_fields=("share_count",))
        return self.share_count


class DairyService(models.Model):
    class ServiceType(models.TextChoices):
        ANIMAL_CARE = "animal_care", "Dairy animal care"
        FARM_CONSULTING = "farm_consulting", "Farm consulting"
        MILK_COLLECTION = "milk_collection", "Milk collection"
        MILK_PROCESSING = "milk_processing", "Milk processing"
        DELIVERY = "delivery", "Delivery"
        EQUIPMENT_REPAIR = "equipment_repair", "Equipment repair"
        TRAINING = "training", "Dairy farming training"

    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dairy_services",
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        related_name="dairy_services",
        null=True,
        blank=True,
    )
    farm = models.ForeignKey(
        "companies.Farm",
        on_delete=models.SET_NULL,
        related_name="dairy_services",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    service_type = models.CharField(max_length=30, choices=ServiceType.choices)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=120)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} - {self.provider.username}"

    def get_absolute_url(self):
        return reverse("dairys:dairy_service_detail", kwargs={"slug": self.slug})