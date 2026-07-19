from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
# Create your models here.
from django.db.models import Avg, Count
from django.forms import ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

class Category(MPTTModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )
    # Quan hệ phân cấp (cây) sử dụng để quản lý danh mục cha con liên quan đến breadcrumb
    parent = TreeForeignKey('self',blank=True, null=True ,related_name='children', on_delete=models.CASCADE)
    
    # Nội dung & SEO
    title = models.CharField(max_length=50)
    keywords = models.CharField(max_length=255)
    description = models.TextField(max_length=255)

    # Ảnh & trạng thái
    image=models.ImageField(blank=True,upload_to='images/')
    status=models.CharField(max_length=10, choices=STATUS)

    # duong link slug để tạo đường dẫn thân thiện cho người dùng
    slug = models.SlugField(null=False, unique=True)
    
    # Thời gian
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    class MPTTMeta:
        order_insertion_by=['title']

class Product(models.Model):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )

    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
        ('Color', 'Color'),
        ('Size-Color', 'Size-Color'),

    )

    # Thể loại sản phẩm
    category = models.ForeignKey(Category, on_delete=models.CASCADE) #many to one relation with Category
    
    #SEO Meta và  nội dung
    title = models.CharField(max_length=150)
    keywords = models.CharField(max_length=255)
    description = RichTextUploadingField(blank=True)
    
    #hình ảnh của sản phẩm
    image=models.ImageField(upload_to='images/',null=False)

   #giá sản phẩm,giảm giá ,số lượng, số lượng tối thiểu, biến thể,
    price = models.DecimalField(max_digits=15, decimal_places=2,default=0)
    promotion = models.IntegerField(default=0)
    amount=models.IntegerField(default=0)
    minamount=models.IntegerField(default=3)
    variant=models.CharField(max_length=10,choices=VARIANTS, default='None')
    
    #chi tiết và slug của sản phẩm
    detail=RichTextUploadingField(blank=True)
    slug = models.SlugField(null=False, unique=True)
    
    #Trang thái và thời gian
    status=models.CharField(max_length=10,choices=STATUS)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
        ## method to create a fake table field in read only mode

    def image_tag(self):

        return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
    image_tag.short_description= 'Image'

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    @property
    def has_promotion(self):
        """True nếu sản phẩm đang có phần trăm khuyến mãi hợp lệ (1-99%)."""
        return 0 < self.promotion < 100

    @property
    def final_price(self):
        """
        Giá thực tế khách hàng phải trả sau khi áp dụng khuyến mãi (promotion %).
        Nếu không có khuyến mãi (promotion = 0), trả về đúng giá gốc.
        Dùng Decimal xuyên suốt để tránh lệch số học với trường price (DecimalField).
        """
        if not self.has_promotion:
            return self.price
        from decimal import Decimal
        discount_multiplier = Decimal('1') - (Decimal(self.promotion) / Decimal('100'))
        return (self.price * discount_multiplier).quantize(Decimal('0.01'))

    def avaregereview(self):
        reviews = Comment.objects.filter(product=self, status='New').aggregate(avarage=Avg('rate'))
        avg = 0
        if reviews["avarage"] is not None:
            avg = float(reviews["avarage"])
        return avg

    def countreview(self):
        reviews = Comment.objects.filter(product=self, status='New').aggregate(count=Count('id'))
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt

class Images(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    title = models.CharField(max_length=50,blank=True)
    image = models.ImageField(blank=True, upload_to='images/')

    def __str__(self):
        return self.title


        #Phần xử lý luieen quan đến comment
class Comment(models.Model):
    STATUS = (
        ('New', 'New'),
        ('True', 'True'),
        ('False', 'False'),
    )
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    comment = models.CharField(max_length=250,blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status=models.CharField(max_length=10,choices=STATUS, default='New')
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.comment



# //Phần xử lý form comment sử dụng http request
class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [ 'comment', 'rate']

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.title