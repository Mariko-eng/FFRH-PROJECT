from django.urls import path
from . import views
from inventory.views import dashboard

urlpatterns =[
    path('products/dashboard/',views.admin_dashboard,name='productsDashboard'),
    path('product/detail/', views.product_visual, name='productVisual'),
    path('consumption/method/2/<int:cde>/',views.get_consumption_method_2_month,name='cmethod2cde'),
    path('consumption/method/list/2/', views.get_consumption_method_2_month_list, name='cmethod2list'),
    path('consumption/method/3/<int:cde>/', views.get_consumption_method_3_month, name='cmethod3cde'),
    path('consumption/method/list/3/', views.get_consumption_method_3_month_list, name='cmethod3list'),
    path('eoq2/<int:cde>/',views.get_eoq_model_2_month,name="eoq2cde"),
    path('eoq2/list/', views.get_eoq_model_2_month_list, name="eoq2list"),
    path('eoq3/<int:cde>/', views.get_eoq_model_3_month, name="eoq3cde"),
    path('eoq3/list/', views.get_eoq_model_3_month_list, name="eoq3list"),
    path('eoq/2month/under/funding/', views.under_funding_2_month, name='underfunding2'),
    path('eoq/2month/over/funding/',views.over_funding_2_month,name='overfunding2'),
    path('eoq/3month/under/funding/', views.under_funding_3_month, name='underfunding3'),
    path('eoq/3month/over/funding/', views.over_funding_3_month, name='overfunding3'),
    path('view/all/stock/', views.all_current_stock, name='a_currentStock'),
    path('view/all/stock/<int:cde>/', views.all_current_stock_single_stats, name='ap_currentStock'),
    path('inventory/', dashboard, name='inventoryLink'),
    path('ajax/request/',views.ajaxrequest,name='ajx'),
    path('ajax/request1/', views.ajaxrequest1, name='ajx1'),
    path('ajax/request/<int:cde>/', views.ajaxrequestp, name='ajxn'),
    path('ajax/request1/<int:cde>/', views.ajaxrequestp1, name='ajxn1'),

    path('graph/product/<int:cde>/',views.product_graph,name="pgraph"),
    path('graphs/more/stats/',views.get_more_graphs,name='graphs'),
    path('graphs/2/c_method',views.get_graphs_2_consumption,name='graphs2c'),
    path('graphs/2/eoq',views.get_graphs_2_eoq,name='graphs2e'),
    path('graphs/3/c_method',views.get_graphs_3_consumption,name='graphs3c'),
    path('graphs/3/eoq',views.get_graphs_3_eoq,name='graphs3e'),

    path('prac/',views.practice),
]