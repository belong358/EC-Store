from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_alter_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('Chờ xác nhận', 'Chờ xác nhận'),
                    ('Chờ lấy hàng', 'Chờ lấy hàng'),
                    ('Chờ giao hàng', 'Chờ giao hàng'),
                    ('Đã giao hàng', 'Đã giao hàng'),
                    ('Trả hàng', 'Trả hàng'),
                    ('Đã hủy', 'Đã hủy'),
                ],
                default='Chờ xác nhận',
                max_length=20,
            ),
        ),
    ]
