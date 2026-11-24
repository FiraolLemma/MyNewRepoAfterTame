from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import DairyConsultation, DairyProduct, DairyService


class DairyLivestockTests(TestCase):
    def setUp(self):
        self.seller = get_user_model().objects.create_user(
            username="livestock-seller",
            phone_number="+251911111103",
            password="7391",
        )

    def create_listing(self, **overrides):
        values = {
            "name": "Highland Dairy Cow",
            "slug": "highland-dairy-cow",
            "description": "Healthy cow with a calm temperament.",
            "price": Decimal("42000.00"),
            "main_category": "livestock",
            "livestock_type": "dairy_cow",
            "breed": "Holstein",
            "age_months": 48,
            "daily_milk_yield": Decimal("12.50"),
            "location": "Bishoftu",
            "created_by": self.seller,
        }
        values.update(overrides)
        return DairyProduct.objects.create(**values)

    def test_guest_can_browse_and_filter_livestock_listings(self):
        cow = self.create_listing()
        goat = self.create_listing(
            name="Local Goat",
            slug="local-goat",
            livestock_type="goat",
            breed="Afar",
        )

        response = self.client.get(reverse("dairys:cattle_livestock"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, cow.name)
        self.assertContains(response, goat.name)
        self.assertContains(response, reverse("dairys:cattle_livestock_create"))
        self.assertContains(response, 'data-filter="goat"')

    def test_guest_can_view_livestock_details_and_buy_available_listing(self):
        listing = self.create_listing()

        response = self.client.get(
            reverse(
                "dairys:cattle_livestock_detail",
                kwargs={"cattle_livestock_id": listing.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, listing.name)
        self.assertContains(response, "Holstein")
        self.assertContains(response, "12.50 liters")
        self.assertContains(
            response,
            reverse("cart:add_to_cart", args=("dairys", "dairyproduct", listing.pk)),
        )

    def test_livestock_listing_creation_requires_login(self):
        response = self.client.get(reverse("dairys:cattle_livestock_create"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_seller_can_create_livestock_listing(self):
        self.client.force_login(self.seller)

        response = self.client.post(
            reverse("dairys:cattle_livestock_create"),
            {
                "name": "Afar Goat",
                "livestock_type": "goat",
                "breed": "Afar",
                "description": "Healthy and vaccinated.",
                "price": "8500.00",
                "age_months": "18",
                "quantity_available": "2",
                "unit": "animals",
                "location": "Adama",
            },
        )

        listing = DairyProduct.objects.get(name="Afar Goat")
        self.assertRedirects(
            response,
            reverse(
                "dairys:cattle_livestock_detail",
                kwargs={"cattle_livestock_id": listing.pk},
            ),
        )
        self.assertEqual(listing.created_by, self.seller)
        self.assertEqual(listing.main_category, "livestock")
        self.assertEqual(listing.livestock_type, "goat")
        self.assertEqual(listing.slug, "afar-goat")

    def test_seller_cannot_submit_negative_daily_milk_yield(self):
        self.client.force_login(self.seller)

        response = self.client.post(
            reverse("dairys:cattle_livestock_create"),
            {
                "name": "Cow with invalid yield",
                "livestock_type": "dairy_cow",
                "description": "A test listing.",
                "price": "12000.00",
                "daily_milk_yield": "-1.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ensure this value is greater than or equal to 0.")
        self.assertFalse(DairyProduct.objects.filter(name="Cow with invalid yield").exists())

    def test_seller_cannot_submit_livestock_without_an_animal_type(self):
        self.client.force_login(self.seller)

        response = self.client.post(
            reverse("dairys:cattle_livestock_create"),
            {
                "name": "Uncategorized Animal",
                "livestock_type": "",
                "description": "A listing without a selected type.",
                "price": "1000.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertFalse(DairyProduct.objects.filter(name="Uncategorized Animal").exists())


class DairyConsultancyTests(TestCase):
    def setUp(self):
        self.provider = get_user_model().objects.create_user(
            username="dairy-vet",
            phone_number="+251911111101",
            password="7391",
        )
        self.service = self.create_service()

    def create_service(self, **overrides):
        values = {
            "name": "Dr. Bekele",
            "slug": "dr-bekele",
            "service_kind": "consulting",
            "service_type": "herd_health",
            "description": "Herd health and mastitis prevention.",
            "location": "Adama",
            "availability": "Weekdays, 9:00-17:00",
            "price": Decimal("350.00"),
            "provider": self.provider,
        }
        values.update(overrides)
        return DairyService.objects.create(**values)

    def test_consultancy_page_shows_only_available_consulting_services(self):
        hidden_service = self.create_service(
            name="Unavailable vet",
            slug="unavailable-vet",
            is_available=False,
        )
        training_service = self.create_service(
            name="Training only",
            slug="training-only",
            service_kind="training",
        )

        response = self.client.get(reverse("dairys:veterinary_consultancy"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dairys/consultacy.html")
        self.assertContains(response, self.service.name)
        self.assertNotContains(response, hidden_service.name)
        self.assertNotContains(response, training_service.name)

    def test_consultancy_page_filters_by_specialty_and_search(self):
        other_service = self.create_service(
            name="Dr. Alemu",
            slug="dr-alemu",
            service_type="milk_yield",
        )

        response = self.client.get(
            reverse("dairys:veterinary_consultancy"),
            {"specialty": "herd_health", "q": "Bekele"},
        )

        self.assertContains(response, self.service.name)
        self.assertNotContains(response, other_service.name)

    def test_consultant_registration_requires_login(self):
        response = self.client.get(reverse("dairys:consultacy_create"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_logged_in_user_can_register_a_consulting_profile(self):
        self.client.force_login(self.provider)

        response = self.client.post(
            reverse("dairys:consultacy_create"),
            {
                "name": "Dr. Tadesse",
                "service_type": "milk_yield",
                "description": "Advice for improving dairy herd yield.",
                "schedule": "Farm visits and video calls",
                "location": "Bishoftu",
                "service_area": "East Shewa",
                "availability": "Weekdays",
                "price": "500.00",
            },
        )

        self.assertRedirects(response, reverse("dairys:veterinary_consultancy"))
        service = DairyService.objects.get(name="Dr. Tadesse")
        self.assertEqual(service.provider, self.provider)
        self.assertEqual(service.service_kind, "consulting")
        self.assertEqual(service.slug, "dr-tadesse")

    def test_guest_can_request_a_consultation_for_a_future_date(self):
        response = self.client.post(
            reverse(
                "dairys:consultation_create",
                kwargs={"service_id": self.service.pk},
            ),
            {
                "name": "Farm Owner",
                "email": "farmer@example.com",
                "phone": "+251911111102",
                "preferred_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
                "message": "Please advise about herd health.",
            },
        )

        self.assertRedirects(response, reverse("dairys:veterinary_consultancy"))
        consultation = DairyConsultation.objects.get()
        self.assertEqual(consultation.service, self.service)
        self.assertIsNone(consultation.customer)

    def test_past_consultation_date_is_rejected(self):
        response = self.client.post(
            reverse(
                "dairys:consultation_create",
                kwargs={"service_id": self.service.pk},
            ),
            {
                "name": "Farm Owner",
                "email": "farmer@example.com",
                "phone": "+251911111102",
                "preferred_date": (timezone.localdate() - timedelta(days=1)).isoformat(),
                "message": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose today or a future date.")
        self.assertFalse(DairyConsultation.objects.exists())

    def test_provider_cannot_book_their_own_profile(self):
        self.client.force_login(self.provider)

        response = self.client.get(
            reverse(
                "dairys:consultation_create",
                kwargs={"service_id": self.service.pk},
            )
        )

        self.assertRedirects(response, reverse("dairys:veterinary_consultancy"))
        self.assertFalse(DairyConsultation.objects.exists())
