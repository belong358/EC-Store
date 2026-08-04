"""
Module hỗ trợ tích hợp SePay — cổng thanh toán QR chuyển khoản ngân hàng
(VietQR), dùng để bổ sung thêm 1 phương thức thanh toán online có thể
test đầy đủ luồng mà không cần dùng tiền thật (SePay có tính năng
"giả lập giao dịch" trên dashboard của họ để bắn webhook thử).

Khác với VNPay/MoMo (đứng giữa xử lý giao dịch), SePay chỉ đóng vai trò
"người quan sát" tài khoản ngân hàng thật của người bán:
1. Web tạo ảnh QR chứa sẵn số tài khoản + số tiền + nội dung (chuẩn VietQR,
   không cần gọi API, chỉ cần dựng đúng URL ảnh).
2. Khách quét QR bằng app ngân hàng bất kỳ, chuyển khoản thẳng vào tài
   khoản người bán (không qua SePay giữ tiền).
3. SePay phát hiện biến động số dư, gửi webhook (HTTP POST) báo cho web
   biết "vừa có giao dịch abc" — web tự đối chiếu nội dung chuyển khoản
   với mã đơn hàng để xác nhận.
"""
from django.conf import settings


def build_qr_image_url(amount, description):
    """
    Dựng URL ảnh QR VietQR động từ dịch vụ công khai qr.sepay.vn — không
    cần gọi API/xác thực gì, chỉ cần đúng số tài khoản + ngân hàng đã cấu
    hình trong .env (SEPAY_ACCOUNT_NUMBER, SEPAY_BANK_NAME).
    """
    return (
        "https://qr.sepay.vn/img"
        f"?acc={settings.SEPAY_ACCOUNT_NUMBER}"
        f"&bank={settings.SEPAY_BANK_NAME}"
        f"&amount={int(amount)}"
        f"&des={description}"
        "&template=compact"
    )


def build_transfer_content(order_code):
    """
    Nội dung chuyển khoản dùng để đối chiếu với đơn hàng — SePay không có
    khái niệm "mã đơn hàng" riêng như VNPay/MoMo, nên phải tự quy ước:
    chèn 1 tiền tố cố định (SEPAY_PREFIX, mặc định 'DH') + mã đơn hàng vào
    nội dung chuyển khoản, sau đó dò tìm chuỗi này trong nội dung giao
    dịch thật mà webhook gửi về.
    """
    return f"{settings.SEPAY_PREFIX}{order_code}"


def verify_webhook_auth(request):
    """
    Xác thực webhook đến từ đúng SePay (không phải giả mạo) bằng API Key
    cấu hình sẵn — SePay gửi kèm header 'Authorization: Apikey <key>'.
    """
    expected = f"Apikey {settings.SEPAY_API_KEY}"
    received = request.headers.get("Authorization", "")
    return bool(settings.SEPAY_API_KEY) and received == expected


def extract_order_code_from_content(content, prefix=None):
    """
    Tìm mã đơn hàng (chuỗi 5 ký tự viết hoa, đúng định dạng get_random_string(5).upper()
    dùng khi tạo đơn — xem order/views.py) nằm trong nội dung chuyển khoản thật.
    Nội dung thật do ngân hàng xử lý có thể bị thêm khoảng trắng/ký tự thừa
    xung quanh, nên dò theo tiền tố thay vì so khớp chính xác toàn chuỗi.
    """
    prefix = prefix or settings.SEPAY_PREFIX
    content = (content or "").upper().replace(" ", "")
    idx = content.find(prefix.upper())
    if idx == -1:
        return None
    return content[idx + len(prefix): idx + len(prefix) + 5] or None
