from django.db import migrations


DAIRY_CATEGORIES = (
    (
        "Butter and cream",
        "butter-cream",
        "Butter, cream, and related dairy products.",
        "fa-bottle-droplet",
    ),
    (
        "Cheese",
        "cheese",
        "Farm-made and locally produced cheeses.",
        "fa-cheese",
    ),
    (
        "Dairy livestock",
        "dairy-livestock",
        "Dairy cattle and farm animals.",
        "fa-cow",
    ),
    (
        "Feed and equipment",
        "feed-equipment",
        "Dairy feed, milking tools, and farm equipment.",
        "fa-wheat-awn",
    ),
    (
        "Fresh milk",
        "fresh-milk",
        "Fresh cow and goat milk.",
        "fa-glass-water",
    ),
    (
        "Yogurt",
        "yogurt",
        "Cultured dairy products.",
        "fa-bowl-food",
    ),
)


def ensure_dairy_categories(apps, schema_editor):
    DairyCategory = apps.get_model("clothings", "DairyCategory")
    manager = DairyCategory.objects.using(schema_editor.connection.alias)
    for name, slug, description, icon in DAIRY_CATEGORIES:
        manager.get_or_create(
            slug=slug,
            defaults={"name": name, "description": description, "icon": icon},
        )


class Migration(migrations.Migration):
    dependencies = [("clothings", "0004_seed_virtual_dairy_marketplace")]

    operations = [
        migrations.RunPython(
            ensure_dairy_categories,
            migrations.RunPython.noop,
        )
    ]
