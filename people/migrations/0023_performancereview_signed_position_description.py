# Generated by Django 3.0.7 on 2021-02-10 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0022_auto_20210209_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancereview',
            name='signed_position_description',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='signed position description'),
        ),
    ]
