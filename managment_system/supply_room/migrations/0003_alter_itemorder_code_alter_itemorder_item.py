# Generated by Django 5.0.4 on 2025-03-20 01:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_room", "0002_alter_classgroups_class_id_alter_users_role_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="itemorder",
            name="code",
            field=models.CharField(blank=True, max_length=200, verbose_name="Código"),
        ),
        migrations.AlterField(
            model_name="itemorder",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                to="supply_room.item",
                verbose_name="Artículo",
            ),
        ),
    ]
