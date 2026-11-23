from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from .forms import DairyProductForm, DairyServiceForm
from .models import (
    DairyCategory,
    DairyProduct,
    DairyService,
    PRODUCT_CATEGORY_SPECS,
    ensure_product_categories,
)


class DairyAppTests(TestCase):
    def test_marketplace_and_main_pages_are_available(self):
        for name in ("dairys:index", "dairys:marketplace", "dairys:services", "dairys:training"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)

    def test_seed_categories_include_main_dairy_sections(self):
        ensure_product_categories()
        slugs = set(DairyCategory.objects.values_list("slug", flat=True))
        self.assertTrue({
            "fresh-milk",
            "feed-equipment",
            "dairy-cattle",
            "dairy-training",
            "dairy-consulting",
        }.issubset(slugs))

    def test_all_product_subcategories_are_seeded_and_seller_form_captures_fresh_milk_fields(self):
        ensure_product_categories()
        self.assertTrue(
            set(slug for slug, _name, _main, _group in PRODUCT_CATEGORY_SPECS).issubset(
                set(DairyCategory.objects.values_list("slug", flat=True))
            )
        )
        category = DairyCategory.objects.get(slug="fresh-milk")
        form = DairyProductForm(data={
            "name": "Goat milk",
            "description": "Freshly collected goat milk",
            "price": "12.50",
            "main_category": "milk",
            "category": str(category.pk),
            "milk_source": "goat",
            "milk_unit": "liters",
            "collection_date": "2026-11-23",
            "quantity_available": "1",
        })
        self.assertTrue(form.is_valid(), form.errors)
        product = form.save(commit=False)
        self.assertEqual(product.subcategory, "Raw milk")

    def test_marketplace_filters_by_main_category_and_equipment_group(self):
        ensure_product_categories()
        seller = get_user_model().objects.create_user(
            username="dairy-seller",
            phone_number="+251900000001",
            password="1234",
        )
        milk_category = DairyCategory.objects.get(slug="fresh-milk")
        cooling_category = DairyCategory.objects.get(slug="cooling-storage")
        DairyProduct.objects.create(
            name="Raw milk",
            description="Milk listing",
            price=Decimal("10.00"),
            main_category="milk",
            category=milk_category,
            subcategory=milk_category.name,
            milk_source="cow",
            milk_unit="liters",
            created_by=seller,
        )
        cooling_item = DairyProduct.objects.create(
            name="Cooling tank",
            description="Farm cooling equipment",
            price=Decimal("100.00"),
            main_category="items",
            category=cooling_category,
            subcategory=cooling_category.name,
            item_group="cooling",
            created_by=seller,
        )

        response = self.client.get(reverse("dairys:marketplace"), {
            "main_category": "items",
            "item_group": "cooling",
        })
        self.assertEqual(list(response.context["items"]), [cooling_item])

    def test_service_topics_must_match_training_or_consulting_kind(self):
        form = DairyServiceForm(data={
            "name": "Training",
            "service_kind": "training",
            "service_type": "farm_setup",
            "description": "A test service",
            "price": "25.00",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("service_type", form.errors)

    def test_buyers_can_filter_training_and_consulting_offers_by_topic(self):
        provider = get_user_model().objects.create_user(
            username="dairy-provider",
            phone_number="+251900000002",
            password="1234",
        )
        training = DairyService.objects.create(
            provider=provider,
            name="Calf rearing workshop",
            service_kind="training",
            service_type="calf_rearing",
            description="A dairy training offer",
            training_format="online",
            schedule="Two days",
            price=Decimal("50.00"),
        )
        DairyService.objects.create(
            provider=provider,
            name="Farm layout advice",
            service_kind="consulting",
            service_type="farm_setup",
            description="A dairy consulting offer",
            service_area="Regional",
            availability="Weekdays",
            price=Decimal("75.00"),
        )

        response = self.client.get(reverse("dairys:services"), {
            "kind": "training",
            "service_type": "calf_rearing",
        })
        self.assertEqual(list(response.context["services"]), [training])

    def test_legacy_category_routes_open_their_filtered_browse_pages(self):
        expected_filters = {
            "dairys:Products": ("main_category", "milk"),
            "dairys:Items": ("main_category", "items"),
            "dairys:CattleLiveStock": ("main_category", "livestock"),
            "dairys:Consultancy": ("kind", "consulting"),
            "dairys:TrainingOffers": ("kind", "training"),
        }
        for name, (field, value) in expected_filters.items():
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context[field], value)
        self.assertEqual(self.client.get(reverse("dairys:Training")).status_code, 200)