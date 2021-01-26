# Generated by Django 3.0 on 2020-12-31 07:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_user_usertype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('product_price', models.CharField(max_length=100)),
                ('product_image', models.ImageField(upload_to='images/')),
                ('product_desc', models.TextField()),
                ('product_category', models.CharField(choices=[('Kids', 'Kids'), ('Women', 'Women'), ('Men', 'Men')], max_length=100)),
                ('product_seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.User')),
            ],
        ),
    ]
