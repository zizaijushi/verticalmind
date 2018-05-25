# Generated by Django 2.0.4 on 2018-04-25 05:03

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('object', '0002_objects_userobject'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyReplay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TITLE', models.CharField(max_length=200)),
                ('SLUG', models.SlugField(max_length=500)),
                ('BODY', models.TextField()),
                ('CREATE_DT', models.DateTimeField(default=datetime.datetime(2018, 4, 25, 5, 3, 1, 386093, tzinfo=utc))),
                ('LAST_DT', models.DateTimeField(auto_now=True)),
                ('AUTHOR', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='DailyReplay', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('TITLE',),
            },
        ),
        migrations.AlterField(
            model_name='apps',
            name='AUTHOR',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Apps', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='objects',
            name='CREATER',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Objects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userobject',
            name='USER',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='UserObject', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dailyreplay',
            name='OBJECT',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='object.Objects'),
        ),
        migrations.AlterIndexTogether(
            name='dailyreplay',
            index_together={('id', 'SLUG')},
        ),
    ]