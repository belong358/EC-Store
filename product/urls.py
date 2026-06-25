from django.urls import path, include
from . import views
urlpatterns = [

    path('',views.index,name='index'),
    path('addcomment/<int:id>', views.addcomment, name='addcomment'),
    path('compare/add/<int:id>/', views.add_to_compare, name='add_to_compare'),
    path('compare/remove/<int:id>/', views.remove_from_compare, name='remove_from_compare'),
    path('compare/', views.compare_products, name='compare_products'),
    path('wishlist/add/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    ]