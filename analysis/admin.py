from django.contrib import admin
from .models import ProductDetailExp,ConsumptionData,HospitalUserUnit,TargetHospitalUserUnit,StockDeliveryData
# Register your models here.

admin.site.register(ProductDetailExp)
admin.site.register(ConsumptionData)
admin.site.register(StockDeliveryData)
admin.site.register(HospitalUserUnit)
admin.site.register(TargetHospitalUserUnit)

