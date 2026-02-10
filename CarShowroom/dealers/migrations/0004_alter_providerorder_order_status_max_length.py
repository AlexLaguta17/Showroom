# Generated manually to fix order_status max_length

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dealers", "0003_remove_providercar_price_currency_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="providerorder",
            name="order_status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Completed", "Completed"),
                    ("Rejected", "Rejected"),
                    ("Cancelled", "Cancelled"),
                    ("Sold", "Sold"),
                    ("Booked", "Booked"),
                ],
                default="Pending",
                max_length=9,
            ),
        ),
    ]
