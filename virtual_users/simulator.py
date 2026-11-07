import random
import uuid

from django.utils import timezone

from poultrys.models import Item

from .models import ActivityHistory, VirtualAgent


ROLE_ACTIONS = {
    VirtualAgent.Role.FARMER: (
        ('supplier_search', 'Compared local suppliers for {product} to {goal}.'),
        ('farm_planning', 'Reviewed the flock and feed plan for {product}, focused on {goal}.'),
        ('health_research', 'Looked for poultry health guidance related to {product} and {goal}.'),
    ),
    VirtualAgent.Role.POULTRY_BUSINESS: (
        ('catalog_review', 'Reviewed the listing for {product} while working to {goal}.'),
        ('stock_planning', 'Checked stock and seasonal demand for {product} to {goal}.'),
        ('buyer_research', 'Compared marketplace interest in {product} to {goal}.'),
    ),
    VirtualAgent.Role.SUPPLIER: (
        ('stock_review', 'Reviewed stock and pricing for {product} to {goal}.'),
        ('buyer_search', 'Looked for poultry businesses that may need {product} to {goal}.'),
        ('delivery_planning', 'Reviewed delivery options for {product} to {goal}.'),
    ),
    VirtualAgent.Role.SERVICE_PROVIDER: (
        ('service_planning', 'Reviewed availability for {service} to {goal}.'),
        ('farm_research', 'Prepared farm consultation notes about {goal}.'),
        ('service_profile_review', 'Reviewed {service} details to {goal}.'),
    ),
}


def simulate_agent_activity(agent):
    """Record one locally simulated, role-specific action without external side effects."""
    activity_count = agent.activity_history.count()
    rng = random.Random(agent.pk * 1009 + activity_count)
    action, summary_template = rng.choice(ROLE_ACTIONS[agent.role])

    product = (
        Item.objects.filter(created_by=agent.user).order_by('pk').first()
        or Item.objects.order_by('pk').first()
    )
    service = agent.services.order_by('pk').first()
    product_name = product.name if product else 'poultry products'
    service_name = service.name if service else 'poultry support'
    summary = summary_template.format(
        product=product_name,
        service=service_name,
        goal=agent.persona.get('goal', 'support local poultry businesses'),
    )

    activity = ActivityHistory.objects.create(
        agent=agent,
        event_key=f'simulation-{uuid.uuid4().hex}',
        action=action,
        summary=summary,
        metadata={
            'mode': 'local_persona_simulation',
            'role': agent.role,
            'product_id': product.pk if product else None,
            'service_id': service.pk if service else None,
            'persona_style': agent.persona.get('style', ''),
            'goal': agent.persona.get('goal', ''),
        },
    )
    agent.last_simulated_at = timezone.now()
    agent.save(update_fields=('last_simulated_at',))
    return activity


def simulate_enabled_agents():
    activities = []
    agents = VirtualAgent.objects.filter(is_enabled=True).select_related('user').order_by('pk')
    for agent in agents.iterator():
        activities.append(simulate_agent_activity(agent))
    return activities
