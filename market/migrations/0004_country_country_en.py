# Generated by Django 2.0.2 on 2018-03-22 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0003_auto_20180322_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='COUNTRY_EN',
            field=models.CharField(default=1, help_text='ENGLISH', max_length=20, verbose_name='ENGLISH'),
            preserve_default=False,
        ),
    ]