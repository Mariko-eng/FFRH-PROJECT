from django.db import models
from django.db.models.signals import pre_save,post_save

# Create your models here.


class ProductDetailExp(models.Model):
    code = models.IntegerField(default=100000,unique=True)
    description = models.CharField(unique=True,max_length=500)
    ven = models.CharField(max_length=5, null=True, blank=True)
    unit = models.DecimalField(max_digits=100, decimal_places=1, null=True)
    price = models.DecimalField(max_digits=100, decimal_places=1, null=True)
    planned_Qty_2Month_Mean = models.DecimalField(max_digits=100, decimal_places=1, null=True)
    currentStock = models.DecimalField(max_digits=100,decimal_places=3,default=0)

    @property
    def full_description(self):
        return '%s : %s' % (str(self.code), self.description)

    def __str__(self):
        return self.full_description


class StockDeliveryData(models.Model):
    deliveryDate = models.DateTimeField(auto_now_add=True)
    productDetail = models.ForeignKey(ProductDetailExp,on_delete=models.CASCADE,null=True)
    deliveredQty = models.DecimalField(max_digits=100,decimal_places=3)

    def __str__(self):
        return str(self.deliveryDate)


class HospitalUserUnit(models.Model):
    user_unit = models.CharField(unique=True,max_length=100)

    def __str__(self):
        return str(self.user_unit)


class ConsumptionData(models.Model):
    consumptionDate = models.DateTimeField(auto_now_add=True)
    consumptionQty = models.DecimalField(max_digits=100,decimal_places=1)
    productDetail = models.ForeignKey(ProductDetailExp, on_delete=models.CASCADE)
    pharmacies = models.ForeignKey(HospitalUserUnit,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return str(self.consumptionDate)


class TargetHospitalUserUnit(models.Model):
    user_unit = models.ForeignKey(HospitalUserUnit,null=True,on_delete=models.SET_NULL)
    productDetail = models.ForeignKey(ProductDetailExp,null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.productDetail) + " " + str(self.user_unit)


def add_new_stock(sender,instance,created,**kwargs):
    if created : #mMeans a Product already exists
        plinkStr = str(instance.productDetail)
        plinkSplit =  plinkStr.split(':')
        plinkStrip = plinkSplit[1].strip()
        drug = ProductDetailExp.objects.get(description = plinkStrip)
        drug_qty = drug.currentStock
        new_drug_qty = drug_qty + instance.deliveredQty
        ProductDetailExp.objects.filter(description = plinkStrip).update(currentStock = new_drug_qty)
    else:
        pass


post_save.connect(add_new_stock, sender=StockDeliveryData)


def subtract_from_stock(sender, instance, *args, **kwargs):
    plinkStr = str(instance.productDetail)
    plinkSplit = plinkStr.split(':')
    plinkStrip = plinkSplit[1].strip()
    drug = ProductDetailExp.objects.get(description=plinkStrip)
    drug_qty = drug.currentStock
    if drug_qty > 0 and drug_qty >= instance.consumptionQty:
        new_drug_qty = drug_qty - instance.consumptionQty
        ProductDetailExp.objects.filter(description=plinkStrip).update(currentStock=new_drug_qty)
    else:
        new_drug_qty = drug_qty
        ProductDetailExp.objects.filter(description=plinkStrip).update(currentStock=new_drug_qty)
        raise Exception("Too Many Drugs Were Requested For; Current Drugs Available:" + str(drug_qty))


pre_save.connect(subtract_from_stock, sender=ConsumptionData)
