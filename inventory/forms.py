from django import forms
# from .models import ProductDetails,TheDailyConsumption,StockDelivered,HospitalPharmacy
from analysis.models import ProductDetailExp,ConsumptionData,StockDeliveryData,HospitalUserUnit,TargetHospitalUserUnit
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm,UserChangeForm
from django.contrib.auth.models import User,Group


# Inherit django's UserCreationForm to automatically use its attributes and methods such as automatic password hashing
# Also make use of the User model from django
class RegisterNewUser(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductDetailExp
        fields = "__all__"
        # fields = ['code','description','ven','unit','price','planned_Qty_2Month_Mean','currentStock']


class DailyConsumptionForm(forms.ModelForm):
    class Meta:
        model = ConsumptionData
        fields = "__all__"


class StockDeliveredForm(forms.ModelForm):
    class Meta:
        model = StockDeliveryData
        fields = "__all__"


class HospitalPharmacyForm(forms.ModelForm):
    class Meta:
        model = HospitalUserUnit
        fields = "__all__"


class TargetedUserUnitForm(forms.ModelForm):
    class Meta:
        model = TargetHospitalUserUnit
        fields = "__all__"