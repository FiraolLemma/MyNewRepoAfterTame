from django.conf import settings
from django.db import models


class VirtualAgent(models.Model):
    class Role(models.TextChoices):
        FARMER = 'farmer', 'Farmer'
        POULTRY_BUSINESS = 'poultry_business', 'Poultry business'
        SUPPLIER = 'supplier', 'Supplier'
        SERVICE_PROVIDER = 'service_provider', 'Service provider'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='virtual_agent',
    )
    role = models.CharField(max_length=30, choices=Role.choices)
    persona_label = models.CharField(max_length=100)
    persona = models.JSONField(default=dict)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_simulated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('user__username',)

    def __str__(self):
        return f'{self.persona_label} ({self.get_role_display()})'


class VirtualService(models.Model):
    agent = models.ForeignKey(
        VirtualAgent,
        on_delete=models.CASCADE,
        related_name='services',
    )
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('agent__user__username', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=('agent', 'name'),
                name='unique_virtual_service_per_agent',
            ),
        ]

    def __str__(self):
        return f'{self.name} - {self.agent.persona_label}'


class ActivityHistory(models.Model):
    agent = models.ForeignKey(
        VirtualAgent,
        on_delete=models.CASCADE,
        related_name='activity_history',
    )
    event_key = models.CharField(max_length=100)
    action = models.CharField(max_length=50)
    summary = models.CharField(max_length=250)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('agent', 'event_key'),
                name='unique_virtual_activity_event',
            ),
        ]
        indexes = [
            models.Index(fields=('agent', '-created_at'), name='virtual_act_agent_date'),
        ]

    def __str__(self):
        return f'{self.agent.persona_label}: {self.action}'
