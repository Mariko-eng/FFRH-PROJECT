from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Max, Min, Sum, Avg,StdDev,Variance
from analysis.models import ProductDetailExp,ConsumptionData,StockDeliveryData,HospitalUserUnit,TargetHospitalUserUnit
# from .models import ProductDetails,TheDailyConsumption,StockDelivered,HospitalPharmacy
from .forms import ProductForm,DailyConsumptionForm,StockDeliveredForm,HospitalPharmacyForm,TargetedUserUnitForm
from .forms import RegisterNewUser
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .decorators import already_signed_in,main_admin_authorized
from django.contrib.auth.models import Group
from django.utils import timezone
import os


# Create your views here.
@already_signed_in
def register_new_user(request):
    form = RegisterNewUser()
    if request.method == 'POST':
        form = RegisterNewUser(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name= 'sub_admin')
            user.groups.add(group)
            messages.success(request,'Account created for '+ str(form.cleaned_data['username']))
            return redirect('login_user')

    context = {'form':form}
    return render(request,'inventory/user_register.html',context)


@already_signed_in
def login_user(request):
    if request.method == 'POST':
        u = request.POST.get('user')
        p = request.POST.get('pass')
        user = authenticate(request,username = u,password = p)
        if user is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.info(request,"Incorrect email and password")

    context = {"title": 'LOGIN'}
    return render(request,'inventory/user_login.html',context)


def logout_user(request):
    logout(request)
    return redirect('login_user')


@login_required(login_url='login_user')
@main_admin_authorized(status="main_admin")
def new_product(request):
    code_max = ProductDetailExp.objects.all().aggregate(Max('code'))
    code_no = code_max['code__max'] + 1
    if request.method == 'POST':
        data = {
            'code': code_no,
            'description': request.POST['description'],
            'ven':request.POST['ven'],
            'unit':request.POST['unit'],
            'price': request.POST['price'],
            'planned_Qty_2Month_Mean':request.POST['planned_Qty_2Month_Mean'],
            'currentStock': request.POST['currentStock'],
        }
        form = ProductForm(data)
        if form.is_valid():
            form.save()

        code_no = code_no + 1
        context = {
            'data': data,
            'title': 'INVENTORY  | ADD PRODUCT',
            'form': ProductForm,
            'max_code': code_no,
        }
        return render(request, 'inventory/product.html', context)

    context = {
        'title': 'INVENTORY  | ADD PRODUCT',
        'form' : ProductForm,
        'max_code': code_no,
    }
    return render(request,'inventory/newproduct.html',context)


@login_required(login_url='login_user')
def add_target_user_unit(request):
    if request.method == 'POST':
        data = request.POST
        form_data = TargetedUserUnitForm(data)
        if form_data.is_valid():
            a = TargetHospitalUserUnit.objects.filter(user_unit = request.POST['user_unit'],
                                                      productDetail=request.POST['productDetail'])
            if len(a) == 0:
                print("Empty")
                form_data.save()
                context = {
                    'title': 'INVENTORY|ADD|USER|UNIT',
                    'form': TargetedUserUnitForm(),
                    'status': "Success! The Product Has Been Added To User Unit, Try Out Another"
                }
                return render(request, 'inventory/new_user_unit.html', context)
            else:
                if len(a) >= 2:
                    a[0].delete()
                    context = {
                        'title': 'INVENTORY|ADD|USER|UNIT',
                        'form': TargetedUserUnitForm(),
                        'status': "The Product You Tried To Add Was Already Added To User Unit, Try Out Another"
                    }
                    return render(request, 'inventory/new_user_unit.html', context)
                else:
                    context = {
                        'title': 'INVENTORY|ADD|USER|UNIT',
                        'form': TargetedUserUnitForm(),
                        'status': "The Product You Tried To Add Was Already Added To User Unit, Try Out Another"
                    }
                    return render(request, 'inventory/new_user_unit.html', context)
        else:
            context = {
                'title': 'INVENTORY|ADD|USER|UNIT',
                'form': TargetedUserUnitForm(),
            }
            return render(request, 'inventory/new_user_unit.html', context)
    context = {
        'title': 'INVENTORY|ADD|USER|UNIT',
        'form': TargetedUserUnitForm,
    }
    return render(request,'inventory/new_user_unit.html',context)


@login_required(login_url='login_user')
# @sub_admin_authorized(status="sub_admin")
def dashboard(request):
    all_products = ProductDetailExp.objects.all()
    #last5deliveries = ConsumptionData.objects.filter(consumptionDate__lte = timezone.now)[:5]
    #last5orders = StockDelivered.objects.filter(deliveryDate__lte = timezone.now())[:5]
    last5orders = ConsumptionData.objects.all()[:5]
    last5deliveries = StockDeliveryData.objects.all()[:5]
    total_orders = ConsumptionData.objects.all().count()
    total_deliveries = StockDeliveryData.objects.all().count()
    total_products = all_products.count()
    context = {
        'title' : 'INVENTORY | DASHBOARD',
        'allproducts' : all_products,
        'last5deliveries' : last5deliveries,
        'last5orders' : last5orders,
        'total_orders':total_orders,
        'total_deliveries':total_deliveries,
        'total_products':total_products,
    }
    return render(request,'inventory/dashboard.html',context)


@login_required(login_url='login_user')
# @sub_admin_authorized(status="sub_admin")
def available_current_stock(request):
    products = ProductDetailExp.objects.all()
    context = {
        'title' : 'ANALYSIS | PRODUCTS',
        'allProducts': products,
    }
    return render(request,'inventory/allproducts.html',context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def update_delete_stock(request):
    products = ProductDetailExp.objects.all()

    context = {
        'title' : 'ANALYSIS | PRODUCTS',
        'allProducts': products,
    }
    return render(request,'inventory/update_delete.html',context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def update_stock(request,cde):
    product = ProductDetailExp.objects.get(code=cde)
    form = ProductForm(instance=product)
    if request.method == "POST":
        form = ProductForm(request.POST,instance=product)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('update_delete'))
            #return HttpResponseRedirect(reverse('polls:results', args=(question.id,))) -> '/polls/3/results/'

    context = {
        'title': 'INVENTORY |' + str(product.description),
        'product': product,
        'form' : form
    }
    return render(request,'inventory/update.html',context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def delete_item(request ,cde):
    product = ProductDetailExp.objects.get(code=cde)
    product.delete()
    products = ProductDetailExp.objects.all()
    context = {
        'title': 'ANALYSIS | PRODUCTS',
        'allProducts': products,
    }
    return render(request, 'inventory/update_delete.html', context)


@login_required(login_url='login_user')
# @sub_admin_authorized(status="sub_admin")
def more_product_info(request,cde):
    product = ProductDetailExp.objects.get(code=cde)
    productDelivery = product.stockdeliverydata_set.all()
    productConsumption = product.consumptiondata_set.all()
    cQty_Min = product.consumptiondata_set.all().aggregate(Min('consumptionQty'))
    cQty_Max = product.consumptiondata_set.all().aggregate(Max('consumptionQty'))
    cQty_Sum = product.consumptiondata_set.all().aggregate(Sum('consumptionQty'))
    cQty_Avg = product.consumptiondata_set.all().aggregate(Avg('consumptionQty'))

    context = {
        'title': 'INVENTORY |' + str(product.description),
        'product' : str(product.code) + ' '+ str(product.description),
        'productCurrentStock': product.currentStock,
        'productDelivery' : productDelivery,
        'productConsumption' : productConsumption,
        'cQty_Min' : cQty_Min,
        'cQty_Max' : cQty_Max,
        'cQty_Sum' : cQty_Sum,
        'cQty_Avg' : cQty_Avg,
    }
    return render(request,'inventory/productDashboard.html',context)


@login_required(login_url='login_user')
@main_admin_authorized(status='main_admin')
def new_stock(request):
    if request.method == 'POST':
        data = request.POST
        formData = StockDeliveredForm(data)
        if formData.is_valid():
            formData.save()
        else:
            print("Inavlid")

    context = {
        'title': 'INVENTORY  | STOCK DELIVERY',
        'form': StockDeliveredForm,
    }
    return render(request,'inventory/newStock.html',context)


@login_required(login_url='login_user')
# @sub_admin_authorized(status="sub_admin")
def consumption(request):
    if request.method == 'POST':
        data = request.POST
        formData = DailyConsumptionForm(data)
        if formData.is_valid():
            try:
                formData.save()
                context = {
                    'title': 'INVENTORY  | STOCK CONSUMPTION',
                    'form': DailyConsumptionForm,
                }
                return render(request, 'inventory/outputStock.html', context)
            except Exception:
                context = {
                    'title': 'INVENTORY  | OUT OF STOCK ',
                }
                return render(request, 'inventory/outOfStock.html', context)
        else:
            context = {
                'title': 'INVENTORY  | OUT OF STOCK ',
            }
            return render(request, 'inventory/outOfStock.html', context)
    else:
        context = {
            'title': 'INVENTORY  | STOCK CONSUMPTION',
            'form': DailyConsumptionForm,
        }
        return render(request, 'inventory/outputStock.html', context)

