from django.contrib import admin

from .models import (
    DairyCategory,
    DairyConsultation,
    DairyProduct,
    DairyService,
    TrainingEnrollment,
)


@admin.register(DairyCategory)
class DairyCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "main_category", "slug")
    list_filter = ("main_category",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(DairyProduct)
class DairyProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "main_category",
        "category",
        "item_group",
        "livestock_type",
        "breed",
        "price",
        "location",
        "is_featured",
    )
    list_filter = ("main_category", "category", "item_group", "is_featured", "milk_source", "livestock_type")
    search_fields = (
        "name",
        "description",
        "subcategory",
        "item_group",
        "breed",
        "location",
        "created_by__username",
        "company__name",
        "farm__name",
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(DairyService)
class DairyServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "service_kind",
        "service_type",
        "training_date",
        "duration_hours",
        "provider",
        "price",
        "is_available",
        "is_featured",
        "created_at",
    )
    list_filter = ("service_kind", "service_type", "is_available", "is_featured")
    search_fields = (
        "name",
        "description",
        "provider__username",
        "provider__phone_number",
        "location",
        "service_area",
    )
    readonly_fields = ("created_at",)
    list_select_related = ("provider",)
    list_per_page = 30
    prepopulated_fields = {"slug": ("name",)}


@admin.register(TrainingEnrollment)
class TrainingEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "training",
        "trainee",
        "get_topic_display",
        "format",
        "status",
        "created_at",
    )
    list_filter = ("status", "topic", "format", "training__service_type")
    search_fields = (
        "name",
        "email",
        "phone",
        "training__name",
        "trainee__username",
        "training__provider__username",
    )
    readonly_fields = ("created_at",)
    list_select_related = ("training", "trainee", "training__provider")
    list_per_page = 30


@admin.register(DairyConsultation)
class DairyConsultationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "service",
        "customer",
        "preferred_date",
        "status",
        "created_at",
    )
    list_filter = ("status", "preferred_date", "service__service_type")
    search_fields = (
        "name",
        "email",
        "phone",
        "service__name",
        "service__provider__username",
    )
    readonly_fields = ("created_at",)
    list_select_related = ("service", "service__provider", "customer")
    list_per_page = 30
    date_hierarchy = "created_at"
