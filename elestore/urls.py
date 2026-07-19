"""elestore URL Configuration"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from user.api_views import GoogleLogin, FacebookLogin
import home
from home import views
from home import dashboard_views
from order import views as OrderViews
from user import views as UserViews

urlpatterns = [
    path('', include('home.urls')),
    path('home/', include('home.urls')),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('contact/', views.contact, name='contactus'),
    path('product/', include('product.urls')),
    path('order/', include('order.urls')),
    path('user/', include('user.urls')),
    path('search/', views.search, name='search'),
    path('shopcart/', OrderViews.shopcart, name='shopcart'),
    path('login/', UserViews.login_form, name='login_form'),
    path('logout/', UserViews.logout_func, name='logout_func'),
    path('signup/', UserViews.signup_form, name='signup_form'),
    path('search_auto/', views.search_auto, name='search_auto'),
    path('admin/', admin.site.urls),

    # ── DASHBOARD ────────────────────────────────────────
    path('dashboard-login/',                                   dashboard_views.dashboard_login,            name='dashboard_login'),
    path('dashboard-logout/',                                  dashboard_views.dashboard_logout,           name='dashboard_logout'),
    path('dashboard/',                                          dashboard_views.dashboard,                  name='dashboard'),
    path('dashboard/api/notifications/',                        dashboard_views.dashboard_notifications_api, name='dashboard_notifications_api'),
    path('dashboard/orders/',                                   dashboard_views.dashboard_orders,           name='dashboard_orders'),
    path('dashboard/orders/<int:order_id>/',                   dashboard_views.dashboard_order_detail,     name='dashboard_order_detail'),
    path('dashboard/orders/<int:order_id>/delete/',             dashboard_views.dashboard_order_delete,     name='dashboard_order_delete'),
    path('dashboard/orders/reset/',                            dashboard_views.dashboard_orders_reset,     name='dashboard_orders_reset'),
    path('dashboard/products/',                                 dashboard_views.dashboard_products,         name='dashboard_products'),
    path('dashboard/products/add/',                            dashboard_views.dashboard_product_add,      name='dashboard_product_add'),
    path('dashboard/products/<int:product_id>/edit/',          dashboard_views.dashboard_product_edit,     name='dashboard_product_edit'),
    path('dashboard/products/<int:product_id>/delete/',        dashboard_views.dashboard_product_delete,   name='dashboard_product_delete'),
    # Users
    path('dashboard/users/',                                    dashboard_views.dashboard_users,            name='dashboard_users'),
    path('dashboard/users/<int:user_id>/',                     dashboard_views.dashboard_user_detail,      name='dashboard_user_detail'),
    path('dashboard/users/<int:user_id>/toggle-active/',       dashboard_views.dashboard_user_toggle_active, name='dashboard_user_toggle_active'),
    path('dashboard/users/<int:user_id>/toggle-staff/',        dashboard_views.dashboard_user_toggle_staff,  name='dashboard_user_toggle_staff'),
    path('dashboard/users/<int:user_id>/delete/',              dashboard_views.dashboard_user_delete,      name='dashboard_user_delete'),
    path('dashboard/users/<int:user_id>/set-role/',           dashboard_views.dashboard_user_set_role,    name='dashboard_user_set_role'),
    # Messages
    path('dashboard/messages/',                                 dashboard_views.dashboard_messages_list,    name='dashboard_messages'),
    path('dashboard/messages/<int:msg_id>/update/',            dashboard_views.dashboard_message_update,   name='dashboard_message_update'),
    path('dashboard/messages/<int:msg_id>/reply/',              dashboard_views.dashboard_message_reply,    name='dashboard_message_reply'),
    path('dashboard/messages/<int:msg_id>/delete/',            dashboard_views.dashboard_message_delete,   name='dashboard_message_delete'),
    # Banners
    path('dashboard/banners/',                                  dashboard_views.dashboard_banners,          name='dashboard_banners'),
    path('dashboard/banners/add/',                             dashboard_views.dashboard_banner_add,       name='dashboard_banner_add'),
    path('dashboard/banners/<int:banner_id>/edit/',            dashboard_views.dashboard_banner_edit,      name='dashboard_banner_edit'),
    path('dashboard/banners/<int:banner_id>/delete/',          dashboard_views.dashboard_banner_delete,    name='dashboard_banner_delete'),

    path('dashboard/reviews/',                                  dashboard_views.dashboard_reviews,          name='dashboard_reviews'),
    path('dashboard/reviews/<int:review_id>/delete/',           dashboard_views.dashboard_review_delete,    name='dashboard_review_delete'),

    path('', views.index, name='home'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('category/<int:id>/<slug:slug>', views.category_products, name='category_products'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    # API AUTH & JWT
    path('api/token/',              TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/',      TokenRefreshView.as_view(),    name='token_refresh'),
    path('api/auth/',               include('dj_rest_auth.urls')),
    path('api/auth/registration/',  include('dj_rest_auth.registration.urls')),
    path('api/auth/google/',        GoogleLogin.as_view(),  name='google_login'),
    path('api/auth/facebook/',      FacebookLogin.as_view(), name='facebook_login'),
    path('accounts/',               include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
