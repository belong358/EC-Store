from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from product.models import CommentForm, Comment, Product, Category, Wishlist
from home.models import Setting
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.html import strip_tags
from google import genai

# --- Wishlist ---

@login_required(login_url='/login')
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    w_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        message = "Đã thêm vào danh sách yêu thích."
        status = "success"
    else:
        message = "Sản phẩm này đã có trong danh sách yêu thích."
        status = "info"
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({'status': status, 'message': message, 'count': count})
    messages.success(request, message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/login')
def remove_from_wishlist(request, id):
    Wishlist.objects.filter(user=request.user, product_id=id).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({'status': 'success', 'count': count})
    messages.success(request, "Đã xóa khỏi danh sách yêu thích.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/login')
def wishlist_view(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {
        'category': category,
        'setting': setting,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist.html', context)

def index(request):
    return HttpResponse("My product page")


def add_to_compare(request, id):
    compare_list = request.session.get('compare_list', [])
    if id in compare_list:
        return JsonResponse({'status': 'info', 'message': 'Sản phẩm đã có trong danh sách so sánh.'})
    if len(compare_list) >= 4:
        return JsonResponse({'status': 'warning', 'message': 'Bạn chỉ có thể so sánh tối đa 4 sản phẩm.'})
    compare_list.append(id)
    request.session['compare_list'] = compare_list
    return JsonResponse({
        'status': 'success',
        'message': 'Đã thêm vào danh sách so sánh.',
        'count': len(compare_list)
    })

def remove_from_compare(request, id):
    compare_list = request.session.get('compare_list', [])
    if id in compare_list:
        compare_list.remove(id)
        request.session['compare_list'] = compare_list
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'count': len(compare_list)})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def compare_products(request):
    compare_list = request.session.get('compare_list', [])
    products = Product.objects.filter(id__in=compare_list)
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)

    ai_summary = None
    if products.count() >= 2:
        try:
            comparison_data = []
            for p in products:
                detail_clean = strip_tags(p.detail)[:500] if p.detail else ""
                comparison_data.append(f"Tên: {p.title}\nGiá: {p.price}\nChi tiết: {detail_clean}")

            data_str = "\n---\n".join(comparison_data)

            _client = genai.Client(api_key=settings.GEMINI_API_KEY)

            prompt = f"""
Bạn là chuyên gia tư vấn công nghệ. Dưới đây là thông tin của {products.count()} sản phẩm đang được so sánh:
{data_str}

Hãy đưa ra một bản tóm tắt so sánh thông minh bằng tiếng Việt:
1. Điểm mạnh vượt trội của từng sản phẩm so với các sản phẩm còn lại.
2. Sản phẩm nào đáng mua nhất trong tầm giá.
3. Lời khuyên nhanh cho khách hàng (ví dụ: Ai nên mua con nào).

Trả lời ngắn gọn, định dạng Markdown, súc tích (tối đa 150 từ).
"""
            response = _client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt
            )
            if response.text:
                ai_summary = response.text
        except Exception as e:
            print(f"Lỗi AI Compare: {str(e)}")
            ai_summary = None

    context = {
        'products': products,
        'category': category,
        'setting': setting,
        'ai_summary': ai_summary,
    }
    return render(request, 'compare.html', context)


def addcomment(request, id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = id
            current_user = request.user
            data.user_id = current_user.id
            data.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Cảm ơn! Đánh giá của bạn đã được gửi.',
                    'comment': data.comment,
                    'rate': data.rate,
                    'user': current_user.first_name,
                    'date': data.create_at.strftime("%d/%m/%Y")
                })
            messages.success(request, "Bài đánh giá của bạn đã được duyệt, cảm ơn vì đã gửi đánh giá.")
            return HttpResponseRedirect(url)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Dữ liệu không hợp lệ.'}, status=400)
    return HttpResponseRedirect(url)
