import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.embed.standalone import components
from bokeh.models import ColumnDataSource
from bokeh.resources import INLINE
from bokeh.transform import factor_cmap
from bokeh.models import FactorRange
from bokeh.palettes import Spectral5,Set3_12
from bokeh.layouts import Column
import json
from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from .models import ProductDetailExp, ConsumptionData,TargetHospitalUserUnit
from inventory.models import ProductDetails,StockDelivered,TheDailyConsumption
from .views_functions import calc_stats

from .views_functions import consumption_method_1_month_cycle, eoq_model_1_month_cycle
from .views_functions import standardised_consumption_plan_1_week_cycle

from .views_graphs_functions import get_initial_graphs_data, more_graphs_data
from .views_graphs_functions import get_graphs_consumption_method_1_month_cycle, get_graphs_eoq_model_1_month_cycle
from .views_graphs_functions import get_graphs_standardised_consumption_plan_1_week_cycle

from django.core.paginator import Paginator,EmptyPage
from django.contrib.auth.decorators import login_required
from inventory.decorators import main_admin_authorized
from scipy import stats

# Create your views here.


def practice(request):
    return render(request,'analysis/prac.html')


def get_df_to_make_graphs(products_df):
    products_df['STAT'] = products_df['STAT'].astype(float)  # Convert from str to float
    products_df['STAT'] = products_df['STAT'].fillna(0)
    products_df['CODE'] = products_df['CODE'].apply(str)  # From integer to string
    dt2 = products_df.drop(['CODE', 'DESCRIPTION', 'VEN', 'PRICE', 'CURRENT_STOCK'], axis=1)
    z_scores = stats.zscore(dt2)
    abs_z_scores = np.abs(z_scores)
    filtered_entries_less = (abs_z_scores < 3).all(axis=1)
    # filtered_entries_more = (abs_z_scores > 3).all(axis=1)
    new_df_less = products_df[filtered_entries_less]
    new_df_less = new_df_less[new_df_less['STAT'] > 0]
    # new_df_more = products_df[filtered_entries_more]
    v_df = new_df_less[new_df_less['VEN'] == 'V']
    v_df = v_df.sort_values(by='STAT', ascending=True)
    e_df = new_df_less[new_df_less['VEN'] == 'E']
    e_df = e_df.sort_values(by='STAT', ascending=True)
    n_df = new_df_less[new_df_less['VEN'] == 'N']
    n_df = n_df.sort_values(by='STAT', ascending=True)
    return pd.concat([n_df, e_df, v_df])


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def admin_dashboard(request):
    products = ProductDetailExp.objects.all()
    items = []
    items_columns = ['CODE', 'DESCRIPTION', 'VEN', 'PRICE', 'CURRENT_STOCK', 'STAT', ]
    for p in products:
        data = get_initial_graphs_data(p)
        if data is not None:
            items.append([data['code'], data['description'], data['ven'],
                          data['price'], data['current_stock'], data['stat']])

    products_df = pd.DataFrame(items, columns=items_columns)
    df = get_df_to_make_graphs(products_df)
    df1 = df.reset_index()
    factors = np.array(df1.CODE)
    factors2 = ['V', 'E', 'N']

    source = ColumnDataSource(data=df1)
    tools = "pan,wheel_zoom, box_zoom,reset,box_select,lasso_select, hover"
    p = figure(title="Average Consumption of Drugs At Fort Portal Regional Referral Hospital",
               y_range=factors,plot_height=2000, plot_width=2000, tools=tools, toolbar_location="left",
               x_axis_label="MEAN CONSUMPTION",y_axis_label="PRODUCT CODE",
               tooltips=[("PRODUCT CODE", "@CODE"), ("DESCRIPTION","@DESCRIPTION"), ("VEN","@VEN"),
                         ("PRICE","@PRICE"), ("CURRENT STOCK","@CURRENT_STOCK"), ("MEAN VALUE", "@STAT")]
               )
    p.hbar(y='CODE', right='STAT', height=0.7, source = source,
           color = factor_cmap('VEN', ['red', 'yellow', 'black'], factors2), legend_field='VEN')

    p.title.text_color = "olive"
    p.title.text_font = "times"
    p.title.text_font_style = "italic"
    p.xaxis.major_label_orientation = 1.5
    p.outline_line_color = "brown"
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.x_range.start = 0
    p.legend.location = "top_center"
    div, script = components(p)

    context = {
        'the_div': div,
        'the_script': script,
        'resources': INLINE.render(),
    }
    return render(request,'analysis/productdashboard.html',context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def all_current_stock(request):
    products = ProductDetails.objects.all()
    context = {
        'title' : 'ANALYSIS | PRODUCTS',
        'allProducts': products,
    }
    return render(request, 'analysis/all_products.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def all_current_stock_single_stats(request,cde):
    item = ProductDetailExp.objects.get(code=cde)
    c_data = ConsumptionData.objects.filter(productDetail=item)
    items_list = []

    for p in c_data:
        items_list.append([p.consumptionDate, p.consumptionQty])

    items_columns = ['consumptionDate', 'consumptionQty']
    items_df = pd.DataFrame(items_list, columns=items_columns)
    items_df['Date'] = pd.to_datetime(items_df['consumptionDate'])
    items_df['Year'] = pd.DatetimeIndex(items_df['Date']).year
    items_df['Month'] = pd.DatetimeIndex(items_df['Date']).strftime("%b")
    items_df['Day'] = pd.DatetimeIndex(items_df['Date']).strftime("%a")
    items_df['consumptionQty'] = items_df['consumptionQty'].astype(float)  # Convert from str to float
    items_df['Year'] = items_df['Year'].apply(str)  # From integer to string

    plt = figure(width=500, height=400, title="CONSUMPTION GRAPHS", x_axis_type="datetime")
    plt.line(x=items_df.consumptionDate, y=items_df.consumptionQty, line_color='green')
    plt.title.text_color = "olive"
    plt.title.text_font = "times"
    plt.title.text_font_style = "italic"
    plt.xaxis.axis_label = "Consumption Date"
    plt.xaxis.axis_line_width = 1
    plt.xaxis.axis_line_color = "red"
    plt.xaxis.axis_label_text_color = "brown"
    plt.yaxis.axis_label = "Consumption Quantity"
    plt.yaxis.axis_line_width = 1
    plt.yaxis.axis_line_color = "yellow"
    plt.yaxis.axis_label_text_color = "red"
    plt.yaxis.major_label_text_color = "blue"
    plt.yaxis.major_label_orientation = "vertical"
    plt.toolbar.autohide = True

    by_year = items_df.groupby('Year')['consumptionQty'].mean()
    by_month = items_df.groupby('Month')['consumptionQty'].mean()
    by_year_df = pd.DataFrame(by_year).reset_index().sort_values(by='consumptionQty', ascending=True)
    by_month_df = pd.DataFrame(by_month).reset_index().sort_values(by='consumptionQty', ascending=True)

    years = by_year_df['Year'].unique()
    source1 = ColumnDataSource(data=by_year_df)
    plt1 = figure(title="AVERAGE YEARLY CONSUMPTION",
                  y_range=by_year_df['Year'], plot_height=350, plot_width=500, toolbar_location="left",
                  x_axis_label="Mean", y_axis_label="Year",
                  tooltips=[("Year", "@Year"),("Mean", "@consumptionQty")])

    plt1.hbar(y='Year', right='consumptionQty', height=0.7, source=source1,
           color=factor_cmap('Year', Spectral5, years))

    months = by_month_df['Month'].unique()
    source2 = ColumnDataSource(data=by_month_df)
    plt2 = figure(title="AVERAGE MONTHLY CONSUMPTION",
                    y_range=by_month_df['Month'], plot_height=350, plot_width=500, toolbar_location="left",
                    x_axis_label="Mean", y_axis_label="Months",
                  tooltips=[("Month", "@Month"), ("Mean", "@consumptionQty")])
    plt1.x_range.start = 0
    plt1.outline_line_color = "brown"
    plt1.xgrid.grid_line_color = None
    plt1.ygrid.grid_line_color = None
    plt1.toolbar.autohide = True
    plt1.outline_line_color = None

    plt2.hbar(y='Month', right='consumptionQty', height=0.7, source=source2,
              color=factor_cmap('Month', Set3_12,months))
    plt2.x_range.start = 0
    plt2.outline_line_color = "brown"
    plt2.xgrid.grid_line_color = None
    plt2.ygrid.grid_line_color = None
    plt2.toolbar.autohide = True
    plt2.outline_line_color= None

    plots = Column(plt,plt2,plt1)

    div, script = components(plots)
    s_type = 'STATISTICS'
    qty_stats = calc_stats(item)

    context = {'title': 'ANALYSIS |STATS|'+str(cde),
                   'productData': item,
                   'qty_stats': qty_stats,
                   's_type': s_type,
                   'the_div': div,
                   'the_script': script,
                   'resources': INLINE.render(),
                   }
    return render(request, 'analysis/visuals_product.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def product_visual(request):
    products = ProductDetailExp.objects.all()

    if request.method == 'POST':
        var_stat = request.POST['stat']
        var_time = request.POST['time']
        item = ProductDetailExp.objects.get(code = request.POST['productSelect'])
        data = ProductDetailExp.objects.get(code=request.POST['productSelect'])
        c_data = ConsumptionData.objects.filter(productDetail=item)
        items_list = []

        for p in c_data:
            items_list.append([p.consumptionDate, p.consumptionQty])

        items_columns = ['consumptionDate', 'consumptionQty']
        items_df = pd.DataFrame(items_list, columns=items_columns)
        items_df['Date'] = pd.to_datetime(items_df['consumptionDate'])
        items_df['Year'] = pd.DatetimeIndex(items_df['Date']).year
        items_df['Month'] = pd.DatetimeIndex(items_df['Date']).strftime("%b")
        items_df['Day'] = pd.DatetimeIndex(items_df['Date']).strftime("%a")
        items_df['consumptionQty'] = items_df['consumptionQty'].astype(float)  # Convert from str to float
        items_df['Year'] = items_df['Year'].apply(str)  # From integer to string

        if var_stat == 'stats':
            s_type = 'STATISTICS'
            qty_stats = calc_stats(data)
            plt = figure(width=400, height=400, title="CONSUMPTION GRAPH",x_axis_type="datetime")
            plt.line(x=items_df.consumptionDate, y=items_df.consumptionQty,line_color='green')
            plt.title.text_color = "olive"
            plt.title.text_font = "times"
            plt.title.text_font_style = "italic"
            plt.xaxis.axis_label = "Consumption Quantity"
            plt.xaxis.axis_line_width = 1
            plt.xaxis.axis_line_color = "red"
            plt.xaxis.axis_label_text_color = "brown"
            plt.yaxis.axis_label = "Consumption Date"
            plt.yaxis.axis_line_width = 1
            plt.yaxis.axis_line_color = "yellow"
            plt.yaxis.axis_label_text_color = "red"
            plt.yaxis.major_label_text_color = "blue"
            plt.yaxis.major_label_orientation = "vertical"
            plt.toolbar.autohide = True
            div,script = components(plt)

            context = {'title': 'ANALYSIS | PRODUCTS',
                       'allProducts': products,
                       'productData': item,
                       'qty_stats': qty_stats,
                       's_type': s_type,
                       'the_div': div,
                       'the_script': script,
                       'resources': INLINE.render(),
                       }
            return render(request, 'analysis/visuals.html', context)

        elif var_stat == 'Sum':
            s_type = 'SUM'
            if var_time == 'Year':
                v_type = 'Year'
                by_group = items_df.groupby('Year')['consumptionQty'].sum()
                result_df = pd.DataFrame(by_group).reset_index()
            elif var_time == 'YMonth':
                v_type = 'YMonth'
                by_group = items_df.groupby(['Year', 'Month'])['consumptionQty'].sum()
                result_df = pd.DataFrame(by_group).reset_index()
            elif var_time == 'Month':
                v_type = 'Month'
                by_group = items_df.groupby('Month')['consumptionQty'].sum()
                result_df = pd.DataFrame(by_group).reset_index()
            else:
                v_type = 'Day' # For the day

            json_records = result_df.to_json(orient='records')
            data = []
            data = json.loads(json_records)
            context = {'title': 'ANALYSIS | PRODUCTS', 'allProducts': products,
                       'productData': c_data, 's_type': s_type, 'v_type': v_type,
                       'data_df': data, }
            return render(request, 'analysis/visuals.html', context)
        else:
            s_type = 'MEAN'
            if var_time == 'Year':
                v_type = 'Year'
                by_group = items_df.groupby('Year')['consumptionQty'].mean()
                result_df = pd.DataFrame(by_group).reset_index()
            elif var_time == 'YMonth':
                v_type = 'YMonth'
                by_group = items_df.groupby(['Year', 'Month'])['consumptionQty'].mean()
                result_df = pd.DataFrame(by_group).reset_index()
            elif var_time == 'Month':
                v_type = 'Month'
                by_group = items_df.groupby('Month')['consumptionQty'].mean()
                result_df = pd.DataFrame(by_group).reset_index()
            else:
                v_type = 'Day'

            json_records = result_df.to_json(orient='records')
            data = []
            data = json.loads(json_records)
            context = {'title': 'ANALYSIS | PRODUCTS', 'allProducts': products,
                       'productData': c_data, 's_type': s_type, 'v_type': v_type,
                       'data_df': data, }
            return render(request, 'analysis/visuals.html', context)

    context = {
        'title': 'ANALYSIS | PRODUCTS',
        'allProducts': products,
    }
    return render(request, 'analysis/visuals.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_consumption_method_1_month_list(request):
    data = ProductDetailExp.objects.all()
    items = []
    items_columns = ['code','desc',
                     'price',
                     'planned_qty_1_month_mean',
                     'planned_qty_1_month_order_cost',
                     'planned_qty_1_month_order_cost_thousands',
                     'annual_plan_cost',
                     'amc_in_packs',
                     'amc_adjusted_for_stock_outs',
                     'percentage_change_in_consumption',
                     'min_amc',
                     'max_amc',
                     'poisson_mode_quantity',
                     'safety_stock',
                     'qty_to_procure',
                     'calculated_1_month_cycle_cost_of_procurement',
                     'calculated_1_month_cycle_cost_of_procurement_thousand',
                     'consumption_annual_procurement_cost',
                     'budget_deficit_in_plan',
                     'percentage_available_funding',]
    for p in data:
        c_method_data = consumption_method_1_month_cycle(p)
        items.append((c_method_data['code'], c_method_data['desc'],
                      c_method_data['price'],
                      c_method_data['planned_qty_1_month_mean'],
                      c_method_data['planned_qty_1_month_order_cost'],
                      c_method_data['planned_qty_1_month_order_cost_thousands'],
                      c_method_data['annual_plan_cost'],
                      c_method_data['amc_in_packs'],c_method_data['amc_adjusted_for_stock_outs'],
                      c_method_data['percentage_change_in_consumption'],
                      c_method_data['min_amc'],
                      c_method_data['max_amc'],
                      c_method_data['poisson_mode_quantity'],
                      c_method_data['safety_stock'],
                      c_method_data['qty_to_procure'],
                      c_method_data['calculated_1_month_cycle_cost_of_procurement'],
                      c_method_data['calculated_1_month_cycle_cost_of_procurement_thousand'],
                      c_method_data['consumption_annual_procurement_cost'],
                      c_method_data['budget_deficit_in_plan'],
                      c_method_data['percentage_available_funding']
                      ))

    items_df = pd.DataFrame(items, columns=items_columns)
    items_df.dropna(axis=0, inplace=True)
    items_df.code = items_df['code'].astype(int)

    json_records = items_df.to_json(orient='records')
    data = json.loads(json_records)
    p = Paginator(data, 8)
    page_num = request.GET.get('page', 1)
    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)
    context = {'title': 'ANALYSIS | EOQ THREE',
               'data_df': page, }
    return render(request, 'analysis/c_method_1_month_list.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_eoq_1_month_list(request):
    data = ProductDetailExp.objects.all()
    items = []
    items_columns = ['CODE', 'DESCRIPTION','price',
                     'planned_qty_1_month_mean','planned_qty_1_month_order_cost',
                     'planned_qty_1_month_order_cost_thousands','year_demand',
                     'carrying_cost','ordering_cost','economic_order_quantity',
                     'annual_carrying_cost','annual_ordering_cost', 'annual_inventory_mgt_cost', 'annual_demand_cost',
                     'length_of_order_cycle_days', 'number_cycles_per_year', 'investment_cost_per_cycle',
                     'annual_investment_cost', 'annual_investment_cost_millions', 'annual_total_cost',
                     'annual_total_cost_millions', 'percentage_annual_inventory_mgt_cost_per_demand_cost',
                     'plan_budget_deficit','percentage_available_funding']
    for p in data:
        eoq_data = eoq_model_1_month_cycle(p)
        items.append([eoq_data['code'],eoq_data['desc'],eoq_data['price'],
                      eoq_data['planned_qty_1_month_mean'],eoq_data['planned_qty_1_month_order_cost'],
                      eoq_data['planned_qty_1_month_order_cost_thousands'],eoq_data['year_demand'],
                      eoq_data['carrying_cost'],eoq_data['ordering_cost'],eoq_data['economic_order_quantity'],
                      eoq_data['annual_carrying_cost'],eoq_data['annual_ordering_cost'],
                      eoq_data['annual_inventory_mgt_cost'],
                      eoq_data['annual_demand_cost'],
                      eoq_data['length_of_order_cycle_days'],eoq_data['number_cycles_per_year'],
                      eoq_data['investment_cost_per_cycle'],
                      eoq_data['annual_investment_cost'],eoq_data['annual_investment_cost_millions'],
                      eoq_data['annual_total_cost'],eoq_data['annual_total_cost_millions'],
                      eoq_data['percentage_annual_inventory_mgt_cost_per_demand_cost'],
                      eoq_data['plan_budget_deficit'],
                      eoq_data['percentage_available_funding']])

    items_df = pd.DataFrame(items, columns=items_columns)
    items_df.dropna(axis=0, inplace=True)
    items_df.CODE = items_df['CODE'].astype(int)
    items_df['Funding_Position'] = np.where(items_df.percentage_available_funding < 95.0,
                                            'Under Funding',np.where(items_df.percentage_available_funding > 105.0,
                                                                     'Over Funding','Adequate Funding'))

    json_records = items_df.to_json(orient='records')
    data = json.loads(json_records)
    p = Paginator(data,8)
    page_num = request.GET.get('page',1)
    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)
    context = {'title': 'ANALYSIS | EOQ THREE',
               'data_df': page, }
    return render(request, 'analysis/eoq_1_month_list.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_standard_consumption_method_1_week_list(request):
    data = ProductDetailExp.objects.all()
    items = []
    items_columns = ['code', 'desc',
                     'price',
                     'planned_qty_1_month_mean',
                     'amc_in_packs',
                     'adjusted_quantity_per_week_cycle',
                     'adjusted_annual_carrying_cost',
                     'adjusted_annual_ordering_cost',
                     'adjusted_annual_inventory_mgt_cost',
                     'adjusted_investment_cost_per_cycle',
                     'adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost',
                     'net_effect_on_inventory_mgt_costs']
    for p in data:
        c_method_data = standardised_consumption_plan_1_week_cycle(p)
        items.append((c_method_data['code'], c_method_data['desc'],
                      c_method_data['price'],
                      c_method_data['planned_qty_1_month_mean'],
                      c_method_data['amc_in_packs'],
                      c_method_data['adjusted_quantity_per_week_cycle'],
                      c_method_data['adjusted_annual_carrying_cost'],
                      c_method_data['adjusted_annual_ordering_cost'],
                      c_method_data['adjusted_annual_inventory_mgt_cost'],
                      c_method_data['adjusted_investment_cost_per_cycle'],
                      c_method_data['adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost'],
                      c_method_data['net_effect_on_inventory_mgt_costs']
                      ))
    items_df = pd.DataFrame(items, columns=items_columns)
    items_df.dropna(axis=0, inplace=True)
    items_df.code = items_df['code'].astype(int)
    json_records = items_df.to_json(orient='records')
    data = json.loads(json_records)
    p = Paginator(data, 8)
    page_num = request.GET.get('page', 1)
    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)
    context = {'title': 'ANALYSIS | EOQ THREE',
               'data_df': page, }
    return render(request, 'analysis/standard_c_method_1_week.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_consumption_method_1_month_cde(request,cde):
    data = ProductDetailExp.objects.get(code=cde)
    eoq_data = consumption_method_1_month_cycle(data)
    context = {'title': 'ANALYSIS|CONSUMPTION 1-MONTH METHOD',
               'productData': eoq_data}
    return render(request, 'analysis/c_method_1.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_eoq_1_month_1_month_cde(request,cde):
    data = ProductDetailExp.objects.get(code=cde)
    eoq_data = eoq_model_1_month_cycle(data)
    context = {'title': 'ANALYSIS | EOQ 1',
               'productData': eoq_data}
    return render(request, 'analysis/eoq_1.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_standard_consumption_method_1_week_cde(request,cde):
    data = ProductDetailExp.objects.get(code=cde)
    eoq_data = standardised_consumption_plan_1_week_cycle(data)
    context = {'title': 'ANALYSIS|CONSUMPTION|1-WEEK',
               'productData': eoq_data}
    return render(request, 'analysis/standard_c_method_1.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def under_funding_1_month(request):
    data = ProductDetailExp.objects.all()
    items = []
    items_columns = ['CODE', 'DESCRIPTION', 'price',
                     'planned_qty_1_month_mean', 'planned_qty_1_month_order_cost',
                     'planned_qty_1_month_order_cost_thousands', 'year_demand',
                     'carrying_cost', 'ordering_cost', 'economic_order_quantity',
                     'annual_carrying_cost', 'annual_ordering_cost', 'annual_inventory_mgt_cost', 'annual_demand_cost',
                     'length_of_order_cycle_days', 'number_cycles_per_year', 'investment_cost_per_cycle',
                     'annual_investment_cost', 'annual_investment_cost_millions', 'annual_total_cost',
                     'annual_total_cost_millions', 'percentage_annual_inventory_mgt_cost_per_demand_cost',
                     'plan_budget_deficit', 'percentage_available_funding']
    for p in data:
        eoq_data = eoq_model_1_month_cycle(p)
        items.append([eoq_data['code'], eoq_data['desc'], eoq_data['price'],
                      eoq_data['planned_qty_1_month_mean'], eoq_data['planned_qty_1_month_order_cost'],
                      eoq_data['planned_qty_1_month_order_cost_thousands'], eoq_data['year_demand'],
                      eoq_data['carrying_cost'], eoq_data['ordering_cost'], eoq_data['economic_order_quantity'],
                      eoq_data['annual_carrying_cost'], eoq_data['annual_ordering_cost'],
                      eoq_data['annual_inventory_mgt_cost'],
                      eoq_data['annual_demand_cost'],
                      eoq_data['length_of_order_cycle_days'], eoq_data['number_cycles_per_year'],
                      eoq_data['investment_cost_per_cycle'],
                      eoq_data['annual_investment_cost'], eoq_data['annual_investment_cost_millions'],
                      eoq_data['annual_total_cost'], eoq_data['annual_total_cost_millions'],
                      eoq_data['percentage_annual_inventory_mgt_cost_per_demand_cost'],
                      eoq_data['plan_budget_deficit'],
                      eoq_data['percentage_available_funding']])

    items_df = pd.DataFrame(items, columns=items_columns)
    items_df.dropna(axis=0, inplace=True)
    items_df.CODE = items_df['CODE'].astype(int)
    items_df['Funding_Position'] = np.where(items_df.percentage_available_funding < 95.0,
                                            'Under Funding', np.where(items_df.percentage_available_funding > 105.0,
                                                                      'Over Funding', 'Adequate Funding'))

    items_df_over = items_df[items_df['Funding_Position'] == 'Under Funding']

    json_records = items_df_over.to_json(orient='records')
    data = json.loads(json_records)
    context = {'title': 'ANALYSIS|EOQ|1|UNDER FUNDING',
               'data_df': data, }
    return render(request, 'analysis/eoq_1_month_list.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def adequate_funding_1_month(request):
    data = ProductDetailExp.objects.all()
    items = []
    items_columns = ['CODE', 'DESCRIPTION', 'price',
                     'planned_qty_1_month_mean', 'planned_qty_1_month_order_cost',
                     'planned_qty_1_month_order_cost_thousands', 'year_demand',
                     'carrying_cost', 'ordering_cost', 'economic_order_quantity',
                     'annual_carrying_cost', 'annual_ordering_cost', 'annual_inventory_mgt_cost', 'annual_demand_cost',
                     'length_of_order_cycle_days', 'number_cycles_per_year', 'investment_cost_per_cycle',
                     'annual_investment_cost', 'annual_investment_cost_millions', 'annual_total_cost',
                     'annual_total_cost_millions', 'percentage_annual_inventory_mgt_cost_per_demand_cost',
                     'plan_budget_deficit', 'percentage_available_funding']
    for p in data:
        eoq_data = eoq_model_1_month_cycle(p)
        items.append([eoq_data['code'], eoq_data['desc'], eoq_data['price'],
                      eoq_data['planned_qty_1_month_mean'], eoq_data['planned_qty_1_month_order_cost'],
                      eoq_data['planned_qty_1_month_order_cost_thousands'], eoq_data['year_demand'],
                      eoq_data['carrying_cost'], eoq_data['ordering_cost'], eoq_data['economic_order_quantity'],
                      eoq_data['annual_carrying_cost'], eoq_data['annual_ordering_cost'],
                      eoq_data['annual_inventory_mgt_cost'],
                      eoq_data['annual_demand_cost'],
                      eoq_data['length_of_order_cycle_days'], eoq_data['number_cycles_per_year'],
                      eoq_data['investment_cost_per_cycle'],
                      eoq_data['annual_investment_cost'], eoq_data['annual_investment_cost_millions'],
                      eoq_data['annual_total_cost'], eoq_data['annual_total_cost_millions'],
                      eoq_data['percentage_annual_inventory_mgt_cost_per_demand_cost'],
                      eoq_data['plan_budget_deficit'],
                      eoq_data['percentage_available_funding']])

    items_df = pd.DataFrame(items, columns=items_columns)
    items_df.dropna(axis=0, inplace=True)
    items_df.CODE = items_df['CODE'].astype(int)
    items_df['Funding_Position'] = np.where(items_df.percentage_available_funding < 95.0,
                                            'Under Funding', np.where(items_df.percentage_available_funding > 105.0,
                                                                      'Over Funding', 'Adequate Funding'))

    items_df_over = items_df[items_df['Funding_Position'] == 'Adequate Funding']

    json_records = items_df_over.to_json(orient='records')
    data = json.loads(json_records)
    context = {'title': 'ANALYSIS|EOQ|1|ADEQUATE FUNDING',
               'data_df': data, }
    return render(request, 'analysis/eoq_1_month_list.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def over_funding_1_month(request):
    data = ProductDetailExp.objects.all()
    items = []
    items_columns = ['CODE', 'DESCRIPTION', 'price',
                     'planned_qty_1_month_mean', 'planned_qty_1_month_order_cost',
                     'planned_qty_1_month_order_cost_thousands', 'year_demand',
                     'carrying_cost', 'ordering_cost', 'economic_order_quantity',
                     'annual_carrying_cost', 'annual_ordering_cost', 'annual_inventory_mgt_cost', 'annual_demand_cost',
                     'length_of_order_cycle_days', 'number_cycles_per_year', 'investment_cost_per_cycle',
                     'annual_investment_cost', 'annual_investment_cost_millions', 'annual_total_cost',
                     'annual_total_cost_millions', 'percentage_annual_inventory_mgt_cost_per_demand_cost',
                     'plan_budget_deficit', 'percentage_available_funding']
    for p in data:
        eoq_data = eoq_model_1_month_cycle(p)
        items.append([eoq_data['code'], eoq_data['desc'], eoq_data['price'],
                      eoq_data['planned_qty_1_month_mean'], eoq_data['planned_qty_1_month_order_cost'],
                      eoq_data['planned_qty_1_month_order_cost_thousands'], eoq_data['year_demand'],
                      eoq_data['carrying_cost'], eoq_data['ordering_cost'], eoq_data['economic_order_quantity'],
                      eoq_data['annual_carrying_cost'], eoq_data['annual_ordering_cost'],
                      eoq_data['annual_inventory_mgt_cost'],
                      eoq_data['annual_demand_cost'],
                      eoq_data['length_of_order_cycle_days'], eoq_data['number_cycles_per_year'],
                      eoq_data['investment_cost_per_cycle'],
                      eoq_data['annual_investment_cost'], eoq_data['annual_investment_cost_millions'],
                      eoq_data['annual_total_cost'], eoq_data['annual_total_cost_millions'],
                      eoq_data['percentage_annual_inventory_mgt_cost_per_demand_cost'],
                      eoq_data['plan_budget_deficit'],
                      eoq_data['percentage_available_funding']])

    items_df = pd.DataFrame(items, columns=items_columns)
    items_df.dropna(axis=0, inplace=True)
    items_df.CODE = items_df['CODE'].astype(int)
    items_df['Funding_Position'] = np.where(items_df.percentage_available_funding < 95.0,
                                            'Under Funding', np.where(items_df.percentage_available_funding > 105.0,
                                                                      'Over Funding', 'Adequate Funding'))

    items_df_over = items_df[items_df['Funding_Position'] == 'Over Funding']

    json_records = items_df_over.to_json(orient='records')
    data = json.loads(json_records)
    context = {'title': 'ANALYSIS|EOQ|1|OVER FUNDING',
               'data_df': data, }
    return render(request, 'analysis/eoq_1_month_list.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def ajax_request_sidebar(request):
    if request.GET['cde'] == "":
        return HttpResponse("<p></p>")
    else:
        ps = ProductDetailExp.objects.filter(code__contains=request.GET['cde'])
        return HttpResponse("<p><a href=" + "/analysis/ajax/request/" +
                        str(p.code)+"/"+">"+str(p.code)+" " +
                        "</a><p>" for p in ps)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def ajax_request_main(request):
    if request.GET['cde'] == "":
        return HttpResponse("<p></p>")
    else:
        ps = ProductDetailExp.objects.filter(description__contains=request.GET['cde'])
        return HttpResponse("<p><a href=" + "/analysis/ajax/request/" +
                        str(p.code)+"/"+">"+str(p.code)+" " + p.description +
                        "</a><p>" for p in ps)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def ajax_request_all_products(request):
    if request.GET['cde'] == "":
        return HttpResponse("<p></p>")
    else:
        ps = ProductDetailExp.objects.filter(description__contains=request.GET['cde'])
        return HttpResponse("<p><a href=" + "/analysis/view/all/stock/" +
                        str(p.code)+"/"+">"+str(p.code)+" " + p.description +
                        "</a><p>" for p in ps)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def ajax_request_product_consumption(request,cde):
    data = ProductDetailExp.objects.get(code=int(cde))
    consumption_data = consumption_method_1_month_cycle(data)
    context = {'title': 'ANALYSIS|1|CONSUMPTION DATA',
               'productData': consumption_data,}
    return render(request, 'analysis/c_method_eoq_standard_1.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def ajax_request_product_eoq(request,cde):
    data = ProductDetailExp.objects.get(code=int(cde))
    eoq_data = eoq_model_1_month_cycle(data)
    context = {'title': 'ANALYSIS|1|EOQ DATA',
               'productData': eoq_data,}
    return render(request, 'analysis/c_method_eoq_standard_2.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def ajax_request_product_standard(request,cde):
    data = ProductDetailExp.objects.get(code=int(cde))
    eoq_data = eoq_model_1_month_cycle(data)
    context = {'title': 'ANALYSIS|1|STANDARD',
               'productData': eoq_data,}
    return render(request, 'analysis/c_method_eoq_standard_3.html', context)


########################################################################################################
#GRAPHS


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def product_graph(request ,cde):
    item = ProductDetailExp.objects.get(code=cde)
    c_data = ConsumptionData.objects.filter(productDetail=item)
    items_list = []

    for p in c_data:
        items_list.append([p.consumptionDate, p.consumptionQty])

    items_columns = ['consumptionDate', 'consumptionQty']
    items_df = pd.DataFrame(items_list, columns=items_columns)
    items_df['consumptionQty'] = items_df['consumptionQty'].astype(float)  # Convert from str to float

    plt = figure(width=1200, height=550, title="CONSUMPTION GRAPH", x_axis_type="datetime")
    plt.line(x=items_df.consumptionDate, y=items_df.consumptionQty, line_color='green')
    plt.title.text_color = "olive"
    plt.title.text_font = "times"
    plt.title.text_font_style = "italic"
    plt.xaxis.axis_label = "Consumption Quantity"
    plt.xaxis.axis_line_width = 1
    plt.xaxis.axis_line_color = "red"
    plt.xaxis.axis_label_text_color = "brown"
    plt.yaxis.axis_label = "Consumption Date"
    plt.yaxis.axis_line_width = 1
    plt.yaxis.axis_line_color = "yellow"
    plt.yaxis.axis_label_text_color = "red"
    plt.yaxis.major_label_text_color = "blue"
    plt.yaxis.major_label_orientation = "vertical"
    plt.toolbar.autohide = True
    div, script = components(plt)

    context = {'title': 'ANALYSIS|'+str(cde)+'GRAPH',
               'the_div': div,
               'the_script': script,
               'resources': INLINE.render(),
               }
    return render(request, 'analysis/product_graph.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_more_graphs(request):
    if request.method == 'GET':
        stat = request.GET.get('stat')
    else:
        stat = 'mean'

    products = ProductDetailExp.objects.all()
    items = []
    items_columns = ['CODE', 'DESCRIPTION', 'VEN', 'CURRENT_STOCK', 'STAT', ]
    for p in products:
        data = more_graphs_data(p,stat)
        if data is not None:
            items.append([data['code'], data['description'], data['ven'],data['current_stock'], data['stat']])

    products_df = pd.DataFrame(items, columns=items_columns)
    df = get_df_to_make_graphs(products_df)
    df1 = df.reset_index()

    factors = np.array(df1.CODE)
    factors2 = ['V','E','N']

    if stat is None:
        stat = 'Mean'

    source = ColumnDataSource(data=df1)
    tools = "pan,wheel_zoom, box_zoom,reset,box_select,lasso_select, hover"
    p = figure(title="Average Consumption of Drugs At Fort Portal Regional Referral Hospital",
               y_range=factors,plot_height=2000, plot_width=2000, tools=tools, toolbar_location="left",
               x_axis_label=str(stat),y_axis_label="PRODUCT CODE",
               tooltips=[("PRODUCT CODE", "@CODE"),("DESCRIPTION","@DESCRIPTION"),
                         ("VEN","@VEN"),("CURRENT STOCK","@CURRENT_STOCK"),(str(stat), "@STAT")]
               )
    p.hbar(y='CODE', right='STAT', height=0.7, source = source,
           color = factor_cmap('VEN',['red','yellow','black'],factors2),legend_field='VEN')

    p.title.text_color = "olive"
    p.title.text_font = "times"
    p.title.text_font_style = "italic"
    p.xaxis.major_label_orientation = 1.5
    p.outline_line_color = "brown"
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.x_range.start = 0
    # p.xaxis.visible = False
    p.legend.location = "top_center"
    div, script = components(p)

    context = {
        'the_div': div,
        'the_script': script,
        'resources': INLINE.render(),
    }
    return render(request,'analysis/graphs_stats.html',context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_graphs_1_month_consumption(request):
    if request.method == 'GET':
        stat = request.GET.get('stat')
    else:
        stat = 'mean'
    products = ProductDetailExp.objects.all()
    items = []
    items_columns = ['CODE', 'DESCRIPTION', 'VEN','PRICE','CURRENT_STOCK','STAT' ]
    for p in products:
        data = get_graphs_consumption_method_1_month_cycle(p, stat)
        if data is not None:
            items.append([data['code'], data['description'], data['ven'],data['PRICE'],data['current_stock'],
                          data['stat']])

    products_df = pd.DataFrame(items, columns=items_columns)
    df = get_df_to_make_graphs(products_df)
    df1 = df.reset_index()
    factors = np.array(df1.CODE)
    factors2 = ['V', 'E', 'N']
    if stat is None:
        stat = 'mean'

    source = ColumnDataSource(data=df1)
    tools = "pan,wheel_zoom, box_zoom,reset,box_select,lasso_select, hover"
    p = figure(title= str(stat),
               y_range=factors, plot_height=2000, plot_width=2000, tools=tools, toolbar_location="left",
               x_axis_label=str(stat), y_axis_label="PRODUCT CODE",
               tooltips=[("PRODUCT CODE", "@CODE"), ("DESCRIPTION", "@DESCRIPTION"), ("VEN", "@VEN"),
                         (str(stat), "@STAT")]
               )
    p.hbar(y='CODE', right='STAT', height=0.7, source=source,
           color=factor_cmap('VEN', ['red', 'yellow', 'black'], factors2), legend_field='VEN')

    p.title.text_color = "olive"
    p.title.text_font = "times"
    p.title.text_font_style = "italic"
    p.xaxis.major_label_orientation = 1.5
    p.outline_line_color = "brown"
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.x_range.start = 0
    # p.xaxis.visible = False
    p.legend.location = "top_center"
    div, script = components(p)

    context = {
        'the_div': div,
        'the_script': script,
        'resources': INLINE.render(),
    }
    return render(request, 'analysis/graphs_1_c_method.html', context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_graphs_1_month_eoq(request):
    if request.method == 'GET':
        stat = request.GET.get('stat')
    else:
        stat = 'economic_order_quantity'
    products = ProductDetailExp.objects.all()
    items = []
    items_columns = ['CODE', 'DESCRIPTION', 'VEN','PRICE','CURRENT_STOCK', 'STAT', ]
    for p in products:
        data = get_graphs_eoq_model_1_month_cycle(p,stat)
        if data is not None:
            items.append([data['code'], data['description'], data['ven'],data['PRICE'],data['current_stock'],
                          data['stat']])

    products_df = pd.DataFrame(items, columns=items_columns)
    df = get_df_to_make_graphs(products_df)
    df1 = df.reset_index()
    factors = np.array(df1.CODE)
    factors2 = ['V','E','N']

    if stat is None:
        stat = 'mean'
    source = ColumnDataSource(data=df1)
    tools = "pan,wheel_zoom, box_zoom,reset,box_select,lasso_select, hover"
    p = figure(title=str(stat),
               y_range=factors,plot_height=2000, plot_width=2000, tools=tools, toolbar_location="left",
               x_axis_label=stat,y_axis_label="PRODUCT CODE",
               tooltips=[("PRODUCT CODE", "@CODE"),("DESCRIPTION","@DESCRIPTION"),("VEN","@VEN"),(str(stat), "@STAT")]
               )
    p.hbar(y='CODE', right='STAT', height=0.7, source = source,
           color = factor_cmap('VEN',['red','yellow','black'],factors2),legend_field='VEN')

    p.title.text_color = "olive"
    p.title.text_font = "times"
    p.title.text_font_style = "italic"
    p.xaxis.major_label_orientation = 1.5
    p.outline_line_color = "brown"
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.x_range.start = 0
    p.legend.location = "top_center"
    div, script = components(p)

    context = {
        'the_div': div,
        'the_script': script,
        'resources': INLINE.render(),
    }
    return render(request,'analysis/graphs_1_eoq.html',context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def get_graphs_standard_c_method_1_week_consumption(request):
    if request.method == 'GET':
        stat = request.GET.get('stat')
    else:
        stat = 'mean'
    products = ProductDetailExp.objects.all()
    items = []
    items_columns = ['CODE', 'DESCRIPTION', 'VEN','PRICE','CURRENT_STOCK','STAT' ]
    for p in products:
        data = get_graphs_standardised_consumption_plan_1_week_cycle(p, stat)
        if data is not None:
            items.append([data['code'], data['description'], data['ven'],data['PRICE'],data['current_stock'],
                          data['stat']])

    products_df = pd.DataFrame(items, columns=items_columns)
    df = get_df_to_make_graphs(products_df)
    df1 = df.reset_index()
    factors = np.array(df1.CODE)
    factors2 = ['V', 'E', 'N']
    if stat is None:
        stat = 'mean'

    source = ColumnDataSource(data=df1)
    tools = "pan,wheel_zoom, box_zoom,reset,box_select,lasso_select, hover"
    p = figure(title= str(stat),
               y_range=factors, plot_height=2000, plot_width=2000, tools=tools, toolbar_location="left",
               x_axis_label=str(stat), y_axis_label="PRODUCT CODE",
               tooltips=[("PRODUCT CODE", "@CODE"), ("DESCRIPTION", "@DESCRIPTION"), ("VEN", "@VEN"),
                         (str(stat), "@STAT")]
               )
    p.hbar(y='CODE', right='STAT', height=0.7, source=source,
           color=factor_cmap('VEN', ['red', 'yellow', 'black'], factors2), legend_field='VEN')

    p.title.text_color = "olive"
    p.title.text_font = "times"
    p.title.text_font_style = "italic"
    p.xaxis.major_label_orientation = 1.5
    p.outline_line_color = "brown"
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.x_range.start = 0
    p.legend.location = "top_center"
    div, script = components(p)

    context = {
        'the_div': div,
        'the_script': script,
        'resources': INLINE.render(),
    }
    return render(request, 'analysis/graphs_standard_c_method_1_week.html', context)