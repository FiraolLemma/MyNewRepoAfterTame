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
    list_display = ("name", "main_category", "category", "item_group", "price", "location", "is_featured")
    list_filter = ("main_category", "category", "item_group", "is_featured", "milk_source", "livestock_type")
    search_fields = ("name", "description", "breed", "location")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(DairyService)
class DairyServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "service_kind", "service_type", "training_format", "price", "is_available")
    list_filter = ("service_kind", "service_type", "training_format", "is_available")
    search_fields = ("name", "service_type", "location", "service_area")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(TrainingEnrollment)
class TrainingEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("name", "get_topic_display", "format", "email", "created_at")
    list_filter = ("topic", "format")
    search_fields = ("name", "email", "phone")


@admin.register(DairyConsultation)
class DairyConsultationAdmin(admin.ModelAdmin):
    list_display = ("name", "service", "preferred_date", "status", "created_at")
    list_filter = ("status", "preferred_date")
    search_fields = ("name", "email", "phone")
