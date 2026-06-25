"""
Thêm 2 banner, 2 laptop, 3 linh kiện, 4 phụ kiện vào EleStore.
Chạy: python add_products_and_banners.py
"""
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
import django
django.setup()

from PIL import Image, ImageDraw, ImageFont
from django.core.files import File
from django.utils import timezone
from datetime import timedelta
from product.models import Product, Images, Category
from home.models import Banner

# ─── FONTS (dùng font có sẵn trong dự án, chạy được cả Windows lẫn Linux) ───
import os as _os
_BASE = _os.path.dirname(_os.path.abspath(__file__))
FONT_BOLD = _os.path.join(_BASE, 'static', 'fonts', 'pdf', 'DejaVuSans-Bold.ttf')
FONT_REG  = _os.path.join(_BASE, 'static', 'fonts', 'pdf', 'DejaVuSans.ttf')

IMG_DIR    = 'uploads/images'
BANNER_DIR = 'uploads/images/banner'

def make_banner(out_filename, badge_text, title_line1, title_line2,
                specs, price_str, product_img_path, accent=(209, 0, 36)):
    """Tạo banner 1600×800 theo đúng phong cách hiện có."""
    W, H = 1600, 800
    img = Image.new('RGB', (W, H), (14, 12, 26))
    draw = ImageDraw.Draw(img)

    # --- Gradient nền trái sang phải ---
    for x in range(W):
        t = x / W
        r = int(14 + (22 - 14) * t)
        g = int(12 + (10 - 12) * t)
        b = int(26 + (18 - 26) * t)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    # --- Sọc đỏ chéo ---
    cx = 820
    poly = [(cx - 60, 0), (cx + 80, 0), (cx - 80, H), (cx - 220, H)]
    draw.polygon(poly, fill=accent)
    draw.polygon([(p[0] - 18, p[1]) for p in poly], fill=(180, 0, 18))

    # --- Khung trắng bên phải cho ảnh sản phẩm ---
    box_x, box_y, box_w, box_h = 900, 80, 620, 640
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h],
                            radius=24, fill=(245, 245, 245))

    prod_img = Image.open(product_img_path).convert('RGBA')
    prod_img.thumbnail((580, 600))
    px = box_x + (box_w - prod_img.width) // 2
    py = box_y + (box_h - prod_img.height) // 2
    if prod_img.mode == 'RGBA':
        img.paste(prod_img, (px, py), prod_img)
    else:
        img.paste(prod_img, (px, py))

    # --- Badge label ---
    fb = ImageFont.truetype(FONT_BOLD, 28)
    badge_w = draw.textlength(badge_text, font=fb) + 32
    draw.rounded_rectangle([50, 60, 50 + int(badge_w), 104], radius=22, fill=accent)
    draw.text((66, 68), badge_text, font=fb, fill=(255, 255, 255))

    # --- Tên sản phẩm ---
    f_big  = ImageFont.truetype(FONT_BOLD, 84)
    f_big2 = ImageFont.truetype(FONT_BOLD, 84)
    draw.text((50, 120), title_line1, font=f_big,  fill=(255, 255, 255))
    draw.text((50, 210), title_line2, font=f_big2, fill=accent)

    # --- Specs ---
    f_spec = ImageFont.truetype(FONT_REG, 32)
    draw.text((50, 330), specs, font=f_spec, fill=(200, 200, 200))

    # --- Giá ---
    f_price_label = ImageFont.truetype(FONT_REG, 30)
    f_price       = ImageFont.truetype(FONT_BOLD, 72)
    draw.text((50, 400), 'Chi còn', font=f_price_label, fill=(210, 210, 210))
    draw.text((50, 435), price_str, font=f_price, fill=(255, 255, 255))

    # --- Nút MUA NGAY ---
    btn_y = 560
    btn_text = 'MUA NGAY  \u2192'
    f_btn = ImageFont.truetype(FONT_BOLD, 30)
    btn_w = int(draw.textlength(btn_text, font=f_btn)) + 52
    draw.rounded_rectangle([50, btn_y, 50 + btn_w, btn_y + 60],
                            radius=30, outline=(255, 255, 255), width=3)
    draw.text((50 + 26, btn_y + 14), btn_text, font=f_btn, fill=(255, 255, 255))

    out_path = os.path.join(BANNER_DIR, out_filename)
    img.save(out_path, quality=95)
    print(f"  ✏️  Đã tạo ảnh banner: {out_path}")
    return out_path


def add_banner(title, description, link, img_path):
    start = timezone.now()
    end   = start + timedelta(days=120)
    b = Banner(title=title, description=description, link=link,
               start_at=start, end_at=end, status='True')
    with open(img_path, 'rb') as f:
        b.image.save(os.path.basename(img_path), File(f), save=False)
    b.save()
    print(f"  ✅ Thêm banner: {title}")


def add_product(title, slug, category_id, price, promotion, amount,
                keywords, description, detail, main_img, gallery_imgs=None):
    if Product.objects.filter(slug=slug).exists():
        print(f"  ⚠️  Đã tồn tại: {slug} — bỏ qua")
        return None
    p = Product(
        title=title, slug=slug,
        category_id=category_id,
        price=price, promotion=promotion, amount=amount,
        keywords=keywords, description=description, detail=detail,
        variant='None', status='True',
    )
    with open(os.path.join(IMG_DIR, main_img), 'rb') as f:
        p.image.save(main_img, File(f), save=False)
    p.save()
    if gallery_imgs:
        for gimg in gallery_imgs:
            gi = Images(product=p)
            with open(os.path.join(IMG_DIR, gimg), 'rb') as f:
                gi.image.save(gimg, File(f), save=False)
            gi.save()
    print(f"  ✅ Thêm sản phẩm: {title}")
    return p


# ════════════════════════════════════════════════════════════════
print("\n── BƯỚC 1: Tạo ảnh banner ──")
# ════════════════════════════════════════════════════════════════

make_banner(
    out_filename   = 'banner_zephyrus.jpg',
    badge_text     = 'NÂNG CẤP HIỆU NĂNG',
    title_line1    = 'ROG ZEPHYRUS',
    title_line2    = 'M16 GU603ZX',
    specs          = 'RTX 4090 • Core i9-13900H • Màn 16" QHD+ 240Hz',
    price_str      = '42.990.000\u0111',
    product_img_path = os.path.join(IMG_DIR, '67102_hacom_asus_gaming_rog_zephyrus_gu603zx_5.png'),
)

make_banner(
    out_filename   = 'banner_rtx4080super.jpg',
    badge_text     = 'HOT DEAL',
    title_line1    = 'RTX 4080',
    title_line2    = 'SUPER ROG',
    specs          = '16GB GDDR6X • DLSS 3.5 • Ray Tracing thế hệ mới',
    price_str      = '28.500.000\u0111',
    product_img_path = os.path.join(IMG_DIR, 'lkc.png'),
)

# ════════════════════════════════════════════════════════════════
print("\n── BƯỚC 2: Thêm banner vào DB ──")
# ════════════════════════════════════════════════════════════════

add_banner(
    title       = 'ASUS ROG Zephyrus M16 - Mỏng nhẹ, sức mạnh đỉnh cao',
    description = 'RTX 4090, Core i9-13900H, Màn 16" QHD+ 240Hz - 42.990.000đ',
    link        = '/category/4/laptop',
    img_path    = os.path.join(BANNER_DIR, 'banner_zephyrus.jpg'),
)
add_banner(
    title       = 'ASUS ROG STRIX RTX 4080 SUPER - Sức mạnh tuyệt đỉnh',
    description = '16GB GDDR6X, DLSS 3.5, Ray Tracing thế hệ mới - 28.500.000đ',
    link        = '/category/11/linh-kien',
    img_path    = os.path.join(BANNER_DIR, 'banner_rtx4080super.jpg'),
)

# ════════════════════════════════════════════════════════════════
print("\n── BƯỚC 3: Thêm 2 Laptop ──")
# ════════════════════════════════════════════════════════════════

add_product(
    title       = 'ASUS ROG Zephyrus M16 GU603ZX',
    slug        = 'asus-rog-zephyrus-m16-gu603zx',
    category_id = 6,   # Laptop ASUS
    price       = 42990000, promotion=5, amount=15,
    keywords    = 'ASUS ROG Zephyrus M16 GU603ZX laptop gaming mỏng nhẹ RTX 4090',
    description = 'Laptop gaming cao cấp ASUS ROG Zephyrus M16, mỏng nhẹ nhưng sức mạnh vượt trội với RTX 4090 và Core i9-13900H.',
    detail      = '<p><strong>ASUS ROG Zephyrus M16 GU603ZX</strong> là dòng laptop gaming mỏng nhẹ hàng đầu của ASUS ROG.</p><ul><li>CPU: Intel Core i9-13900H (up to 5.4GHz)</li><li>GPU: NVIDIA GeForce RTX 4090 16GB</li><li>RAM: 32GB DDR5 4800MHz</li><li>Ổ cứng: 2TB SSD NVMe PCIe 4.0</li><li>Màn hình: 16 inch QHD+ (2560x1600) IPS 240Hz</li><li>Trọng lượng: 2.0 kg</li></ul>',
    main_img    = '67102_hacom_asus_gaming_rog_zephyrus_gu603zx_5.png',
    gallery_imgs= ['67102_hacom_asus_gaming_rog_zephyrus_gu603zx_7.png'],
)

add_product(
    title       = 'LENOVO LEGION 7 GEN 6 16ACHg6',
    slug        = 'lenovo-legion-7-gen6-16achg6',
    category_id = 5,   # Laptop Lenovo
    price       = 35500000, promotion=8, amount=10,
    keywords    = 'Lenovo Legion 7 Gen 6 laptop gaming AMD Ryzen',
    description = 'Lenovo Legion 7 Gen 6 - Laptop gaming AMD Ryzen 7 5800H, RTX 3080, màn 16" WQXGA 165Hz.',
    detail      = '<p><strong>Lenovo Legion 7 Gen 6</strong> mang lại hiệu suất gaming cực mạnh với AMD Ryzen.</p><ul><li>CPU: AMD Ryzen 7 5800H (up to 4.4GHz)</li><li>GPU: NVIDIA GeForce RTX 3080 16GB</li><li>RAM: 32GB DDR4 3200MHz</li><li>Ổ cứng: 1TB SSD NVMe PCIe 4.0</li><li>Màn hình: 16 inch WQXGA (2560x1600) IPS 165Hz</li><li>Trọng lượng: 2.4 kg</li></ul>',
    main_img    = '63924_laptop_lenovo_legion_7_1.jpeg',
    gallery_imgs= ['63924_laptop_lenovo_legion_7_6.jpeg', '63924_laptop_lenovo_legion_7_1_IXQyEi5.jpeg'],
)

# ════════════════════════════════════════════════════════════════
print("\n── BƯỚC 4: Thêm 3 Linh kiện ──")
# ════════════════════════════════════════════════════════════════

add_product(
    title       = 'CARD MÀN HÌNH ASUS ROG STRIX RTX 4080 SUPER OC 16GB',
    slug        = 'card-man-hinh-asus-rog-strix-rtx-4080-super-oc',
    category_id = 12,  # VGA
    price       = 28500000, promotion=0, amount=8,
    keywords    = 'ASUS ROG STRIX RTX 4080 SUPER card màn hình VGA gaming',
    description = 'ASUS ROG STRIX GeForce RTX 4080 SUPER OC Edition 16GB GDDR6X - Card đồ họa gaming cao cấp nhất trong phân khúc.',
    detail      = '<p><strong>ASUS ROG STRIX RTX 4080 SUPER OC 16G</strong></p><ul><li>GPU: NVIDIA GeForce RTX 4080 SUPER</li><li>Bộ nhớ: 16GB GDDR6X 256-bit</li><li>Boost Clock: 2625 MHz (OC mode)</li><li>CUDA Cores: 10240</li><li>Bus interface: PCIe 4.0 x16</li><li>Xuất hình: 3x DisplayPort 1.4a, 2x HDMI 2.1</li><li>Công suất TDP: 320W</li></ul>',
    main_img    = 'lkc.png',
    gallery_imgs= ['lkc2.png'],
)

add_product(
    title       = 'CARD MÀN HÌNH ASUS PROART GEFORCE RTX 4080 OC 16GB',
    slug        = 'card-man-hinh-asus-proart-rtx-4080-oc',
    category_id = 12,  # VGA
    price       = 25990000, promotion=5, amount=6,
    keywords    = 'ASUS ProArt RTX 4080 card màn hình đồ họa sáng tạo',
    description = 'ASUS ProArt GeForce RTX 4080 OC 16GB - Thiết kế sang trọng cho cả gaming lẫn sáng tạo nội dung chuyên nghiệp.',
    detail      = '<p><strong>ASUS ProArt GeForce RTX 4080 OC 16G</strong></p><ul><li>GPU: NVIDIA GeForce RTX 4080</li><li>Bộ nhớ: 16GB GDDR6X 256-bit</li><li>Boost Clock: 2565 MHz (OC mode)</li><li>CUDA Cores: 9728</li><li>Bus interface: PCIe 4.0 x16</li><li>Xuất hình: 3x DisplayPort 1.4a, 2x HDMI 2.1</li><li>Thiết kế tinh tế, phù hợp workstation sáng tạo</li></ul>',
    main_img    = '9802-rtx-asus-27.png',
    gallery_imgs= [],
)

add_product(
    title       = 'ASUS ROG STRIX G513RM GAMING LAPTOP',
    slug        = 'asus-rog-strix-g513rm',
    category_id = 6,   # Laptop ASUS
    price       = 28900000, promotion=10, amount=12,
    keywords    = 'ASUS ROG STRIX G513RM laptop gaming AMD Ryzen 9',
    description = 'ASUS ROG STRIX G513RM - Laptop gaming mạnh mẽ với AMD Ryzen 9 6900HX và RTX 3060, thiết kế Eclipse Gray ấn tượng.',
    detail      = '<p><strong>ASUS ROG STRIX G513RM</strong> thiết kế Eclipse Gray cực đẹp.</p><ul><li>CPU: AMD Ryzen 9 6900HX (up to 4.9GHz)</li><li>GPU: NVIDIA GeForce RTX 3060 6GB</li><li>RAM: 16GB DDR5 4800MHz</li><li>Ổ cứng: 512GB SSD NVMe PCIe 4.0</li><li>Màn hình: 15.6 inch FHD 300Hz IPS</li><li>Trọng lượng: 2.3 kg</li></ul>',
    main_img    = '63683_asus_gaming_rog_strix_g513_16.jpeg',
    gallery_imgs= ['63683_asus_gaming_rog_strix_g513_19.jpeg', '63683_asus_gaming_rog_strix_g513_20.jpeg'],
)

# ════════════════════════════════════════════════════════════════
print("\n── BƯỚC 5: Thêm 4 Phụ kiện ──")
# ════════════════════════════════════════════════════════════════

add_product(
    title       = 'CHUỘT GAMING KHÔNG DÂY ASUS ROG GLADIUS III AIMPOINT WHITE',
    slug        = 'chut-gaming-asus-rog-gladius-iii-aimpoint-white',
    category_id = 10,  # Chuột
    price       = 2990000, promotion=0, amount=25,
    keywords    = 'chuột không dây ASUS ROG Gladius III white trắng gaming',
    description = 'ASUS ROG Gladius III Wireless AimPoint White - Phiên bản màu trắng cao cấp, cảm biến AimPoint Pro 36000 DPI.',
    detail      = '<p><strong>ASUS ROG Gladius III Wireless AimPoint White</strong></p><ul><li>Cảm biến: ROG AimPoint Pro 36,000 DPI</li><li>Kết nối: 2.4GHz RF / Bluetooth / USB-C</li><li>Nút: 6 nút lập trình được</li><li>Trọng lượng: 79g</li><li>Pin: đến 62 giờ (BT) / 37 giờ (2.4GHz)</li><li>Màu sắc: Trắng (White)</li></ul>',
    main_img    = '72533_chuot_gaming_khong_day_asus_rog_gladius_iii_wireless_aimpoint_white_90mp02y_C3ffITP.jpg',
    gallery_imgs= ['72533_chuot_gaming_khong_day_asus_rog_gladius_iii_wireless_aimpoint_white_90mp02y_CqN4eQl.jpg'],
)

add_product(
    title       = 'TAI NGHE GAMING STEELSERIES ARCTIS NOVA 7 WIRELESS',
    slug        = 'tai-nghe-gaming-steelseries-arctis-nova-7-wireless',
    category_id = 14,  # Tai nghe
    price       = 3990000, promotion=0, amount=20,
    keywords    = 'tai nghe SteelSeries Arctis Nova 7 wireless gaming',
    description = 'SteelSeries Arctis Nova 7 Wireless - Tai nghe gaming không dây với âm thanh vòm 360° Spatial Audio và mic ClearCast Gen 2.',
    detail      = '<p><strong>SteelSeries Arctis Nova 7 Wireless</strong></p><ul><li>Driver: 40mm Neodymium</li><li>Đáp ứng tần số: 20Hz - 22,000Hz</li><li>Kết nối: 2.4GHz lossless wireless</li><li>Pin: lên đến 38 giờ</li><li>Mic: ClearCast Gen 2 Bidirectional</li><li>Âm thanh vòm: 360° Spatial Audio</li></ul>',
    main_img    = '80461_tai_nghe_steelseries_arctis_nova_7_wireless_dragon_red_gold_limited_edition_sM1MhDx.jpg',
    gallery_imgs= ['80461_tai_nghe_steelseries_arctis_nova_7_wireless_dragon_red_gold_limited_edition_ym5grlG.jpg'],
)

add_product(
    title       = 'BÀN PHÍM CƠ FL-ESPORT Q75 BLUE JELLY 3 MODE',
    slug        = 'ban-phim-fl-esport-q75-blue-jelly-3-mode',
    category_id = 9,   # Bàn phím
    price       = 3499000, promotion=5, amount=18,
    keywords    = 'bàn phím cơ FL-Esport Q75 Blue Jelly 3 Mode không dây',
    description = 'FL-Esport Q75 Blue Jelly - Bàn phím cơ không dây 75%, kết nối 3 mode, gasket mount, phiên bản Blue Jelly.',
    detail      = '<p><strong>FL-Esport Q75 Blue Jelly 3 Mode</strong></p><ul><li>Layout: 75% (84 phím)</li><li>Kết nối: Bluetooth 5.0 / 2.4GHz / USB-C</li><li>Switch: Kailh Box White (linear)</li><li>Mounting: Gasket mount</li><li>Backlit: RGB mỗi phím</li><li>Pin: 4000mAh</li><li>Màu sắc: Blue Jelly</li></ul>',
    main_img    = '81157_ban_phim_co_khong_day_fl_esport_q75_azure_green_3_mode_jellyfish_sw_kailh_box_2.jpg',
    gallery_imgs= ['81157_ban_phim_co_khong_day_fl_esport_q75_azure_green_3_mode_jellyfish_sw_kailh_box_3.jpg'],
)

add_product(
    title       = 'BÀN PHÍM GAMING ASUS ROG AZOTH 75% WIRELESS PBT',
    slug        = 'ban-phim-asus-rog-azoth-75-wireless-pbt',
    category_id = 9,   # Bàn phím
    price       = 6500000, promotion=0, amount=15,
    keywords    = 'bàn phím ASUS ROG Azoth 75% wireless PBT gaming',
    description = 'ASUS ROG Azoth 75% Wireless - Bàn phím gaming 75% không dây cao cấp với keycap PBT double-shot, pre-lube switch ROG NX.',
    detail      = '<p><strong>ASUS ROG Azoth 75% Wireless PBT</strong></p><ul><li>Layout: 75% (82 phím)</li><li>Kết nối: 2.4GHz RF / Bluetooth / USB-C</li><li>Switch: ROG NX Snow (pre-lubed)</li><li>Keycap: PBT double-shot</li><li>Mounting: Gasket mount 3-layer foam</li><li>Pin: đến 2000 giờ (2.4GHz)</li><li>OLED display + control knob</li></ul>',
    main_img    = '77465_ban_phim_gaming_asus_rog_azoth_nxsw_us_pbt_wht_trang___90mp031a_bkua11_2.jpg',
    gallery_imgs= ['77465_ban_phim_gaming_asus_rog_azoth_nxsw_us_pbt_wht_trang___90mp031a_bkua11_3.jpg',
                   '77465_ban_phim_gaming_asus_rog_azoth_nxsw_us_pbt_wht_trang___90mp031a_bkua11_4.jpg'],
)

# ════════════════════════════════════════════════════════════════
print("\n" + "="*55)
print("🎉  HOÀN TẤT!")
total_products = Product.objects.count()
total_banners  = Banner.objects.count()
print(f"   Tổng sản phẩm trong DB: {total_products}")
print(f"   Tổng banner trong DB  : {total_banners}")
print("="*55)