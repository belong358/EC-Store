import json

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.shortcuts import render, get_object_or_404

from home.forms import SearchForm
from django.utils import timezone
from home.models import Setting, ContactForm, ContactMessage, Banner
from product.models import Category, Product, Images, Comment
from order.models import OrderProduct
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse

import random

def get_random_products(queryset, n):
    """Lấy ngẫu nhiên n sản phẩm từ queryset, nhanh hơn order_by('?')."""
    ids = list(queryset.values_list('id', flat=True))
    random_ids = random.sample(ids, min(n, len(ids)))
    return Product.objects.filter(id__in=random_ids)
# Phần lấy data trong database và hiển thị ra trang chủ
def index(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)

    # Lấy Banner Carousel
    now = timezone.now()
    banners = Banner.objects.filter(
        status='True',
        start_at__lte=now,
        end_at__gte=now
    ).order_by('-id')

    category_slide = Category.objects.all().order_by('-id')[:3]
    products_slider = Product.objects.all().order_by('-id')[:3]

    # Lấy các sản phẩm theo category_slug
    products_latest = get_random_products(
        Product.objects.filter(Q(category__slug='laptop-asus') | Q(category__slug='laptop-lenovo') | Q(category__slug='laptop-acer')),
        6
    )
    pk_latest = get_random_products(
        Product.objects.filter(Q(category__slug='chut') | Q(category__slug='ban-phim') | Q(category__slug='tai-nghe')),
        6
    )
    lk_latest = get_random_products(
        Product.objects.filter(
            Q(category__slug='cpu') | Q(category__slug='mainboard') | Q(category__slug='psu') |
            Q(category__slug='vga') | Q(category__slug='ram') | Q(category__slug='cng')
        ),
        6
    )
    products_picked = get_random_products(Product.objects.all(), 5)
    products_chunks = [products_latest[i:i + 3] for i in range(0, len(products_latest), 3)]
    pk_chunks = [pk_latest[i:i + 3] for i in range(0, len(pk_latest ), 3)]
    lk_chunks = [lk_latest[i:i + 3] for i in range(0, len(lk_latest), 3)]

    page = 'home'
    context = {
        'setting': setting, 'page': page, 'category': category,
        'products_slider': products_slider,
        'category_slide': category_slide,
        'banners': banners,
        'products_latest': products_latest,
        'products_picked': products_picked,
        'products_chunks': products_chunks, 'pk_chunks': pk_chunks, 'lk_chunks': lk_chunks,
    }
    return render(request, 'index.html', context)


def privacy_policy(request):
    setting = Setting.objects.get(pk=1)
    category = Category.objects.all()
    context = {'setting': setting, 'category': category}
    return render(request, 'privacy_policy.html', context)


def aboutus(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting, 'category': category}
    return render(request, 'about.html', context)


def contact(request):
    category = Category.objects.all()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = ContactMessage()
            data.name = form.cleaned_data['name']
            data.email = form.cleaned_data['email']
            data.subject = form.cleaned_data['subject']
            data.message = form.cleaned_data['message']
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            messages.success(request, "Tin của bạn đã được gửi.Cảm ơn về phản hồi của bạn.")
            return HttpResponseRedirect('/contact')
    setting = Setting.objects.get(pk=1)
    form = ContactForm
    context = {'setting': setting, 'form': form, 'category': category}
    return render(request, 'contact.html', context)


# ════════════════════════════════════════════════════════════════
#  CATEGORY — danh sách sản phẩm theo danh mục (redesign GearVN style)
# ════════════════════════════════════════════════════════════════
def category_products(request, id, slug):
    setting = Setting.objects.get(pk=1)
    category = Category.objects.all()  # dùng cho menu nav (recursetree)

    category_all = get_object_or_404(Category, id=id, slug=slug)
    categories_all = category_all.get_descendants(include_self=True)
    products_fil = Product.objects.filter(category__in=categories_all, status='True')

    # ── Lọc theo khoảng giá ──
    price_range = request.GET.get('price', '')
    if price_range == 'under10':
        products_fil = products_fil.filter(price__lt=10000000)
    elif price_range == '10-20':
        products_fil = products_fil.filter(price__gte=10000000, price__lt=20000000)
    elif price_range == '20-30':
        products_fil = products_fil.filter(price__gte=20000000, price__lt=30000000)
    elif price_range == 'over30':
        products_fil = products_fil.filter(price__gte=30000000)

    # ── Sắp xếp ──
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products_fil = products_fil.order_by('price')
    elif sort == 'price_desc':
        products_fil = products_fil.order_by('-price')
    elif sort == 'name':
        products_fil = products_fil.order_by('title')
    else:
        sort = 'newest'
        products_fil = products_fil.order_by('-id')

    # ── Phân trang ──
    paginator = Paginator(products_fil, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # ── Cây danh mục (cha + con) để hiển thị sidebar lọc, gọn & đúng cấp ──
    top_categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')

    # Xác định danh mục cha hiện tại (để highlight đúng nhánh trong sidebar)
    current_parent_id = category_all.parent_id if category_all.parent_id else category_all.id

    # Chuỗi query string phụ (sort/price) để giữ lại khi chuyển trang phân trang
    qs_extra = f"&sort={sort}" + (f"&price={price_range}" if price_range else "")

    context = {
        'category': category,
        'category_all': category_all,
        'top_categories': top_categories,
        'current_parent_id': current_parent_id,
        'products_fil': products_page,
        'total_count': paginator.count,
        'setting': setting,
        'sort': sort,
        'price_range': price_range,
        'qs_extra': qs_extra,
    }
    return render(request, 'category_product.html', context)


def search(request):
    products_mo = get_random_products(Product.objects.all(), 3)
    setting = Setting.objects.get(pk=1)

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            products = Product.objects.filter(title__icontains=query)
            category = Category.objects.all()
            context = {
                'products': products, 'query': query,
                'category': category, 'products_mo': products_mo, 'setting': setting,
            }
            return render(request, 'search_products.html', context)

    return HttpResponseRedirect('/')


def search_auto(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        q = request.GET.get('term', '')
        products = Product.objects.filter(title__icontains=q)[:10]
        results = []
        for p in products:
            results.append({
                'label': p.title,
                'value': p.title,
                'price': '{:,.0f}'.format(p.final_price),
                'image': p.image.url if p.image else '',
                'url': reverse('product_detail', args=[p.id, p.slug]),
            })
        data = json.dumps(results)
    else:
        data = json.dumps([])
    return HttpResponse(data, content_type='application/json')


def product_detail(request, id, slug):
    query = request.GET.get('q')
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)

    product = get_object_or_404(Product, pk=id)

    products_picked = get_random_products(Product.objects.all(), 4)
    images = Images.objects.filter(product_id=id)

    all_comments = Comment.objects.filter(product_id=id, status="New").order_by('-create_at')
    paginator = Paginator(all_comments, 5)
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)

    # ── Kiểm tra quyền đánh giá: khách hàng phải mua sản phẩm này
    # và đơn hàng tương ứng phải có trạng thái "Đã giao hàng" ──
    can_review = False
    already_reviewed = False
    if request.user.is_authenticated:
        can_review = OrderProduct.objects.filter(
            user=request.user,
            product_id=id,
            order__status='Đã giao hàng'
        ).exists()
        already_reviewed = Comment.objects.filter(
            user=request.user,
            product_id=id
        ).exists()

    context = {
        'product': product, 'category': category,
        'products_picked': products_picked,
        'images': images, 'comments': comments, 'setting': setting,
        'can_review': can_review, 'already_reviewed': already_reviewed,
    }

    if product.variant != "None":
        if request.method == 'POST':
            variant_id = request.POST.get('productid')
            variant = get_object_or_404(Product, id=variant_id)
            colors = Product.objects.filter(product_id=id, size_id=variant.size_id)
            sizes = Product.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [id])
            query += variant.title + ' Size:' + str(variant.size) + ' Color:' + str(variant.color)
        else:
            variants = Product.objects.filter(product_id=id)
            colors = Product.objects.filter(product_id=id, size_id=variants[0].size_id)
            sizes = Product.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [id])
            variant = get_object_or_404(Product, id=variants[0].id)
        context.update({
            'sizes': sizes, 'colors': colors,
            'variant': variant, 'query': query,
        })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'reviews_list_fragment.html', {'comments': comments})

    return render(request, 'product_detail.html', context)
