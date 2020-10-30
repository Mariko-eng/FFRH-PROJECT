# Generated by Django 3.0.3 on 2020-10-24 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0002_delete_targetuserunit'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockDeliveryData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deliveryDate', models.DateTimeField(auto_now_add=True)),
                ('deliveredQty', models.DecimalField(decimal_places=3, max_digits=100)),
                ('productLink', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='analysis.ProductDetailExp')),
            ],
        ),
    ]
