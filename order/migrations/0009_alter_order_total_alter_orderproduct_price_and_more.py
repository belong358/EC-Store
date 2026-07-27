# Generated manually to accompany the FloatField -> DecimalField fix for
# money fields (Order.total, OrderProduct.price, OrderProduct.amount).
# Run `python manage.py makemigrations --check` after pulling this to make
# sure Django doesn't detect any further model changes it needs to migrate.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_alter_order_first_name_alter_order_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(max_digits=15, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='price',
            field=models.DecimalField(max_digits=15, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='amount',
            field=models.DecimalField(max_digits=15, decimal_places=2),
        ),
    ]
