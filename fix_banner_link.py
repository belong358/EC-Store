"""
Script fix link sai của banner "Combo Gaming Gear"
Chạy: python fix_banner_link.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
django.setup()

from home.models import Banner

count = Banner.objects.filter(link='/category/2/linh-kien').update(link='/category/11/link-kin')
print(f"✅ Đã sửa {count} banner có link sai thành /category/11/link-kin")

# In ra toàn bộ banner hiện có để kiểm tra lại
print("\n=== Danh sách banner hiện tại ===")
for b in Banner.objects.all():
    print(f"- {b.title}: {b.link}")
