from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index,name='index'),
    path('addtoshopcart/<int:id>', views.addtoshopcart, name='addtoshopcart'),
    path('deletefromcart/<int:id>', views.deletefromcart, name='deletefromcart'),
    path('update_shopcart/<int:id>', views.update_shopcart, name='update_shopcart'),
    path('orderproduct/', views.orderproduct, name='orderproduct'),
    path('get-checkout-config/<int:order_id>/', views.get_checkout_config, name='get_checkout_config'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('vnpay_return/', views.vnpay_return, name='vnpay_return'),
    path('vnpay_return', views.vnpay_return), # Fallback cho VNPay redirect không dấu /
    path('momo_return/', views.momo_return, name='momo_return'),
    path('momo_ipn/', views.momo_ipn, name='momo_ipn'),
    path('check_order_status/<int:order_id>/', views.check_order_status, name='check_order_status'),
]