/* ============================================
   AJAX Add-to-Cart — không reload trang
   ============================================ */
$(document).ready(function () {

    function showCartToast(message, type) {
        type = type || 'success';
        var $toast = $('#cart-toast');
        if ($toast.length === 0) {
            $toast = $('<div id="cart-toast"></div>').appendTo('body');
            $toast.css({
                position: 'fixed', top: '20px', right: '20px', zIndex: 9999,
                color: '#fff', padding: '12px 20px',
                borderRadius: '8px', fontSize: '13px', fontWeight: '600',
                boxShadow: '0 8px 24px rgba(0,0,0,.2)', opacity: 0,
                transition: 'opacity .25s, transform .25s', transform: 'translateY(-10px)',
                maxWidth: '320px'
            });
        }
        var isError = (type === 'error');
        $toast.css('background', isError ? '#dc2626' : '#1e2230');
        var icon = isError
            ? '<i class="fa fa-circle-exclamation" style="color:#fff;margin-right:8px"></i>'
            : '<i class="fa fa-check-circle" style="color:#10b981;margin-right:8px"></i>';
        $toast.html(icon + message);
        $toast.css({ opacity: 1, transform: 'translateY(0)' });
        clearTimeout($toast.data('timer'));
        var t = setTimeout(function () {
            $toast.css({ opacity: 0, transform: 'translateY(-10px)' });
        }, isError ? 2800 : 2200);
        $toast.data('timer', t);
    }

    function updateCartUI(data) {
        $('#cart-qty-badge').text(data.totalqty);
        $('#cart-dropdown-content').html(data.cart_html);
        showCartToast(data.message);
    }

    // Xử lý khi server từ chối thêm giỏ hàng (vd: chưa đăng nhập)
    function handleCartError(xhr) {
        var data = xhr.responseJSON;
        if (data && data.login_required) {
            showCartToast(data.message || 'Bạn cần đăng nhập để có thể mua hàng', 'error');
            setTimeout(function () {
                window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
            }, 1300);
        } else {
            showCartToast('Có lỗi xảy ra, vui lòng thử lại', 'error');
        }
    }

    // 1) Nút "Thêm Vào Giỏ" dạng link <a href="/order/addtoshopcart/ID"> (trang danh sách sản phẩm)
    $(document).on('click', 'a[href^="/order/addtoshopcart/"]', function (e) {
        e.preventDefault();
        var url = $(this).attr('href');
        var $btn = $(this).find('button, .add-to-cart-btn');
        $btn.css('opacity', 0.6);

        $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                if (data && data.success) {
                    updateCartUI(data);
                }
            },
            error: handleCartError
        }).always(function () {
            $btn.css('opacity', 1);
        });
    });

    // 2) Form "Thêm Vào Giỏ" có chọn số lượng (trang chi tiết sản phẩm)
    $(document).on('submit', '#addchart-form', function (e) {
        e.preventDefault();
        var $form = $(this);

        $.ajax({
            url: $form.attr('action'),
            method: 'POST',
            data: $form.serialize(),
            dataType: 'json',
            success: function (data) {
                if (data && data.success) {
                    updateCartUI(data);
                }
            },
            error: handleCartError
        });
    });

});
