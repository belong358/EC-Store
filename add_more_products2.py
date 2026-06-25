"""
Thêm đợt 2:
  - 4 Linh kiện: 1 CPU + 1 Mainboard + 1 PSU + 1 RAM
  - 6 Ổ Cứng (NVMe/SATA/HDD đa dạng)
  - 6 Laptop Acer/Lenovo
  - 3 Laptop ASUS
Chạy: python add_more_products2.py
"""
import os, math
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elestore.settings')
import django; django.setup()

from PIL import Image, ImageDraw, ImageFont
from django.core.files import File
from product.models import Product, Images

_BASE     = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = os.path.join(_BASE, 'static', 'fonts', 'pdf', 'DejaVuSans-Bold.ttf')
FONT_REG  = os.path.join(_BASE, 'static', 'fonts', 'pdf', 'DejaVuSans.ttf')
IMG_DIR   = os.path.join(_BASE, 'uploads', 'images')

# ─── PIL helpers ────────────────────────────────────────────────────────────

def _fonts(sizes):
    return {s: ImageFont.truetype(FONT_BOLD, s) for s in sizes}

def _reg_fonts(sizes):
    return {s: ImageFont.truetype(FONT_REG, s) for s in sizes}


def make_laptop_image(out_name, brand, line1, line2, specs, color_accent=(209, 0, 36)):
    """Ảnh laptop 800×800 với màn hình giả lập."""
    W = H = 800
    img  = Image.new('RGB', (W, H), (15, 15, 22))
    draw = ImageDraw.Draw(img)
    fb   = _fonts([24, 38, 56, 70])
    fr   = _reg_fonts([28])

    # Gradient nền nhẹ
    for y in range(H):
        t = y / H
        r = int(15 + 10 * t); g = int(15 + 8 * t); b = int(22 + 18 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # ── Hình laptop giả lập ──
    # Phần màn (nắp)
    sx, sy, sw, sh = 100, 60, 600, 380
    draw.rounded_rectangle([sx, sy, sx+sw, sy+sh], radius=12,
                            fill=(25, 25, 35), outline=(60, 60, 80), width=3)
    # Màn hình (nội dung)
    mx, my, mw, mh = sx+18, sy+14, sw-36, sh-28
    draw.rounded_rectangle([mx, my, mx+mw, my+mh], radius=6, fill=(8, 8, 14))
    # Brand logo giả trên màn
    brand_tw = int(draw.textlength(brand, font=fb[38]))
    draw.text((mx + (mw - brand_tw)//2, my + mh//2 - 30), brand,
              font=fb[38], fill=color_accent)

    # Bản lề
    draw.rectangle([sx+20, sy+sh, sx+sw-20, sy+sh+8], fill=(40, 40, 55))
    # Bàn phím (thân)
    kx, ky, kw, kh = sx-30, sy+sh+8, sw+60, 160
    draw.rounded_rectangle([kx, ky, kx+kw, ky+kh], radius=8,
                            fill=(20, 20, 30), outline=(50, 50, 70), width=2)
    # Phím giả
    for row in range(3):
        for col in range(14):
            px_ = kx + 30 + col * 38
            py_ = ky + 20 + row * 38
            draw.rounded_rectangle([px_, py_, px_+30, py_+28],
                                    radius=4, fill=(30, 30, 45), outline=(50,50,70), width=1)
    # Touchpad giả
    tp_w, tp_h = 160, 90
    draw.rounded_rectangle([kx+kw//2-tp_w//2, ky+kh-tp_h-10,
                             kx+kw//2+tp_w//2, ky+kh-10],
                            radius=6, fill=(28, 28, 42), outline=(55,55,75), width=1)

    # ── Text thông tin ──
    y0 = sy + sh + kh + 28
    bw_ = int(draw.textlength(brand, font=fb[24])) + 24
    draw.rounded_rectangle([50, y0, 50+bw_, y0+36], radius=18, fill=color_accent)
    draw.text((62, y0+6), brand, font=fb[24], fill=(255,255,255))

    draw.text((50, y0+50), line1, font=fb[56], fill=(255,255,255))
    draw.text((50, y0+112), line2, font=fb[38], fill=color_accent)
    draw.text((50, y0+162), specs, font=fr[28], fill=(170,170,190))

    out_path = os.path.join(IMG_DIR, out_name)
    img.save(out_path, quality=95)
    print(f"  ✏️  Laptop img: {out_name}")
    return out_name


def make_component_image(out_name, brand, model, category_type, color_accent):
    """Ảnh linh kiện (CPU/MB/PSU/RAM/SSD/HDD) 800×800."""
    W = H = 800
    img  = Image.new('RGB', (W, H), (14, 14, 22))
    draw = ImageDraw.Draw(img)
    fb   = _fonts([22, 34, 52, 66])
    fr   = _reg_fonts([26, 30])

    # Gradient
    for y in range(H):
        v = int(14 + 12 * y / H)
        draw.line([(0,y),(W,y)], fill=(v, v, v+8))

    # Viền bo
    draw.rounded_rectangle([18, 18, W-18, H-18], radius=28,
                            outline=color_accent, width=2)

    # Badge loại linh kiện
    bw_ = int(draw.textlength(category_type, font=fb[22])) + 28
    draw.rounded_rectangle([50, 50, 50+bw_, 88], radius=20, fill=color_accent)
    draw.text((64, 58), category_type, font=fb[22], fill=(255,255,255))

    # Vẽ hình minh họa theo loại
    if category_type == 'CPU':
        # Chip vuông
        cx, cy, cs = 320, 180, 160
        draw.rounded_rectangle([cx, cy, cx+cs, cy+cs], radius=12,
                                fill=(28,28,42), outline=color_accent, width=3)
        for i in range(4): # chân
            for j in range(6):
                draw.rectangle([cx+10+j*25, cy+cs+2, cx+10+j*25+8, cy+cs+20], fill=(100,100,120))
                draw.rectangle([cx+10+j*25, cy-20, cx+10+j*25+8, cy-2], fill=(100,100,120))
        draw.text((cx+18, cy+60), 'CPU', font=fb[52], fill=color_accent)

    elif category_type == 'Mainboard':
        # PCB hình chữ nhật
        draw.rounded_rectangle([60, 140, W-60, 480], radius=8,
                                fill=(18,38,18), outline=(0,180,0), width=2)
        for i in range(3): # PCIe slots
            draw.rectangle([80, 200+i*70, 580, 225+i*70], fill=(30,60,30), outline=(0,150,0), width=1)
        for i in range(4): # RAM slots
            draw.rectangle([620, 145+i*60, 650, 195+i*60], fill=(20,50,20), outline=(0,200,0), width=1)

    elif category_type == 'PSU':
        # Hộp vuông PSU
        draw.rounded_rectangle([100, 150, W-100, 460], radius=16,
                                fill=(22,22,32), outline=color_accent, width=3)
        # Quạt
        cx_, cy_ = W//2, 305
        draw.ellipse([cx_-90, cy_-90, cx_+90, cy_+90], outline=(80,80,100), width=2)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = cx_ + int(30*math.cos(rad)); y1 = cy_ + int(30*math.sin(rad))
            x2 = cx_ + int(80*math.cos(rad)); y2 = cy_ + int(80*math.sin(rad))
            draw.line([(x1,y1),(x2,y2)], fill=color_accent, width=3)
        # Dây modular
        for i in range(5):
            draw.rectangle([120+i*70, 420, 160+i*70, 465], fill=(30,30,45), outline=(70,70,90), width=1)

    elif category_type == 'RAM':
        # RAM stick
        draw.rounded_rectangle([80, 200, W-80, 420], radius=6,
                                fill=(20,20,32), outline=color_accent, width=2)
        # LED RGB
        for i in range(16):
            hue = i * 22.5
            r_ = int(127+127*math.cos(math.radians(hue)))
            g_ = int(127+127*math.cos(math.radians(hue+120)))
            b_ = int(127+127*math.cos(math.radians(hue+240)))
            x_ = 92 + i * 40
            draw.rounded_rectangle([x_, 205, x_+30, 240], radius=4, fill=(r_,g_,b_))
        # Chip RAM
        for i in range(8):
            draw.rounded_rectangle([92+i*80, 260, 150+i*80, 360],
                                    radius=4, fill=(30,30,45), outline=(70,70,90), width=1)
        # Chân
        for i in range(40):
            draw.rectangle([90+i*17, 415, 98+i*17, 435], fill=(180,160,0))

    elif category_type in ('SSD NVMe', 'SSD SATA'):
        draw.rounded_rectangle([100, 220, W-100, 420], radius=10,
                                fill=(22,22,35), outline=color_accent, width=2)
        for i in range(3):
            draw.rounded_rectangle([130+i*200, 250, 290+i*200, 390],
                                    radius=6, fill=(30,30,48), outline=(60,60,80), width=1)
        draw.text((300, 295), category_type.split()[1], font=fb[34], fill=color_accent)

    else:  # HDD
        draw.ellipse([160, 140, W-160, H-300], fill=(22,22,35), outline=color_accent, width=3)
        draw.ellipse([260, 240, W-260, H-400], fill=(30,30,48), outline=(60,60,80), width=2)
        for i in range(8):
            angle = math.radians(i * 45)
            x1_ = W//2 + int(80*math.cos(angle)); y1_ = 320 + int(80*math.sin(angle))
            x2_ = W//2 + int(150*math.cos(angle)); y2_ = 320 + int(150*math.sin(angle))
            draw.line([(x1_,y1_),(x2_,y2_)], fill=color_accent, width=2)
        draw.text((W//2 - 30, 300), 'HDD', font=fb[34], fill=color_accent)

    # Tên sản phẩm
    y0 = 490
    bw_ = int(draw.textlength(brand, font=fb[22])) + 24
    draw.rounded_rectangle([50, y0, 50+bw_, y0+36], radius=18, fill=color_accent)
    draw.text((62, y0+6), brand, font=fb[22], fill=(255,255,255))
    draw.text((50, y0+48), model, font=fb[52], fill=(255,255,255))

    out_path = os.path.join(IMG_DIR, out_name)
    img.save(out_path, quality=95)
    print(f"  ✏️  Component img: {out_name}")
    return out_name


def add_product(title, slug, category_id, price, promotion, amount,
                keywords, description, detail, main_img, gallery_imgs=None):
    if Product.objects.filter(slug=slug).exists():
        print(f"  ⚠️  Đã tồn tại: {slug} — bỏ qua")
        return None
    p = Product(title=title, slug=slug, category_id=category_id,
                price=price, promotion=promotion, amount=amount,
                keywords=keywords, description=description, detail=detail,
                variant='None', status='True')
    with open(os.path.join(IMG_DIR, main_img), 'rb') as f:
        p.image.save(main_img, File(f), save=False)
    p.save()
    for gimg in (gallery_imgs or []):
        gi = Images(product=p)
        with open(os.path.join(IMG_DIR, gimg), 'rb') as f:
            gi.image.save(gimg, File(f), save=False)
        gi.save()
    print(f"  ✅ {title}")
    return p


# ════════════════════════════════════════════════════════════════
print('\n── Sinh ảnh PIL ──')
# ════════════════════════════════════════════════════════════════
# Linh kiện
make_component_image('cpu_amd_ryzen9_7950x.png',   'AMD',     '7950X',    'CPU',       (237, 28, 36))
make_component_image('mb_msi_mag_b760m.png',        'MSI',     'MAG B760M','Mainboard', (200, 0, 0))
make_component_image('psu_seasonic_focus850.png',   'Seasonic','Focus 850','PSU',       (255, 165, 0))
make_component_image('ram_gskill_trident_z5.png',   'G.SKILL', 'Trident Z5','RAM',      (0, 180, 80))
# Ổ cứng
make_component_image('ssd_crucial_p3plus.png',      'Crucial', 'P3 Plus',  'SSD NVMe',  (0, 140, 220))
make_component_image('ssd_seagate_firecuda.png',    'Seagate', 'FireCuda', 'SSD NVMe',  (0, 180, 100))
make_component_image('ssd_samsung870evo.png',       'Samsung', '870 EVO',  'SSD SATA',  (14, 125, 255))
make_component_image('ssd_crucial_mx500.png',       'Crucial', 'MX500',    'SSD SATA',  (0, 140, 220))
make_component_image('hdd_seagate_barracuda.png',   'Seagate', 'Barracuda','HDD',       (60, 180, 60))
make_component_image('hdd_wd_blue.png',             'WD',      'Blue',     'HDD',       (30, 100, 200))
# Laptop
make_laptop_image('laptop_acer_swift_x14.png',   'ACER',   'Swift X',    'SFX14-71G',    'Core i7-12700H • RTX 3050 • 14" OLED')
make_laptop_image('laptop_acer_aspire5.png',     'ACER',   'Aspire 5',   'A515-57G',     'Core i5-12450H • MX550 • 15.6" FHD')
make_laptop_image('laptop_acer_helios_neo.png',  'ACER',   'Helios',     'Neo 16 PHN',   'Core i7-13700HX • RTX 4070 • 16" QHD')
make_laptop_image('laptop_lenovo_idg3.png',      'LENOVO', 'IdeaPad',    'Gaming 3',     'Ryzen 5 5600H • RTX 3050 Ti • 15.6"')
make_laptop_image('laptop_lenovo_slim5.png',     'LENOVO', 'Legion Slim','5 16APH8',     'Ryzen 7 7745HX • RTX 4070 • 16" QHD+')
make_laptop_image('laptop_lenovo_yoga7pro.png',  'LENOVO', 'Yoga Slim',  '7 Pro 14ACH5', 'Ryzen 9 5900HX • Radeon RX 6600M')
make_laptop_image('laptop_asus_vivobook15.png',  'ASUS',   'Vivobook 15','X1502ZA',      'Core i5-12500H • Intel Iris Xe • OLED')
make_laptop_image('laptop_asus_proart16.png',    'ASUS',   'ProArt',     'A16 OLED',     'Ryzen 9 7945HX • RTX 4070 • 16" OLED', (160, 100, 255))
make_laptop_image('laptop_asus_scar16.png',      'ASUS',   'ROG SCAR',   '16 G634JYR',   'Core i9-14900HX • RTX 4090 • 240Hz QHD+')

# ════════════════════════════════════════════════════════════════
print('\n── 4 LINH KIỆN: CPU / Mainboard / PSU / RAM ──')
# ════════════════════════════════════════════════════════════════

add_product(
    title='AMD RYZEN 9 7950X (UP TO 5.7GHZ, 16 NHÂN 32 LUỒNG, AM5)',
    slug='amd-ryzen-9-7950x',
    category_id=15, price=14900000, promotion=5, amount=10,
    keywords='AMD Ryzen 9 7950X CPU AM5 DDR5 Zen 4 overclock',
    description='AMD Ryzen 9 7950X - Flagship CPU Zen 4, 16 nhân 32 luồng, xung nhịp boost 5.7GHz, hiệu năng đỉnh cao cho workstation và gaming.',
    detail='<p><strong>AMD Ryzen 9 7950X</strong></p><ul><li>Kiến trúc: Zen 4 (TSMC 5nm)</li><li>Nhân/Luồng: 16 nhân / 32 luồng</li><li>Base/Boost: 4.5GHz / 5.7GHz</li><li>Cache: L3 64MB + L2 16MB</li><li>TDP: 170W</li><li>RAM hỗ trợ: DDR5-5200 (EXPO up to 6400+)</li><li>PCIe: PCIe 5.0 + PCIe 4.0</li><li>Socket: AM5</li><li>iGPU: AMD Radeon (RDNA 2)</li></ul>',
    main_img='cpu_amd_ryzen9_7950x.png',
)

add_product(
    title='MAINBOARD MSI MAG B760M MORTAR DDR4 WIFI',
    slug='mainboard-msi-mag-b760m-mortar-ddr4-wifi',
    category_id=16, price=4490000, promotion=0, amount=20,
    keywords='Mainboard MSI MAG B760M Mortar DDR4 WiFi Intel LGA1700',
    description='MSI MAG B760M MORTAR DDR4 WIFI - Mainboard Micro-ATX tầm trung, socket LGA1700, hỗ trợ Intel Gen 12/13/14, DDR4 tốc độ cao.',
    detail='<p><strong>MSI MAG B760M MORTAR DDR4 WIFI</strong></p><ul><li>Socket: Intel LGA1700 (Gen 12/13/14)</li><li>Chipset: Intel B760</li><li>RAM: 4x DDR4 (max 128GB, up to 5200MHz OC)</li><li>PCIe: 1x PCIe 4.0 x16, 1x PCIe 3.0 x1</li><li>M.2: 3x M.2 (2x PCIe 4.0, 1x PCIe 3.0)</li><li>Network: 2.5G LAN + Intel WiFi 6E</li><li>Form factor: Micro-ATX</li><li>VRM: 12+1+1 duet rail Power system</li></ul>',
    main_img='mb_msi_mag_b760m.png',
)

add_product(
    title='NGUỒN SEASONIC FOCUS GX-850 80+ GOLD FULL MODULAR 850W',
    slug='nguon-seasonic-focus-gx-850-gold',
    category_id=18, price=3190000, promotion=0, amount=15,
    keywords='Nguồn Seasonic Focus GX-850 850W 80+ Gold full modular PSU',
    description='Seasonic FOCUS GX-850 - Nguồn máy tính 850W Full Modular 80+ Gold, độ bền vượt trội, quạt 135mm Fluid Dynamic Bearing.',
    detail='<p><strong>Seasonic FOCUS GX-850</strong></p><ul><li>Công suất: 850W</li><li>Chứng nhận: 80+ Gold (>90% hiệu suất)</li><li>Modular: Full Modular</li><li>Quạt: 135mm Fluid Dynamic Bearing</li><li>Semi-Fanless: tự tắt quạt dưới 30% tải</li><li>ATX12V v2.4 / EPS12V</li><li>Bảo vệ: OVP, UVP, OCP, OTP, SCP, NLO</li><li>Bảo hành: 12 năm</li></ul>',
    main_img='psu_seasonic_focus850.png',
)

add_product(
    title='RAM G.SKILL TRIDENT Z5 RGB DDR5 32GB (2x16GB) 6400MHz CL32',
    slug='ram-gskill-trident-z5-rgb-ddr5-32gb-6400mhz',
    category_id=13, price=3490000, promotion=5, amount=18,
    keywords='RAM G.Skill Trident Z5 RGB DDR5 32GB 6400MHz XMP 3.0 gaming',
    description='G.Skill Trident Z5 RGB DDR5 32GB - Bộ nhớ DDR5 cao cấp nhất, XMP 3.0 lên đến 6400MHz, tản nhiệt nhôm nguyên khối và LED RGB.',
    detail='<p><strong>G.Skill Trident Z5 RGB DDR5 32GB</strong></p><ul><li>Dung lượng: 32GB (Kit 2x16GB)</li><li>Bus: DDR5-6400 (PC5-51200)</li><li>Timing: CL32-39-39-102</li><li>Điện áp: 1.40V</li><li>XMP 3.0 / EXPO hỗ trợ Intel/AMD</li><li>Tản nhiệt nhôm nguyên khối CNC</li><li>LED RGB full spectrum với phần mềm</li></ul>',
    main_img='ram_gskill_trident_z5.png',
)

# ════════════════════════════════════════════════════════════════
print('\n── 6 Ổ CỨNG ──')
# ════════════════════════════════════════════════════════════════

add_product(
    title='Ổ CỨNG SSD CRUCIAL P3 PLUS NVME M.2 1TB PCIE 4.0',
    slug='ssd-crucial-p3-plus-nvme-1tb',
    category_id=17, price=1390000, promotion=0, amount=40,
    keywords='SSD Crucial P3 Plus NVMe M.2 1TB PCIe 4.0 giá tốt',
    description='Crucial P3 Plus 1TB NVMe PCIe 4.0 - Lựa chọn tầm trung tốc độ đọc 5000 MB/s, giá tốt nhất phân khúc.',
    detail='<p><strong>Crucial P3 Plus NVMe M.2 1TB</strong></p><ul><li>Dung lượng: 1TB</li><li>Giao tiếp: PCIe 4.0 x4, NVMe</li><li>Form factor: M.2 2280</li><li>Tốc độ đọc tuần tự: 5,000 MB/s</li><li>Tốc độ ghi tuần tự: 4,200 MB/s</li><li>TBW: 440 TBW</li><li>Bảo hành: 5 năm</li></ul>',
    main_img='ssd_crucial_p3plus.png',
)

add_product(
    title='Ổ CỨNG SSD SEAGATE FIRECUDA 530 NVME 4TB PCIE 4.0 HEATSINK',
    slug='ssd-seagate-firecuda-530-nvme-4tb',
    category_id=17, price=8990000, promotion=0, amount=8,
    keywords='SSD Seagate FireCuda 530 NVMe 4TB PCIe 4.0 heatsink gaming',
    description='Seagate FireCuda 530 4TB NVMe PCIe 4.0 - Ổ SSD flagship, tốc độ đọc 7300 MB/s, kèm heatsink, bảo hành Rescue 5 năm.',
    detail='<p><strong>Seagate FireCuda 530 NVMe 4TB + Heatsink</strong></p><ul><li>Dung lượng: 4TB</li><li>Giao tiếp: PCIe 4.0 x4, NVMe 1.4</li><li>Form factor: M.2 2280</li><li>Tốc độ đọc: 7,300 MB/s</li><li>Tốc độ ghi: 7,000 MB/s</li><li>Kèm heatsink tản nhiệt kim loại</li><li>TBW: 5,100 TBW</li><li>Data Rescue Service 3 năm</li></ul>',
    main_img='ssd_seagate_firecuda.png',
)

add_product(
    title='Ổ CỨNG SSD SAMSUNG 870 EVO SATA III 1TB 2.5 INCH',
    slug='ssd-samsung-870-evo-sata-1tb',
    category_id=17, price=1690000, promotion=10, amount=35,
    keywords='SSD Samsung 870 EVO SATA 1TB 2.5 inch laptop nâng cấp',
    description='Samsung 870 EVO SATA III 1TB - Ổ SSD SATA phổ biến nhất để nâng cấp laptop/PC, tốc độ đọc 560 MB/s, bền bỉ đáng tin cậy.',
    detail='<p><strong>Samsung 870 EVO SATA III 1TB</strong></p><ul><li>Dung lượng: 1TB</li><li>Giao tiếp: SATA III 6 Gbps</li><li>Form factor: 2.5 inch</li><li>Tốc độ đọc tuần tự: 560 MB/s</li><li>Tốc độ ghi tuần tự: 530 MB/s</li><li>IOPS đọc: 98K | Ghi: 88K</li><li>TBW: 600 TBW</li><li>Bảo hành: 5 năm</li></ul>',
    main_img='ssd_samsung870evo.png',
)

add_product(
    title='Ổ CỨNG SSD CRUCIAL MX500 SATA III 2TB 2.5 INCH',
    slug='ssd-crucial-mx500-sata-2tb',
    category_id=17, price=2490000, promotion=5, amount=28,
    keywords='SSD Crucial MX500 SATA 2TB 2.5 inch laptop PC nâng cấp',
    description='Crucial MX500 2TB SATA III - Giải pháp lưu trữ tầm trung dung lượng lớn, Micron 3D NAND, mã hóa AES 256-bit.',
    detail='<p><strong>Crucial MX500 SATA III 2TB</strong></p><ul><li>Dung lượng: 2TB</li><li>Giao tiếp: SATA III 6 Gbps</li><li>Form factor: 2.5 inch</li><li>Tốc độ đọc: 560 MB/s</li><li>Tốc độ ghi: 510 MB/s</li><li>Micron 3D NAND TLC</li><li>Mã hóa AES 256-bit phần cứng</li><li>TBW: 700 TBW</li><li>Bảo hành: 5 năm</li></ul>',
    main_img='ssd_crucial_mx500.png',
)

add_product(
    title='Ổ CỨNG HDD SEAGATE BARRACUDA 4TB 3.5 INCH 5400RPM SATA',
    slug='hdd-seagate-barracuda-4tb',
    category_id=17, price=2190000, promotion=0, amount=20,
    keywords='HDD Seagate Barracuda 4TB 3.5 inch 5400RPM SATA desktop',
    description='Seagate Barracuda 4TB - Ổ cứng HDD 3.5 inch dung lượng lớn cho PC desktop, lưu trữ game, media và dữ liệu gia đình.',
    detail='<p><strong>Seagate Barracuda 4TB 3.5 Inch</strong></p><ul><li>Dung lượng: 4TB</li><li>Form factor: 3.5 inch</li><li>Giao tiếp: SATA 6Gb/s</li><li>Tốc độ quay: 5400 RPM (SMR)</li><li>Cache: 256MB</li><li>Tốc độ truyền: đến 190 MB/s</li><li>TBW: không giới hạn</li><li>Bảo hành: 2 năm</li></ul>',
    main_img='hdd_seagate_barracuda.png',
)

add_product(
    title='Ổ CỨNG HDD WD BLUE 2TB 3.5 INCH 7200RPM SATA',
    slug='hdd-wd-blue-2tb-7200rpm',
    category_id=17, price=1490000, promotion=0, amount=25,
    keywords='HDD WD Blue 2TB 3.5 inch 7200RPM desktop lưu trữ',
    description='WD Blue 2TB 7200RPM - Ổ cứng HDD desktop tốc độ cao 7200 RPM, lý tưởng lưu trữ ứng dụng và game.',
    detail='<p><strong>WD Blue 2TB 3.5 Inch 7200RPM</strong></p><ul><li>Dung lượng: 2TB</li><li>Form factor: 3.5 inch</li><li>Giao tiếp: SATA 6Gb/s</li><li>Tốc độ quay: 7200 RPM</li><li>Cache: 256MB</li><li>Tốc độ đọc: đến 180 MB/s</li><li>ShockGuard chống rung</li><li>Bảo hành: 2 năm</li></ul>',
    main_img='hdd_wd_blue.png',
)

# ════════════════════════════════════════════════════════════════
print('\n── 6 LAPTOP ACER & LENOVO ──')
# ════════════════════════════════════════════════════════════════

add_product(
    title='ACER SWIFT X 14 SFX14-71G-77HX',
    slug='acer-swift-x-14-sfx14-71g',
    category_id=8, price=26900000, promotion=5, amount=10,
    keywords='Acer Swift X 14 mỏng nhẹ RTX 3050 OLED sáng tạo nội dung',
    description='Acer Swift X 14 - Laptop creator mỏng nhẹ 1.4kg, màn OLED 2.8K 90Hz, RTX 3050, Core i7-12700H.',
    detail='<p><strong>Acer Swift X 14 SFX14-71G</strong></p><ul><li>CPU: Intel Core i7-12700H</li><li>GPU: NVIDIA RTX 3050 4GB</li><li>RAM: 16GB LPDDR5</li><li>SSD: 512GB NVMe PCIe 4.0</li><li>Màn: 14.5" OLED 2.8K (2880x1800) 90Hz, 100% DCI-P3</li><li>Trọng lượng: 1.4kg</li></ul>',
    main_img='laptop_acer_swift_x14.png',
)

add_product(
    title='ACER ASPIRE 5 A515-57G-524A',
    slug='acer-aspire-5-a515-57g',
    category_id=8, price=13900000, promotion=0, amount=30,
    keywords='Acer Aspire 5 A515 Core i5 MX550 văn phòng học sinh giá rẻ',
    description='Acer Aspire 5 A515-57G - Laptop văn phòng/học sinh giá tốt, Core i5-12450H, card đồ họa rời MX550, màn 15.6" FHD IPS.',
    detail='<p><strong>Acer Aspire 5 A515-57G</strong></p><ul><li>CPU: Intel Core i5-12450H</li><li>GPU: NVIDIA MX550 2GB GDDR6</li><li>RAM: 8GB DDR4 (1 khe trống, max 16GB)</li><li>SSD: 512GB NVMe PCIe 3.0</li><li>Màn: 15.6" FHD IPS 60Hz</li><li>Pin: 48Wh</li><li>Trọng lượng: 1.8kg</li></ul>',
    main_img='laptop_acer_aspire5.png',
)

add_product(
    title='ACER PREDATOR HELIOS NEO 16 PHN16-71-76RU',
    slug='acer-predator-helios-neo-16',
    category_id=8, price=38900000, promotion=0, amount=8,
    keywords='Acer Predator Helios Neo 16 i7-13700HX RTX 4070 gaming cao cấp',
    description='Acer Predator Helios Neo 16 - Laptop gaming flagship tầm trung cao cấp, i7-13700HX + RTX 4070, màn Mini LED 2K 165Hz.',
    detail='<p><strong>Acer Predator Helios Neo 16</strong></p><ul><li>CPU: Intel Core i7-13700HX (up to 5.0GHz)</li><li>GPU: NVIDIA GeForce RTX 4070 8GB</li><li>RAM: 16GB DDR5 4800MHz (2 khe)</li><li>SSD: 1TB NVMe PCIe 4.0</li><li>Màn: 16" QHD (2560x1600) Mini LED 165Hz, 100% sRGB</li><li>Tản nhiệt: 5th Gen AeroBlade 3D fan</li></ul>',
    main_img='laptop_acer_helios_neo.png',
)

add_product(
    title='LENOVO IDEAPAD GAMING 3 15ACH6 82K200VKVN',
    slug='lenovo-ideapad-gaming-3-15ach6',
    category_id=5, price=17900000, promotion=8, amount=22,
    keywords='Lenovo IdeaPad Gaming 3 15ACH6 Ryzen 5 RTX 3050 Ti gaming entry',
    description='Lenovo IdeaPad Gaming 3 15ACH6 - Laptop gaming entry-level tốt nhất phân khúc, Ryzen 5 5600H + RTX 3050 Ti, màn 120Hz.',
    detail='<p><strong>Lenovo IdeaPad Gaming 3 15ACH6</strong></p><ul><li>CPU: AMD Ryzen 5 5600H (up to 4.2GHz)</li><li>GPU: NVIDIA RTX 3050 Ti 4GB GDDR6</li><li>RAM: 8GB DDR4 3200MHz (1 khe, max 16GB)</li><li>SSD: 512GB NVMe PCIe 3.0</li><li>Màn: 15.6" FHD IPS 120Hz</li><li>Pin: 45Wh</li><li>Trọng lượng: 2.2kg</li></ul>',
    main_img='laptop_lenovo_idg3.png',
)

add_product(
    title='LENOVO LEGION SLIM 5 16APH8 82Y9002EVN',
    slug='lenovo-legion-slim-5-16aph8',
    category_id=5, price=32900000, promotion=5, amount=12,
    keywords='Lenovo Legion Slim 5 16APH8 Ryzen 7 RTX 4070 mỏng nhẹ gaming',
    description='Lenovo Legion Slim 5 16APH8 - Laptop gaming cao cấp mỏng chỉ 18.9mm, Ryzen 7 7745HX + RTX 4070, màn QHD+ 165Hz.',
    detail='<p><strong>Lenovo Legion Slim 5 16APH8</strong></p><ul><li>CPU: AMD Ryzen 7 7745HX (up to 5.1GHz)</li><li>GPU: NVIDIA RTX 4070 8GB GDDR6</li><li>RAM: 16GB LPDDR5x 6400MHz (onboard + 1 khe)</li><li>SSD: 1TB NVMe PCIe 4.0</li><li>Màn: 16" QHD+ (2560x1600) IPS 165Hz, 500nits</li><li>Độ dày: 18.9mm | Trọng lượng: 2.4kg</li></ul>',
    main_img='laptop_lenovo_slim5.png',
)

add_product(
    title='LENOVO YOGA SLIM 7 PRO 14ACH5 82MS00DHVN',
    slug='lenovo-yoga-slim-7-pro-14ach5',
    category_id=5, price=24900000, promotion=0, amount=10,
    keywords='Lenovo Yoga Slim 7 Pro Ryzen 9 5900HX creator mỏng nhẹ OLED',
    description='Lenovo Yoga Slim 7 Pro 14ACH5 - Laptop creator cao cấp, Ryzen 9 5900HX, màn 14" OLED 2.8K 90Hz, trọng lượng chỉ 1.37kg.',
    detail='<p><strong>Lenovo Yoga Slim 7 Pro 14ACH5</strong></p><ul><li>CPU: AMD Ryzen 9 5900HX (up to 4.6GHz)</li><li>GPU: AMD Radeon RX 6600M 8GB</li><li>RAM: 16GB LPDDR4x 4266MHz (onboard)</li><li>SSD: 1TB NVMe PCIe 4.0</li><li>Màn: 14" OLED 2.8K (2880x1800) 90Hz, 100% DCI-P3</li><li>Trọng lượng: 1.37kg</li></ul>',
    main_img='laptop_lenovo_yoga7pro.png',
)

# ════════════════════════════════════════════════════════════════
print('\n── 3 LAPTOP ASUS ──')
# ════════════════════════════════════════════════════════════════

add_product(
    title='ASUS VIVOBOOK 15 OLED A1505ZA-L1452W',
    slug='asus-vivobook-15-oled-a1505za',
    category_id=6, price=15900000, promotion=5, amount=25,
    keywords='ASUS Vivobook 15 OLED Core i5 văn phòng học sinh màn đẹp',
    description='ASUS Vivobook 15 OLED A1505ZA - Laptop văn phòng/học sinh nổi bật với màn OLED 2.8K sống động, Core i5-12500H, thiết kế mỏng nhẹ.',
    detail='<p><strong>ASUS Vivobook 15 OLED A1505ZA</strong></p><ul><li>CPU: Intel Core i5-12500H</li><li>GPU: Intel Iris Xe Graphics</li><li>RAM: 8GB DDR4 3200MHz (1 khe, max 16GB)</li><li>SSD: 512GB NVMe PCIe 3.0</li><li>Màn: 15.6" OLED 2.8K (2880x1620) 120Hz, 100% DCI-P3, PANTONE Validated</li><li>Trọng lượng: 1.7kg</li></ul>',
    main_img='laptop_asus_vivobook15.png',
)

add_product(
    title='ASUS PROART STUDIOBOOK 16 OLED H7600ZX-L2035W',
    slug='asus-proart-studiobook-16-oled',
    category_id=6, price=78900000, promotion=0, amount=5,
    keywords='ASUS ProArt Studiobook 16 OLED Ryzen 9 7945HX RTX 4070 creator',
    description='ASUS ProArt Studiobook 16 OLED - Laptop workstation creator cao cấp nhất, Ryzen 9 7945HX + RTX 4070, màn 16" OLED 4K 120Hz.',
    detail='<p><strong>ASUS ProArt Studiobook 16 OLED</strong></p><ul><li>CPU: AMD Ryzen 9 7945HX (up to 5.4GHz, 16 nhân)</li><li>GPU: NVIDIA RTX 4070 8GB GDDR6</li><li>RAM: 32GB DDR5 4800MHz (2 khe, max 64GB)</li><li>SSD: 2TB NVMe PCIe 4.0</li><li>Màn: 16" OLED 4K (3840x2400) 120Hz, 100% DCI-P3, PANTONE Validated, Delta-E < 2</li><li>ASUS Dial + DialPad hỗ trợ sáng tạo</li><li>Trọng lượng: 2.4kg</li></ul>',
    main_img='laptop_asus_proart16.png',
)

add_product(
    title='ASUS ROG STRIX SCAR 16 G634JYR-NM024W',
    slug='asus-rog-strix-scar-16-g634jyr',
    category_id=6, price=89900000, promotion=0, amount=4,
    keywords='ASUS ROG STRIX SCAR 16 Core i9-14900HX RTX 4090 gaming flagship',
    description='ASUS ROG STRIX SCAR 16 G634JYR - Laptop gaming flagship đỉnh cao nhất thị trường, Core i9-14900HX + RTX 4090, màn QHD+ 240Hz MiniLED.',
    detail='<p><strong>ASUS ROG STRIX SCAR 16 G634JYR</strong></p><ul><li>CPU: Intel Core i9-14900HX (up to 5.8GHz, 24 nhân)</li><li>GPU: NVIDIA GeForce RTX 4090 16GB GDDR6</li><li>RAM: 32GB DDR5 4800MHz (2 khe, max 64GB)</li><li>SSD: 2TB NVMe PCIe 4.0</li><li>Màn: 16" QHD+ (2560x1600) MiniLED 240Hz, 1100nits, 100% DCI-P3</li><li>ROG Nebula HDR display</li><li>Trọng lượng: 2.69kg</li></ul>',
    main_img='laptop_asus_scar16.png',
)

# ════════════════════════════════════════════════════════════════
from product.models import Product as P
from product.models import Category as C
print(f'\n{"="*60}')
print(f'🎉 HOÀN TẤT! Tổng sản phẩm: {P.objects.count()}')
print()
for cat, cid in [('Laptop ASUS',6),('Laptop Acer',8),('Laptop Lenovo',5),
                  ('CPU',15),('Mainboard',16),('PSU',18),('RAM',13),
                  ('VGA',12),('Ổ Cứng',17),('Bàn phím',9),('Chuột',10),('Tai nghe',14)]:
    cnt = P.objects.filter(category_id=cid).count()
    print(f'  {cat:<20}: {cnt} sản phẩm')
print(f'{"="*60}')
