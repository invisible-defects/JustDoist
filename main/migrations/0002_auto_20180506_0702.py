# Generated by Django 2.0.5 on 2018-05-06 07:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.IntegerField()),
                ('title', models.CharField(max_length=256)),
                ('text', models.CharField(max_length=1000)),
                ('image', models.URLField(max_length=500)),
                ('is_premium', models.BooleanField()),
                ('users', models.ManyToManyField(related_name='achievements', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='achievment',
            name='users',
        ),
        migrations.DeleteModel(
            name='Achievment',
        ),
    ]