from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import DairyCategory, DairyProduct, DairyService


class DairyMarketplaceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="dairy-farmer",
            phone_number="+251911111111",
            password="test-password",
        )
        self.user.groups.remove(Group.objects.get(name="Customer"))
        self.user.groups.add(Group.objects.get(name="Farmer"))
        self.category, _ = DairyCategory.objects.get_or_create(
            slug="fresh-milk",
            defaults={"name": "Fresh milk"},
        )
        self.product = DairyProduct.objects.create(
            category=self.category,
            created_by=self.user,
            name="Farm milk",
            slug="farm-milk",
            description="Fresh milk from a local dairy farm.",
            price="75.00",
            unit=DairyProduct.Unit.LITER,
            quantity_available=10,
            location="Bishoftu",
        )
        self.service = DairyService.objects.create(
            provider=self.user,
            name="Milk collection",
            slug="milk-collection",
            service_type=DairyService.ServiceType.MILK_COLLECTION,
            description="Scheduled collection for local farms.",
            price="20.00",
            location="Bishoftu",
        )

    def test_marketplace_renders_products_and_services(self):
        self.assertEqual(reverse("clothings:clothing_list"), "/en/dairys/")
        response = self.client.get(reverse("clothings:clothing_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dairys/dairy_market.html")
        self.assertContains(response, "/static/dairys/css/dairy_market.css")
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.service.name)

    def test_old_marketplace_url_redirects_to_dairys(self):
        response = self.client.get("/en/clothings/?q=milk")

        self.assertRedirects(
            response,
            "/en/dairys/?q=milk",
            status_code=301,
            fetch_redirect_response=False,
        )

    def test_marketplace_search_filters_products_and_services(self):
        response = self.client.get(
            reverse("clothings:clothing_list"),
            {"q": "collection"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.product.name)
        self.assertContains(response, self.service.name)

    def test_product_and_service_details_render(self):
        product_response = self.client.get(self.product.get_absolute_url())
        service_response = self.client.get(self.service.get_absolute_url())

        self.assertEqual(product_response.status_code, 200)
        self.assertContains(product_response, self.product.description)
        self.assertEqual(service_response.status_code, 200)
        self.assertContains(service_response, self.service.description)

    def test_farmer_can_create_product_and_service_listings(self):
        self.client.force_login(self.user)
        product_response = self.client.post(
            reverse("clothings:clothing_create"),
            {
                "name": "Fresh cream",
                "category": self.category.pk,
                "description": "Cream produced on our farm.",
                "price": "95.00",
                "unit": DairyProduct.Unit.PIECE,
                "quantity_available": 8,
                "location": "Bishoftu",
            },
        )
        service_response = self.client.post(
            reverse("clothings:dairy_service_create"),
            {
                "name": "Farm animal care",
                "service_type": DairyService.ServiceType.ANIMAL_CARE,
                "description": "Routine care for dairy animals.",
                "price": "150.00",
                "location": "Bishoftu",
            },
        )

        self.assertEqual(product_response.status_code, 302)
        self.assertEqual(service_response.status_code, 302)
        self.assertTrue(DairyProduct.objects.filter(name="Fresh cream").exists())
        self.assertTrue(DairyService.objects.filter(name="Farm animal care").exists())
