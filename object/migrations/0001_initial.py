# Generated by Django 2.0.4 on 2018-04-24 01:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Apps',
            fields=[
                ('APP_ID', models.IntegerField(auto_created=True, max_length=10, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('APP_NAME', models.CharField(max_length=50, verbose_name='app名称')),
                ('START_DT', models.DateField(verbose_name='上线日期')),
                ('REQUIER_DT', models.DateField(null=True, verbose_name='提出需求日期')),
                ('AUTHOR', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='作者', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]