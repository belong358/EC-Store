# 🖥️ EleStore (EC Computer) — Website Bán Laptop & Phụ Kiện Máy Tính

Website thương mại điện tử chuyên bán laptop và phụ kiện máy tính, được xây dựng bằng **Django (Python)** theo mô hình **Server-Side Rendering (MVT)**, tích hợp thanh toán đa cổng, đăng nhập mạng xã hội và trợ lý AI tư vấn sản phẩm.

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
| **Xác thực** | django-allauth (Email, Google, Facebook OAuth2) |
| **API / JWT** | Django REST Framework + Simple JWT |
| **Thanh toán** | Stripe, VNPay, MoMo, COD |
| **AI** | Google Gemini API + ChromaDB (RAG chatbot tư vấn sản phẩm) |
| **Khác** | django-ckeditor (rich text), django-mptt (danh mục cây), django-cors-headers |

---

## ✨ Tính năng chính

### 🛍️ Phía khách hàng
- Xem, tìm kiếm sản phẩm với gợi ý tự động (autocomplete kèm ảnh/giá)
- Lọc sản phẩm theo danh mục, khoảng giá
- Giỏ hàng, đặt hàng, theo dõi trạng thái đơn hàng
- Thanh toán qua **Stripe / VNPay / MoMo / COD**
- Đăng ký, đăng nhập bằng Email hoặc liên kết Google / Facebook
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
├── home/           # Trang chủ, layout tổng, SEO, tìm kiếm, chatbot AI
├── product/        # Quản lý sản phẩm, danh mục, đánh giá
├── order/          # Giỏ hàng, đặt hàng, thanh toán
├── user/           # Tài khoản, hồ sơ người dùng
├── elestore/        # Cấu hình project (settings, urls chính)
├── static/          # CSS, JS, hình ảnh giao diện
├── uploads/          # Ảnh sản phẩm, banner do người dùng/admin tải lên
├── manage.py
└── requirements.txt
```

### Chi tiết từng module

<details>
<summary><b>🏠 home/</b> — Layout tổng & trang chủ</summary>

- [`home/templates/homebase.html`](home/templates/homebase.html) — template gốc, mọi trang đều kế thừa từ đây
- [`home/views.py`](home/views.py) — xử lý trang chủ, chi tiết sản phẩm theo danh mục
- [`home/forms.py`](home/forms.py) — xử lý form tìm kiếm sản phẩm
- [`home/chatbot_views.py`](home/chatbot_views.py) — xử lý chatbot AI tư vấn sản phẩm

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
- [`order/models.py`](order/models.py) — cấu trúc dữ liệu đơn hàng, phương thức thanh toán
- [`order/views.py`](order/views.py) — xử lý logic giỏ hàng, đặt hàng, tích hợp cổng thanh toán

</details>

<details>
<summary><b>👤 user/</b> — Tài khoản người dùng</summary>

- Đăng ký, đăng nhập, quản lý hồ sơ, đổi mật khẩu
- [`user/models.py`](user/models.py) — mở rộng thông tin người dùng qua `UserProfile`
- [`user/views.py`](user/views.py) / [`user/urls.py`](user/urls.py) — định tuyến và xử lý logic
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

Copy file `.env.example` thành `.env` và điền đầy đủ giá trị thật (secret key, thông tin cổng thanh toán, email, Gemini API key...):

```bash
cp .env.example .env
```

### 5. Áp dụng migrations cho database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo tài khoản quản trị

```bash
python manage.py createsuperuser
```

### 7. Khởi động server

```bash
python manage.py runserver
```

### 8. Truy cập website

| Trang | Đường dẫn |
|---|---|
| Trang chủ | `http://localhost:8000` |
| Django Admin | `http://localhost:8000/admin` |
| Dashboard quản trị | `http://localhost:8000/dashboard-login` |

### (Tùy chọn) Chạy bằng Docker

```bash
docker-compose up --build
```

---

## 🔑 Tài khoản test

> Toàn bộ tài khoản và thẻ dưới đây đều là dữ liệu **test/sandbox**, không phải tài khoản hay thẻ ngân hàng thật.

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

---

## 👥 Nhóm thực hiện

| Họ và tên | MSSV |
|---|---|
| Lê Quốc Thái | 24810077 |
| Huỳnh Kim Long | 24810067 |

**Ngành:** Công nghệ Thông tin — Trường Đại học Công nghệ Kỹ thuật TP.HCM (HCM-UTE)
