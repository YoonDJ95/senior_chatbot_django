# Generated by Django 5.1.2 on 2024-10-23 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_resume_experience_education'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resume',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='resume',
            name='detailed_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='resume',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
