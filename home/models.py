from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models

# Create your models here.
from django.db.models import Count
from django.forms import ModelForm, TextInput, Textarea

from order.models import ShopCart

class Setting(models.Model):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )

     # Các trường cơ bản của website home page như 
     #      -title, keywords, description, (Meta)
     #      -address, phone, fax, email,company (Contact)
     #      -smtpserver, smtpemail, smtppassword, smtpport (SMTP)
     #      -facebook, instagram, twitter, youtube (Social Media)
     #      -aboutus, contact, references (Content)
     #      -status (Status)
     #      -create_at, update_at (Date)

    title = models.CharField(max_length=150)
    keywords = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    company = models.CharField(max_length=50)
    address = models.CharField(blank=True,max_length=100)
    phone = models.CharField(blank=True,max_length=15)
    fax = models.CharField(blank=True,max_length=15)
    email = models.CharField(blank=True,max_length=50)

    # Cấu hình SMTP để gửi email
    smtpserver = models.CharField(blank=True,max_length=50)
    smtpemail = models.CharField(blank=True,max_length=50)
    smtppassword = models.CharField(blank=True,max_length=10)
    smtpport = models.CharField(blank=True,max_length=5)

    #Logo
    icon = models.ImageField(blank=True,upload_to='images/')
    facebook = models.CharField(blank=True,max_length=50)
    instagram = models.CharField(blank=True,max_length=50)
    twitter = models.CharField(blank=True,max_length=50)
    youtube = models.CharField(blank=True, max_length=50)

    #Nội dung trang cơ bản như giới thiệu, liên hệ, tham khảo
    aboutus = RichTextUploadingField(blank=True)
    contact = RichTextUploadingField(blank=True)
    references = RichTextUploadingField(blank=True)

    #Trạng thái của trang 
    status=models.CharField(max_length=10,choices=STATUS)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    def countreview(self):
        reviews = ShopCart.objects.filter(product=self, status='True').aggregate(count=Count('id'))
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt

class Banner(models.Model):
    STATUS = (
        ('True', 'Có'),
        ('False', 'Không'),
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/banner/')
    link = models.CharField(max_length=255, blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS, default='True')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# Nội dung liên hệ gửi đến mail
class ContactMessage(models.Model):
    STATUS = (
        ('New', 'Mới'),
        ('Read', 'Đã đọc'),
        ('Closed', 'Closed'),
    )

    # Tên người gửi, email, chủ đề, nội dung
    name= models.CharField(blank=True,max_length=20)
    email= models.CharField(blank=True,max_length=50)
    subject= models.CharField(blank=True,max_length=50)
    message= models.TextField(blank=True,max_length=255)

    # Trang thái của tin nhắn
    status=models.CharField(max_length=10,choices=STATUS,default='New')
    
    # Địa chỉ IP, ghi chú , thời gian create và update
    ip = models.CharField(blank=True, max_length=20)
    note = models.CharField(blank=True, max_length=100)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Form liên hệ
class ContactForm(ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject','message']
        widgets = {
            'name'   : TextInput(attrs={'class': 'input','placeholder':'Họ tên'}),
            'subject' : TextInput(attrs={'class': 'input','placeholder':'Vấn Đề'}),
            'email'   : TextInput(attrs={'class': 'input','placeholder':'Email'}),
            'message' : Textarea(attrs={'class': 'input','placeholder':'Nhập tin nhắn','rows':'5'}),
        }