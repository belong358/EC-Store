"""
Fix lỗi chính tả "Link kiện" -> "Linh kiện" và slug "link-kin" -> "linh-kien"
Cập nhật cả category lẫn banner link liên quan.
Chạy: python fix_linhkien.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
django.setup()

from product.models import Category
from home.models import Banner

# 1) Sửa category
cat = Category.objects.filter(slug='link-kin').first()
if cat:
    old_title, old_slug = cat.title, cat.slug
    cat.title = 'Linh kiện'
    cat.slug = 'linh-kien'
    cat.save()
    print(f"✅ Category: '{old_title}' ({old_slug}) → '{cat.title}' ({cat.slug})")
else:
    print("⚠️  Không tìm thấy category slug='link-kin' — có thể đã sửa rồi.")

# 2) Sửa banner link liên quan
count = Banner.objects.filter(link__icontains='link-kin').update(link='/category/11/linh-kien')
print(f"✅ Đã sửa {count} banner có link chứa 'link-kin' → '/category/11/linh-kien'")
