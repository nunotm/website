# Generated by Django 4.1 on 2022-08-06 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("cv", "0015_auto_20220804_2334")]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="education",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="position",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
