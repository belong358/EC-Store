# Laptop E-commerce Website

Dự án với được xây dựng bằng Backend **Django (Python)** với **Server-Side**.

---

## Công Nghệ

- **Back-end**: Django (Python) - 🦸
- **Front-end**: HTML, CSS, JavaScript -
- **Database**: SQL -

## Team

** Lê Quốc Thái**
** Huỳnh Kim Long**

## Hướng Dẫn Setup

### Các Bước Setup

1. **Di chuyển đến thư mục dự án**

   ```bash
   cd elestore
   ```

2. **Tạo môi trường ảo**
   _Windows_:

   ```bash
   py -3.11 -m venv venv
   ```

   ```bash
   venv\Scripts\activate
   ```

````
   _macOS/Linux_:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
````

3. **Cài đặt các gói Python cần thiết**

   ```bash
   pip install -r requirements.txt
   pip install google-genai
   ```

4. **Áp dụng migrations cho database**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Khởi động server**

   ```bash
   python manage.py runserver
   ```

6. **Tạo tài khoản truy cập trang Admin**

   ```bash
   python manage.py createsuperuser
   ```

7. **Truy cập website**

- Mở trình duyệt : `http://localhost:8000`
- Trang Admin : `http://localhost:8000/admin`
- Trang Dashboard : `http://localhost:8000/dashboard`

### Optional(nếu có cài và đang chạy docker)

```bash
   docker-compose up --build
```

## Các tài khoản có thể đăng nhập vào web

** tk: kimlong299 , mk: 123456


## Cấu trúc dự án:

### Giao diện (Phần xử lý Giao diện chính cho website)

```
elestore/
├── home/
```

Thư mục `home` là một trong những thư mục chính của dự án, chứa các thành phần cơ bản của website như layout tổng ,SEO ,....

** Layout template tổng , SEO , render sản phẩm **
[home](home\templates\homebase.html)
-- tất cả những trang cơ bản của web site sẽ đều được kế thừa template từ file này

** Xử lý code python để lấy giữ liệu sản phẩm theo trang tương ứng **
[home,details,sản phẩm theo category](home\views.py)

** Phần xử lý form search sản phẩm **
[search](home\forms.py)

## Chức Năng (Product)

```
elestore/
├── product/
    ├── admin.py     # Quản lý giao diện admin cho sản phẩm và danh mục
    ├── models.py    # Định nghĩa cấu trúc dữ liệu
    ├── views.py     # Xử lý logic và hiển thị
    └── urls.py      # Định tuyến URL
```

Thư mục product là một trong những thư mục Liên quan đến data của sản phẩmphẩm, chứa các thành phần quản lý sản phẩm và danh mục sản phẩm.

** Quản lý danh mục và sản phẩm trong trang admin **
[admin](\product\admin.py) -- quản lý danh mục sản phẩm theo cấu trúc cây, quản lý sản phẩm với hình ảnh và thông tin chi tiết

** Xử lý code python để quản lý dữ liệu sản phẩm **
[models](\product\models.py) -- định nghĩa cấu trúc dữ liệu cho danh mục, sản phẩm, hình ảnh và đánh giá sản phẩm

** Xử lý đánh giá sản phẩm **
[views](\product\view.py) -- xử lý thêm đánh giá và bình luận cho sản phẩm

## Chức Năng (Order)

Thư mục `order` quản lý toàn bộ quy trình mua hàng, từ giỏ hàng đến đơn hàng.

```
elestore/
├── order/
    ├── admin.py     # Quản lý đơn hàng trong admin
    ├── models.py    # Cấu trúc dữ liệu đơn hàng
    ├── views.py     # Xử lý giỏ hàng và đặt hàng
    ├── urls.py      # Định tuyến URL
    └── templates/   # Giao diện người dùng
```

** Template giao diện người dùng **
[order form](\order\templates\Order_Form.html) -- giao diện người dùng cho các chức năng liên quan đến đơn hàng, giỏ hàng, thanh toán
[giao diện cart](\order\templates\shopcart_products.html) -- giao diện người dùng cho giỏ hàng
[Giao diện khi thanh toán thành công](\order\templates\Order_completed.html) -- giao diện người dùng cho khi thanh toán thành công

** Quản lý đơn hàng trong trang admin **

[admin](\order\admin.py) -- quản lý đơn hàng trong trang admin

** Xử lý code python để quản lý đơn hàng **

[models](\order\models.py) -- định nghĩa cấu trúc dữ liệu cho đơn hàng, chi tiết đơn hàng, phương thức thanh toán

** Xử lý logic cho các chức năng liên quan đến đơn hàng **

[views](\order\views.py) -- xử lý logic cho các chức năng liên quan đến đơn hàng, giỏ hàng, thanh toán

** Định tuyến URL cho các chức năng liên quan đến đơn hàng **

[urls](\order\urls.py) -- định tuyến URL cho các chức năng liên quan đến đơn hàng, giỏ hàng, thanh toán

## Chức năng (user)

- Đăng ký & đăng nhập

- Quản lý hồ sơ cá nhân & đổi mật khẩu

- Theo dõi đơn hàng & bình luận

- Tùy chỉnh form và giao diện người dùng với template HTML

- [user](\user\models.py) giúp mở rộng thông tin người dùng thông qua class UserProfile

- Định tuyến và xử lý logic qua [user](\user\views.py) và [user](\user\urls.py)

- Quản trị người dùng qua [user](\user\admin.py)
