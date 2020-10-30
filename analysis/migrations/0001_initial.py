# Generated by Django 3.0.3 on 2020-10-24 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HospitalUserUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_unit', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ProductDetailExp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(default=100000, unique=True)),
                ('description', models.CharField(max_length=500)),
                ('ven', models.CharField(blank=True, max_length=5, null=True)),
                ('unit', models.DecimalField(decimal_places=1, max_digits=100, null=True)),
                ('price', models.DecimalField(decimal_places=1, max_digits=100, null=True)),
                ('planned_Qty_2Month_Mean', models.DecimalField(decimal_places=1, max_digits=100, null=True)),
                ('currentStock', models.DecimalField(decimal_places=3, default=0, max_digits=100)),
            ],
        ),
        migrations.CreateModel(
            name='TargetUserUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_unit', models.CharField(max_length=100)),
                ('productDetail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysis.ProductDetailExp')),
            ],
        ),
        migrations.CreateModel(
            name='TargetHospitalUserUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productDetail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysis.ProductDetailExp')),
                ('user_unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysis.HospitalUserUnit')),
            ],
        ),
        migrations.CreateModel(
            name='ConsumptionData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consumptionDate', models.DateTimeField()),
                ('consumptionQty', models.DecimalField(decimal_places=1, max_digits=100)),
                ('productDetail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.ProductDetailExp')),
            ],
        ),
    ]