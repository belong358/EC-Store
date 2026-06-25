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
        return (self.product.price)

    @property
    def amount(self):
        return (self.quantity * self.product.price)

    @property
    def varamount(self):
        return (self.quantity * self.product.price)

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
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'address', 'phone', 'city', 'country']


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


from django.db import models

# Create your models here.
