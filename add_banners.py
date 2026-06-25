"""
Script thêm 3 banner quảng cáo mới vào database.
Chạy: python add_banners.py
Yêu cầu: đã copy 3 file ảnh vào uploads/images/banner/ trước khi chạy.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from django.core.files import File
from home.models import Banner

start = timezone.now()
end = start + timedelta(days=90)  # banner chạy trong 90 ngày

new_banners = [
    {
        'title': 'Acer Predator Helios 16 - Hot Deal',
        'description': 'RTX 4070, Core i9, màn 16 inch 240Hz - 52.000.000đ',
        'image_path': 'banner_predator.jpg',
        'link': '/product/8/acer-gaming-predator-helios-16/',
    },
    {
        'title': 'ASUS TUF RTX 4070 Ti - Nâng cấp hiệu năng',
        'description': '12GB GDDR6X, Ray Tracing thế hệ mới - 23.500.000đ',
        'image_path': 'banner_vga.jpg',
        'link': '/product/19/card-man-hinh-asus-tuf-rtx-4070-ti-12g-gaming/',
    },
    {
        'title': 'Combo Gaming Gear - Trang bị toàn diện',
        'description': 'Bàn phím, chuột, tai nghe chính hãng ASUS & SteelSeries',
        'image_path': 'banner_combo.jpg',
        'link': '/category/2/linh-kien',
    },
]

created = 0
for b in new_banners:
    banner = Banner(
        title=b['title'],
        description=b['description'],
        link=b['link'],
        start_at=start,
        end_at=end,
        status='True',
    )
    img_full_path = os.path.join('uploads', 'images', 'banner', b['image_path'])
    if not os.path.exists(img_full_path):
        print(f"⚠️  KHÔNG TÌM THẤY: {img_full_path} — bỏ qua banner '{b['title']}'")
        continue
    with open(img_full_path, 'rb') as f:
        banner.image.save(b['image_path'], File(f), save=False)
    banner.save()
    created += 1
    print(f"✅ Đã thêm banner: {b['title']}")

print(f"\n🎉 Hoàn tất! Đã thêm {created}/{len(new_banners)} banner mới.")
