from order.models import ShopCart
from home.models import Setting


def cart_info(request):
    """
    Context processor: cung cấp thông tin giỏ hàng (shopcart, total, totalqty)
    cho TẤT CẢ template, thay cho việc copy-paste đoạn tính giỏ hàng
    ở 4 view khác nhau (index, category_products, search, product_detail).

    Dùng select_related('product') để tránh N+1 query khi truy cập rs.product.
    """
    user = request.user
    if user.is_authenticated:
        shopcart = ShopCart.objects.filter(user_id=user.id).select_related('product')
    else:
        shopcart = ShopCart.objects.none()

    total = 0
    totalqty = 0
    for rs in shopcart:
        if rs.product:
            total += rs.product.final_price * rs.quantity
            totalqty += rs.quantity

    return {
        'shopcart': shopcart,
        'total': total,
        'totalqty': totalqty,
    }


def site_settings(request):
    """
    Context processor: cung cấp 'setting' (SĐT, email, địa chỉ, mạng xã hội...)
    cho TẤT CẢ template (header, footer...) — phòng trường hợp 1 view nào đó
    quên truyền 'setting' vào context (như từng xảy ra ở trang /shopcart/).
    """
    return {'setting': Setting.objects.filter(pk=1).first()}
