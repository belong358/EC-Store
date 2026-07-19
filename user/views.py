from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme

# Create your views here.
from order.models import Order, OrderProduct, restock_order
from product.models import Category, Comment
from user.forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from user.models import UserProfile
from order.models import ShopCart
from home.models import Setting


@login_required(login_url='/login')
def index(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    current_user = request.user  # Access User Session information
    profile = UserProfile.objects.get(user_id=current_user.id)
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    totalqty = 0
    for rs in shopcart:
        total += rs.product.price * rs.quantity
        totalqty += rs.quantity
    context = {'category': category, 'setting': setting,
        'profile': profile, 'shopcart': shopcart, "totalqty": totalqty,
               'total': total}
    return render(request, 'user_profile.html', context)


def login_form(request):
    def _safe_next(raw):
        if raw and url_has_allowed_host_and_scheme(raw, allowed_hosts={request.get_host()}):
            return raw
        return '/'

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        next_url = _safe_next(request.POST.get('next'))
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            current_user = request.user
            userprofile, _ = UserProfile.objects.get_or_create(
                user_id=current_user.id,
                defaults={'image': 'images/users/user.png'}
            )
            request.session['userimage'] = userprofile.image.url
            return HttpResponseRedirect(next_url)
        else:
            # Phân biệt tài khoản bị khóa vs sai mật khẩu
            try:
                check_user = User.objects.get(username=username)
                if not check_user.is_active and check_user.check_password(password):
                    messages.warning(request, "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên!")
                else:
                    messages.warning(request, "Lỗi đăng nhập! Sai tên đăng nhập hoặc mật khẩu")
            except User.DoesNotExist:
                messages.warning(request, "Lỗi đăng nhập! Sai tên đăng nhập hoặc mật khẩu")
            next_param = f"?next={next_url}" if next_url != '/' else ''
            return HttpResponseRedirect(f'/login{next_param}')

    category = Category.objects.all()
    next_url = _safe_next(request.GET.get('next'))
    context = {'category': category, 'next': next_url}
    return render(request, 'login_form.html', context)


def signup_form(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()  # completed sign up
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            # Create data in profile table for user
            current_user = request.user
            data = UserProfile()
            data.user_id = current_user.id
            data.image = "images/users/user.png"
            data.save()
            messages.success(request, 'Tài khoản của bạn đã tạo thành công!')
            return HttpResponseRedirect('/')
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect('/signup')

    form = SignUpForm()
    category = Category.objects.all()
    context = {'category': category,
               'form': form,
               }
    return render(request, 'signup_form.html', context)


def logout_func(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required(login_url='/login')
def user_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tài khoản của bạn đã được cập nhật!')
            return HttpResponseRedirect('/user')
    else:
        category = Category.objects.all()
        setting = Setting.objects.get(pk=1)
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)
        context = {
            'category': category,
            'setting': setting,
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, 'user_update.html', context)


@login_required(login_url='/login')  # Check login
def user_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Đổi mật khẩu thành công!')
            return HttpResponseRedirect('/user')
        else:
            messages.error(request, 'Hãy nhập đúng lỗi bên dưới.<br>' + str(form.errors))
            return HttpResponseRedirect('/user/password')
    else:
        category = Category.objects.all()
        setting = Setting.objects.get(pk=1)
        form = PasswordChangeForm(request.user)
        return render(request, 'user_password.html', {'form': form, 'category': category, 'setting': setting})


@login_required(login_url='/login')  # Check login
def user_orders(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    current_user = request.user
    orders = Order.objects.filter(user_id=current_user.id)
    context = {'category': category,
               'setting': setting,
               'orders': orders,
               }
    return render(request, 'user_orders.html', context)


@login_required(login_url='/login')  # Check login
def user_orderdetail(request, id):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=id)
    orderitems = OrderProduct.objects.filter(order_id=id)
    context = {
        'category': category,
        'setting': setting,
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'user_order_detail.html', context)


@login_required(login_url='/login')  # Check login
def user_order_product(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    current_user = request.user
    order_product = OrderProduct.objects.filter(user_id=current_user.id).order_by('-id')
    context = {'category': category,
               'setting': setting,
               'order_product': order_product,
               }
    return render(request, 'user_order_products.html', context)


@login_required(login_url='/login')  # Check login
def user_order_product_detail(request, id, oid):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=oid)
    orderitems = OrderProduct.objects.filter(id=id, user_id=current_user.id)
    context = {
        'category': category,
        'setting': setting,
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'user_order_detail.html', context)


def user_comments(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    current_user = request.user
    comments = Comment.objects.filter(user_id=current_user.id)
    context = {
        'category': category,
        'setting': setting,
        'comments': comments,
    }
    return render(request, 'user_comments.html', context)


@login_required(login_url='/login')  # Check login
def user_deletecomment(request, id):
    current_user = request.user
    Comment.objects.filter(id=id, user_id=current_user.id).delete()
    messages.success(request, 'Xóa bình luận.')
    return HttpResponseRedirect('/user/comments')

@login_required(login_url='/login')
def cancel_order(request, id):
    """Khách hàng hủy đơn — chỉ khi trạng thái là Chờ xác nhận hoặc Chờ lấy hàng."""
    current_user = request.user
    order = get_object_or_404(Order, id=id, user_id=current_user.id)

    if request.method == 'POST':
        if order.status in ['Chờ xác nhận', 'Chờ lấy hàng']:
            restock_order(order, order.status)
            order.status = 'Đã hủy'
            order.save()
            messages.success(request, f'Đơn hàng #{order.code} đã được hủy thành công.')
        else:
            messages.warning(request, 'Không thể hủy đơn hàng ở trạng thái này.')

    return HttpResponseRedirect(f'/user/orderdetail/{id}')


@login_required(login_url='/login')
def return_order(request, id):
    """Khách hàng yêu cầu trả hàng — chỉ khi trạng thái là Đã giao hàng."""
    current_user = request.user
    order = get_object_or_404(Order, id=id, user_id=current_user.id)

    if request.method == 'POST':
        if order.status == 'Đã giao hàng':
            restock_order(order, order.status)
            order.status = 'Trả hàng'
            order.save()
            messages.success(request, f'Yêu cầu trả hàng cho đơn #{order.code} đã được ghi nhận.')
        else:
            messages.warning(request, 'Không thể trả hàng ở trạng thái này.')

    return HttpResponseRedirect(f'/user/orderdetail/{id}')
