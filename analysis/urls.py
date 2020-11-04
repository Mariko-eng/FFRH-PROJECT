from django.urls import path
from . import views
from inventory.views import dashboard

urlpatterns =[
    path('inventory/', dashboard, name='inventoryLink'),
    path('view/all/stock/', views.all_current_stock, name='a_currentStock'),
    path('view/all/stock/<int:cde>/', views.all_current_stock_single_stats, name='ap_currentStock'),
    path('products/dashboard/',views.admin_dashboard,name='productsDashboard'),
    path('product/detail/', views.product_visual, name='productVisual'),

    path('consumption/method/list/1/month/', views.get_consumption_method_1_month_list, name='cmethod1list'),
    path('graphs/1/consumption/method', views.get_graphs_1_month_consumption, name='graphs1c'), #GRAPH
    path('consumption/method/1/month/<int:cde>/',views.get_consumption_method_1_month_cde,name='cmethod1cde'),
    path('eoq/list/1/month/', views.get_eoq_1_month_list, name="eoq1list"),
    path('graphs/1/month/eoq', views.get_graphs_1_month_eoq, name='grapheoq1'), #GRAPH
    path('eoq/1/month/<int:cde>/', views.get_eoq_1_month_1_month_cde, name="eoq1cde"),
    path('eoq/1/month/under/funding/', views.under_funding_1_month, name='under_funding_1_month'),
    path('eoq/1/month/adequate/funding/',views.adequate_funding_1_month,name='adequate_funding_1_month'),
    path('eoq/1/month/over/funding/', views.over_funding_1_month, name='over_funding_1_month'),
    path('standardised/supply/plan/list/1/week/', views.get_standard_consumption_method_1_week_list,
         name="weeksupplyplanlist"),
    path('graphs/1/week/standardised/supply/plan/', views.get_graphs_standard_c_method_1_week_consumption,
         name='graphweeksupplyplanlist'),
    path('standardised/supply/plan/1/week/<int:cde>/',views.get_standard_consumption_method_1_week_cde,
         name="weeksupplyplancde"),

    path('ajax/request/',views.ajax_request_sidebar,name='ajx'),
    path('ajax/request1/', views.ajax_request_main, name='ajx1'),
    path('ajax/request/<int:cde>/', views.ajax_request_product_consumption, name='ajxn'),
    path('ajax/request1/<int:cde>/', views.ajax_request_product_eoq, name='ajxn1'),
    path('ajax/request2/<int:cde>/', views.ajax_request_product_standard, name='ajxn2'),
    path('ajax/request/all/products/', views.ajax_request_all_products, name='ajxn3'),

    path('graph/product/<int:cde>/',views.product_graph,name="pgraph"),
    path('graphs/more/stats/',views.get_more_graphs,name='graphs'),

    path('prac/',views.practice),
]