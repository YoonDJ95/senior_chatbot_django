# Generated by Django 5.1.2 on 2024-10-23 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_profile_business_types_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='business_types',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
