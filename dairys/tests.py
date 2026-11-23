from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import DairyConsultation, DairyService


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
