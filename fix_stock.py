import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
django.setup()

from product.models import Product

count = Product.objects.update(amount=100)
print(f"✅ Đã cập nhật tồn kho = 100 cho {count} sản phẩm!")