from django.core.management.base import BaseCommand

from virtual_users.simulator import simulate_enabled_agents


class Command(BaseCommand):
    help = 'Run one local persona-simulation cycle for every enabled virtual user.'

    def handle(self, *args, **options):
        activities = simulate_enabled_agents()
        self.stdout.write(self.style.SUCCESS(
            f'Recorded {len(activities)} simulated activities.'
        ))
