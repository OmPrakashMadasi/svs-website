# Generated by Django 5.0.8 on 2024-08-08 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(default=2, upload_to='uploads/product/'),
            preserve_default=False,
        ),
    ]