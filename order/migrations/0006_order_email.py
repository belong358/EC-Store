from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(blank=True, max_length=100, default=''),
            preserve_default=False,
        ),
    ]
