# poultrys/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=110)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            
            self.slug = unique_slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"


class Item(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=110, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='items'
    )
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='items', 
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        related_name="poultry_items",
        null=True,
        blank=True,
    )
    farm = models.ForeignKey(
        "companies.Farm",
        on_delete=models.SET_NULL,
        related_name="poultry_items",
        null=True,
        blank=True,
    )
    main_image = models.ImageField(
        upload_to='products/main_images/',
        default='products/default.jpg',
        blank=True
    )
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_items',
        blank=True
    )

    def increment_likes(self):
        self.like_count += 1
        self.save()
        return self.like_count
    
    def toggle_like(self, user):
        if user in self.liked_by.all():
            self.liked_by.remove(user)
        else:
            self.liked_by.add(user)
        self.like_count = self.liked_by.count()
        self.save()
        return self.like_count
    
    def has_liked(self, user):
        """Return True if the user has liked this item."""
        if user.is_authenticated:
            return self.liked_by.filter(pk=user.pk).exists()
        return False


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            
            while Item.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            
            self.slug = unique_slug
        super().save(*args, **kwargs)

    @property
    def display_price(self):
        return f"${self.price:.2f}"

class SubImage(models.Model):
    item = models.ForeignKey(
        Item, 
        related_name='sub_images', 
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='products/sub_images/',
        default='products/default.jpg',
        blank=True
    )
    alt_text = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Image for {self.item.name}"

# consultancy model

class Consultant(models.Model):
    # Consultant Types/Specialties (you can add more)
    class Specialty(models.TextChoices):
        DISEASE = 'disease', _('Disease Management')
        NUTRITION = 'nutrition', _('Nutrition & Feed')
        PREVENTION = 'prevention', _('Biosecurity & Prevention')
        BREEDING = 'breeding', _('Breeding & Genetics')
        GENERAL = 'general', _('General Practice')

    class Availability(models.TextChoices):
        WEEKDAYS = 'weekdays', _('Weekdays')
        WEEKENDS = 'weekends', _('Weekends')
        ALL_WEEK = 'all_week', _('All Week')
        EMERGENCY = 'emergency', _('24/7 Emergency')

    # Main Fields
    name = models.CharField(max_length=200)
    experience = models.PositiveIntegerField(help_text=_("Years of experience"))
    specialty = models.CharField(max_length=20, choices=Specialty.choices)
    languages = models.CharField(max_length=200, help_text=_("Comma-separated list of languages"))
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0
    )
    rating_count = models.PositiveIntegerField(default=0)
    description = models.TextField()
    availability = models.CharField(max_length=20, choices=Availability.choices)
    # Contact/Social Information (optional)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    facebook = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True) # For click-to-chat

    # Professional details
    is_available = models.BooleanField(default=True)
    consultation_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} - {self.get_specialty_display()}"

    class Meta:
        ordering = ['-rating']

class ConsultationService(models.Model):
    # Types of services offered
    class ServiceType(models.TextChoices):
        VIDEO_CALL = 'video', _('Video Call')
        PHONE_CALL = 'phone', _('Phone Consultation')
        FARM_VISIT = 'visit', _('Farm Visit')
        FEED_ANALYSIS = 'analysis', _('Feed Analysis')
        FARM_ASSESSMENT = 'assessment', _('Farm Assessment')

    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.CharField(max_length=50, blank=True, help_text=_("e.g., 1 hour, per visit"))

    def __str__(self):
        return f"{self.consultant.name} - {self.get_service_type_display()}"

class ConsultationBooking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')

    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    service = models.ForeignKey(ConsultationService, on_delete=models.CASCADE)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="poultry_consultations",
        null=True,
        blank=True,
    )
    user_name = models.CharField(max_length=200)
    user_email = models.EmailField()
    user_phone = models.CharField(max_length=20)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.user_name} with {self.consultant.name}"

class EggSeller(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='egg_seller'
    )
    farm = models.ForeignKey(
        "companies.Farm",
        on_delete=models.SET_NULL,
        related_name="egg_seller_profiles",
        null=True,
        blank=True,
    )
    class EggType(models.TextChoices):
        ORGANIC = 'organic', _('Organic')
        FREE_RANGE = 'free_range', _('Free Range')
        CAGE_FREE = 'cage_free', _('Cage Free')
        CONVENTIONAL = 'conventional', _('Conventional')
        PASTURE_RAISED = 'pasture_raised', _('Pasture Raised')

    class Certification(models.TextChoices):
        NONE = 'none', _('None')
        USDA_ORGANIC = 'usda_organic', _('USDA Organic')
        NON_GMO = 'non_gmo', _('Non-GMO Project Verified')
        ANIMAL_WELFARE = 'animal_welfare', _('Animal Welfare Approved')
        LOCAL = 'local', _('Local Farm Certified')

    # Basic Information
    farm_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    
    # Location
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='USA')
    address = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Egg Details
    egg_type = models.CharField(max_length=20, choices=EggType.choices, default=EggType.CONVENTIONAL)
    certification = models.CharField(max_length=20, choices=Certification.choices, default=Certification.NONE)
    quantity_available = models.PositiveIntegerField(help_text=_("Number of eggs currently available"))
    price_per_dozen = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    min_order_quantity = models.PositiveIntegerField(default=1, help_text=_("Minimum dozen required for order"))
    
    # Contact Information
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Social Media
    facebook = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    
    # Business Details
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    review_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.farm_name} - {self.city}"

    class Meta:
        ordering = ['-is_verified', '-rating']
        verbose_name = _("Egg Seller")
        verbose_name_plural = _("Egg Sellers")

class EggOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')

    seller = models.ForeignKey(EggSeller, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="poultry_orders",
        null=True,
        blank=True,
    )
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()
    
    quantity = models.PositiveIntegerField(help_text=_("Number of dozens ordered"))
    total_price = models.DecimalField(max_digits=18, decimal_places=3)
    special_instructions = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    order_date = models.DateTimeField(auto_now_add=True)
    preferred_delivery_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.quantity * self.seller.price_per_dozen
        super().save(*args, **kwargs)

class ChickenSeller(models.Model):
    BREED_CHOICES = [
        ('rhode_island_red', _('Rhode Island Red')),
        ('plymouth_rock', _('Plymouth Rock')),
        ('leghorn', _('Leghorn')),
        ('sussex', _('Sussex')),
        ('orpington', _('Orpington')),
        ('other', _('Other')),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chicken_seller')
    farm = models.ForeignKey(
        "companies.Farm",
        on_delete=models.SET_NULL,
        related_name="chicken_seller_profiles",
        null=True,
        blank=True,
    )
    farm_name = models.CharField(max_length=200, verbose_name=_("Farm Name"))
    location = models.CharField(max_length=100, verbose_name=_("Location"))
    available_quantity = models.PositiveIntegerField(verbose_name=_("Available Chickens"))
    min_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Minimum Price"))
    max_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Maximum Price"))
    breeds = models.CharField(max_length=300, verbose_name=_("Breeds"))
    description = models.TextField(verbose_name=_("Description"))
    delivery_available = models.BooleanField(default=False, verbose_name=_("Delivery Available"))
    vaccinated = models.BooleanField(default=False, verbose_name=_("Vaccinated"))
    contact_number = models.CharField(max_length=20, verbose_name=_("Contact Number"))
    email = models.EmailField(verbose_name=_("Email"))
    facebook_url = models.URLField(blank=True, null=True, verbose_name=_("Facebook URL"))
    telegram_handle = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Telegram Handle"))
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("WhatsApp Number"))
    instagram_handle = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Instagram Handle"))
    youtube_channel = models.URLField(blank=True, null=True, verbose_name=_("YouTube Channel"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.farm_name
    
    def price_range(self):
        return f"${self.min_price}-{self.max_price} {_('each')}"
    
    class Meta:
        verbose_name = _("Chicken Seller")
        verbose_name_plural = _("Chicken Sellers")
        ordering = ['-created_at']

class TrainingEnrollment(models.Model):
    PROGRAM_CHOICES = [
        ('meat_chickens', 'Meat Chickens'),
        ('layer_chickens', 'Layer Chickens'),
        ('dual_purpose_chickens', 'Dual Purpose Chickens'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    program = models.CharField(max_length=50, choices=PROGRAM_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.program}"
