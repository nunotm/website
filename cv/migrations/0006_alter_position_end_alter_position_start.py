# Generated by Django 4.0 on 2022-08-03 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0005_alter_position_end_alter_position_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='end',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='start',
            field=models.DateField(blank=True, null=True),
        ),
    ]
