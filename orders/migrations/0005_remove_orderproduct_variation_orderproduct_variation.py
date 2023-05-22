# Generated by Django 4.1.5 on 2023-05-20 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_variation"),
        ("orders", "0004_remove_orderproduct_color_remove_orderproduct_size"),
    ]

    operations = [
        migrations.RemoveField(model_name="orderproduct", name="variation",),
        migrations.AddField(
            model_name="orderproduct",
            name="variation",
            field=models.ManyToManyField(blank=True, to="store.variation"),
        ),
    ]
