"""
Thêm sản phẩm VỚI ẢNH THẬT từ GearVN / Newegg / Hãng gốc:
  - 1 Mainboard, 1 PSU, 1 VGA, 2 RAM (Linh kiện)
  - 3 Laptop Acer, 3 Laptop Lenovo
Chạy: python add_real_products.py
Yêu cầu: pip install requests (đã có sẵn trong venv)
"""
import os, sys, requests, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
import django; django.setup()

from django.core.files.base import ContentFile
from product.models import Product, Images

_BASE   = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(_BASE, 'uploads', 'images')
os.makedirs(IMG_DIR, exist_ok=True)

# Headers giống Chrome browser thật — giúp vượt hotlink check của CDN
HEADERS_GEARVN = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://gearvn.com/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-fetch-dest': 'image',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'cross-site',
}
HEADERS_NEWEGG = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.newegg.com/',
    'sec-fetch-dest': 'image',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-site',
}
HEADERS_ASUS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Referer': 'https://www.asus.com/',
    'sec-fetch-dest': 'image', 'sec-fetch-mode': 'no-cors', 'sec-fetch-site': 'same-site',
}
HEADERS_KINGSTON = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Referer': 'https://www.kingston.com/',
    'sec-fetch-dest': 'image', 'sec-fetch-mode': 'no-cors', 'sec-fetch-site': 'same-site',
}
HEADERS_ACER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Referer': 'https://store.acer.com/',
    'sec-fetch-dest': 'image', 'sec-fetch-mode': 'no-cors', 'sec-fetch-site': 'same-site',
}
HEADERS_LENOVO = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Referer': 'https://www.lenovo.com/',
    'sec-fetch-dest': 'image', 'sec-fetch-mode': 'no-cors', 'sec-fetch-site': 'same-site',
}

# ── Ảnh thật — mỗi file có danh sách URL (thử theo thứ tự, dùng cái đầu thành công)
# Nguồn ưu tiên: GearVN CDN, Newegg CDN, ASUS/Kingston/Acer/Lenovo CDN
# Mọi CDN đều hoạt động bình thường khi chạy từ IP nhà (residential),
# nhưng có thể block IP datacenter. Script thử nhiều nguồn để tăng tỉ lệ thành công.
IMAGES = {
    # ── Linh kiện ──
    'mb_msi_z790_tomahawk.jpg': [
        (HEADERS_GEARVN,  'https://product.hstatic.net/200000722513/product/msi-mag-z790-tomahawk-wifi_ac7449a3b5754dc5ba0a99b311ef6b8b_de489e81b5104e2a93c3bab8a4d4127b_grande.jpg'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/13-144-567-17.png'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/13-144-567-02.jpg'),
    ],
    'psu_corsair_rm750x_white.jpg': [
        (HEADERS_GEARVN,  'https://product.hstatic.net/200000722513/product/inh-corsair-rm750x-white-80-plus-gold_8f0f4b35ef2b47acbb3552955f64f258_4e15c42699744a8585796fd175f4daba_grande.jpg'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/17-139-326-06.png'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/17-139-326-01.png'),
    ],
    'vga_asus_dual_rtx4060_oc.jpg': [
        (HEADERS_GEARVN,  'https://product.hstatic.net/200000722513/product/dual-rtx4060-o8g-01_4aac0e1328c74e9fb308a2a9113cfcc0_grande.jpg'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/14-126-665-01.jpg'),
        (HEADERS_ASUS,    'https://dlcdnwebimgs.asus.com/gain/5115cf8f-23b5-4e3c-a147-561a4764bfa3/w800'),
    ],
    'ram_kingston_fury_beast_ddr5.jpg': [
        (HEADERS_GEARVN,   'https://product.hstatic.net/200000722513/product/kt_21e4b29cfb884502a80947468b28691c_504652cca912458380820172402d1928_grande.jpg'),
        (HEADERS_KINGSTON, 'https://media.kingston.com/kingston/product/ktc-product-memory-ddr5-fury-beast-rgb-black-1.png'),
        (HEADERS_KINGSTON, 'https://media.kingston.com/kingston/key-features/ktc-keyfeatures-memory-beast-ddr5-rgb-1-lg.jpg'),
    ],
    'ram_corsair_vengeance_rgb_ddr5.png': [
        (HEADERS_GEARVN,  'https://product.hstatic.net/200000722513/product/gearvn-corsair-vengeance-rgb-ddr-5600-ddr5-6_e6d7b18ac5ef482c9459e38f10add37f_grande.png'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/20-236-918-01.jpg'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/20-236-918-02.jpg'),
    ],
    # ── Laptop Acer ──
    'laptop_acer_nitro5_an515_58.png': [
        (HEADERS_GEARVN, 'https://product.hstatic.net/200000722513/product/nitro-5-tiger_221e0f1045724a01afa55afa2ed821a1_grande.png'),
        (HEADERS_ACER,   'https://static.acer.com/up/Resource/Acer/Laptops/Nitro_5/Images/20220524/AN515-58-52R4-01.png'),
        (HEADERS_NEWEGG, 'https://c1.neweggimages.com/productimage/nb640/34-316-354-01.jpg'),
    ],
    'laptop_acer_helios_neo_phn16.png': [
        (HEADERS_GEARVN, 'https://product.hstatic.net/200000722513/product/05a3b4354b5a27555f4510780_large_19db3dd766fa42f1983f345b05bf6887_large_b12e91a08927490d9905ca9ea507ce62_grande.png'),
        (HEADERS_ACER,   'https://static.acer.com/up/Resource/Acer/Laptops/Predator_Helios_Neo/Images/20230323/PHN16-71-76RU-01.png'),
        (HEADERS_NEWEGG, 'https://c1.neweggimages.com/productimage/nb640/34-316-389-01.jpg'),
    ],
    'laptop_acer_swift_x14_sfx14.png': [
        (HEADERS_GEARVN, 'https://product.hstatic.net/200000722513/product/ava_426f720508c745cbb130c469ae257efc_grande.png'),
        (HEADERS_ACER,   'https://static.acer.com/up/Resource/Acer/Laptops/Swift_X_14/Images/20230323/SFX14-71G-78SY-01.png'),
        (HEADERS_NEWEGG, 'https://c1.neweggimages.com/productimage/nb640/34-316-387-01.jpg'),
    ],
    # ── Laptop Lenovo ──
    'laptop_lenovo_loq_15aph8.png': [
        (HEADERS_GEARVN,  'https://product.hstatic.net/200000722513/product/82xt00btvn_555050c06a2d44d1b7b0b5bcbfb18eb6_grande.png'),
        (HEADERS_LENOVO,  'https://p4-ofp.static.pub/fes/cms/2023/05/05/rjxhvqahm3uh3a65l2rba9m6etafcr690780.png'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/34-152-354-01.jpg'),
    ],
    'laptop_lenovo_ideapad_gaming3.png': [
        (HEADERS_GEARVN,  'https://product.hstatic.net/200000722513/product/82k2027qvn_d2f65bf202be4bbf871858de1ff32eb8_grande.png'),
        (HEADERS_LENOVO,  'https://p4-ofp.static.pub/fes/cms/2021/10/22/c8hj7k0pfm6pfkm2k3o3iqjlhgmpef695617.png'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/34-152-310-01.jpg'),
    ],
    'laptop_lenovo_legion5_15ach6.png': [
        (HEADERS_GEARVN,  'https://product.hstatic.net/200000722513/product/legion_5_15ach6_82jw0038vn-1_2e68be2e6f7b48b5a428b2d14b8447d5_36dd29e2a8f44627b486b97cc8f81476_grande.png'),
        (HEADERS_LENOVO,  'https://p4-ofp.static.pub/fes/cms/2021/10/20/qidfr3o2v8cz5njbdg2bqzgnbdx0be985979.png'),
        (HEADERS_NEWEGG,  'https://c1.neweggimages.com/productimage/nb640/34-152-295-01.jpg'),
    ],
}


def download_image(filename, url_list):
    """Thử từng URL trong danh sách, dùng cái đầu tiên tải thành công."""
    path = os.path.join(IMG_DIR, filename)
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        print(f"  ✅ Đã có: {filename}")
        return filename
    for i, (headers, url) in enumerate(url_list):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200 and len(r.content) > 5000:
                with open(path, 'wb') as f:
                    f.write(r.content)
                print(f"  ⬇️  Tải về: {filename} ({len(r.content)//1024} KB) [nguồn {i+1}]")
                time.sleep(0.3)
                return filename
            else:
                print(f"  ⚠️  Nguồn {i+1} lỗi {r.status_code} — thử tiếp...")
        except Exception as e:
            print(f"  ⚠️  Nguồn {i+1} exception: {e} — thử tiếp...")
    print(f"  ❌ Không tải được {filename} từ {len(url_list)} nguồn")
    return None


def add_product(title, slug, category_id, price, promotion, amount,
                keywords, description, detail, img_filename):
    if Product.objects.filter(slug=slug).exists():
        print(f"  ⚠️  Tồn tại rồi: {slug}")
        return None
    path = os.path.join(IMG_DIR, img_filename)
    if not os.path.exists(path) or os.path.getsize(path) < 5000:
        print(f"  ❌ Không có ảnh cho {slug} — bỏ qua")
        return None
    p = Product(title=title, slug=slug, category_id=category_id,
                price=price, promotion=promotion, amount=amount,
                keywords=keywords, description=description, detail=detail,
                variant='None', status='True')
    with open(path, 'rb') as f:
        p.image.save(img_filename, f, save=False)
    p.save()
    print(f"  ✅ {title}")
    return p


# ════════════════════════════════════════════════════════════════
print('\n── BƯỚC 1: Tải ảnh thật ──')
ok_imgs = {}
for fname, url_list in IMAGES.items():
    result = download_image(fname, url_list)
    ok_imgs[fname] = result is not None

ok_count = sum(ok_imgs.values())
print(f"\n  → Kết quả: {ok_count}/{len(ok_imgs)} ảnh tải thành công")
if ok_count < len(ok_imgs):
    failed = [f for f, ok in ok_imgs.items() if not ok]
    print(f"  ⚠️  Các ảnh CHƯA tải được: {failed}")
    print(f"  ℹ️  Sản phẩm có ảnh chưa tải sẽ bị bỏ qua (không thêm vào DB).")
    print(f"  ℹ️  Hãy thử chạy lại script — thường là do IP datacenter bị chặn,")
    print(f"      chạy từ máy nhà Windows sẽ thành công.")
    if ok_count == 0:
        print("\n  ❌ Không tải được ảnh nào! Dừng lại.")
        sys.exit(1)


# ════════════════════════════════════════════════════════════════
print('\n── BƯỚC 2: Thêm 4 Linh kiện ──')
# ════════════════════════════════════════════════════════════════

add_product(
    title='MAINBOARD MSI MAG Z790 TOMAHAWK WIFI DDR5',
    slug='mainboard-msi-mag-z790-tomahawk-wifi-ddr5',
    category_id=16, price=7990000, promotion=0, amount=12,
    keywords='Mainboard MSI MAG Z790 TOMAHAWK WIFI DDR5 Intel LGA1700',
    description='MSI MAG Z790 TOMAHAWK WIFI DDR5 - Bo mạch chủ ATX cao cấp cho Intel Gen 12/13/14, PCIe 5.0, DDR5, WiFi 6E.',
    detail='<p><strong>MSI MAG Z790 TOMAHAWK WIFI DDR5</strong></p><ul><li>Socket: Intel LGA1700 (Gen 12/13/14)</li><li>Chipset: Intel Z790</li><li>RAM: 4x DDR5 (max 128GB, up to 7200+ MHz OC)</li><li>PCIe: 1x PCIe 5.0 x16, 1x PCIe 4.0 x16</li><li>M.2: 4x M.2 (PCIe 4.0 Gen4 với M.2 Shield Frozr)</li><li>Network: 2.5G LAN + Intel WiFi 6E</li><li>USB: 1x USB 3.2 Gen2x2 Type-C (20Gbps)</li><li>Form factor: ATX | 6-layer PCB</li></ul>',
    img_filename='mb_msi_z790_tomahawk.jpg',
)

add_product(
    title='NGUỒN CORSAIR RM750X WHITE 80+ GOLD FULL MODULAR 750W',
    slug='nguon-corsair-rm750x-white-750w-80-plus-gold',
    category_id=18, price=2990000, promotion=17, amount=20,
    keywords='Nguồn Corsair RM750x White 750W 80+ Gold Full Modular PSU trắng',
    description='Corsair RM750x White 750W 80+ Gold Full Modular - Nguồn máy tính màu trắng cao cấp, Semi-Fanless mode, bảo hành 10 năm.',
    detail='<p><strong>Corsair RM750x White 750W</strong></p><ul><li>Công suất: 750W</li><li>Hiệu suất: 80+ Gold (>90%)</li><li>Modular: Full Modular</li><li>Màu sắc: Trắng (White)</li><li>Quạt: 135mm, Semi-Fanless (tắt quạt khi tải nhẹ)</li><li>ATX 3.0 / PCIe 5.0 ready</li><li>Bảo hành: 10 năm</li></ul>',
    img_filename='psu_corsair_rm750x_white.jpg',
)

add_product(
    title='CARD MÀN HÌNH ASUS DUAL GEFORCE RTX 4060 OC EDITION 8GB GDDR6',
    slug='vga-asus-dual-rtx4060-oc-8gb-gddr6',
    category_id=12, price=8790000, promotion=12, amount=10,
    keywords='Card màn hình ASUS Dual RTX 4060 OC 8GB VGA gaming 1080p 1440p',
    description='ASUS Dual GeForce RTX 4060 OC Edition 8GB - Card đồ họa gaming tầm trung mạnh mẽ, DLSS 3, Ray Tracing, 2 quạt Axial-tech.',
    detail='<p><strong>ASUS Dual GeForce RTX 4060 OC Edition 8GB</strong></p><ul><li>GPU: NVIDIA GeForce RTX 4060 (Ada Lovelace)</li><li>VRAM: 8GB GDDR6 128-bit</li><li>Boost Clock: 2490 MHz (OC mode)</li><li>CUDA Cores: 3072</li><li>PCIe: 4.0 x16</li><li>Xuất hình: 1x HDMI 2.1, 3x DisplayPort 1.4a</li><li>Công suất TDP: 115W</li><li>Kích thước: 2.5-slot, 227mm</li></ul>',
    img_filename='vga_asus_dual_rtx4060_oc.jpg',
)

add_product(
    title='RAM KINGSTON FURY BEAST RGB 32GB (2x16GB) DDR5 5600MHz CL40',
    slug='ram-kingston-fury-beast-rgb-ddr5-32gb-5600mhz',
    category_id=13, price=3990000, promotion=0, amount=25,
    keywords='RAM Kingston Fury Beast RGB DDR5 32GB 5600MHz XMP 3.0 gaming',
    description='Kingston Fury Beast RGB 32GB DDR5 5600MHz - Bộ nhớ gaming hiệu năng cao, XMP 3.0, LED RGB sinh động với Infrared Sync Technology.',
    detail='<p><strong>Kingston Fury Beast RGB 32GB DDR5</strong></p><ul><li>Dung lượng: 32GB (Kit 2x16GB)</li><li>Bus: DDR5-5600 (PC5-44800)</li><li>Timing: CL40</li><li>Điện áp: 1.25V</li><li>XMP 3.0 / EXPO</li><li>LED RGB với Infrared Sync Technology</li><li>On-Die ECC (ODECC) ổn định</li></ul>',
    img_filename='ram_kingston_fury_beast_ddr5.jpg',
)

add_product(
    title='RAM CORSAIR VENGEANCE RGB 32GB (2x16GB) DDR5 5600MHz CL40',
    slug='ram-corsair-vengeance-rgb-ddr5-32gb-5600mhz',
    category_id=13, price=6690000, promotion=0, amount=15,
    keywords='RAM Corsair Vengeance RGB DDR5 32GB 5600MHz iCUE gaming đen',
    description='Corsair Vengeance RGB 32GB DDR5 5600MHz - RAM gaming DDR5 cao cấp, đèn RGB 10 vùng điều khiển qua iCUE, chip Samsung hàng đầu.',
    detail='<p><strong>Corsair Vengeance RGB 32GB DDR5</strong></p><ul><li>Dung lượng: 32GB (Kit 2x16GB)</li><li>Bus: DDR5-5600 (PC5-44800)</li><li>Timing: CL40</li><li>Điện áp: 1.25V</li><li>XMP 3.0</li><li>LED RGB 10 vùng điều khiển qua Corsair iCUE</li><li>Chip DRAM từ Samsung hàng đầu</li></ul>',
    img_filename='ram_corsair_vengeance_rgb_ddr5.png',
)


# ════════════════════════════════════════════════════════════════
print('\n── BƯỚC 3: Thêm 3 Laptop Acer ──')
# ════════════════════════════════════════════════════════════════

add_product(
    title='LAPTOP GAMING ACER NITRO 5 TIGER AN515-58-5935',
    slug='laptop-acer-nitro5-tiger-an515-58-5935',
    category_id=8, price=26990000, promotion=0, amount=15,
    keywords='Laptop Acer Nitro 5 Tiger AN515-58 i5-12450H RTX 4050 gaming',
    description='Acer Nitro 5 Tiger AN515-58-5935 - Laptop gaming tầm trung với i5-12450H và RTX 4050, màn 15.6" FHD IPS 144Hz, thiết kế đậm chất gaming.',
    detail='<p><strong>Acer Nitro 5 Tiger AN515-58-5935</strong></p><ul><li>CPU: Intel Core i5-12450H (up to 4.4GHz, 8 nhân)</li><li>GPU: NVIDIA GeForce RTX 4050 6GB GDDR6</li><li>RAM: 8GB DDR5 4800MHz (2 khe, max 32GB)</li><li>SSD: 512GB NVMe PCIe 4.0</li><li>Màn: 15.6" FHD IPS 144Hz</li><li>Tản nhiệt: Dual Fan, 4 ống xả</li><li>Pin: 57.5Wh | Trọng lượng: 2.5kg</li></ul>',
    img_filename='laptop_acer_nitro5_an515_58.png',
)

add_product(
    title='LAPTOP GAMING ACER PREDATOR HELIOS NEO PHN16-71-54CD',
    slug='laptop-acer-predator-helios-neo-phn16-71-54cd',
    category_id=8, price=24990000, promotion=0, amount=8,
    keywords='Laptop Acer Predator Helios Neo PHN16-71 i5-13500HX RTX 4050 gaming cao cấp',
    description='Acer Predator Helios Neo PHN16-71-54CD - Dòng laptop gaming cao cấp nhà Predator, i5-13500HX, RTX 4050, màn 16" WQXGA 165Hz 100% sRGB.',
    detail='<p><strong>Acer Predator Helios Neo PHN16-71-54CD</strong></p><ul><li>CPU: Intel Core i5-13500HX (up to 4.7GHz)</li><li>GPU: NVIDIA GeForce RTX 4050 6GB GDDR6</li><li>RAM: 8GB DDR5 (2 khe, max 32GB)</li><li>SSD: 512GB NVMe PCIe 4.0</li><li>Màn: 16" WQXGA (2560x1600) IPS 165Hz, 100% sRGB</li><li>Tản nhiệt: 2 quạt AeroBlade 3D Gen 5</li><li>Trọng lượng: 2.8kg</li></ul>',
    img_filename='laptop_acer_helios_neo_phn16.png',
)

add_product(
    title='LAPTOP ACER SWIFT X14 SFX14-71G-78SY (I7-13700H/ RTX 4050/ OLED 2K)',
    slug='laptop-acer-swift-x14-sfx14-71g-78sy',
    category_id=8, price=32990000, promotion=5, amount=7,
    keywords='Laptop Acer Swift X14 mỏng nhẹ sáng tạo OLED RTX 4050 32GB',
    description='Acer Swift X14 SFX14-71G-78SY - Laptop mỏng nhẹ 1.5kg cho sáng tạo nội dung, i7-13700H, RTX 4050, màn 14.5" OLED 2.8K 120Hz.',
    detail='<p><strong>Acer Swift X14 SFX14-71G-78SY</strong></p><ul><li>CPU: Intel Core i7-13700H (up to 5.0GHz, 14 nhân)</li><li>GPU: NVIDIA RTX 4050 6GB GDDR6</li><li>RAM: 32GB LPDDR5 (onboard)</li><li>SSD: 1TB NVMe PCIe 4.0</li><li>Màn: 14.5" OLED WQXGA+ (2880x1800) 120Hz, 100% DCI-P3</li><li>Intel Evo certified | Thunderbolt 4</li><li>Trọng lượng: 1.5kg</li></ul>',
    img_filename='laptop_acer_swift_x14_sfx14.png',
)


# ════════════════════════════════════════════════════════════════
print('\n── BƯỚC 4: Thêm 3 Laptop Lenovo ──')
# ════════════════════════════════════════════════════════════════

add_product(
    title='LAPTOP GAMING LENOVO LOQ 15APH8 82XT00BTVN (R7-7745HX/ RTX 4060/ 16GB)',
    slug='laptop-lenovo-loq-15aph8-82xt00btvn',
    category_id=5, price=23490000, promotion=13, amount=18,
    keywords='Laptop Lenovo LOQ 15APH8 Ryzen 7 RTX 4060 gaming tầm trung giá tốt',
    description='Lenovo LOQ 15APH8 - Laptop gaming tầm trung cấu hình cao: Ryzen 7 7745HX + RTX 4060, RAM 16GB DDR5, màn 15.6" FHD 144Hz.',
    detail='<p><strong>Lenovo LOQ 15APH8 82XT00BTVN</strong></p><ul><li>CPU: AMD Ryzen 7 7745HX (up to 5.1GHz, 8 nhân)</li><li>GPU: NVIDIA GeForce RTX 4060 8GB GDDR6</li><li>RAM: 16GB DDR5 5600MHz (2 khe, max 64GB)</li><li>SSD: 512GB NVMe PCIe 4.0</li><li>Màn: 15.6" FHD IPS 144Hz, 45% NTSC</li><li>Pin: 60Wh, sạc 230W</li><li>Trọng lượng: 2.4kg</li></ul>',
    img_filename='laptop_lenovo_loq_15aph8.png',
)

add_product(
    title='LAPTOP GAMING LENOVO IDEAPAD GAMING 3 15ACH6 82K2027QVN (R5-5500H/ RTX 2050)',
    slug='laptop-lenovo-ideapad-gaming-3-15ach6-82k2027qvn',
    category_id=5, price=15990000, promotion=11, amount=20,
    keywords='Laptop Lenovo IdeaPad Gaming 3 15ACH6 Ryzen 5 RTX 2050 entry gaming giá rẻ',
    description='Lenovo IdeaPad Gaming 3 15ACH6 - Laptop gaming entry tầm trung tốt nhất cho sinh viên, Ryzen 5 5500H + RTX 2050, màn 144Hz.',
    detail='<p><strong>Lenovo IdeaPad Gaming 3 15ACH6</strong></p><ul><li>CPU: AMD Ryzen 5 5500H (up to 4.2GHz)</li><li>GPU: NVIDIA GeForce RTX 2050 4GB GDDR6</li><li>RAM: 8GB DDR4 3200MHz (1 khe, max 16GB)</li><li>SSD: 512GB NVMe PCIe 3.0</li><li>Màn: 15.6" FHD IPS 144Hz</li><li>Pin: 45Wh | Trọng lượng: 2.2kg</li></ul>',
    img_filename='laptop_lenovo_ideapad_gaming3.png',
)

add_product(
    title='LAPTOP GAMING LENOVO LEGION 5 15ACH6 82JW0038VN (R5-5600H/ RTX 3050Ti)',
    slug='laptop-lenovo-legion-5-15ach6-82jw0038vn',
    category_id=5, price=22990000, promotion=0, amount=12,
    keywords='Laptop Lenovo Legion 5 15ACH6 Ryzen 5 RTX 3050 Ti Phantom Blue',
    description='Lenovo Legion 5 15ACH6 - Laptop gaming dòng Legion cao cấp, Ryzen 5 5600H + RTX 3050 Ti, thiết kế hợp kim nhôm màu Phantom Blue.',
    detail='<p><strong>Lenovo Legion 5 15ACH6 82JW0038VN</strong></p><ul><li>CPU: AMD Ryzen 5 5600H (up to 4.2GHz, 6 nhân)</li><li>GPU: NVIDIA RTX 3050 Ti 4GB GDDR6</li><li>RAM: 8GB DDR4 3200MHz (2 khe, max 32GB)</li><li>SSD: 512GB NVMe PCIe 4.0</li><li>Màn: 15.6" FHD IPS 144Hz</li><li>Legion Coldfront 3.0 tản nhiệt cao cấp</li><li>Vỏ hợp kim nhôm màu Phantom Blue</li></ul>',
    img_filename='laptop_lenovo_legion5_15ach6.png',
)


# ════════════════════════════════════════════════════════════════
from product.models import Product as P
print(f'\n{"="*60}')
print(f'🎉 HOÀN TẤT! Tổng sản phẩm: {P.objects.count()}')
for cat, cid in [('Laptop Acer',8),('Laptop Lenovo',5),
                  ('Mainboard',16),('PSU',18),('VGA',12),('RAM',13)]:
    print(f'  {cat:<20}: {P.objects.filter(category_id=cid).count()} SP')
print(f'{"="*60}')
