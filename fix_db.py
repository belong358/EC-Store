import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Xóa 3 sản phẩm test tên 'cac' (id 25, 26, 27)
    cursor.execute("DELETE FROM product_product WHERE title = 'cac'")
    print(f"Đã xóa {cursor.rowcount} sản phẩm test")