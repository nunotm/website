# Generated by Django 3.1.7 on 2022-08-04 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0014_course_certificate_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='education',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='position',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
