from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

def get_item_model(app_label, model_name, object_id):
    """Get any item model using app label and model name"""
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    model_class = content_type.model_class()
    return get_object_or_404(model_class, id=object_id)