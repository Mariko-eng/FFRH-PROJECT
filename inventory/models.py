from django.db import models
from django.db.models.signals import post_save, pre_save

# Create your models here.


class ProductDetails(models.Model):
    code = models.IntegerField(default=100000,unique=True)
    description = models.CharField(max_length=500)
    ven = models.CharField(max_length=5, null=True, blank=True)
    unit = models.DecimalField(max_digits=100, decimal_places=1, null=True)
    price = models.DecimalField(max_digits=100, decimal_places=3, null=True)
    planned_Qty_2Month_Mean = models.DecimalField(max_digits=100, decimal_places=3, null=True)
    currentStock = models.DecimalField(max_digits=100,decimal_places=3,default=0)

    @property
    def full_description(self):
        return '%s : %s' % (str(self.code), self.description)

    def __str__(self):
        return str(self.full_description)



class HospitalPharmacy(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class StockDelivered(models.Model):
    deliveryDate = models.DateTimeField(auto_now_add=True)
    productLink = models.ForeignKey(ProductDetails,on_delete=models.CASCADE,null=True)
    deliveredQty = models.DecimalField(max_digits=100,decimal_places=3)

    def __str__(self):
        return str(self.deliveryDate)


class TheDailyConsumption(models.Model):
    consumptionDate = models.DateTimeField(auto_now_add=True)
    productLink = models.ForeignKey(ProductDetails,on_delete=models.CASCADE,null=True)
    consumptionQty = models.IntegerField()
    pharmacies = models.ForeignKey(HospitalPharmacy,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return str(self.consumptionDate)


def add_new_stock(sender,instance,created,**kwargs):
    # print("Signal called")
    if created : #mMeans a Product already exists
        # print("Signal called 1")
        plinkStr = str(instance.productLink)
        plinkSplit =  plinkStr.split(':')
        plinkStrip = plinkSplit[1].strip()
        drug = ProductDetails.objects.get(description = plinkStrip)
        #drug = ProductDetails.objects.get(description = instance.productLink)
        drug_qty = drug.currentStock
        new_drug_qty = drug_qty + instance.deliveredQty
        ProductDetails.objects.filter(description = plinkStrip).update(currentStock = new_drug_qty)
        #ProductDetails.objects.filter(description = instance.productLink).update(currentStock = new_drug_qty)
        # print(instance.deliveredQty)
        # print(new_drug_qty)
        # print(instance.productLink)
    else:
        pass
        # print("Signal called 2")


post_save.connect(add_new_stock, sender=StockDelivered)


def subtract_from_stock(sender, instance, *args, **kwargs):
    plinkStr = str(instance.productLink)
    plinkSplit = plinkStr.split(':')
    plinkStrip = plinkSplit[1].strip()
    drug = ProductDetails.objects.get(description=plinkStrip)

    # drug = ProductDetails.objects.get(description = instance.productLink)
    drug_qty = drug.currentStock
    # print(instance.consumptionQty)
    # print(instance.productLink)
    if drug_qty > 0 and drug_qty >= instance.consumptionQty:
        new_drug_qty = drug_qty - instance.consumptionQty
        ProductDetails.objects.filter(description=plinkStrip).update(currentStock=new_drug_qty)
        # ProductDetails.objects.filter(description=instance.productLink).update(currentStock=new_drug_qty)
        # print(new_drug_qty)
    else:
        new_drug_qty = drug_qty
        ProductDetails.objects.filter(description=plinkStrip).update(currentStock=new_drug_qty)
        # ProductDetails.objects.filter(description=instance.productLink).update(currentStock=new_drug_qty)
        #print(new_drug_qty)
        raise Exception("Too Many Drugs Were Requested For; Current Drugs Available:" + str(drug_qty))


pre_save.connect(subtract_from_stock, sender=TheDailyConsumption)


def check_unique_code_number(sender, instance, *args, **kwargs):
    print(instance.code)



pre_save.connect(check_unique_code_number, sender=ProductDetails)


