# Generated by Django 4.2.3 on 2023-12-17 22:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("logika_statistics", "0011_remove_paymentrecord_tutor"),
    ]

    operations = [
        migrations.RenameField(
            model_name="masterclassrecord",
            old_name="recent_group_lms_id",
            new_name="mc_lms_id",
        ),
        migrations.RenameField(
            model_name="paymentrecord",
            old_name="mc_lms_id",
            new_name="recent_group_lms_id",
        ),
    ]
