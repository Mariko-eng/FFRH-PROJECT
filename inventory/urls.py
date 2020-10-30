from django.urls import path
from . import views
from analysis.views import admin_dashboard

urlpatterns = [
    path('register/',views.register_new_user,name='register_user'),
    path('login/', views.login_user,name='login_user'),
    path('logout/', views.logout_user,name='logout_user'),
    path('view/all/current/stock/',views.available_current_stock,name='currentstock'),
    path('add/new/product/', views.new_product, name='product' ),
    path('',views.dashboard,name='dashboard'),
    path('product/details/<int:cde>/',views.more_product_info,name='productinfo'),
    path('new/stock/',views.new_stock,name= 'stockNew'),
    path('new/user/unit/',views.add_target_user_unit,name='new_user_unit'),
    path('update/delete/item/',views.update_delete_stock,name='update_delete'),
    path('update/item/<int:cde>/', views.update_stock, name='update_stock'),
    path('delete/item/<int:cde>/', views.delete_item, name='delete_stock'),
    path('new/order/items/',views.consumption,name='output'),
    path('analysis/admin/',admin_dashboard,name='adminlink'),
]