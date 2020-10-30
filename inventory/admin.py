from django.contrib import admin
from .models import ProductDetails, HospitalPharmacy, StockDelivered,TheDailyConsumption
# Register your models here.

admin.site.register(ProductDetails)
admin.site.register(HospitalPharmacy)
admin.site.register(StockDelivered)
admin.site.register(TheDailyConsumption)


