from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from dairys.models import DairyProduct, DairyService
from poultrys.models import Item

from .models import ActivityHistory, VirtualAgent, VirtualService


class VirtualUserManagementTests(TestCase):
    def test_seed_command_creates_idempotent_virtual_marketplace(self):
        output = StringIO()
        call_command('seed_virtual_users', stdout=output)
        call_command('seed_virtual_users', stdout=StringIO())

        self.assertEqual(VirtualAgent.objects.count(), 25)
        self.assertEqual(get_user_model().objects.filter(username__startswith='virtual_user_').count(), 25)
        role_counts = {
            role: VirtualAgent.objects.filter(role=role).count()
            for role, _ in VirtualAgent.Role.choices
        }
        self.assertEqual(role_counts, {
            VirtualAgent.Role.FARMER: 7,
            VirtualAgent.Role.POULTRY_BUSINESS: 6,
            VirtualAgent.Role.SUPPLIER: 6,
            VirtualAgent.Role.SERVICE_PROVIDER: 6,
        })
        for agent in VirtualAgent.objects.select_related('user').all():
            self.assertFalse(agent.user.has_usable_password())
            self.assertIn('[Virtual demo account]', agent.user.profile.bio)
            self.assertTrue(Item.objects.filter(created_by=agent.user).exists())
            self.assertTrue(VirtualService.objects.filter(agent=agent).exists())
            self.assertTrue(DairyProduct.objects.filter(created_by=agent.user).exists())
            self.assertTrue(DairyService.objects.filter(provider=agent.user).exists())
            self.assertEqual(agent.activity_history.count(), 5)

    def test_simulation_records_one_separate_activity_per_enabled_agent(self):
        call_command('seed_virtual_users', stdout=StringIO())
        call_command('simulate_virtual_users', stdout=StringIO())

        self.assertEqual(ActivityHistory.objects.count(), 25 * 6)
        self.assertEqual(
            ActivityHistory.objects.filter(action__in=(
                'supplier_search', 'farm_planning', 'health_research',
                'catalog_review', 'stock_planning', 'buyer_research',
                'stock_review', 'buyer_search', 'delivery_planning',
                'service_planning', 'farm_research', 'service_profile_review',
            )).count(),
            25,
        )
