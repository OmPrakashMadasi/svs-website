# Generated by Django 5.1 on 2024-08-26 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0012_alter_testimonial_customer_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testimonial',
            name='customer_rating',
            field=models.PositiveIntegerField(),
        ),
    ]