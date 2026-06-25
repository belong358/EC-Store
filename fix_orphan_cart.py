import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
django.setup()

from order.models import ShopCart

# Các dòng giỏ hàng "mồ côi": user đã bị xóa (on_delete=SET_NULL) nhưng sản phẩm
# trong giỏ của họ vẫn còn sót lại với user_id = NULL. Trước đây trang /shopcart/
# vô tình hiển thị nhầm các dòng này cho khách CHƯA đăng nhập.
orphans = ShopCart.objects.filter(user__isnull=True)
count = orphans.count()
for rs in orphans:
    print(f"  - Xóa: ShopCart #{rs.id} | sản phẩm: {rs.product} | số lượng: {rs.quantity}")
orphans.delete()

print(f"✅ Đã xóa {count} dòng giỏ hàng mồ côi (user_id NULL)!")
