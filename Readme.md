# 🖥️ EleStore (EC Computer) — Website Bán Laptop & Phụ Kiện Máy Tính

Website thương mại điện tử chuyên bán laptop và phụ kiện máy tính, được xây dựng bằng **Django (Python)** theo mô hình **Server-Side Rendering (MVT)**, tích hợp thanh toán đa cổng, đăng nhập Google và trợ lý AI tư vấn sản phẩm.

---

## 📋 Mục lục

- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Tính năng chính](#-tính-năng-chính)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Hướng dẫn cài đặt](#-hướng-dẫn-cài-đặt)
- [Tài khoản test](#-tài-khoản-test)
- [Nhóm thực hiện](#-nhóm-thực-hiện)

---

## 🛠 Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| **Back-end** | Django 5.x (Python) |
| **Front-end** | Django Template Engine, HTML5, CSS3, JavaScript, jQuery + jQuery UI |
| **Database** | SQLite |
| **Xác thực** | django-allauth (Email, Google OAuth2) |
| **API / JWT** | Django REST Framework + Simple JWT + dj-rest-auth (đăng nhập Google qua API) |
| **Thanh toán** | Stripe, VNPay, MoMo, SePay (QR chuyển khoản ngân hàng), COD |
| **AI** | Google Gemini API + ChromaDB (RAG chatbot tư vấn sản phẩm) |
| **Khác** | django-ckeditor (rich text), django-mptt (danh mục cây), django-cors-headers |

---

## ✨ Tính năng chính

### 🛍️ Phía khách hàng
- Xem, tìm kiếm sản phẩm với gợi ý tự động (autocomplete kèm ảnh/giá)
- Lọc sản phẩm theo danh mục, khoảng giá
- Giỏ hàng, đặt hàng, theo dõi trạng thái đơn hàng
- Thanh toán qua **Stripe / VNPay / MoMo / SePay (QR chuyển khoản ngân hàng) / COD**
- Đăng ký, đăng nhập bằng Email hoặc liên kết Google
- Đánh giá, bình luận sản phẩm
- **Chatbot AI** tư vấn sản phẩm theo nhu cầu (tích hợp Gemini + RAG)

### 🔧 Phía quản trị (Dashboard)
- Quản lý sản phẩm, danh mục (cấu trúc cây cha - con)
- Quản lý đơn hàng, cập nhật trạng thái xử lý
- Quản lý người dùng, banner quảng cáo, đánh giá khách hàng
- Thống kê doanh thu, đơn hàng theo thời gian thực (biểu đồ, thông báo tự động cập nhật)

---

## 📁 Cấu trúc dự án

```
elestore/
├── home/            # Trang chủ, layout tổng, SEO, tìm kiếm, dashboard, chatbot AI
├── product/         # Quản lý sản phẩm, danh mục, đánh giá
├── order/           # Giỏ hàng, đặt hàng, thanh toán
├── user/            # Tài khoản, hồ sơ người dùng, API đăng nhập Google
├── elestore/         # Cấu hình project (settings, urls chính)
├── static/           # CSS, JS, hình ảnh giao diện
├── uploads/           # Ảnh sản phẩm, banner do người dùng/admin tải lên
├── images/            # Ảnh mẫu dùng trong seed/demo dữ liệu
├── index_rag.py        # Script build/cập nhật Vector DB (ChromaDB) cho chatbot AI
├── test_gemini.py       # Script kiểm tra nhanh kết nối Gemini API
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### Chi tiết từng module

<details>
<summary><b>🏠 home/</b> — Layout tổng & trang chủ</summary>

- [`home/templates/homebase.html`](home/templates/homebase.html) — template gốc, mọi trang đều kế thừa từ đây
- [`home/views.py`](home/views.py) — xử lý trang chủ, chi tiết sản phẩm theo danh mục
- [`home/forms.py`](home/forms.py) — xử lý form tìm kiếm sản phẩm
- [`home/chatbot_views.py`](home/chatbot_views.py) — xử lý chatbot AI tư vấn sản phẩm (Gemini + truy vấn Vector DB)
- [`home/dashboard_views.py`](home/dashboard_views.py) — xử lý các trang trong Dashboard quản trị (thống kê, quản lý banner, đánh giá...)
- [`home/signals.py`](home/signals.py) — xử lý các signal tự động (VD: cập nhật liên quan khi có thay đổi dữ liệu)
- [`index_rag.py`](index_rag.py) (thư mục gốc) — script build/cập nhật dữ liệu sản phẩm vào ChromaDB để chatbot AI tìm kiếm theo ngữ nghĩa (RAG)

</details>

<details>
<summary><b>📦 product/</b> — Quản lý sản phẩm</summary>

- [`product/admin.py`](product/admin.py) — quản lý danh mục (dạng cây) và sản phẩm trong trang admin
- [`product/models.py`](product/models.py) — cấu trúc dữ liệu danh mục, sản phẩm, hình ảnh, đánh giá
- [`product/views.py`](product/views.py) — xử lý hiển thị, tìm kiếm, đánh giá sản phẩm

</details>

<details>
<summary><b>🛒 order/</b> — Giỏ hàng & đơn hàng</summary>

- [`order/templates/Order_Form.html`](order/templates/Order_Form.html) — giao diện đặt hàng, thanh toán
- [`order/templates/shopcart_products.html`](order/templates/shopcart_products.html) — giao diện giỏ hàng
- [`order/templates/Order_completed.html`](order/templates/Order_completed.html) — giao diện sau khi thanh toán thành công
- [`order/templates/Sepay_QR_Payment.html`](order/templates/Sepay_QR_Payment.html) — giao diện hiển thị mã QR chuyển khoản SePay
- [`order/models.py`](order/models.py) — cấu trúc dữ liệu đơn hàng, phương thức thanh toán
- [`order/views.py`](order/views.py) — xử lý logic giỏ hàng, đặt hàng, tích hợp cổng thanh toán
- [`order/sepay.py`](order/sepay.py) — sinh URL ảnh QR VietQR động và xác thực webhook từ SePay

</details>

<details>
<summary><b>👤 user/</b> — Tài khoản người dùng</summary>

- Đăng ký, đăng nhập, quản lý hồ sơ, đổi mật khẩu
- [`user/models.py`](user/models.py) — mở rộng thông tin người dùng qua `UserProfile`
- [`user/views.py`](user/views.py) / [`user/urls.py`](user/urls.py) — định tuyến và xử lý logic
- [`user/api_views.py`](user/api_views.py) — API đăng nhập bằng Google (JWT, dùng cho client ngoài như mobile/SPA)
- [`user/admin.py`](user/admin.py) — quản trị người dùng

</details>

---

## 🚀 Hướng dẫn cài đặt

### 1. Di chuyển đến thư mục dự án

```bash
cd elestore
```

### 2. Tạo môi trường ảo

**Windows:**
```bash
py -3.11 -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt các gói cần thiết

```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường

Copy file `.env.example` thành `.env`:

**macOS / Linux:**
```bash
cp .env.example .env
```

**Windows (Command Prompt):**
```bash
copy .env.example .env
```

> ⚠️ Sau khi copy, mở file `.env` lên và điền giá trị thật vào — **không xóa hay đổi tên biến**, chỉ thay phần sau dấu `=`. Không cần bỏ giá trị trong dấu nháy hay thêm khoảng trắng quanh dấu `=`.

Chi tiết từng nhóm biến trong `.env`:

| Biến | Bắt buộc? | Ghi chú |
|---|---|---|
| `DJANGO_SECRET_KEY` | ✅ Có | Xem cách lấy bên dưới |
| `DJANGO_DEBUG` | Không | Để `True` khi chạy local (demo/chấm điểm), `False` khi deploy thật |
| `DJANGO_ALLOWED_HOSTS` | Không | Giữ mặc định `localhost,127.0.0.1` nếu chạy máy local |
| `DB_ENGINE`, `DB_NAME`... | Không | Giữ mặc định SQLite, không cần sửa nếu không dùng PostgreSQL/MySQL |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Không* | Để trống vẫn chạy được — hệ thống tự in email xác nhận đăng ký ra terminal thay vì gửi thật (console backend). Chỉ cần điền nếu muốn test gửi email thật, khi đó với Gmail phải dùng **App Password** (16 ký tự), không dùng mật khẩu đăng nhập Gmail thường |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Không* | Chỉ cần nếu muốn test đăng nhập Google, lấy tại [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY` | Không* | Chỉ cần nếu muốn test thanh toán Stripe, lấy tại [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys) (chế độ Test mode) |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | ✅ Có (nếu muốn dùng chatbot AI) | Xem cách lấy bên dưới |
| `VNP_TMN_CODE`, `VNP_HASH_SECRET` | Không* | Chỉ cần nếu muốn test thanh toán VNPay, đăng ký sandbox tại [VNPay Sandbox](https://sandbox.vnpayment.vn/devreport/) |
| `MOMO_ACCESS_KEY`, `MOMO_SECRET_KEY` | Không | Có thể giữ nguyên bộ test công khai của MoMo (xem mục [Tài khoản test](#-tài-khoản-test)) |
| `SEPAY_ACCOUNT_NUMBER`, `SEPAY_BANK_NAME`, `SEPAY_API_KEY`, `SEPAY_PREFIX` | Không* | Chỉ cần nếu muốn test thanh toán QR chuyển khoản ngân hàng qua [SePay](https://sepay.vn) — cần đăng ký tài khoản, liên kết ngân hàng và tạo Webhook (xem hướng dẫn bên dưới) |
| `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | Không | Giữ mặc định nếu chỉ chạy local, không public qua domain/ngrok |

*Không* = có thể để trống, tính năng liên quan sẽ không hoạt động nhưng không làm sập toàn bộ website.

**Cách lấy `DJANGO_SECRET_KEY`:**

Chạy lệnh sau (cần đã cài Django ở bước 3) để sinh ngẫu nhiên một secret key, sau đó dán vào biến `DJANGO_SECRET_KEY` trong `.env`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Cách lấy `GEMINI_API_KEY`:**

1. Truy cập [Google AI Studio](https://aistudio.google.com/apikey)
2. Đăng nhập bằng tài khoản Google, chọn **Create API key**
3. Copy key vừa tạo và dán vào biến `GEMINI_API_KEY` trong `.env`
4. (Tùy chọn) Kiểm tra key hoạt động bằng script có sẵn: `python test_gemini.py`

**Cách lấy `EMAIL_HOST_PASSWORD`** *(chỉ cần nếu muốn test gửi email thật, VD: xác nhận đăng ký tài khoản)*:

> ⚠️ Không dùng mật khẩu đăng nhập Gmail bình thường — Google đã chặn cách này. Phải tạo **App Password** riêng.

1. Bật xác minh 2 bước (2-Step Verification) cho tài khoản Gmail dùng để gửi mail, tại [myaccount.google.com/security](https://myaccount.google.com/security) — bắt buộc phải bật thì mới tạo được App Password
2. Truy cập [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Đặt tên bất kỳ (VD: `EleStore`) → chọn **Create/Tạo**
4. Google sẽ hiện ra một mã gồm 16 ký tự (dạng `xxxx xxxx xxxx xxxx`) — copy mã này (bỏ khoảng trắng hoặc giữ nguyên đều được) và dán vào biến `EMAIL_HOST_PASSWORD` trong `.env`
5. Biến `EMAIL_HOST_USER` điền đúng địa chỉ Gmail đã tạo App Password ở bước trên

> Nếu không cần test gửi email thật, có thể để trống 2 biến này — hệ thống sẽ tự in nội dung email xác nhận (kèm link kích hoạt tài khoản) ra terminal khi chạy `python manage.py runserver`, vẫn test được luồng đăng ký/xác nhận email bình thường mà không cần cấu hình Gmail.

**Cách lấy cấu hình `SEPAY_*`** *(chỉ cần nếu muốn test thanh toán QR chuyển khoản ngân hàng qua SePay)*:

1. Đăng ký tài khoản tại [my.sepay.vn](https://my.sepay.vn), chọn gói **"Chỉ cần chia sẻ biến động số dư"**
2. Vào mục **Ngân hàng** → liên kết 1 tài khoản ngân hàng cá nhân qua API (một số ngân hàng như MB Bank, Vietcombank hỗ trợ liên kết trực tiếp, không cần giấy phép kinh doanh)
3. `SEPAY_ACCOUNT_NUMBER` = số tài khoản vừa liên kết, `SEPAY_BANK_NAME` = tên ngân hàng (VD: `MBBank`)
4. Vào mục **Tích hợp Webhook** → tạo Webhook mới, ở bước **Bảo mật** chọn phương thức **API Key** rồi **tự đặt** 1 chuỗi bất kỳ làm khóa (VD: `elestore_sepay_2026_xK9p`) → dán chuỗi đó vào `SEPAY_API_KEY`
5. `SEPAY_PREFIX` giữ mặc định `DH` — đây là tiền tố được chèn vào nội dung chuyển khoản để đối chiếu đúng mã đơn hàng

> ⚠️ **Cần chạy được webhook cục bộ (local)**: vì SePay cần gọi được vào server Django của bạn qua Internet, trong khi `localhost:8000` chỉ chạy trên máy — cần dùng công cụ như [ngrok](https://ngrok.com) để tạo đường hầm public tạm thời (`ngrok http 8000`). Lấy link ngrok hiện ra (dạng `https://xxxx.ngrok-free.dev`) và **thêm đúng đuôi `/order/sepay_webhook/` vào cuối** để có URL Webhook đầy đủ (VD: `https://xxxx.ngrok-free.dev/order/sepay_webhook/`) — dán chính xác URL đầy đủ này vào ô Webhook URL trên SePay, **không dán riêng link ngrok gốc** (nếu thiếu đuôi, SePay sẽ gọi nhầm vào trang chủ, không tới đúng chỗ xử lý, dẫn tới lỗi). Đồng thời thêm domain ngrok đó vào `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` trong `.env`. Link `ngrok` miễn phí sẽ đổi mỗi lần khởi động lại, cần cập nhật lại cả `.env` lẫn URL Webhook trên SePay sau mỗi lần restart.
>
> Để test không cần tiền thật: bật **"Test mode"** trên my.sepay.vn, tạo lại 1 Webhook riêng trong chế độ này, rồi dùng tính năng **"Mô phỏng giao dịch"** (điền đúng số tiền + nội dung chuyển khoản hiện trên trang QR của đơn hàng) để giả lập webhook mà không cần chuyển khoản thật.

### 5. Áp dụng migrations cho database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo tài khoản quản trị

```bash
python manage.py createsuperuser
```

### 7. Build dữ liệu cho chatbot AI (RAG)

Chạy script sau để đưa dữ liệu sản phẩm vào ChromaDB — cần thiết để chatbot AI tư vấn được sản phẩm. Nên chạy lại mỗi khi thêm/sửa sản phẩm:

```bash
python index_rag.py
```

### 8. Khởi động server

```bash
python manage.py runserver
```

### 9. Truy cập website

| Trang | Đường dẫn |
|---|---|
| Trang chủ | `http://localhost:8000` |
| Django Admin | `http://localhost:8000/admin` |
| Dashboard quản trị | `http://localhost:8000/dashboard-login` |

### (Tùy chọn) Chạy bằng Docker

> Mục này **không bắt buộc** — có thể bỏ qua hoàn toàn nếu đã chạy được bằng cách venv + `pip install` ở các bước 1–9 phía trên. Docker chỉ hữu ích khi cần triển khai lên server hoặc chia sẻ môi trường chạy giống hệt nhau giữa nhiều máy.

<details>
<summary>Xem hướng dẫn nếu vẫn muốn dùng Docker</summary>

Cần hoàn thành bước 4 (tạo file `.env`) trước, container sẽ tự đọc file này:

```bash
docker-compose up --build
```

Mở terminal khác để chạy migrate, tạo tài khoản quản trị và build dữ liệu chatbot (tương đương bước 5, 6, 7 nhưng chạy bên trong container):

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python index_rag.py
```

</details>

---

## 🔑 Tài khoản test

> Toàn bộ tài khoản và thẻ dưới đây đều là dữ liệu **test/sandbox**, không phải tài khoản hay thẻ ngân hàng thật.

> ⚠️ Các tài khoản demo bên dưới chỉ có sẵn nếu bạn dùng **file `db.sqlite3` đã có sẵn dữ liệu** (VD: bản nộp bài dạng zip). Nếu clone code từ GitHub và tự chạy `migrate` từ đầu, database sẽ trống — chỉ có tài khoản quản trị do chính bạn tạo ở bước "Tạo tài khoản quản trị" (`createsuperuser`), vì repo hiện chưa có fixture/seed data để tự sinh các tài khoản này.

### Tài khoản đăng nhập demo

| Tài khoản | Mật khẩu | Vai trò |
|---|---|---|
| kimlong299 | 123456 | Quản trị viên |
| quocthai438 | 12345678 | Nhân viên |
| tuancuong123 | 12345678910 | Khách hàng |
| quocanh123 | quocanh123 | Khách hàng |
| kimtruc456 | kimtruc456 | Khách hàng |

### Thẻ test VNPay (NCB)

- **Số thẻ:** 9704198526191432198
- **Tên chủ thẻ:** NGUYEN VAN A
- **Ngày phát hành:** 07/15
- **OTP:** 123456

### Cổng thanh toán khác

- **MoMo**: sử dụng bộ tài khoản test sandbox công khai theo tài liệu tích hợp của MoMo
- **Stripe**: sử dụng [thẻ test của Stripe](https://docs.stripe.com/testing)
- **SePay**: bật **Test mode** trên my.sepay.vn rồi dùng tính năng **"Mô phỏng giao dịch"** — không cần thẻ hay tài khoản test riêng, chỉ cần điền đúng số tiền và nội dung chuyển khoản hiện trên trang QR của đơn hàng

---

## 👥 Nhóm thực hiện

| Họ và tên | MSSV |
|---|---|
| Lê Quốc Thái | 24810077 |
| Huỳnh Kim Long | 24810067 |

**Ngành:** Công nghệ Thông tin — Trường Đại học Công nghệ Kỹ thuật TP.HCM (HCM-UTE)
