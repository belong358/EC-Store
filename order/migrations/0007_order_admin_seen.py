from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_order_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='admin_seen',
            field=models.BooleanField(default=False),
        ),
    ]
