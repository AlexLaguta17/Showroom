# Generated manually to fix order_status max_length

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("car_showrooms", "0003_remove_carshowroomorder_price_currency_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="carshowroomorder",
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
