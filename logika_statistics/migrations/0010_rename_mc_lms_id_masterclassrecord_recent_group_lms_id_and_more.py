# Generated by Django 4.2.3 on 2023-12-17 22:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logika_statistics", "0009_paymentrecord_alter_masterclassrecord_business"),
    ]

    operations = [
        migrations.RenameField(
            model_name="masterclassrecord",
            old_name="mc_lms_id",
            new_name="recent_group_lms_id",
        ),
        migrations.AddField(
            model_name="paymentrecord",
            name="payment_amount",
            field=models.CharField(max_length=16, null=True),
        ),
    ]