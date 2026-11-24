from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import DairyConsultation, DairyProduct, DairyService, TrainingEnrollment


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


class DairyTrainingTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.trainer = user_model.objects.create_user(
            username="dairy-trainer",
            phone_number="+251911111104",
            password="7391",
        )
        self.farmer = user_model.objects.create_user(
            username="dairy-farmer",
            phone_number="+251911111105",
            password="7391",
            email="farmer@example.com",
        )
        self.course = self.create_course()

    def create_course(self, **overrides):
        values = {
            "name": "Dairy Farm Management",
            "slug": "dairy-farm-management",
            "service_kind": "training",
            "service_type": "cattle_feeding",
            "description": "Practical feeding plans for dairy cattle.",
            "training_format": "in_person",
            "training_date": timezone.localdate() + timedelta(days=7),
            "duration_hours": 3,
            "location": "Bishoftu",
            "price": Decimal("250.00"),
            "provider": self.trainer,
        }
        values.update(overrides)
        return DairyService.objects.create(**values)

    def enroll(self, course=None, **overrides):
        values = {
            "name": self.farmer.username,
            "email": self.farmer.email,
            "phone": self.farmer.phone_number,
        }
        values.update(overrides)
        return self.client.post(
            reverse(
                "dairys:training_enroll",
                kwargs={"slug": (course or self.course).slug},
            ),
            values,
        )

    def test_guest_can_browse_and_filter_available_dairy_training(self):
        other_course = self.create_course(
            name="Clean Milk Hygiene",
            slug="clean-milk-hygiene",
            service_type="clean_milk_hygiene",
        )

        response = self.client.get(
            reverse("dairys:training"),
            {"topic": "cattle_feeding"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.name)
        self.assertNotContains(response, other_course.name)
        self.assertContains(response, reverse("dairys:training_create"))

    def test_trainer_can_publish_a_dated_training_course(self):
        self.client.force_login(self.trainer)
        training_date = timezone.localdate() + timedelta(days=14)

        response = self.client.post(
            reverse("dairys:training_create"),
            {
                "name": "Calf Rearing Basics",
                "service_type": "calf_rearing",
                "description": "Hands-on calf rearing fundamentals.",
                "training_format": "online",
                "training_date": training_date.isoformat(),
                "duration_hours": "2",
                "schedule": "Saturday morning",
                "location": "",
                "service_area": "All regions",
                "availability": "20 places",
                "price": "0",
            },
        )

        course = DairyService.objects.get(name="Calf Rearing Basics")
        self.assertRedirects(
            response,
            reverse("dairys:training_detail", kwargs={"slug": course.slug}),
        )
        self.assertEqual(course.provider, self.trainer)
        self.assertEqual(course.service_kind, "training")
        self.assertEqual(course.training_date, training_date)
        self.assertEqual(course.slug, "calf-rearing-basics")

    def test_trainer_cannot_publish_a_past_course_date(self):
        self.client.force_login(self.trainer)

        response = self.client.post(
            reverse("dairys:training_create"),
            {
                "name": "Past Dairy Course",
                "service_type": "calf_rearing",
                "description": "A course in the past.",
                "training_format": "online",
                "training_date": (timezone.localdate() - timedelta(days=1)).isoformat(),
                "duration_hours": "2",
                "price": "0",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose today or a future date.")
        self.assertFalse(DairyService.objects.filter(name="Past Dairy Course").exists())

    def test_guest_must_sign_in_to_enroll(self):
        response = self.client.get(
            reverse("dairys:training_enroll", kwargs={"slug": self.course.slug})
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_farmer_can_enroll_and_trainer_can_view_registration(self):
        self.client.force_login(self.farmer)

        response = self.enroll()

        self.assertRedirects(
            response,
            reverse("dairys:training_detail", kwargs={"slug": self.course.slug}),
        )
        enrollment = TrainingEnrollment.objects.get()
        self.assertEqual(enrollment.training, self.course)
        self.assertEqual(enrollment.trainee, self.farmer)
        self.assertEqual(enrollment.topic, self.course.service_type)
        self.assertEqual(enrollment.format, self.course.training_format)

        self.client.force_login(self.trainer)
        dashboard_response = self.client.get(reverse("dairys:training_dashboard"))

        self.assertContains(dashboard_response, self.course.name)
        self.assertContains(dashboard_response, self.farmer.username)
        self.assertContains(dashboard_response, self.farmer.phone_number)

    def test_farmer_cannot_enroll_twice_or_in_own_course(self):
        self.client.force_login(self.farmer)
        self.enroll()

        duplicate_response = self.enroll()

        self.assertEqual(duplicate_response.status_code, 200)
        self.assertContains(duplicate_response, "already registered")
        self.assertEqual(TrainingEnrollment.objects.count(), 1)

        self.client.force_login(self.trainer)
        owner_response = self.enroll()

        self.assertRedirects(
            owner_response,
            reverse("dairys:training_detail", kwargs={"slug": self.course.slug}),
        )
        self.assertEqual(TrainingEnrollment.objects.count(), 1)

    def test_past_courses_are_not_listed_or_open_for_registration(self):
        past_course = self.create_course(
            name="Earlier course",
            slug="earlier-course",
            training_date=timezone.localdate() - timedelta(days=1),
        )

        listing = self.client.get(reverse("dairys:training"))
        self.assertNotContains(listing, past_course.name)

        self.client.force_login(self.farmer)
        response = self.client.get(
            reverse("dairys:training_enroll", kwargs={"slug": past_course.slug})
        )
        self.assertRedirects(
            response,
            reverse("dairys:training_detail", kwargs={"slug": past_course.slug}),
        )
        self.assertFalse(TrainingEnrollment.objects.filter(training=past_course).exists())


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
