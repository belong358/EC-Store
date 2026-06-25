import json
from functools import wraps
from datetime import datetime, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages as flash
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify

from order.models import Order, OrderProduct
from product.models import Product, Category, Comment
from home.models import ContactMessage, Banner


# ── Shared context (sidebar badges) ──────────────────────────────
def _ctx(request):
    return {
        'pending_orders': Order.objects.filter(status='Chờ xác nhận').count(),
        'new_messages':   ContactMessage.objects.filter(status='New').count(),
        'notify_orders':  Order.objects.select_related('user')
                               .filter(status='Chờ xác nhận')
                               .order_by('-create_at')[:5],
    }


# ── Quyền: chỉ Quản trị viên (superuser) mới được vào ────────────
# Khác với @staff_member_required: nếu đã đăng nhập nhưng không phải
# superuser thì báo "không có quyền" và đưa về trang Sản phẩm,
# thay vì đá lại trang login (tránh vòng lặp redirect cho Nhân viên).
def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/dashboard-login/?next={request.path}')
        if not request.user.is_superuser:
            flash.warning(request, 'Bạn không có quyền truy cập mục này. Chỉ Quản trị viên mới được phép.')
            return redirect('dashboard_products')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ════════════════════════════════════════════════════════════════
#  DASHBOARD LOGIN (riêng biệt, tách khỏi /login/ của khách hàng)
# ════════════════════════════════════════════════════════════════
def dashboard_login(request):
    raw_next = request.POST.get('next') or request.GET.get('next') or ''
    next_url = raw_next if raw_next and url_has_allowed_host_and_scheme(raw_next, allowed_hosts={request.get_host()}) else '/dashboard/'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                auth_login(request, user)
                return redirect(next_url)
            else:
                flash.warning(request, 'Tài khoản này không có quyền truy cập trang quản trị.')
        else:
            flash.warning(request, 'Sai tên đăng nhập hoặc mật khẩu.')
    elif request.user.is_authenticated:
        # Vào trang login bằng GET trong khi đã có sẵn 1 phiên đăng nhập
        if request.user.is_staff:
            return redirect(next_url)
        flash.warning(request, 'Tài khoản hiện tại không có quyền truy cập trang quản trị. Vui lòng đăng nhập bằng tài khoản quản trị viên.')

    return render(request, 'dashboard_login.html', {'next': next_url})


def dashboard_logout(request):
    auth_logout(request)
    return redirect('/dashboard-login/')


@staff_member_required(login_url='/dashboard-login/')
def dashboard(request):
    today = timezone.now()

    total_revenue   = Order.objects.filter(status='Đã giao hàng').aggregate(t=Sum('total'))['t'] or 0
    total_orders    = Order.objects.count()
    pending_orders  = Order.objects.filter(status='Chờ xác nhận').count()
    total_products  = Product.objects.filter(status='True').count()
    new_users_month = User.objects.filter(date_joined__month=today.month, date_joined__year=today.year).count()
    new_messages    = ContactMessage.objects.filter(status='New').count()

    # Revenue chart — last 6 months
    six_ago = today - timedelta(days=180)
    rev_qs  = (Order.objects
               .filter(status='Đã giao hàng', create_at__gte=six_ago)
               .annotate(month=TruncMonth('create_at'))
               .values('month').annotate(total=Sum('total')).order_by('month'))
    MONTHS  = ['','Th1','Th2','Th3','Th4','Th5','Th6','Th7','Th8','Th9','Th10','Th11','Th12']
    chart_labels = [MONTHS[r['month'].month] + f"/{r['month'].year}" for r in rev_qs]
    chart_data   = [float(r['total']) for r in rev_qs]

    # Status donut
    st_qs        = Order.objects.values('status').annotate(count=Count('id')).order_by('-count')
    status_labels = [s['status'] for s in st_qs]
    status_data   = [s['count']  for s in st_qs]

    recent_orders = Order.objects.select_related('user').order_by('-create_at')[:8]
    top_products  = (OrderProduct.objects
                     .values('product__id','product__title','product__image','product__price')
                     .annotate(total_sold=Sum('quantity'), revenue=Sum('amount'))
                     .order_by('-total_sold')[:5])
    new_users       = User.objects.order_by('-date_joined')[:5]
    recent_messages = ContactMessage.objects.filter(status='New').order_by('-create_at')[:5]

    ctx = _ctx(request)
    ctx.update(dict(
        total_revenue=total_revenue, total_orders=total_orders,
        pending_orders=pending_orders, total_products=total_products,
        new_users_month=new_users_month, new_messages=new_messages,
        chart_labels=json.dumps(chart_labels), chart_data=json.dumps(chart_data),
        status_labels=json.dumps(status_labels), status_data=json.dumps(status_data),
        recent_orders=recent_orders, top_products=top_products,
        new_users=new_users, recent_messages=recent_messages, today=today,
    ))
    return render(request, 'dashboard.html', ctx)


# ════════════════════════════════════════════════════════════════
#  ORDERS
# ════════════════════════════════════════════════════════════════
@staff_member_required(login_url='/dashboard-login/')
def dashboard_orders(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').order_by('-create_at')
    if status_filter:
        orders = orders.filter(status=status_filter)

    ctx = _ctx(request)
    ctx.update({'orders': orders, 'status_filter': status_filter, 'status_choices': Order.STATUS})
    return render(request, 'dashboard_orders.html', ctx)


@staff_member_required(login_url='/dashboard-login/')
def dashboard_order_detail(request, order_id):
    order         = get_object_or_404(Order, id=order_id)
    order_products = OrderProduct.objects.filter(order=order).select_related('product')

    if request.method == 'POST':
        if order.status == 'Đã hủy':
            flash.warning(request, f'Đơn hàng #{order.code} đã bị hủy, không thể thay đổi trạng thái.')
        else:
            new_status = request.POST.get('status')
            if new_status:
                order.status = new_status
                order.save()
                flash.success(request, f'Đã cập nhật trạng thái đơn hàng #{order.code}')
        return redirect('dashboard_orders')

    ctx = _ctx(request)
    ctx.update({'order': order, 'order_products': order_products, 'status_choices': Order.STATUS})
    return render(request, 'dashboard_order_detail.html', ctx)


# ════════════════════════════════════════════════════════════════
#  PRODUCTS
# ════════════════════════════════════════════════════════════════
@staff_member_required(login_url='/dashboard-login/')
def dashboard_products(request):
    from django.core.paginator import Paginator
    q        = request.GET.get('q', '')
    products = Product.objects.select_related('category').order_by('-create_at')
    if q:
        products = products.filter(title__icontains=q)
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    ctx = _ctx(request)
    ctx.update({'products': products_page, 'q': q})
    return render(request, 'dashboard_products.html', ctx)


def _save_product(request, product=None):
    """Shared logic for add & edit product."""
    title   = request.POST.get('title', '')
    slug    = slugify(title)
    base    = slug
    i       = 1
    qs      = Product.objects.filter(slug=slug)
    if product:
        qs = qs.exclude(pk=product.pk)
    while qs.exists():
        slug = f"{base}-{i}"; i += 1
        qs   = Product.objects.filter(slug=slug)
        if product:
            qs = qs.exclude(pk=product.pk)

    if not product:
        product = Product()

    product.title       = title
    product.keywords    = request.POST.get('keywords', '')
    product.description = request.POST.get('description', '')
    product.price       = request.POST.get('price', 0)
    product.promotion   = request.POST.get('promotion', 0)
    product.amount      = request.POST.get('amount', 0)
    product.minamount   = request.POST.get('minamount', 3)
    product.variant     = request.POST.get('variant', 'None')
    product.detail      = request.POST.get('detail', '')
    product.slug        = slug
    product.status      = request.POST.get('status', 'True')
    product.category_id = request.POST.get('category')

    if 'image' in request.FILES and request.FILES['image']:
        product.image = request.FILES['image']

    product.save()
    return product


@staff_member_required(login_url='/dashboard-login/')
def dashboard_product_add(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        p = _save_product(request)
        flash.success(request, f'Đã thêm sản phẩm "{p.title}"')
        return redirect('dashboard_products')

    ctx = _ctx(request)
    ctx.update({'categories': categories, 'product': None, 'page_title': 'Thêm sản phẩm'})
    return render(request, 'dashboard_product_form.html', ctx)


@staff_member_required(login_url='/dashboard-login/')
def dashboard_product_edit(request, product_id):
    product    = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        _save_product(request, product)
        flash.success(request, f'Đã cập nhật sản phẩm "{product.title}"')
        return redirect('dashboard_products')

    ctx = _ctx(request)
    ctx.update({'categories': categories, 'product': product, 'page_title': 'Sửa sản phẩm'})
    return render(request, 'dashboard_product_form.html', ctx)


@staff_member_required(login_url='/dashboard-login/')
def dashboard_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        name = product.title
        product.delete()
        flash.success(request, f'Đã xóa sản phẩm "{name}"')
    return redirect('dashboard_products')


# ════════════════════════════════════════════════════════════════
#  USERS
# ════════════════════════════════════════════════════════════════
@staff_member_required(login_url='/dashboard-login/')
def dashboard_users(request):
    from django.core.paginator import Paginator
    q     = request.GET.get('q', '')
    users = User.objects.order_by('-date_joined')
    if q:
        users = users.filter(username__icontains=q) | User.objects.filter(email__icontains=q)
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    ctx = _ctx(request)
    ctx.update({'users': users_page, 'q': q})
    return render(request, 'dashboard_users.html', ctx)


# ════════════════════════════════════════════════════════════════
#  MESSAGES
# ════════════════════════════════════════════════════════════════
@staff_member_required(login_url='/dashboard-login/')
def dashboard_messages_list(request):
    status_filter = request.GET.get('status', '')
    msgs          = ContactMessage.objects.order_by('-create_at')
    if status_filter:
        msgs = msgs.filter(status=status_filter)

    ctx = _ctx(request)
    ctx.update({
        'msgs': msgs,
        'status_filter': status_filter,
        'status_choices': ContactMessage.STATUS,
    })
    return render(request, 'dashboard_messages.html', ctx)


@staff_member_required(login_url='/dashboard-login/')
def dashboard_message_update(request, msg_id):
    msg = get_object_or_404(ContactMessage, id=msg_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            msg.status = new_status
            msg.save()
        flash.success(request, 'Đã cập nhật trạng thái tin nhắn')
    return redirect('dashboard_messages')


# ════════════════════════════════════════════════════════════════
#  BANNERS
# ════════════════════════════════════════════════════════════════
def _parse_dt(value):
    """Parse datetime-local input (YYYY-MM-DDTHH:MM) → aware datetime."""
    if not value:
        return timezone.now()
    try:
        naive = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        return timezone.make_aware(naive)
    except ValueError:
        return timezone.now()


@staff_member_required(login_url='/dashboard-login/')
def dashboard_banners(request):
    banners = Banner.objects.order_by('-create_at')
    ctx     = _ctx(request)
    ctx.update({'banners': banners})
    return render(request, 'dashboard_banners.html', ctx)


@staff_member_required(login_url='/dashboard-login/')
def dashboard_banner_add(request):
    if request.method == 'POST':
        banner = Banner(
            title       = request.POST.get('title', ''),
            description = request.POST.get('description', ''),
            link        = request.POST.get('link', ''),
            start_at    = _parse_dt(request.POST.get('start_at')),
            end_at      = _parse_dt(request.POST.get('end_at')),
            status      = request.POST.get('status', 'True'),
        )
        if 'image' in request.FILES and request.FILES['image']:
            banner.image = request.FILES['image']
        banner.save()
        flash.success(request, f'Đã thêm banner "{banner.title}"')
        return redirect('dashboard_banners')

    ctx = _ctx(request)
    ctx.update({'banner': None, 'page_title': 'Thêm banner'})
    return render(request, 'dashboard_banner_form.html', ctx)


@staff_member_required(login_url='/dashboard-login/')
def dashboard_banner_edit(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    if request.method == 'POST':
        banner.title       = request.POST.get('title', banner.title)
        banner.description = request.POST.get('description', '')
        banner.link        = request.POST.get('link', '')
        banner.start_at    = _parse_dt(request.POST.get('start_at'))
        banner.end_at      = _parse_dt(request.POST.get('end_at'))
        banner.status      = request.POST.get('status', 'True')
        if 'image' in request.FILES and request.FILES['image']:
            banner.image = request.FILES['image']
        banner.save()
        flash.success(request, f'Đã cập nhật banner "{banner.title}"')
        return redirect('dashboard_banners')

    ctx = _ctx(request)
    ctx.update({
        'banner': banner,
        'page_title': 'Sửa banner',
        'start_at_fmt': banner.start_at.strftime('%Y-%m-%dT%H:%M') if banner.start_at else '',
        'end_at_fmt':   banner.end_at.strftime('%Y-%m-%dT%H:%M')   if banner.end_at   else '',
    })
    return render(request, 'dashboard_banner_form.html', ctx)


@staff_member_required(login_url='/dashboard-login/')
def dashboard_banner_delete(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    if request.method == 'POST':
        name = banner.title
        banner.delete()
        flash.success(request, f'Đã xóa banner "{name}"')
    return redirect('dashboard_banners')


# ════════════════════════════════════════════════════════════════
#  REVIEWS — đánh giá sản phẩm từ khách hàng
# ════════════════════════════════════════════════════════════════
@staff_member_required(login_url='/dashboard-login/')
def dashboard_reviews(request):
    q            = request.GET.get('q', '').strip()
    rate_filter  = request.GET.get('rate', '')
    reviews      = Comment.objects.select_related('user', 'product').order_by('-create_at')

    if q:
        reviews = reviews.filter(
            Q(comment__icontains=q) |
            Q(product__title__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q)
        )
    if rate_filter:
        reviews = reviews.filter(rate=rate_filter)

    paginator    = Paginator(reviews, 20)
    page_number  = request.GET.get('page')
    reviews_page = paginator.get_page(page_number)

    ctx = _ctx(request)
    ctx.update({
        'reviews': reviews_page,
        'q': q,
        'rate_filter': rate_filter,
    })
    return render(request, 'dashboard_reviews.html', ctx)


@staff_member_required(login_url='/dashboard-login/')
def dashboard_review_delete(request, review_id):
    review = get_object_or_404(Comment, id=review_id)
    if request.method == 'POST':
        product_name = review.product.title
        review.delete()
        flash.success(request, f'Đã xóa đánh giá sản phẩm "{product_name}"')
    return redirect('dashboard_reviews')


# ════════════════════════════════════════════════════════════════
#  USERS — extended (chi tiết, khóa, phân quyền, xóa)
# ════════════════════════════════════════════════════════════════
@staff_member_required(login_url='/dashboard-login/')
def dashboard_user_detail(request, user_id):
    target = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=target).order_by('-create_at')
    total_spent = orders.filter(status='Đã giao hàng').aggregate(t=Sum('total'))['t'] or 0
    ctx = _ctx(request)
    ctx.update({'target': target, 'orders': orders, 'total_spent': total_spent})
    return render(request, 'dashboard_user_detail.html', ctx)


@staff_member_required(login_url='/dashboard-login/')
def dashboard_user_toggle_active(request, user_id):
    if request.method == 'POST':
        target = get_object_or_404(User, id=user_id)
        if target == request.user:
            flash.error(request, 'Không thể tự khóa tài khoản của mình!')
        elif target.is_superuser:
            flash.error(request, 'Không thể khóa tài khoản Superuser!')
        else:
            target.is_active = not target.is_active
            target.save()
            status = 'mở khóa' if target.is_active else 'khóa'
            flash.success(request, f'Đã {status} tài khoản {target.username}')
    return redirect('dashboard_users')


@superuser_required
def dashboard_user_toggle_staff(request, user_id):
    if request.method == 'POST':
        target = get_object_or_404(User, id=user_id)
        if target == request.user:
            flash.error(request, 'Không thể thay đổi quyền của chính mình!')
        elif target.is_superuser:
            flash.error(request, 'Không thể thay đổi quyền Superuser!')
        else:
            target.is_staff = not target.is_staff
            target.save()
            action = 'cấp' if target.is_staff else 'thu hồi'
            flash.success(request, f'Đã {action} quyền Staff cho {target.username}')
    return redirect('dashboard_users')


@staff_member_required(login_url='/dashboard-login/')
def dashboard_user_delete(request, user_id):
    if request.method == 'POST':
        target = get_object_or_404(User, id=user_id)
        if target == request.user:
            flash.error(request, 'Không thể xóa tài khoản của chính mình!')
        elif target.is_superuser:
            flash.error(request, 'Không thể xóa tài khoản Superuser!')
        else:
            username = target.username
            target.delete()
            flash.success(request, f'Đã xóa tài khoản {username}')
    return redirect('dashboard_users')


@superuser_required
def dashboard_user_set_role(request, user_id):
    if request.method == 'POST':
        target = get_object_or_404(User, id=user_id)
        if target == request.user:
            flash.error(request, 'Không thể thay đổi quyền của chính mình!')
            return redirect('dashboard_users')
        role = request.POST.get('role')
        if role == 'user':
            target.is_staff = False
            target.is_superuser = False
            label = 'Khách hàng'
        elif role == 'staff':
            target.is_staff = True
            target.is_superuser = False
            label = 'Nhân viên'
        elif role == 'admin':
            target.is_staff = True
            target.is_superuser = True
            label = 'Quản trị viên'
        else:
            flash.error(request, 'Quyền không hợp lệ!')
            return redirect('dashboard_users')
        target.save()
        flash.success(request, f'Đã đổi quyền {target.username} thành {label}')
    return redirect('dashboard_users')


@staff_member_required(login_url='/dashboard-login/')
def dashboard_message_delete(request, msg_id):
    if request.method == 'POST':
        msg = get_object_or_404(ContactMessage, id=msg_id)
        msg.delete()
        flash.success(request, 'Đã xóa tin nhắn thành công!')
    return redirect('dashboard_messages')


@staff_member_required(login_url='/dashboard-login/')
def dashboard_orders_reset(request):
    """Xóa toàn bộ đơn hàng — chỉ chấp nhận POST."""
    if request.method == 'POST':
        count = Order.objects.count()
        OrderProduct.objects.all().delete()
        Order.objects.all().delete()
        flash.success(request, f'Đã xóa {count} đơn hàng. Dữ liệu đã được reset về 0.')
    return redirect('dashboard_orders')
