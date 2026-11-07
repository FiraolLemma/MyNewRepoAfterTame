from django import template
from django.core.cache import cache
from conversation.models import ConversationMessage

register = template.Library()

@register.filter(name='get_unread_count')
def get_unread_count(unread_counts, conversation_id):
    """
    Gets unread count from dictionary safely.
    Usage: {{ unread_counts|get_unread_count:conversation.id }}
    """
    return unread_counts.get(str(conversation_id), 0)

@register.filter(name='unread_messages_count')
def unread_messages_count(user):
    """
    Get unread messages count for user with caching
    """
    if not user or not user.is_authenticated:
        return 0
    
    cache_key = f"user_{user.id}_total_unread"
    count = cache.get(cache_key)
    
    if count is None:
        count = ConversationMessage.objects.filter(
            conversation__members=user,
            is_read=False
        ).exclude(created_by=user).count()
        cache.set(cache_key, count, timeout=300)  # Cache for 5 minutes
    
    return count

@register.filter
def get_item_image_url(item):
    if not item:
        return None

    for field_name in ('main_image', 'image', 'photo', 'picture', 'avatar', 'profile_picture'):
        image = getattr(item, field_name, None)
        if image:
            try:
                return image.url
            except ValueError:
                continue

    images = getattr(item, 'images', None)
    if images:
        image = (
            images.filter(is_main=True).first()
            if item.__class__.__name__ == 'ClothingItem'
            else images.first()
        )
        if image and image.image:
            try:
                return image.image.url
            except ValueError:
                return None

    return None

@register.filter
def get_item_name(item):
    """Get the display name for any item"""
    if not item:
        return "Unknown Item"
    
    if hasattr(item, 'name') and item.name:
        return item.name
    elif hasattr(item, 'title') and item.title:
        return item.title
    elif hasattr(item, 'farm_name') and item.farm_name:
        return item.farm_name
    
    # Fallback to string representation
    return str(item)

@register.filter
def get_item_description(item):
    """Get description for any item"""
    if not item:
        return ""
    
    description_fields = ['description', 'desc', 'details', 'info']
    for field in description_fields:
        if hasattr(item, field):
            value = getattr(item, field, '')
            if value:
                return str(value)
    
    return ""