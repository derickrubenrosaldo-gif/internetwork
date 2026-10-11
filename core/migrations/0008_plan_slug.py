"""Añade Plan.slug (URL corta) y lo rellena para los planes existentes."""

from django.db import migrations, models
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    Plan = apps.get_model("core", "Plan")
    used = set()
    for plan in Plan.objects.all().order_by("pk"):
        base = slugify(plan.name) or f"plan-{plan.pk}"
        slug = base
        index = 2
        while slug in used:
            slug = f"{base}-{index}"
            index += 1
        Plan.objects.filter(pk=plan.pk).update(slug=slug)
        used.add(slug)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_usedlogintoken_payment_confirmed_by_payment_paid_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="plan",
            name="slug",
            field=models.SlugField(
                blank=True,
                default="",
                help_text="Se genera del nombre. Se usa en ?plan=… para preseleccionar el plan.",
                max_length=90,
                verbose_name="URL corta",
            ),
            preserve_default=False,
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="plan",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="Se genera del nombre. Se usa en ?plan=… para preseleccionar el plan.",
                max_length=90,
                unique=True,
                verbose_name="URL corta",
            ),
        ),
    ]
