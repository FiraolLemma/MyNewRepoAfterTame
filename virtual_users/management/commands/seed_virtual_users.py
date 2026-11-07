from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from poultrys.models import Category, Item
from dairys.models import DairyCategory, DairyProduct, DairyService
from users.models import Profile

from virtual_users.models import ActivityHistory, VirtualAgent, VirtualService


PERSONAS = (
    {
        'name': 'Hana Bekele', 'role': VirtualAgent.Role.FARMER, 'city': 'Addis Ababa',
        'style': 'careful planner', 'goal': 'improve flock health and feed efficiency',
        'product': 'Demo: Local Layer Eggs', 'product_description': 'Fresh layer eggs from a small Addis Ababa poultry farm. Demo listing by a virtual account.',
        'product_price': '280.00', 'service': 'Demo: Farm egg collection',
        'service_description': 'Arrange a local farm-gate egg collection. Demo service listing.',
        'service_price': '0.00',
    },
    {
        'name': 'Abebe Tadesse', 'role': VirtualAgent.Role.FARMER, 'city': 'Bishoftu',
        'style': 'quality focused', 'goal': 'raise healthy dual-purpose chickens',
        'product': 'Demo: Free-range Eggs', 'product_description': 'Free-range eggs from a demonstration poultry farm near Bishoftu.',
        'product_price': '300.00', 'service': 'Demo: Poultry farm visit',
        'service_description': 'Coordinate a farm visit to discuss small-flock management. Demo service listing.',
        'service_price': '50.00',
    },
    {
        'name': 'Mekdes Girma', 'role': VirtualAgent.Role.FARMER, 'city': 'Adama',
        'style': 'community minded', 'goal': 'find reliable chick and feed suppliers',
        'product': 'Demo: Farm-grown Eggs', 'product_description': 'Locally produced eggs from a virtual farm profile in Adama.',
        'product_price': '270.00', 'service': 'Demo: Small flock starter advice',
        'service_description': 'Share a basic starter checklist for small poultry flocks. Demo service listing.',
        'service_price': '25.00',
    },
    {
        'name': 'Dawit Alemu', 'role': VirtualAgent.Role.FARMER, 'city': 'Hawassa',
        'style': 'budget conscious', 'goal': 'keep feed costs predictable',
        'product': 'Demo: Farm Eggs - Hawassa', 'product_description': 'Sample egg listing for a virtual poultry farmer in Hawassa.',
        'product_price': '260.00', 'service': 'Demo: Farm pickup coordination',
        'service_description': 'Coordinate farm pickup windows for local buyers. Demo service listing.',
        'service_price': '0.00',
    },
    {
        'name': 'Selamawit Worku', 'role': VirtualAgent.Role.FARMER, 'city': 'Jimma',
        'style': 'experiment oriented', 'goal': 'compare local feed and vaccination options',
        'product': 'Demo: Mixed-size Eggs', 'product_description': 'Mixed-size eggs from a virtual family poultry farm in Jimma.',
        'product_price': '250.00', 'service': 'Demo: Flock care discussion',
        'service_description': 'Discuss everyday flock care and record keeping. Demo service listing.',
        'service_price': '20.00',
    },
    {
        'name': 'Kebede Mulu', 'role': VirtualAgent.Role.FARMER, 'city': 'Dire Dawa',
        'style': 'practical and direct', 'goal': 'sell surplus eggs to nearby businesses',
        'product': 'Demo: Weekly Egg Basket', 'product_description': 'A sample weekly egg basket offered by a virtual farm in Dire Dawa.',
        'product_price': '290.00', 'service': 'Demo: Weekly egg delivery planning',
        'service_description': 'Plan a recurring local egg delivery. Demo service listing.',
        'service_price': '15.00',
    },
    {
        'name': 'Rahel Tesfaye', 'role': VirtualAgent.Role.FARMER, 'city': 'Gondar',
        'style': 'patient and observant', 'goal': 'build a resilient layer flock',
        'product': 'Demo: Layer Eggs - Gondar', 'product_description': 'Sample layer egg listing from a virtual farm in Gondar.',
        'product_price': '275.00', 'service': 'Demo: Farm production notes',
        'service_description': 'Share a sample weekly production record template. Demo service listing.',
        'service_price': '10.00',
    },
    {
        'name': 'Netsanet Poultry', 'role': VirtualAgent.Role.POULTRY_BUSINESS, 'city': 'Addis Ababa',
        'style': 'customer focused', 'goal': 'keep a dependable supply of table eggs',
        'product': 'Demo: Table Eggs - Addis', 'product_description': 'Sample table egg listing from a virtual poultry business.',
        'product_price': '310.00', 'service': 'Demo: Bulk order coordination',
        'service_description': 'Coordinate sample bulk-order quantities and pickup. Demo service listing.',
        'service_price': '0.00',
    },
    {
        'name': 'Biftu Layers', 'role': VirtualAgent.Role.POULTRY_BUSINESS, 'city': 'Bishoftu',
        'style': 'consistent and data driven', 'goal': 'match egg production to buyer demand',
        'product': 'Demo: Fresh Layer Eggs - Bishoftu', 'product_description': 'Sample fresh egg listing from a virtual layer business.',
        'product_price': '295.00', 'service': 'Demo: Recurring supply plan',
        'service_description': 'Set a sample recurring supply schedule for local buyers. Demo service listing.',
        'service_price': '20.00',
    },
    {
        'name': 'Lomi Poultry House', 'role': VirtualAgent.Role.POULTRY_BUSINESS, 'city': 'Adama',
        'style': 'growth focused', 'goal': 'serve restaurants and neighborhood shops',
        'product': 'Demo: Restaurant Egg Crate', 'product_description': 'Sample restaurant-size egg order from a virtual poultry business.',
        'product_price': '325.00', 'service': 'Demo: Restaurant order planning',
        'service_description': 'Plan a sample weekly restaurant order. Demo service listing.',
        'service_price': '30.00',
    },
    {
        'name': 'Lakeview Layers', 'role': VirtualAgent.Role.POULTRY_BUSINESS, 'city': 'Hawassa',
        'style': 'quality first', 'goal': 'offer reliable regional egg supply',
        'product': 'Demo: Regional Layer Eggs', 'product_description': 'Sample regional egg supply listing from a virtual business in Hawassa.',
        'product_price': '305.00', 'service': 'Demo: Local delivery coordination',
        'service_description': 'Coordinate local sample deliveries for poultry products. Demo service listing.',
        'service_price': '15.00',
    },
    {
        'name': 'Jimma Chickens', 'role': VirtualAgent.Role.POULTRY_BUSINESS, 'city': 'Jimma',
        'style': 'straightforward and responsive', 'goal': 'grow repeat local customers',
        'product': 'Demo: Farm Chicken Pair', 'product_description': 'Sample poultry product listing from a virtual business in Jimma.',
        'product_price': '900.00', 'service': 'Demo: Poultry sourcing support',
        'service_description': 'Help buyers plan sample local poultry sourcing. Demo service listing.',
        'service_price': '40.00',
    },
    {
        'name': 'Eastern Poultry Market', 'role': VirtualAgent.Role.POULTRY_BUSINESS, 'city': 'Dire Dawa',
        'style': 'market aware', 'goal': 'keep product availability transparent',
        'product': 'Demo: Mixed Poultry Pack', 'product_description': 'Sample mixed poultry product pack from a virtual business in Dire Dawa.',
        'product_price': '750.00', 'service': 'Demo: Buyer order preparation',
        'service_description': 'Prepare sample product quantities for a buyer. Demo service listing.',
        'service_price': '25.00',
    },
    {
        'name': 'Alem Feed Supply', 'role': VirtualAgent.Role.SUPPLIER, 'city': 'Addis Ababa',
        'style': 'reliable and detail oriented', 'goal': 'connect farms with consistent feed stock',
        'product': 'Demo: Layer Feed 25kg', 'product_description': 'Sample layer feed listing from a virtual poultry supplier.',
        'product_price': '1250.00', 'service': 'Demo: Feed requirement estimate',
        'service_description': 'Estimate sample feed requirements from flock size. Demo service listing.',
        'service_price': '35.00',
    },
    {
        'name': 'Bishoftu Chick Supply', 'role': VirtualAgent.Role.SUPPLIER, 'city': 'Bishoftu',
        'style': 'careful with sourcing', 'goal': 'help farmers source healthy day-old chicks',
        'product': 'Demo: Day-old Chicks', 'product_description': 'Sample day-old chick listing from a virtual supplier; not a live offer.',
        'product_price': '120.00', 'service': 'Demo: Chick order planning',
        'service_description': 'Plan a sample chick order and collection window. Demo service listing.',
        'service_price': '20.00',
    },
    {
        'name': 'Adama Poultry Inputs', 'role': VirtualAgent.Role.SUPPLIER, 'city': 'Adama',
        'style': 'practical and responsive', 'goal': 'keep essential poultry inputs available',
        'product': 'Demo: Poultry Vitamin Pack', 'product_description': 'Sample poultry vitamin pack listing from a virtual supplier.',
        'product_price': '180.00', 'service': 'Demo: Input sourcing assistance',
        'service_description': 'Help compare sample poultry supply options. Demo service listing.',
        'service_price': '25.00',
    },
    {
        'name': 'Hawassa Farm Equipment', 'role': VirtualAgent.Role.SUPPLIER, 'city': 'Hawassa',
        'style': 'solution oriented', 'goal': 'support small farms with practical equipment',
        'product': 'Demo: Poultry Waterer', 'product_description': 'Sample poultry waterer listing from a virtual equipment supplier.',
        'product_price': '450.00', 'service': 'Demo: Equipment setup guidance',
        'service_description': 'Share sample setup guidance for small-farm poultry equipment. Demo service listing.',
        'service_price': '30.00',
    },
    {
        'name': 'Jimma Grain and Feed', 'role': VirtualAgent.Role.SUPPLIER, 'city': 'Jimma',
        'style': 'value conscious', 'goal': 'provide predictable feed ingredient pricing',
        'product': 'Demo: Poultry Feed Mix', 'product_description': 'Sample poultry feed mix listing from a virtual supplier in Jimma.',
        'product_price': '980.00', 'service': 'Demo: Feed mix information',
        'service_description': 'Provide sample feed mix information for discussion. Demo service listing.',
        'service_price': '15.00',
    },
    {
        'name': 'Dire Dawa Poultry Supplies', 'role': VirtualAgent.Role.SUPPLIER, 'city': 'Dire Dawa',
        'style': 'organized and prompt', 'goal': 'help regional farms replenish supplies',
        'product': 'Demo: Poultry Feeder', 'product_description': 'Sample poultry feeder listing from a virtual supplier in Dire Dawa.',
        'product_price': '390.00', 'service': 'Demo: Supply delivery planning',
        'service_description': 'Plan a sample local delivery route for poultry supplies. Demo service listing.',
        'service_price': '20.00',
    },
    {
        'name': 'Dr. Saba Veterinary', 'role': VirtualAgent.Role.SERVICE_PROVIDER, 'city': 'Addis Ababa',
        'style': 'calm and evidence minded', 'goal': 'help farms plan preventive flock care',
        'product': 'Demo: Poultry Health Guide', 'product_description': 'Sample poultry health guide listing from a virtual service provider.',
        'product_price': '100.00', 'service': 'Demo: Farm health consultation',
        'service_description': 'Sample poultry health consultation; this virtual account does not provide real veterinary care.',
        'service_price': '250.00',
    },
    {
        'name': 'Bekele Feed Advisory', 'role': VirtualAgent.Role.SERVICE_PROVIDER, 'city': 'Bishoftu',
        'style': 'analytical and approachable', 'goal': 'make feed planning easier for small flocks',
        'product': 'Demo: Feed Planning Worksheet', 'product_description': 'Sample feed planning worksheet from a virtual service provider.',
        'product_price': '50.00', 'service': 'Demo: Feed planning session',
        'service_description': 'Sample feed planning session for a poultry farm. Demo service listing.',
        'service_price': '180.00',
    },
    {
        'name': 'Mimi Poultry Training', 'role': VirtualAgent.Role.SERVICE_PROVIDER, 'city': 'Adama',
        'style': 'encouraging and step by step', 'goal': 'share useful poultry business basics',
        'product': 'Demo: Poultry Record Book', 'product_description': 'Sample poultry record book listing from a virtual trainer.',
        'product_price': '80.00', 'service': 'Demo: Small farm training',
        'service_description': 'Sample introductory poultry farm training. Demo service listing.',
        'service_price': '300.00',
    },
    {
        'name': 'Hawassa Biosecurity Support', 'role': VirtualAgent.Role.SERVICE_PROVIDER, 'city': 'Hawassa',
        'style': 'thorough and safety conscious', 'goal': 'help farms improve everyday biosecurity',
        'product': 'Demo: Biosecurity Checklist', 'product_description': 'Sample biosecurity checklist from a virtual service provider.',
        'product_price': '40.00', 'service': 'Demo: Biosecurity walkthrough',
        'service_description': 'Sample biosecurity walkthrough for a poultry farm. Demo service listing.',
        'service_price': '220.00',
    },
    {
        'name': 'Jimma Hatchery Coach', 'role': VirtualAgent.Role.SERVICE_PROVIDER, 'city': 'Jimma',
        'style': 'patient and practical', 'goal': 'support reliable chick brooding routines',
        'product': 'Demo: Brooding Notes', 'product_description': 'Sample chick brooding notes from a virtual service provider.',
        'product_price': '60.00', 'service': 'Demo: Brooding setup review',
        'service_description': 'Sample brooding setup review for a poultry farm. Demo service listing.',
        'service_price': '200.00',
    },
    {
        'name': 'Dire Dawa Farm Consultant', 'role': VirtualAgent.Role.SERVICE_PROVIDER, 'city': 'Dire Dawa',
        'style': 'direct and collaborative', 'goal': 'help poultry businesses improve daily operations',
        'product': 'Demo: Farm Planning Template', 'product_description': 'Sample farm planning template from a virtual consultant.',
        'product_price': '75.00', 'service': 'Demo: Farm operations review',
        'service_description': 'Sample poultry farm operations review. Demo service listing.',
        'service_price': '275.00',
    },
)

DAIRY_LISTINGS = {
    VirtualAgent.Role.FARMER: (
        'Fresh farm milk', 'fresh-milk', 'liter', 'Farm-fresh milk',
        'animal_care', 'Dairy animal care visit',
    ),
    VirtualAgent.Role.POULTRY_BUSINESS: (
        'Farm yogurt', 'yogurt', 'kg', 'Small-batch yogurt',
        'milk_processing', 'Dairy processing support',
    ),
    VirtualAgent.Role.SUPPLIER: (
        'Dairy cattle feed', 'feed-equipment', 'package', 'Dairy farm feed',
        'delivery', 'Dairy supply delivery',
    ),
    VirtualAgent.Role.SERVICE_PROVIDER: (
        'Dairy farm hygiene kit', 'feed-equipment', 'package', 'Dairy hygiene kit',
        'farm_consulting', 'Dairy farm consultation',
    ),
}


class Command(BaseCommand):
    help = 'Create or update the 25 clearly labeled local virtual-user demo accounts.'

    @transaction.atomic
    def handle(self, *args, **options):
        if len(PERSONAS) != 25:
            raise CommandError('The virtual-user seed data must contain exactly 25 personas.')

        User = get_user_model()
        category, _ = Category.objects.get_or_create(
            slug='virtual-demo-products',
            defaults={
                'name': 'Virtual demo products',
                'description': 'Sample listings owned by clearly labeled virtual users.',
                'icon': 'flask',
            },
        )

        for index, data in enumerate(PERSONAS, start=1):
            username = f'virtual_user_{index:02d}'
            phone_number = f'+251000000{index:03d}'
            user = User.objects.filter(username=username).first()
            if user is not None and not hasattr(user, 'virtual_agent'):
                raise CommandError(
                    f'Cannot seed {username}: that username belongs to a non-virtual account.'
                )
            if user is None:
                user = User.objects.create_user(
                    username=username,
                    phone_number=phone_number,
                )

            user.set_unusable_password()
            user.is_active = True
            user.is_staff = False
            user.save(update_fields=('password', 'is_active', 'is_staff'))

            display_name = data['name']
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = (
                f'[Virtual demo account] {display_name} is a {data["style"]} '
                f'{data["role"].replace("_", " ")} based in {data["city"]}. '
                f'Primary goal: {data["goal"]}.'
            )
            profile.location = data['city']
            profile.email = f'{username}@example.invalid'
            profile.save(update_fields=('bio', 'location', 'email'))

            agent, _ = VirtualAgent.objects.update_or_create(
                user=user,
                defaults={
                    'role': data['role'],
                    'persona_label': display_name,
                    'persona': {
                        'style': data['style'],
                        'goal': data['goal'],
                        'city': data['city'],
                        'simulation': 'local_rule_based',
                    },
                    'is_enabled': True,
                },
            )
            product, _ = Item.objects.get_or_create(
                created_by=user,
                name=data['product'],
                defaults={
                    'description': data['product_description'],
                    'price': Decimal(data['product_price']),
                    'category': category,
                    'is_featured': True,
                },
            )
            (
                dairy_product_base,
                dairy_category_slug,
                dairy_unit,
                dairy_product_label,
                dairy_service_type,
                dairy_service_label,
            ) = DAIRY_LISTINGS[data['role']]
            dairy_category = DairyCategory.objects.get(slug=dairy_category_slug)
            dairy_product_name = f'Demo: {dairy_product_base} - {display_name}'
            dairy_product, _ = DairyProduct.objects.get_or_create(
                slug=slugify(f'{username}-{dairy_product_base}'),
                defaults={
                    'category': dairy_category,
                    'created_by': user,
                    'name': dairy_product_name,
                    'description': (
                        f'{dairy_product_label} from a virtual demo profile. '
                        'Demonstration listing only; not a real product offer.'
                    ),
                    'price': Decimal('250.00'),
                    'unit': dairy_unit,
                    'quantity_available': 25,
                    'location': data['city'],
                    'is_featured': False,
                },
            )
            dairy_service_name = f'Demo: {dairy_service_label} - {display_name}'
            dairy_service, _ = DairyService.objects.get_or_create(
                slug=slugify(f'{username}-{dairy_service_label}'),
                defaults={
                    'provider': user,
                    'name': dairy_service_name,
                    'service_type': dairy_service_type,
                    'description': (
                        f'{dairy_service_label} provided by a virtual demo profile. '
                        'Demonstration listing only; no real service is being offered.'
                    ),
                    'price': Decimal('0.00'),
                    'location': data['city'],
                    'is_available': True,
                },
            )
            service, _ = VirtualService.objects.get_or_create(
                agent=agent,
                name=data['service'],
                defaults={
                    'description': data['service_description'],
                    'price': Decimal(data['service_price']),
                },
            )

            seed_events = (
                ('seed-profile', 'profile_created', 'Created a virtual demo profile.'),
                ('seed-product', 'product_listed', f'Published demo product: {product.name}.'),
                ('seed-service', 'service_listed', f'Published demo service: {service.name}.'),
                (
                    'seed-dairy-product',
                    'dairy_demo_product_listed',
                    f'Published demo dairy product: {dairy_product.name}.',
                ),
                (
                    'seed-dairy-service',
                    'dairy_demo_service_listed',
                    f'Published demo dairy service: {dairy_service.name}.',
                ),
            )
            for event_key, action, summary in seed_events:
                ActivityHistory.objects.get_or_create(
                    agent=agent,
                    event_key=event_key,
                    defaults={
                        'action': action,
                        'summary': summary,
                        'metadata': {'mode': 'seed', 'demo_data': True},
                    },
                )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(PERSONAS)} virtual-user accounts with profiles, products, services, and activity history.'
        ))
