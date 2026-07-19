# import Variants as Variants
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Count
from django.forms import ModelForm

from product.models import Product


class ShopCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()

    def __str__(self):
        return self.product.title

    @property
    def price(self):
        return self.product.final_price

    @property
    def amount(self):
        return self.quantity * self.product.final_price

    @property
    def varamount(self):
        return self.quantity * self.product.final_price

    def countreview(self):
        reviews = ShopCart.objects.filter(product=self, status='True').aggregate(count=Count('id'))
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt


class ShopCartForm(ModelForm):
    class Meta:
        model = ShopCart
        fields = ['quantity']


class Order(models.Model):
    STATUS = (
        ('Chờ xác nhận', 'Chờ xác nhận'),
        ('Chờ lấy hàng', 'Chờ lấy hàng'),
        ('Chờ giao hàng', 'Chờ giao hàng'),
        ('Đã giao hàng', 'Đã giao hàng'),
        ('Trả hàng', 'Trả hàng'),
        ('Đã hủy', 'Đã hủy'),
    )
    PAYMENT_METHODS = (
        ('COD', 'Thanh toán khi nhận hàng (COD)'),
        ('Stripe', 'Thanh toán qua Stripe (Thẻ Quốc tế)'),
        ('VNPay', 'Thanh toán qua VNPay (Ngân hàng Nội địa)'),
        ('MoMo', 'Thanh toán qua Ví MoMo'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=5, editable=False)
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    email = models.EmailField(blank=True, max_length=100)
    phone = models.CharField(blank=True, max_length=20)
    address = models.CharField(blank=True, max_length=150)
    city = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    total = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS, default='Chờ xác nhận')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='COD')
    ip = models.CharField(blank=True, max_length=20)
    adminnote = models.CharField(blank=True, max_length=100)
    stripe_payment_id = models.CharField(blank=True, max_length=100, null=True)
    # Đánh dấu admin đã xem đơn hàng này hay chưa. TÁCH BIỆT với `status`:
    # trước đây chuông thông báo lọc theo status='Chờ xác nhận', nhưng đơn COD
    # được tự động chuyển sang 'Chờ lấy hàng' gần như ngay lập tức sau khi đặt
    # (xem confirm_order_paid trong order/views.py), nên đơn hàng gần như luôn
    # "lọt lưới" khỏi chuông thông báo trước khi admin kịp thấy. Dùng cờ riêng
    # này để chuông báo đúng "đơn hàng mới" bất kể status hiện tại là gì.
    admin_seen = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'phone', 'city', 'country']


class OrderProduct(models.Model):
    STATUS = (
        ('Mới', 'Mới'),
        ('Chấp Nhận', 'Chấp Nhận'),
        ('Đã hủy', 'Đã hủy'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title


# ── Trạng thái nào đã từng làm hệ thống TRỪ tồn kho (xem order/views.py::payment_success) ──
# Kho chỉ bị trừ khi đơn rời khỏi "Chờ xác nhận". Nếu đơn bị hủy/trả lúc vẫn còn
# "Chờ xác nhận" thì kho chưa từng bị trừ -> không được cộng lại (tránh cộng dư ảo).
STOCK_DEDUCTED_STATUSES = ['Chờ lấy hàng', 'Chờ giao hàng', 'Đã giao hàng']


# ── Trạng thái nào được phép chuyển tới TIẾP THEO từ trạng thái hiện tại ──
# Trước đây dropdown "Đổi sang" hiện TẤT CẢ trạng thái cùng lúc, khiến admin dễ
# bấm nhầm (VD: đơn đang "Chờ xác nhận" lại bấm nhầm sang "Chờ giao hàng", bỏ
# qua bước "Chờ lấy hàng"). Map này giới hạn dropdown + validate ở backend chỉ
# cho phép đi đúng luồng nghiệp vụ tuyến tính.
# - "Đã hủy" chỉ xảy ra do KHÁCH HÀNG tự hủy (không phải admin đổi tay), nên
#   không xuất hiện trong lựa chọn thủ công của admin ở các bước giữa.
# - "Trả hàng" chỉ có ý nghĩa SAU KHI đã giao hàng, nên không xuất hiện ở
#   "Chờ giao hàng".
# - "Đã giao hàng" và "Trả hàng" là trạng thái CUỐI — admin không thể đổi
#   tiếp nữa (xử lý y hệt "Đã hủy": khóa toàn bộ khung cập nhật).
ORDER_STATUS_TRANSITIONS = {
    'Chờ xác nhận':  ['Chờ xác nhận', 'Chờ lấy hàng', 'Đã hủy'],
    'Chờ lấy hàng':  ['Chờ lấy hàng', 'Chờ giao hàng'],
    'Chờ giao hàng': ['Chờ giao hàng', 'Đã giao hàng'],
    'Đã giao hàng':  ['Đã giao hàng'],
    'Trả hàng':      ['Trả hàng'],
    'Đã hủy':        ['Đã hủy'],
}

# Trạng thái CUỐI — khóa hoàn toàn khung "Cập nhật trạng thái" (không dropdown,
# không nút Lưu), giống hệt cách xử lý "Đã hủy".
ORDER_STATUS_LOCKED = ['Đã hủy', 'Đã giao hàng', 'Trả hàng']


def restock_order(order, old_status):
    """
    Hoàn lại tồn kho cho 1 đơn hàng khi đơn chuyển sang 'Đã hủy' hoặc 'Trả hàng'.
    Chỉ hoàn kho nếu old_status cho thấy kho ĐÃ từng bị trừ (tức là đơn đã đi
    qua bước 'Chờ lấy hàng' trở lên), tránh cộng dư tồn kho cho đơn chưa từng
    được xác nhận/trừ kho.

    Gọi hàm này TRƯỚC khi lưu order.status mới, hoặc truyền old_status đã lưu sẵn.
    Idempotent ở mức best-effort: chỉ nên gọi đúng 1 lần tại thời điểm chuyển status.
    """
    if old_status not in STOCK_DEDUCTED_STATUSES:
        return  # Kho chưa từng bị trừ cho đơn này -> không hoàn

    order_products = OrderProduct.objects.filter(order=order).select_related('product')
    for item in order_products:
        if item.product:
            item.product.amount += item.quantity
            item.product.save()


from django.db import models

# Create your models here.
