import json
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ConsultationBookingForm
from .models import (
    ConsultationService,
    Consultant,
    EggOrder,
    EggSeller,
    PoultryTraining,
    TrainingEnrollment,
)
from users.roles import UserRole, role_group_name
from virtual_users.models import VirtualAgent


class PoultryLandingPageTests(TestCase):
    def test_poultry_landing_page_uses_canonical_url_and_template(self):
        self.assertEqual(reverse("poultrys:index"), "/en/poultrys/")
        self.assertEqual(reverse("poultrys:item_list"), "/en/poultrys/items/")
        self.assertEqual(reverse("poultrys:item_detail", args=[123]), "/en/poultrys/items/123/")
        self.assertEqual(reverse("poultrys:egg_sellers"), "/en/poultrys/egg-sellers/")
        self.assertEqual(
            reverse("poultrys:chicken_sellers_list"),
            "/en/poultrys/chicken-sellers/",
        )
        response = self.client.get(reverse("poultrys:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "poultrys/index.html")

    def test_legacy_poultry_urls_redirect_to_canonical_routes(self):
        legacy_routes = {
            "/en/items/poultry/": reverse("poultrys:index"),
            "/en/items/": reverse("poultrys:item_list"),
            "/en/items/123/": reverse("poultrys:item_detail", args=[123]),
            "/en/items/egg-sellers/": reverse("poultrys:egg_sellers"),
            "/en/items/chicken-sellers/": reverse("poultrys:chicken_sellers_list"),
        }

        for legacy_path, canonical_path in legacy_routes.items():
            with self.subTest(legacy_path=legacy_path):
                response = self.client.get(legacy_path)
                self.assertRedirects(
                    response,
                    canonical_path,
                    status_code=301,
                    fetch_redirect_response=False,
                )


class PoultryTrainingTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.trainer = user_model.objects.create_user(
            username="poultry-trainer",
            phone_number="+251911111140",
            password="7391",
        )
        self.farmer = user_model.objects.create_user(
            username="poultry-trainee",
            phone_number="+251911111141",
            password="7391",
            email="trainee@example.com",
        )
        self.course = self.create_course()

    def create_course(self, **overrides):
        values = {
            "name": "Modern Poultry Farming",
            "slug": "modern-poultry-farming",
            "program": "meat_chickens",
            "description": "Practical broiler farming and flock management.",
            "training_format": "in_person",
            "training_date": timezone.localdate() + timedelta(days=7),
            "duration_hours": 2,
            "location": "Adama",
            "price": Decimal("150.00"),
            "provider": self.trainer,
        }
        values.update(overrides)
        return PoultryTraining.objects.create(**values)

    def enroll(self, course=None, **overrides):
        values = {
            "name": self.farmer.username,
            "email": self.farmer.email,
            "phone": self.farmer.phone_number,
        }
        values.update(overrides)
        return self.client.post(
            reverse(
                "poultrys:poultry_training_enroll",
                kwargs={"slug": (course or self.course).slug},
            ),
            values,
        )

    def test_guest_can_browse_and_filter_available_courses(self):
        other_course = self.create_course(
            name="Layer Chicken Management",
            slug="layer-chicken-management",
            program="layer_chickens",
        )

        response = self.client.get(
            reverse("poultrys:poultry_trainings"),
            {"program": "meat_chickens"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.name)
        self.assertNotContains(response, other_course.name)
        self.assertContains(response, reverse("poultrys:poultry_training_create"))

    def test_trainer_can_publish_a_dated_course(self):
        self.client.force_login(self.trainer)
        training_date = timezone.localdate() + timedelta(days=14)

        response = self.client.post(
            reverse("poultrys:poultry_training_create"),
            {
                "name": "Layer Chicken Management",
                "program": "layer_chickens",
                "description": "Hands-on layer flock management.",
                "training_format": "online",
                "training_date": training_date.isoformat(),
                "duration_hours": "3",
                "schedule": "Saturday morning",
                "location": "",
                "service_area": "All regions",
                "availability": "20 places",
                "price": "0",
            },
        )

        course = PoultryTraining.objects.get(name="Layer Chicken Management")
        self.assertRedirects(
            response,
            reverse("poultrys:poultry_training_detail", kwargs={"slug": course.slug}),
        )
        self.assertEqual(course.provider, self.trainer)
        self.assertEqual(course.program, "layer_chickens")
        self.assertEqual(course.training_date, training_date)
        self.assertEqual(course.slug, "layer-chicken-management")

    def test_trainer_cannot_publish_a_past_course_date(self):
        self.client.force_login(self.trainer)

        response = self.client.post(
            reverse("poultrys:poultry_training_create"),
            {
                "name": "Past poultry course",
                "program": "meat_chickens",
                "description": "A course in the past.",
                "training_format": "online",
                "training_date": (timezone.localdate() - timedelta(days=1)).isoformat(),
                "duration_hours": "2",
                "price": "0",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose today or a future date.")
        self.assertFalse(PoultryTraining.objects.filter(name="Past poultry course").exists())

    def test_guest_must_sign_in_to_enroll(self):
        response = self.client.get(
            reverse(
                "poultrys:poultry_training_enroll",
                kwargs={"slug": self.course.slug},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_farmer_can_enroll_and_trainer_can_see_registrant(self):
        self.client.force_login(self.farmer)

        response = self.enroll()

        self.assertRedirects(
            response,
            reverse("poultrys:poultry_training_detail", kwargs={"slug": self.course.slug}),
        )
        enrollment = TrainingEnrollment.objects.get()
        self.assertEqual(enrollment.training, self.course)
        self.assertEqual(enrollment.trainee, self.farmer)
        self.assertEqual(enrollment.program, self.course.program)

        trainee_dashboard = self.client.get(
            reverse("poultrys:poultry_training_dashboard")
        )
        self.assertContains(trainee_dashboard, self.course.name)

        self.client.force_login(self.trainer)
        dashboard_response = self.client.get(
            reverse("poultrys:poultry_training_dashboard")
        )
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
        own_course_response = self.enroll()
        self.assertRedirects(
            own_course_response,
            reverse("poultrys:poultry_training_detail", kwargs={"slug": self.course.slug}),
        )
        self.assertEqual(TrainingEnrollment.objects.count(), 1)

    def test_past_courses_are_not_listed_or_open_for_registration(self):
        past_course = self.create_course(
            name="Earlier poultry course",
            slug="earlier-poultry-course",
            training_date=timezone.localdate() - timedelta(days=1),
        )
        response = self.client.get(reverse("poultrys:poultry_trainings"))
        self.assertNotContains(response, past_course.name)

        self.client.force_login(self.farmer)
        response = self.client.get(
            reverse(
                "poultrys:poultry_training_enroll",
                kwargs={"slug": past_course.slug},
            )
        )
        self.assertRedirects(
            response,
            reverse(
                "poultrys:poultry_training_detail",
                kwargs={"slug": past_course.slug},
            ),
        )
        self.assertFalse(TrainingEnrollment.objects.filter(training=past_course).exists())

    def test_trainee_dashboard_only_shows_the_current_users_enrollments(self):
        other_farmer = get_user_model().objects.create_user(
            username="another-trainee",
            phone_number="+251911111142",
            password="7391",
        )
        TrainingEnrollment.objects.create(
            name=other_farmer.username,
            email="another@example.com",
            phone=other_farmer.phone_number,
            program=self.course.program,
            training=self.course,
            trainee=other_farmer,
        )
        self.client.force_login(self.farmer)

        response = self.client.get(reverse("poultrys:poultry_trainees"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_farmer.username)


class PoultryAccountRelationshipTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.customer = user_model.objects.create_user(
            username="poultry-customer",
            phone_number="+251911111129",
            password="Safe-Test-Password-123!",
        )
        self.farmer = user_model.objects.create_user(
            username="poultry-farmer",
            phone_number="+251911111130",
            password="Safe-Test-Password-123!",
        )
        user_model.objects.filter(
            pk__in=(self.customer.pk, self.farmer.pk)
        ).update(onboarding_complete=True, pin_setup_required=False)
        self.customer.onboarding_complete = True
        self.farmer.onboarding_complete = True
        self.farmer.groups.remove(Group.objects.get(name="Customer"))
        self.farmer.groups.add(Group.objects.get(name="Farmer"))
        self.farmer.profile.email = "farmer@example.com"
        self.farmer.profile.save(update_fields=("email",))
        self.consultant = Consultant.objects.create(
            name="Dr. Saba",
            experience=5,
            specialty=Consultant.Specialty.GENERAL,
            languages="Amharic, English",
            description="Poultry health consultant",
            availability=Consultant.Availability.WEEKDAYS,
        )
        self.service = ConsultationService.objects.create(
            consultant=self.consultant,
            service_type=ConsultationService.ServiceType.VIDEO_CALL,
            price="100.00",
        )
        self.seller = EggSeller.objects.create(
            user=self.farmer,
            farm_name="Bishoftu Farm",
            description="Fresh eggs",
            city="Bishoftu",
            quantity_available=100,
            price_per_dozen="25.00",
            phone="+251911111130",
        )
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.customer)

    def test_booking_form_rejects_service_for_another_consultant(self):
        other_consultant = Consultant.objects.create(
            name="Dr. Alem",
            experience=3,
            specialty=Consultant.Specialty.GENERAL,
            languages="Amharic",
            description="Poultry consultant",
            availability=Consultant.Availability.WEEKDAYS,
        )
        other_service = ConsultationService.objects.create(
            consultant=other_consultant,
            service_type=ConsultationService.ServiceType.PHONE_CALL,
            price="75.00",
        )

        form = ConsultationBookingForm({
            "consultant": self.consultant.pk,
            "service": other_service.pk,
            "user_name": "Poultry Customer",
            "user_email": "customer@example.com",
            "user_phone": "+251911111129",
            "preferred_date": "2027-01-15",
            "preferred_time": "10:00",
            "message": "",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("service", form.errors)

    def make_farmer(self, username, phone_number, email):
        farmer = get_user_model().objects.create_user(
            username=username,
            phone_number=phone_number,
            password="Safe-Test-Password-123!",
        )
        farmer.groups.remove(Group.objects.get(name="Customer"))
        farmer.groups.add(Group.objects.get(name="Farmer"))
        farmer.profile.email = email
        farmer.profile.save(update_fields=("email",))
        return farmer

    def test_egg_seller_registration_uses_account_contact_details(self):
        farmer = self.make_farmer(
            "new-egg-farmer",
            "+251911111133",
            "newfarmer@example.com",
        )
        self.client.force_login(farmer)
        token = self.csrf_token_from_page(reverse("poultrys:add_egg_seller"))
        response = self.client.post(
            reverse("poultrys:add_egg_seller"),
            {
                "farm_name": "New Bishoftu Farm",
                "description": "Fresh local eggs",
                "city": "Bishoftu",
                "country": "Ethiopia",
                "egg_type": EggSeller.EggType.FREE_RANGE,
                "certification": EggSeller.Certification.NONE,
                "quantity_available": 240,
                "price_per_dozen": "30.00",
                "min_order_quantity": 1,
                "owner_name": "Untrusted submitted name",
                "phone": "+251900000000",
                "email": "fake@example.com",
            },
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertRedirects(
            response,
            reverse("poultrys:egg_sellers"),
            fetch_redirect_response=False,
        )
        seller = EggSeller.objects.get(user=farmer)
        self.assertEqual(seller.owner_name, farmer.username)
        self.assertEqual(seller.phone, farmer.phone_number)
        self.assertEqual(seller.email, farmer.profile.email)
        self.assertEqual(seller.farm.phone, farmer.phone_number)
        self.assertEqual(seller.farm.email, farmer.profile.email)
        marketplace_response = self.client.get(reverse("poultrys:egg_sellers"))
        self.assertContains(marketplace_response, farmer.phone_number)
        self.assertContains(marketplace_response, farmer.profile.email)

    def test_egg_seller_card_uses_current_user_profile_details(self):
        self.farmer.profile.phone_number = "+251911111131"
        self.farmer.profile.profile_picture.name = "profile_pics/farm-avatar.jpg"
        self.farmer.profile.telegram = "bishoftufarm"
        self.farmer.profile.facebook = "bishoftufarm"
        self.farmer.profile.instagram = "bishoftu_farm"
        self.farmer.profile.save(
            update_fields=(
                "phone_number",
                "profile_picture",
                "telegram",
                "facebook",
                "instagram",
            )
        )
        self.seller.phone = "+251900000000"
        self.seller.email = "outdated@example.com"
        self.seller.save(update_fields=("phone", "email"))

        response = self.client.get(reverse("poultrys:egg_sellers"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/media/profile_pics/farm-avatar.jpg")
        self.assertContains(response, "tel:+251911111131")
        self.assertContains(response, "farmer@example.com")
        self.assertContains(response, "https://t.me/bishoftufarm")
        self.assertContains(response, "https://facebook.com/bishoftufarm")
        self.assertContains(response, "https://instagram.com/bishoftu_farm")
        self.assertNotContains(response, "tel:+251900000000")
        self.assertNotContains(response, "outdated@example.com")

    def test_egg_seller_edit_keeps_contact_details_from_owner_account(self):
        self.client.force_login(self.farmer)
        token = self.csrf_token_from_page(
            reverse("poultrys:edit_egg_seller", kwargs={"pk": self.seller.pk})
        )
        response = self.client.post(
            reverse("poultrys:edit_egg_seller", kwargs={"pk": self.seller.pk}),
            {
                "farm_name": self.seller.farm_name,
                "description": "Updated egg details",
                "city": self.seller.city,
                "country": self.seller.country,
                "egg_type": self.seller.egg_type,
                "certification": self.seller.certification,
                "quantity_available": self.seller.quantity_available,
                "price_per_dozen": self.seller.price_per_dozen,
                "min_order_quantity": self.seller.min_order_quantity,
                "owner_name": "Fake name",
                "phone": "+251900000000",
                "email": "fake@example.com",
            },
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertRedirects(
            response,
            reverse("poultrys:egg_sellers"),
            fetch_redirect_response=False,
        )
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.owner_name, self.farmer.username)
        self.assertEqual(self.seller.phone, self.farmer.phone_number)
        self.assertEqual(self.seller.email, self.farmer.profile.email)

    def test_egg_seller_form_shows_account_contact_fields_as_read_only(self):
        farmer = self.make_farmer(
            "egg-form-farmer",
            "+251911111134",
            "formfarmer@example.com",
        )
        self.client.force_login(farmer)
        response = self.client.get(reverse("poultrys:add_egg_seller"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, farmer.username)
        self.assertContains(response, farmer.phone_number)
        self.assertContains(response, farmer.profile.email)
        self.assertNotContains(response, 'name="owner_name"')
        self.assertNotContains(response, 'name="phone"')
        self.assertNotContains(response, 'name="email"')
        self.assertNotContains(response, 'name="facebook"')
        self.assertNotContains(response, 'name="telegram"')
        self.assertNotContains(response, 'name="instagram"')

    def test_customer_can_browse_but_cannot_add_egg_sellers(self):
        veterinarian = get_user_model().objects.create_user(
            username="egg-veterinarian",
            phone_number="+251911111146",
            password="1234",
        )
        veterinarian.groups.remove(Group.objects.get(name="Customer"))
        veterinarian.groups.add(Group.objects.get(name="Veterinarian"))

        for user in (self.customer, veterinarian):
            with self.subTest(role=user.username):
                self.client.force_login(user)
                listing_response = self.client.get(
                    reverse("poultrys:egg_sellers")
                )
                self.assertEqual(listing_response.status_code, 200)
                self.assertNotContains(listing_response, "Add Egg Seller")

                add_response = self.client.get(
                    reverse("poultrys:add_egg_seller")
                )
                self.assertEqual(add_response.status_code, 403)
        self.assertEqual(EggSeller.objects.count(), 1)

    def test_admin_and_supplier_can_open_egg_seller_creation(self):
        admin = get_user_model().objects.create_user(
            username="egg-admin",
            phone_number="+251911111143",
            password="1234",
        )
        admin.groups.remove(Group.objects.get(name="Customer"))
        admin.groups.add(Group.objects.get(name="Admin"))
        self.assertTrue(admin.has_role(UserRole.ADMIN))
        self.assertTrue(
            admin.groups.filter(name=role_group_name(UserRole.ADMIN)).exists()
        )

        supplier = get_user_model().objects.create_user(
            username="egg-supplier",
            phone_number="+251911111144",
            password="1234",
        )
        supplier.groups.remove(Group.objects.get(name="Customer"))
        supplier.groups.add(Group.objects.get(name="Supplier"))

        for user in (admin, self.farmer, supplier):
            with self.subTest(role=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("poultrys:add_egg_seller"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Add New Egg Seller")

    def test_ai_virtual_users_can_browse_but_cannot_add_egg_sellers(self):
        ai_user = get_user_model().objects.create_user(
            username="egg-ai-user",
            phone_number="+251911111145",
            password="1234",
        )
        VirtualAgent.objects.create(
            user=ai_user,
            role=VirtualAgent.Role.FARMER,
            persona_label="AI Farmer",
        )
        self.client.force_login(ai_user)

        listing_response = self.client.get(reverse("poultrys:egg_sellers"))
        self.assertEqual(listing_response.status_code, 200)
        self.assertNotContains(listing_response, "Add Egg Seller")
        self.assertEqual(
            self.client.get(reverse("poultrys:add_egg_seller")).status_code,
            403,
        )

    def csrf_token_from_page(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return self.client.cookies["csrftoken"].value

    def test_booking_endpoint_uses_csrf_and_links_authenticated_customer(self):
        token = self.csrf_token_from_page(
            reverse("poultrys:veterinary_consultancy")
        )
        response = self.client.post(
            reverse("poultrys:book_consultation"),
            data=json.dumps({
                "consultant_id": self.consultant.pk,
                "service_id": self.service.pk,
                "user_name": "Poultry Customer",
                "user_email": "customer@example.com",
                "user_phone": "+251911111129",
                "preferred_date": "2027-01-15",
                "preferred_time": "10:00",
                "message": "Flock health consultation",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.consultant.consultationbooking_set.count(), 1)
        self.assertEqual(
            self.consultant.consultationbooking_set.get().customer_id,
            self.customer.pk,
        )

    def test_egg_order_endpoint_uses_csrf_and_links_authenticated_customer(self):
        token = self.csrf_token_from_page(reverse("poultrys:egg_sellers"))
        response = self.client.post(
            reverse("poultrys:place_egg_order"),
            data=json.dumps({
                "seller_id": self.seller.pk,
                "customer_name": "Poultry Customer",
                "customer_email": "customer@example.com",
                "customer_phone": "+251911111129",
                "customer_address": "Bishoftu",
                "quantity": 2,
                "special_instructions": "",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 200)
        order = EggOrder.objects.get()
        self.assertEqual(order.customer_id, self.customer.pk)
        self.assertEqual(order.total_price, 50)

    def test_invalid_json_is_reported_as_bad_request(self):
        token = self.csrf_token_from_page(reverse("poultrys:egg_sellers"))
        response = self.client.post(
            reverse("poultrys:place_egg_order"),
            data="{",
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 400)
