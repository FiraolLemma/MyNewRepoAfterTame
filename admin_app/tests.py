from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardAccessTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff_user = user_model.objects.create(
            username="dashboard-staff",
            phone_number="+12025550101",
            is_staff=True,
            onboarding_complete=True,
        )
        self.regular_user = user_model.objects.create(
            username="dashboard-user",
            phone_number="+12025550102",
            onboarding_complete=True,
        )
        self.dashboard_url = reverse("admin_app:dashboard")

    def test_dashboard_redirects_anonymous_users_to_login(self):
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 302)

    def test_dashboard_forbids_authenticated_non_staff_users(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 403)

    def test_staff_dashboard_renders_integrated_metrics_and_actions(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["users_count"], 2)
        self.assertEqual(response.context["dairy_farms_count"], 0)
        self.assertEqual(response.context["poultry_farms_count"], 0)
        self.assertContains(response, "Dairy farms and inventory")
        self.assertContains(response, "Poultry sales records")
