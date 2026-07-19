from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.conf import settings
from django.urls import reverse
from django.template.loader import get_template
from django.core.mail import EmailMessage
import stripe
import io
import os
from urllib.parse import urlencode, urlparse
from fpdf import FPDF

from order.models import ShopCart, ShopCartForm, OrderForm, Order, OrderProduct
from home.models import Setting
from product.models import Category, Product
from user.models import UserProfile
from order.vnpay import vnpay
from order.momo import MoMoPayment
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

stripe.api_key = settings.STRIPE_SECRET_KEY


# ════════════════════════════════════════════════════════════════
#  TẠO PDF HÓA ĐƠN (fpdf2 — hỗ trợ tiếng Việt qua font DejaVu Sans)
# ════════════════════════════════════════════════════════════════
def generate_invoice_pdf(order, order_products):
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'pdf')
    font_regular = os.path.join(font_dir, 'DejaVuSans.ttf')
    font_bold    = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', font_regular)
    pdf.add_font('DejaVu', 'B', font_bold)

    # Tiêu đề
    pdf.set_font('DejaVu', 'B', 18)
    pdf.cell(0, 14, 'HÓA ĐƠN MUA HÀNG', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    # Thông tin đơn hàng
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 8, f'Mã đơn hàng: #{order.code}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Ngày: {order.create_at.strftime("%d/%m/%Y %H:%M")}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(35, 8, 'Khách hàng:')
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 8, f'{order.first_name} {order.last_name}', new_x='LMARGIN', new_y='NEXT')

    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(35, 8, 'Địa chỉ:')
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 8, f'{order.address}, {order.city}', new_x='LMARGIN', new_y='NEXT')

    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(35, 8, 'Điện thoại:')
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 8, f'{order.phone}', new_x='LMARGIN', new_y='NEXT')

    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(35, 8, 'Thanh toán:')
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 8, f'{order.payment_method}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # Bảng sản phẩm
    col_w = [90, 25, 35, 40]
    pdf.set_font('DejaVu', 'B', 10.5)
    pdf.set_fill_color(238, 238, 238)
    pdf.cell(col_w[0], 9, 'Sản phẩm', border=1, align='L', fill=True)
    pdf.cell(col_w[1], 9, 'Số lượng', border=1, align='C', fill=True)
    pdf.cell(col_w[2], 9, 'Giá', border=1, align='R', fill=True)
    pdf.cell(col_w[3], 9, 'Tổng', border=1, align='R', fill=True, new_x='LMARGIN', new_y='NEXT')

    pdf.set_font('DejaVu', '', 10.5)
    for item in order_products:
        title = item.product.title
        price = f'{item.price:,.0f} VND'
        amount = f'{item.amount:,.0f} VND'

        # Tự xuống dòng nếu tên sản phẩm dài
        line_h = 7
        n_lines = pdf.multi_cell(col_w[0], line_h, title, border=0, align='L', dry_run=True, output="LINES")
        row_h = line_h * max(len(n_lines), 1)

        x, y = pdf.get_x(), pdf.get_y()
        pdf.multi_cell(col_w[0], line_h, title, border=1, align='L')
        pdf.set_xy(x + col_w[0], y)
        pdf.cell(col_w[1], row_h, str(item.quantity), border=1, align='C')
        pdf.cell(col_w[2], row_h, price, border=1, align='R')
        pdf.cell(col_w[3], row_h, amount, border=1, align='R', new_x='LMARGIN', new_y='NEXT')

    # Tổng cộng
    pdf.set_font('DejaVu', 'B', 12)
    pdf.ln(4)
    pdf.cell(0, 10, f'Tổng cộng: {order.total:,.0f} VND', align='R', new_x='LMARGIN', new_y='NEXT')

    pdf.ln(8)
    pdf.set_font('DejaVu', '', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 6, 'Cảm ơn bạn đã mua hàng tại EleStore!\nMọi thắc mắc vui lòng liên hệ hotline hoặc email hỗ trợ của chúng tôi.')

    return bytes(pdf.output())


def index(request):
    return HttpResponse("Order Page")

def addtoshopcart(request, id):
    url = request.META.get('HTTP_REFERER')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    # ── Chưa đăng nhập: không cho thêm giỏ hàng ──
    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'login_required': True,
                'message': 'Bạn cần đăng nhập để có thể mua hàng',
            }, status=401)
        messages.warning(request, 'Bạn cần đăng nhập để có thể mua hàng')
        login_url = reverse('login_form')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            parsed = urlparse(referer)
            next_path = parsed.path + (f'?{parsed.query}' if parsed.query else '')
        else:
            next_path = request.path
        return HttpResponseRedirect(f'{login_url}?{urlencode({"next": next_path})}')

    current_user = request.user
    product = get_object_or_404(Product, pk=id)
    checkinproduct = ShopCart.objects.filter(product_id=id, user_id=current_user.id)
    if checkinproduct:
        control = 1
    else:
        control = 0
    if request.method == 'POST':
        form = ShopCartForm(request.POST)
        if form.is_valid():
            if control == 1:
                data = ShopCart.objects.get(product_id=id, user_id=current_user.id)
                data.quantity += form.cleaned_data['quantity']
                data.save()
            else:
                data = ShopCart()
                data.user_id = current_user.id
                data.product_id = id
                data.quantity = form.cleaned_data['quantity']
                data.save()
        messages.success(request, "Đã thêm sản phẩm vào giỏ hàng ")
    else:
        if control == 1:
            data = ShopCart.objects.get(product_id=id, user_id=current_user.id)
            data.quantity += 1
            data.save()
        else:
            data = ShopCart()
            data.user_id = current_user.id
            data.product_id = id
            data.quantity = 1
            data.save()
        messages.success(request, "Đã thêm sản phẩm vào giỏ hàng")

    # ── AJAX: trả JSON để cập nhật giỏ hàng không cần reload trang ──
    if is_ajax:
        shopcart = ShopCart.objects.filter(user_id=current_user.id).select_related('product')
        total = 0
        totalqty = 0
        for rs in shopcart:
            if rs.product:
                total += rs.product.final_price * rs.quantity
                totalqty += rs.quantity
        cart_html = render_to_string('cart_dropdown_content.html', {
            'shopcart': shopcart, 'total': total, 'totalqty': totalqty,
        }, request=request)
        return JsonResponse({
            'success': True,
            'totalqty': totalqty,
            'total': total,
            'cart_html': cart_html,
            'message': 'Đã thêm sản phẩm vào giỏ hàng',
        })

    return HttpResponseRedirect(url)

@login_required(login_url='/login')
def shopcart(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id).select_related('product')
    total = 0
    for rs in shopcart:
        if rs.product:
            total += rs.product.final_price * rs.quantity
    context = {'shopcart': shopcart, 'category': category, 'total': total, 'setting': setting}
    return render(request, 'shopcart_products.html', context)

@login_required(login_url='/login')
def deletefromcart(request, id):
    ShopCart.objects.filter(id=id).delete()
    messages.success(request, "Sản phẩm đã xóa khỏi giỏ hàng.")
    return HttpResponseRedirect("/shopcart")

@login_required(login_url='/login')
def update_shopcart(request, id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            shopcart_item = ShopCart.objects.get(id=id, user_id=request.user.id)
            
            if quantity > 0:
                shopcart_item.quantity = quantity
                shopcart_item.save()
                
                # Tính toán lại tổng tiền để trả về cho AJAX
                current_user = request.user
                all_items = ShopCart.objects.filter(user_id=current_user.id)
                total = sum(item.product.final_price * item.quantity for item in all_items)
                
                return JsonResponse({
                    'status': 'success',
                    'amount': shopcart_item.amount, # Thành tiền của item này
                    'total': total,                 # Tổng tiền toàn giỏ hàng
                    'quantity': shopcart_item.quantity
                })
            else:
                shopcart_item.delete()
                # Tính lại tổng sau khi xóa
                all_items = ShopCart.objects.filter(user_id=request.user.id)
                total = sum(item.product.final_price * item.quantity for item in all_items)
                return JsonResponse({
                    'status': 'removed',
                    'total': total
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/shopcart/'))

@login_required(login_url='/login')
def get_checkout_config(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user_id=request.user.id)
        if not order.stripe_payment_id:
            return JsonResponse({'error': 'No payment session found'}, status=404)
        session = stripe.checkout.Session.retrieve(order.stripe_payment_id)
        return JsonResponse({
            'publicKey': settings.STRIPE_PUBLISHABLE_KEY,
            'clientSecret': session.client_secret
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='/login')
def orderproduct(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    if not shopcart:
        messages.warning(request, "Giỏ hàng của bạn đang trống.")
        return HttpResponseRedirect("/shopcart")
    total = 0
    for rs in shopcart:
        total += rs.product.final_price * rs.quantity
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            payment_method = request.POST.get('payment_method')
            
            data = Order()
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.phone = form.cleaned_data['phone']
            data.user_id = current_user.id
            data.total = total
            data.payment_method = payment_method
            data.ip = request.META.get('REMOTE_ADDR')
            ordercode = get_random_string(5).upper()
            data.code = ordercode
            data.status = 'Chờ xác nhận'
            data.save()
            
            for rs in shopcart:
                detail = OrderProduct()
                detail.order_id = data.id
                detail.product_id = rs.product_id
                detail.user_id = current_user.id
                detail.quantity = rs.quantity
                detail.price = rs.product.final_price
                detail.amount = rs.amount
                detail.save()

            if payment_method == 'Stripe':
                line_items = []
                for rs in shopcart:
                    line_items.append({
                        'price_data': {
                            'currency': 'vnd',
                            'product_data': {'name': rs.product.title},
                            'unit_amount': int(rs.product.final_price),
                        },
                        'quantity': rs.quantity,
                    })
                try:
                    checkout_session = stripe.checkout.Session.create(
                        ui_mode='embedded_page',
                        line_items=line_items,
                        mode='payment',
                        return_url=request.build_absolute_uri(reverse('payment_success')) + "?session_id={CHECKOUT_SESSION_ID}",
                        metadata={'order_id': data.id, 'order_code': ordercode}
                    )
                    data.stripe_payment_id = checkout_session.id
                    data.save()
                    return render(request, 'Order_Payment.html', {'order': data, 'category': category, 'setting': setting})
                except Exception as e:
                    messages.error(request, str(e))
                    return HttpResponseRedirect("/order/orderproduct")
            
            elif payment_method == 'VNPay':
                vnp = vnpay()
                vnp.request_data['vnp_Version'] = '2.1.0'
                vnp.request_data['vnp_Command'] = 'pay'
                vnp.request_data['vnp_TmnCode'] = settings.VNP_TMN_CODE
                vnp.request_data['vnp_Amount'] = int(total * 100)
                vnp.request_data['vnp_CurrCode'] = 'VND'
                vnp.request_data['vnp_TxnRef'] = ordercode
                vnp.request_data['vnp_OrderInfo'] = f"Thanh toan don hang {ordercode}"
                vnp.request_data['vnp_OrderType'] = 'billpayment'
                vnp.request_data['vnp_Locale'] = 'vn'
                vnp.request_data['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
                vnp.request_data['vnp_ReturnUrl'] = settings.VNP_RETURN_URL
                
                # Tranh loi IP IPv6 ::1 tren local
                vnp_ip = request.META.get('REMOTE_ADDR')
                if vnp_ip == '::1':
                    vnp_ip = '127.0.0.1'
                vnp.request_data['vnp_IpAddr'] = vnp_ip
                
                vnpay_payment_url = vnp.get_payment_url(settings.VNP_URL, settings.VNP_HASH_SECRET)
                return render(request, 'VNPay_Redirect.html', {
                    'order': data,
                    'category': category,
                    'setting': setting,
                    'vnpay_payment_url': vnpay_payment_url,
                })

            elif payment_method == 'MoMo':
                momo = MoMoPayment(
                    settings.MOMO_PARTNER_CODE,
                    settings.MOMO_ACCESS_KEY,
                    settings.MOMO_SECRET_KEY,
                    settings.MOMO_ENDPOINT
                )
                
                redirect_url = request.build_absolute_uri(reverse('momo_return'))
                ipn_url = request.build_absolute_uri(reverse('momo_ipn'))
                
                # MoMo rất nhạy cảm với ký tự đặc biệt trong orderInfo khi băm chữ ký
                order_info_clean = f"EleStore_Order_{ordercode}"
                
                response = momo.create_payment(
                    order_id=ordercode,
                    amount=int(total), # Đảm bảo là số nguyên
                    order_info=order_info_clean,
                    redirect_url=redirect_url,
                    ipn_url=ipn_url
                )
                
                if response.get('resultCode') == 0:
                    return render(request, 'Momo_QR_Payment.html', {
                        'order': data, 
                        'category': category,
                        'setting': setting,
                        'payUrl': response.get('payUrl')
                    })
                else:
                    messages.error(request, f"Lỗi MoMo: {response.get('message')}")
                    return HttpResponseRedirect("/order/orderproduct")

            else: # COD
                # Thanh toán khi nhận hàng, hoàn tất luôn hoặc chờ xác nhận
                messages.success(request, "Đơn hàng của bạn đã được tiếp nhận (COD).")
                return HttpResponseRedirect(reverse('payment_success') + f"?order_id={data.id}&method=COD")
                
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect("/order/orderproduct")
    
    form = OrderForm()
    profile = UserProfile.objects.filter(user_id=current_user.id).first()
    context = {'shopcart': shopcart, 'category': category, 'total': total, 'form': form, 'profile': profile, 'setting': setting}
    return render(request, 'Order_Form.html', context)

def vnpay_return(request):
    inputData = request.GET.dict()
    vnp = vnpay()
    vnp.response_data = inputData
    order_code = inputData.get('vnp_TxnRef')
    vnp_ResponseCode = inputData.get('vnp_ResponseCode')
    
    if vnp.validate_response(settings.VNP_HASH_SECRET):
        if vnp_ResponseCode == "00":
            try:
                order = Order.objects.get(code=order_code)
                # Sử dụng reverse để lấy URL chính xác của payment_success
                success_url = reverse('payment_success')
                return HttpResponseRedirect(f"{success_url}?order_id={order.id}&method=VNPay")
            except Order.DoesNotExist:
                messages.error(request, "Không tìm thấy đơn hàng sau khi thanh toán.")
                return HttpResponseRedirect('/shopcart/')
        else:
            messages.error(request, f"Thanh toán VNPay không thành công. Mã lỗi: {vnp_ResponseCode}")
            return HttpResponseRedirect('/shopcart/')
    else:
        messages.error(request, "Sai chữ ký bảo mật VNPay.")
        return HttpResponseRedirect('/shopcart/')

def confirm_order_paid(order):
    """
    Xử lý 1 đơn hàng vừa được xác nhận thanh toán/tiếp nhận thành công:
    trừ tồn kho, gửi email kèm hóa đơn PDF, xóa giỏ hàng của khách.

    Idempotent: chỉ thực thi nếu order.status hiện đang là 'Chờ xác nhận'
    (trạng thái khởi tạo, chưa từng bị trừ kho — xem STOCK_DEDUCTED_STATUSES
    trong order/models.py). Gọi lại hàm này nhiều lần trên cùng 1 đơn đã xử lý
    rồi sẽ không trừ kho/gửi mail thêm lần nữa — quan trọng vì VNPay/MoMo có
    thể trigger việc xác nhận từ cả luồng redirect (return URL) lẫn webhook (IPN)
    gần như đồng thời.

    Trả về True nếu vừa xử lý xong (lần đầu), False nếu đơn đã được xử lý từ trước.
    """
    if order.status != 'Chờ xác nhận':
        return False

    order.status = 'Chờ lấy hàng'
    order.save()

    order_products = OrderProduct.objects.filter(order_id=order.id)
    for rs in order_products:
        product = Product.objects.get(id=rs.product_id)
        product.amount -= rs.quantity
        product.save()

    try:
        pdf = generate_invoice_pdf(order, order_products)
        if pdf:
            subject = f'Hóa đơn EleStore - Đơn hàng #{order.code}'
            message = f'Chào {order.first_name},\n\nCảm ơn bạn đã mua hàng tại EleStore. Đơn hàng #{order.code} của bạn đã được xác nhận thành công ({order.payment_method}).\n\nVui lòng xem chi tiết hóa đơn trong tệp đính kèm.'
            email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [order.user.email])
            email.attach(f'Invoice_{order.code}.pdf', pdf, 'application/pdf')
            email.send()
    except Exception as mail_err:
        print(f"Lỗi gửi mail: {mail_err}")

    ShopCart.objects.filter(user_id=order.user_id).delete()

    return True


def payment_success(request):
    session_id = request.GET.get('session_id')
    order_id = request.GET.get('order_id')
    method = request.GET.get('method')
    
    order = None
    if session_id: # Stripe
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                order_id = session.metadata.order_id
                order = Order.objects.get(id=order_id)
        except Exception as e:
            messages.error(request, f"Lỗi xác thực Stripe: {str(e)}")
            return HttpResponseRedirect('/')
    elif order_id: # COD, VNPay hoặc MoMo
        order = Order.objects.get(id=order_id)

    if order:
        if order.status == 'Chờ xác nhận':
            confirm_order_paid(order)

            if 'cart_items' in request.session:
                request.session['cart_items'] = 0

            category = Category.objects.all()
            setting = Setting.objects.get(pk=1)
            msg = "Thanh toán thành công!" if order.payment_method != 'COD' else "Đặt hàng thành công!"
            messages.success(request, f"{msg} Hóa đơn đã được gửi vào email của bạn.")
            return render(request, 'Order_Completed.html', {'ordercode': order.code, 'category': category, 'setting': setting})

        elif order.status in ('Chờ lấy hàng', 'Chờ giao hàng', 'Đã giao hàng'):
            # Đơn đã được xác nhận từ trước (ví dụ MoMo IPN xử lý nhanh hơn lượt
            # redirect của người dùng) -> chỉ hiển thị lại trang hoàn tất, không
            # trừ kho/gửi mail thêm lần nữa.
            category = Category.objects.all()
            setting = Setting.objects.get(pk=1)
            return render(request, 'Order_Completed.html', {'ordercode': order.code, 'category': category, 'setting': setting})

    return HttpResponseRedirect('/')

def payment_cancel(request):
    messages.warning(request, "Giao dịch đã bị hủy.")
    return HttpResponseRedirect('/shopcart')

def momo_return(request):
    data = request.GET.dict()
    momo = MoMoPayment(
        settings.MOMO_PARTNER_CODE,
        settings.MOMO_ACCESS_KEY,
        settings.MOMO_SECRET_KEY,
        settings.MOMO_ENDPOINT
    )
    
    if momo.validate_signature(data):
        result_code = data.get('resultCode')
        order_code = data.get('orderId')
        
        if result_code == '0': # Thành công
            try:
                order = Order.objects.get(code=order_code)
                success_url = reverse('payment_success')
                return HttpResponseRedirect(f"{success_url}?order_id={order.id}&method=MoMo")
            except Order.DoesNotExist:
                messages.error(request, "Không tìm thấy đơn hàng MoMo.")
                return HttpResponseRedirect('/shopcart/')
        else:
            messages.error(request, f"Thanh toán MoMo thất bại: {data.get('message')}")
            return HttpResponseRedirect('/shopcart/')
    else:
        messages.error(request, "Sai chữ ký bảo mật MoMo.")
        return HttpResponseRedirect('/shopcart/')

@csrf_exempt
def momo_ipn(request):
    # MoMo gọi IPN bằng POST JSON
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        momo = MoMoPayment(
            settings.MOMO_PARTNER_CODE,
            settings.MOMO_ACCESS_KEY,
            settings.MOMO_SECRET_KEY,
            settings.MOMO_ENDPOINT
        )
        
        if momo.validate_signature(data):
            result_code = data.get('resultCode')
            order_code = data.get('orderId')
            
            if result_code == 0:
                try:
                    order = Order.objects.get(code=order_code)
                    # Dùng chung logic với payment_success: tự kiểm tra idempotent,
                    # tự trừ kho + gửi hóa đơn nếu đây là lần xác nhận đầu tiên cho đơn này.
                    confirm_order_paid(order)
                except Order.DoesNotExist:
                    pass
            
            return JsonResponse({"message": "Received"}, status=200)
            
    return JsonResponse({"message": "Invalid request"}, status=400)

@login_required(login_url='/login')
def check_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user_id=request.user.id)
        return JsonResponse({'status': order.status})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)