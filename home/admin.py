from django.contrib import admin

# Đăng ký model từ Setting
from home.models import Setting, ContactMessage, Banner


# Phần cho phép các trường hiển thị  trong admin
class SettingtAdmin(admin.ModelAdmin):
    list_display = ['title','company', 'update_at','status']

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name','subject', 'update_at','status']
    readonly_fields = ['name','subject','email','message','ip']
    list_filter = ['status']
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_at', 'end_at', 'status']
    list_filter = ['status']

admin.site.register(Setting,SettingtAdmin)
admin.site.register(ContactMessage,ContactMessageAdmin)
admin.site.register(Banner, BannerAdmin)

