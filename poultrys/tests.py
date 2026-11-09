import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

from .forms import ConsultationBookingForm
from .models import (
    ConsultationService,
    Consultant,
    EggOrder,
    EggSeller,
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
