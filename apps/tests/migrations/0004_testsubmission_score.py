# Generated by Django 5.2.1 on 2025-07-10 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tests", "0003_alter_testdeployment_test"),
    ]

    operations = [
        migrations.AddField(
            model_name="testsubmission",
            name="score",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
